#!/usr/bin/env python3
"""Reproducibility script for "BERT-Based Requirement Classification for Agile Backlog Management".

One file, five stages:
  data      download PROMISE NFR (Zenodo 10.5281/zenodo.268542), verify MD5, parse ARFF -> data/promise_nfr.csv
  folds     build the evaluation splits
              random : stratified 10-fold (StratifiedKFold, shuffle, seed)
              grouped: project-held-out 5-fold (StratifiedGroupKFold by PROMISE project id, shuffle, seed)
  baselines TF-IDF + {Multinomial NB, LinearSVM, Logistic Regression}; out-of-fold predictions
  bert      DistilBERT fine-tuning (CPU), out-of-fold predictions + max softmax probability; resumable per fold
  evaluate  metrics, mean/SD over seeds, exact McNemar tests, confidence-gate table -> outputs/results.json
  figures   Fig. 4 of the paper -> outputs/fig4_results.{png,pdf}

Usage examples
  python reproduce.py data
  python reproduce.py folds
  python reproduce.py baselines                       # all tasks, both protocols, seeds 42 43 44
  python reproduce.py bert --task A --protocol random  --seed 42
  python reproduce.py bert --task A --protocol grouped --seed 43
  python reproduce.py evaluate
  python reproduce.py figures
  python reproduce.py all        # everything in the paper (about 2.5 h on a 2-core CPU)

Tasks: A = functional (F) vs non-functional (all other labels), 625 items;
       B = the four most frequent NFR classes US, SE, O, PE, 249 items.
"""
import argparse, csv, hashlib, io, json, os, random, re, sys, tarfile, time, urllib.request
from math import comb
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, 'data'); OUT = os.path.join(ROOT, 'outputs'); PRED = os.path.join(OUT, 'predictions')
ZENODO_URL = 'https://zenodo.org/api/records/268542/files/nfr.tar/content'
ZENODO_MD5 = 'c3e68d6c9c84b44b5636383b353a522e'
SEEDS = [42, 43, 44]
BASELINES = ['MNB', 'LogReg', 'LinearSVM']
TASK_LABELS = {'A': ['F', 'NFR'], 'B': ['US', 'SE', 'O', 'PE']}
N_SPLITS = {'random': 10, 'grouped': 5}
# DistilBERT settings (as reported in Sec. IV-A of the paper)
BERT = dict(model='distilbert-base-uncased', epochs=5, lr=5e-5, batch=8, maxlen=64, frozen_blocks=2,
            weight_decay=0.01, warmup=0.1, clip=1.0, eval_batch=32)


