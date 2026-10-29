"""Fine-tune DistilBERT (distilbert-base-uncased) on the same stratified 10-fold splits used by baselines.py.
CPU-only, 2 cores, ~2 GB RAM: the embedding layer is frozen to reduce optimizer memory.
Usage: python finetune_bert.py A|B"""
import json, sys, time, os, random, numpy as np, torch
from torch.utils.data import DataLoader, TensorDataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup

TASK = sys.argv[1]
EPOCHS = int(os.environ.get('EPOCHS', 5)); LR = 5e-5; BS = 8; MAXLEN = 64; SEED = 42
MODEL = 'distilbert-base-uncased'
FROZEN = 2  # lower transformer blocks frozen (memory limit)
torch.set_num_threads(2)
F = json.load(open('/home/user/work/exp/folds.json'))[TASK]
texts, y_str, labels = F['texts'], F['y'], F['labels']
lab2id = {l: i for i, l in enumerate(labels)}; y = np.array([lab2id[v] for v in y_str])
tok = AutoTokenizer.from_pretrained(MODEL)
enc = tok(texts, truncation=True, max_length=MAXLEN, padding='max_length', return_tensors='pt')
lens = (enc['attention_mask'].sum(1)).numpy()
print('token length: median', np.median(lens), 'max', lens.max(), 'truncated', int((lens >= MAXLEN).sum()), flush=True)
out_path = f'/home/user/work/exp/bert_preds_{TASK}.json'
state = json.load(open(out_path)) if os.path.exists(out_path) else {'pred': [None] * len(y), 'done': [], 'secs': []}

for k, (tr, te) in enumerate(F['folds']):
    if k in state['done']:
        continue
    random.seed(SEED + k); np.random.seed(SEED + k); torch.manual_seed(SEED + k)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=len(labels))
    for p in model.distilbert.embeddings.parameters():
        p.requires_grad = False
    for layer in model.distilbert.transformer.layer[:FROZEN]:
        for p in layer.parameters():
            p.requires_grad = False
    counts = np.bincount(y[tr], minlength=len(labels))
    w = torch.tensor(len(tr) / (len(labels) * counts), dtype=torch.float)   # inverse-frequency class weights
    lossf = torch.nn.CrossEntropyLoss(weight=w)
    ds = TensorDataset(enc['input_ids'][tr], enc['attention_mask'][tr], torch.tensor(y[tr]))
    dl = DataLoader(ds, batch_size=BS, shuffle=True, generator=torch.Generator().manual_seed(SEED + k))
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=LR, weight_decay=0.01)
    total = EPOCHS * len(dl); sch = get_linear_schedule_with_warmup(opt, int(0.1 * total), total)
    t0 = time.time(); model.train()
    for ep in range(EPOCHS):
        tl = 0
        for ids, am, yy in dl:
            opt.zero_grad(); loss = lossf(model(input_ids=ids, attention_mask=am).logits, yy)
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sch.step(); tl += loss.item()
        print(f'fold {k} epoch {ep} loss {tl/len(dl):.4f} t={time.time()-t0:.0f}s', flush=True)
    model.eval()
    with torch.no_grad():
        logits = torch.cat([model(input_ids=enc['input_ids'][te][i:i+32], attention_mask=enc['attention_mask'][te][i:i+32]).logits
                            for i in range(0, len(te), 32)])
    assert logits.shape[0] == len(te)
    pr = logits.argmax(1).numpy()
    for i, idx in enumerate(te):
        state['pred'][idx] = labels[pr[i]]
    state['done'].append(k); state['secs'].append(time.time() - t0)
    json.dump(state, open(out_path, 'w'))
    acc = float((pr == y[te]).mean()); print(f'fold {k} acc {acc:.3f} secs {time.time()-t0:.0f}', flush=True)
    del model, opt
print('ALL_DONE', flush=True)