# ----------------------------------------------------------------------------- data
def stage_data(_):
    os.makedirs(DATA, exist_ok=True)
    tar_path = os.path.join(DATA, 'nfr.tar')
    if not os.path.exists(tar_path):
        print('downloading', ZENODO_URL)
        urllib.request.urlretrieve(ZENODO_URL, tar_path)
    md5 = hashlib.md5(open(tar_path, 'rb').read()).hexdigest()
    assert md5 == ZENODO_MD5, f'MD5 mismatch {md5}'
    with tarfile.open(tar_path) as tf:
        member = [m for m in tf.getmembers() if m.name.endswith('nfr.arff')][0]
        lines = tf.extractfile(member).read().decode('latin-1').splitlines()
    rows = []
    for line in lines:
        line = line.strip()
        if re.match(r'^\d+,', line):
            m = re.match(r"^(\d+),'(.*)',([A-Z]+)$", line)
            assert m, line[:80]
            rows.append((int(m.group(1)), m.group(2).replace("\\'", "'"), m.group(3)))
    with open(os.path.join(DATA, 'promise_nfr.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['project', 'text', 'label']); w.writerows(rows)
    print(len(rows), 'requirements,', len({r[0] for r in rows}), 'projects')
    assert len(rows) == 625


def load_task(task):
    import pandas as pd
    df = pd.read_csv(os.path.join(DATA, 'promise_nfr.csv'))
    if task == 'A':
        d = df.assign(y=np.where(df.label == 'F', 'F', 'NFR'))
    else:
        d = df[df.label.isin(TASK_LABELS['B'])].assign(y=lambda x: x.label)
    return d.reset_index(drop=True)


# ----------------------------------------------------------------------------- folds
def make_folds(task, protocol, seed):
    from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
    d = load_task(task); X, y, g = d.text.values, d.y.values, d.project.values
    if protocol == 'random':
        sp = StratifiedKFold(n_splits=10, shuffle=True, random_state=seed).split(X, y)
    else:
        sp = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed).split(X, y, g)
    folds = [(tr.tolist(), te.tolist()) for tr, te in sp]
    if protocol == 'grouped':   # sanity: no project on both sides
        for tr, te in folds:
            assert not set(g[tr]) & set(g[te])
    return folds


def stage_folds(_):
    os.makedirs(OUT, exist_ok=True)
    allf = {}
    for task in 'AB':
        for protocol in ('random', 'grouped'):
            for seed in SEEDS:
                d = load_task(task); folds = make_folds(task, protocol, seed)
                allf[f'{task}|{protocol}|{seed}'] = folds
                if protocol == 'grouped':
                    print(task, protocol, seed, 'test projects per fold:',
                          [sorted(set(d.project.values[te].tolist())) for _, te in folds])
    json.dump(allf, open(os.path.join(OUT, 'folds.json'), 'w'))


def get_folds(task, protocol, seed):
    return json.load(open(os.path.join(OUT, 'folds.json')))[f'{task}|{protocol}|{seed}']


# ----------------------------------------------------------------------------- prediction CSVs
def pred_path(task, protocol, seed):
    return os.path.join(PRED, f'{task}_{protocol}_seed{seed}.csv')


def read_preds(task, protocol, seed):
    import pandas as pd
    p = pred_path(task, protocol, seed)
    if os.path.exists(p):
        return pd.read_csv(p, keep_default_na=False)
    d = load_task(task); folds = get_folds(task, protocol, seed)
    fold = np.empty(len(d), dtype=int)
    for k, (_, te) in enumerate(folds): fold[te] = k
    return pd.DataFrame({'idx': range(len(d)), 'project': d.project, 'fold': fold, 'gold': d.y, 'text': d.text})


def write_preds(df, task, protocol, seed):
    os.makedirs(PRED, exist_ok=True); df.to_csv(pred_path(task, protocol, seed), index=False)


# ----------------------------------------------------------------------------- baselines
def baseline_model(name, seed):
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.svm import LinearSVC
    from sklearn.linear_model import LogisticRegression
    return {'MNB': lambda: MultinomialNB(alpha=0.1),
            'LinearSVM': lambda: LinearSVC(C=1.0, class_weight='balanced', random_state=seed),
            'LogReg': lambda: LogisticRegression(C=10, max_iter=2000, class_weight='balanced')}[name]()


def stage_baselines(args):
    from sklearn.feature_extraction.text import TfidfVectorizer
    for task in 'AB':
        d = load_task(task); X, y = d.text.values, d.y.values
        for protocol in ('random', 'grouped'):
            for seed in SEEDS:
                df = read_preds(task, protocol, seed)
                for name in BASELINES:
                    pr = np.empty(len(y), dtype=object)
                    for tr, te in get_folds(task, protocol, seed):
                        vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1, stop_words='english')
                        clf = baseline_model(name, seed).fit(vec.fit_transform(X[tr]), y[tr])
                        pr[te] = clf.predict(vec.transform(X[te]))
                    df[name] = pr
                write_preds(df, task, protocol, seed)
                print('baselines done', task, protocol, seed)


# ----------------------------------------------------------------------------- DistilBERT
def stage_bert(args):
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
    from torch.utils.data import DataLoader, TensorDataset
    torch.set_num_threads(args.threads)
    task, protocol, seed = args.task, args.protocol, args.seed
    d = load_task(task); labels = TASK_LABELS[task]; lab2id = {l: i for i, l in enumerate(labels)}
    texts = d.text.tolist(); y = np.array([lab2id[v] for v in d.y])
    folds = get_folds(task, protocol, seed)
    tok = AutoTokenizer.from_pretrained(BERT['model'])
    enc = tok(texts, truncation=True, max_length=BERT['maxlen'], padding='max_length', return_tensors='pt')
    state_p = os.path.join(PRED, f'.bert_state_{task}_{protocol}_{seed}.json')
    state = json.load(open(state_p)) if os.path.exists(state_p) else {'pred': [''] * len(y), 'pmax': [''] * len(y), 'done': [], 'secs': []}
    only = None if args.folds is None else [int(k) for k in args.folds.split(',')]
    for k, (tr, te) in enumerate(folds):
        if k in state['done'] or (only is not None and k not in only):
            continue
        random.seed(seed + k); np.random.seed(seed + k); torch.manual_seed(seed + k)
        model = AutoModelForSequenceClassification.from_pretrained(BERT['model'], num_labels=len(labels))
        for p in model.distilbert.embeddings.parameters(): p.requires_grad = False
        for layer in model.distilbert.transformer.layer[:BERT['frozen_blocks']]:
            for p in layer.parameters(): p.requires_grad = False
        counts = np.bincount(y[tr], minlength=len(labels))
        w = torch.tensor(len(tr) / (len(labels) * counts), dtype=torch.float)       # inverse-frequency weights (Eq. 1)
        lossf = torch.nn.CrossEntropyLoss(weight=w)
        ds = TensorDataset(enc['input_ids'][tr], enc['attention_mask'][tr], torch.tensor(y[tr]))
        dl = DataLoader(ds, batch_size=BERT['batch'], shuffle=True, generator=torch.Generator().manual_seed(seed + k))
        opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=BERT['lr'], weight_decay=BERT['weight_decay'])
        total = BERT['epochs'] * len(dl); sch = get_linear_schedule_with_warmup(opt, int(BERT['warmup'] * total), total)
        t0 = time.time(); model.train()
        for ep in range(BERT['epochs']):
            tl = 0.0
            for ids, am, yy in dl:
                opt.zero_grad(); loss = lossf(model(input_ids=ids, attention_mask=am).logits, yy)
                loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), BERT['clip']); opt.step(); sch.step(); tl += loss.item()
            print(f'{task} {protocol} seed {seed} fold {k} epoch {ep} loss {tl / len(dl):.4f} t={time.time() - t0:.0f}s', flush=True)
        model.eval()
        with torch.no_grad():
            eb = BERT['eval_batch']
            logits = torch.cat([model(input_ids=enc['input_ids'][te][i:i + eb], attention_mask=enc['attention_mask'][te][i:i + eb]).logits
                                for i in range(0, len(te), eb)])
        assert logits.shape[0] == len(te)
        prob = torch.softmax(logits, 1).numpy()
        for i, idx in enumerate(te):
            state['pred'][idx] = labels[int(prob[i].argmax())]; state['pmax'][idx] = float(prob[i].max())
        state['done'].append(k); state['secs'].append(time.time() - t0)
        os.makedirs(PRED, exist_ok=True); json.dump(state, open(state_p, 'w'))
        print(f'{task} {protocol} seed {seed} fold {k} acc {float((prob.argmax(1) == y[te]).mean()):.3f} secs {time.time() - t0:.0f}', flush=True)
        del model, opt
    if len(state['done']) == len(folds):
        df = read_preds(task, protocol, seed)
        df['DistilBERT'] = state['pred']; df['DistilBERT_pmax'] = state['pmax']
        df['DistilBERT_secs_per_fold'] = float(np.mean(state['secs']))
        write_preds(df, task, protocol, seed)
        print('DistilBERT complete', task, protocol, seed)


# ----------------------------------------------------------------------------- evaluation
def metrics(y, pred, labels):
    from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix
    p, r, f, s = precision_recall_fscore_support(y, pred, labels=labels, zero_division=0)
    mp, mr, mf, _ = precision_recall_fscore_support(y, pred, labels=labels, average='macro', zero_division=0)
    return {'per_class': {l: {'P': float(p[i]), 'R': float(r[i]), 'F1': float(f[i]), 'n': int(s[i])} for i, l in enumerate(labels)},
            'macro_P': float(mp), 'macro_R': float(mr), 'macro_F1': float(mf), 'acc': float(accuracy_score(y, pred)),
            'cm': confusion_matrix(y, pred, labels=labels).tolist()}


def mcnemar_exact(b, c):
    """Exact two-sided McNemar test: b = only model 1 correct, c = only model 2 correct."""
    n = b + c
    if n == 0: return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def stage_evaluate(_):
    res = {'runs': {}, 'summary': {}, 'mcnemar': {}, 'gate': {}}
    for task in 'AB':
        labels = TASK_LABELS[task]
        for protocol in ('random', 'grouped'):
            for seed in SEEDS:
                p = pred_path(task, protocol, seed)
                if not os.path.exists(p): continue
                df = read_preds(task, protocol, seed); y = df.gold.values
                models = BASELINES + (['DistilBERT'] if 'DistilBERT' in df and (df.DistilBERT != '').all() else [])
                for m in models:
                    r = metrics(y, df[m].values, labels)
                    r['fold_acc'] = [float((df[m].values[df.fold == k] == y[df.fold == k]).mean()) for k in sorted(df.fold.unique())]
                    if m == 'DistilBERT': r['secs_per_fold'] = float(df.DistilBERT_secs_per_fold.iloc[0])
                    res['runs'][f'{task}|{protocol}|{seed}|{m}'] = r
                if 'DistilBERT' in models:
                    for m in BASELINES:
                        bo = (df.DistilBERT.values == y); so = (df[m].values == y)
                        b, c = int((bo & ~so).sum()), int((~bo & so).sum())
                        res['mcnemar'][f'{task}|{protocol}|{seed}|DistilBERT_vs_{m}'] = {'bert_only': b, 'base_only': c, 'p': mcnemar_exact(b, c)}
                    if 'DistilBERT_pmax' in df and (df.DistilBERT_pmax != '').all():
                        pm = df.DistilBERT_pmax.astype(float).values; ok = df.DistilBERT.values == y
                        res['gate'][f'{task}|{protocol}|{seed}'] = {str(t): {'coverage': float((pm >= t).mean()),
                                                                           'precision_auto': float(ok[pm >= t].mean()) if (pm >= t).any() else None}
                                                                   for t in (0.5, 0.8, 0.9, 0.95, 0.99)}
            for m in BASELINES + ['DistilBERT']:
                runs = [res['runs'][k] for k in res['runs'] if k.startswith(f'{task}|{protocol}|') and k.endswith(f'|{m}')]
                if runs:
                    mf = [r['macro_F1'] for r in runs]; ac = [r['acc'] for r in runs]
                    res['summary'][f'{task}|{protocol}|{m}'] = {'n_seeds': len(runs), 'macro_F1_mean': float(np.mean(mf)),
                                                               'macro_F1_sd': float(np.std(mf, ddof=1)) if len(mf) > 1 else None,
                                                               'macro_F1_min': float(min(mf)), 'macro_F1_max': float(max(mf)),
                                                               'acc_mean': float(np.mean(ac)), 'acc_sd': float(np.std(ac, ddof=1)) if len(ac) > 1 else None}
    json.dump(res, open(os.path.join(OUT, 'results.json'), 'w'), indent=1)
    print(f"{'task|protocol|model':34s} seeds  macroF1 mean (sd) [min-max]   acc mean")
    for k, v in res['summary'].items():
        sd = f"{v['macro_F1_sd']:.3f}" if v['macro_F1_sd'] is not None else '  -  '
        print(f"{k:34s} {v['n_seeds']}    {v['macro_F1_mean']:.3f} ({sd}) [{v['macro_F1_min']:.3f}-{v['macro_F1_max']:.3f}]   {v['acc_mean']:.3f}")
    for k, v in res['mcnemar'].items(): print('McNemar', k, v)
    for k, v in res['gate'].items(): print('Gate', k, {t: (round(x['coverage'], 3), round(x['precision_auto'], 3) if x['precision_auto'] else None) for t, x in v.items()})


# ----------------------------------------------------------------------------- figures
def stage_figures(_):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'STIXGeneral', 'mathtext.fontset': 'stix', 'font.size': 7.5,
                         'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6})
    S = json.load(open(os.path.join(OUT, 'results.json')))['summary']
    models = [('MNB', 'TF-IDF+NB'), ('LogReg', 'TF-IDF+LogReg'), ('LinearSVM', 'TF-IDF+SVM'), ('DistilBERT', 'DistilBERT')]
    colors = ['#C9D6E8', '#8FA9CC', '#3A5A80', '#C8833A']; hatches = ['', '', '', '//']
    fig, axes = plt.subplots(1, 2, figsize=(3.45, 2.35), sharey=True)
    for ax, task, title in zip(axes, 'AB', ['Task A: FR vs. NFR', 'Task B: US/SE/O/PE']):
        x = np.arange(2); w = 0.2
        for i, (m, lab) in enumerate(models):
            vals, errs = [], []
            for prot in ('random', 'grouped'):
                s = S[f'{task}|{prot}|{m}']; vals.append(s['macro_F1_mean']); errs.append(s['macro_F1_sd'] or 0)
            ax.bar(x + (i - 1.5) * w, vals, w, yerr=errs, capsize=1.2, error_kw={'elinewidth': 0.5, 'capthick': 0.5},
                   label=lab, color=colors[i], edgecolor='#333333', linewidth=0.4, hatch=hatches[i])
        ax.set_xticks(x); ax.set_xticklabels(['Random\n10-fold', 'Project-held-\nout 5-fold'])
        ax.set_title(title, fontsize=7.5); ax.set_ylim(0.4, 1.0); ax.grid(axis='y', lw=0.3, alpha=0.6); ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    axes[0].set_ylabel('Macro-F1 (mean over seeds)')
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, ncol=4, fontsize=6.3, frameon=False, loc='upper center', bbox_to_anchor=(0.53, 1.0), handlelength=1.2, columnspacing=0.7)
    fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=0.6)
    for ext in ('png', 'pdf'): fig.savefig(os.path.join(OUT, f'fig4_results.{ext}'), dpi=300)
    print('figure written')


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('stage', choices=['data', 'folds', 'baselines', 'bert', 'evaluate', 'figures', 'all'])
    ap.add_argument('--task', choices=['A', 'B']); ap.add_argument('--protocol', choices=['random', 'grouped'])
    ap.add_argument('--seed', type=int, default=42); ap.add_argument('--folds', help='comma-separated fold ids (optional)')
    ap.add_argument('--threads', type=int, default=2)
    a = ap.parse_args()
    if a.stage == 'all':
        stage_data(a); stage_folds(a); stage_baselines(a)
        runs = [('A', 'random', 42), ('B', 'random', 42)] + [(t, 'grouped', s) for t in 'AB' for s in SEEDS]
        for t, p, s in runs:
            a.task, a.protocol, a.seed, a.folds = t, p, s, None; stage_bert(a)
        stage_evaluate(a); stage_figures(a)
    else:
        {'data': stage_data, 'folds': stage_folds, 'baselines': stage_baselines, 'bert': stage_bert,
         'evaluate': stage_evaluate, 'figures': stage_figures}[a.stage](a)


if __name__ == '__main__':
    main()
