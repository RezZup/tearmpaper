"""Builds paper_v2_experiments.ipynb (run on Colab T4)."""
import nbformat as nbf

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip()))

md(r"""
# Paper v2: external validation, labelling-scheme test and an LLM zero-shot baseline (Colab T4)

**Before you run:** Runtime → Change runtime type → **T4 GPU**. Then Runtime → **Run all**.
Expected time on a T4: about 30–45 minutes. Results are saved to Google Drive after every run, so if Colab disconnects just press Run all again and it resumes.

**What this notebook adds to the paper (nothing here needs human annotation):**
1. **External test set (main new result).** Models are trained on all 625 PROMISE requirements and tested on four *public industrial requirement sets labelled by other researchers* (Dronology, ReqView, Leeds library, WASP; 331 requirements; Dalpiaz et al., RE'19, Zenodo doi:10.5281/zenodo.3309669, GPL-3.0). None of these texts occur in PROMISE (checked in cell 3).
2. **Labelling-scheme test.** The same models are trained a second time on Dalpiaz et al.'s *relabelled* PROMISE ("has a quality aspect" instead of the original F/NFR label) to see whether the label definition, not the encoder, drives external errors.
3. **Does the confidence gate transfer?** Temperature and threshold are chosen on PROMISE out-of-fold predictions from your earlier run (`bert_paper_results`) and then applied unchanged to the external sets.
4. **Zero-shot LLM baseline** (Qwen2.5-1.5B-Instruct, no training) on PROMISE Task A, Task B and the external sets.

Same hyper-parameters as `rezz_bert_experiments.ipynb` (5 epochs, batch 16, max length 64, class-weighted loss, seeds 42–44) and the same TF-IDF + linear SVM baseline.

**When it finishes:** the last cell downloads `paper_v2_results.zip`. Upload that zip (or push the folder to GitHub) and share it with me. Do not edit any file in it.
""")

code(r"""
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "transformers", "accelerate", "sentencepiece", "scikit-learn", "scipy", "pandas", "matplotlib"], check=False)

import os, io, re, csv, json, time, glob, random, tarfile, zipfile, platform, urllib.request
import numpy as np, pandas as pd, torch
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from scipy.optimize import minimize_scalar
import transformers
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          AutoModelForCausalLM, get_linear_schedule_with_warmup)

dev = "cuda" if torch.cuda.is_available() else "cpu"
print("Device:", dev, "|", torch.cuda.get_device_name(0) if dev == "cuda" else "no GPU")
if dev == "cpu":
    print("WARNING: no GPU. Switch the runtime to T4 GPU, otherwise this takes many hours.")
""")

code(r"""
# ---------------- Configuration ----------------
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
QUICK_TEST = os.environ.get("V2_QUICK_TEST", "0") == "1"   # leave False for the real run

MODELS = {
    "distilbert": ("distilbert-base-uncased", 5e-5),
    "bert":       ("bert-base-uncased", 3e-5),
    "roberta":    ("roberta-base", 3e-5),
}
SEEDS = [42, 43, 44]
EPOCHS, BATCH, MAX_LEN = 5, 16, 64
RUN_LLM = True
LLM_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
LLM_LIMIT = None                     # None = all items
SCHEMES = ["orig", "reclass"]        # orig = PROMISE F/NFR labels; reclass = Dalpiaz IsQuality labels
N_BOOT = 2000

if QUICK_TEST:                        # tiny smoke test only; numbers are meaningless
    MODELS = {"distilbert": ("google/bert_uncased_L-2_H-128_A-2", 5e-5)}            # tiny stand-in, code-path check only
    SEEDS, EPOCHS, LLM_NAME, LLM_LIMIT, N_BOOT = [42], 1, "HuggingFaceTB/SmolLM2-135M-Instruct", 40, 200

# Where results go (Drive survives disconnects)
try:
    from google.colab import drive
    drive.mount("/content/drive")
    BASE = "/content/drive/MyDrive"
except Exception:
    BASE = "."
OUT = f"{BASE}/paper_v2_results" + ("_QUICKTEST" if QUICK_TEST else "")
os.makedirs(OUT, exist_ok=True)

# Earlier run with out-of-fold predictions (used only for the calibration-transfer test)
BPR = next((p for p in [f"{BASE}/bert_paper_results", "bert_paper_results", "/content/bert_paper_results"]
            if os.path.exists(f"{p}/A_project_distilbert_42.npz")), None)
if BPR is None and os.path.exists("bert_paper_results.zip"):
    zipfile.ZipFile("bert_paper_results.zip").extractall("bert_paper_results"); BPR = "bert_paper_results"
print("Saving to:", OUT)
print("Earlier out-of-fold results:", BPR or "NOT FOUND -> calibration-transfer test will be skipped "
      "(upload bert_paper_results.zip to the Colab file panel and re-run to include it)")

json.dump(dict(python=platform.python_version(), torch=torch.__version__, transformers=transformers.__version__,
               gpu=torch.cuda.get_device_name(0) if dev == "cuda" else "cpu", quick_test=QUICK_TEST,
               models=MODELS, seeds=SEEDS, epochs=EPOCHS, batch=BATCH, max_len=MAX_LEN, llm=LLM_NAME if RUN_LLM else None),
          open(f"{OUT}/environment.json", "w"), indent=1)
""")

code(r"""
# ---------------- Data ----------------
os.makedirs("data", exist_ok=True)
def fetch(url, path):
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    return path

# PROMISE NFR (Zenodo record 268542 ships a tar file containing nfr/nfr.arff)
arff_path = "data/nfr/nfr.arff"
if not os.path.exists(arff_path):
    if os.path.exists("nfr.arff"):                      # manual upload fallback
        os.makedirs("data/nfr", exist_ok=True); os.replace("nfr.arff", arff_path)
    else:
        tarfile.open(fetch("https://zenodo.org/api/records/268542/files/nfr.tar/content", "data/nfr.tar")).extractall("data")
rows, in_data = [], False
for line in open(arff_path, encoding="utf-8", errors="ignore"):
    line = line.strip()
    if line.lower().startswith("@data"): in_data = True; continue
    if in_data and line and not line.startswith("%"):
        rows.append(next(csv.reader([line], quotechar="'", escapechar="\\")))
P = pd.DataFrame(rows, columns=["project", "text", "cls"])
P["project"] = P.project.astype(int); P["cls"] = P.cls.str.strip()
assert len(P) == 625, len(P)

# Dalpiaz et al. RE'19 materials (Zenodo 3309669): relabelled PROMISE + public industrial sets
zp = fetch("https://zenodo.org/api/records/3309669/files/explainable-re/RE-2019-Materials-v0.zip/content", "data/re19.zip")
zipfile.ZipFile(zp).extractall("data/re19")
TAG = glob.glob("data/re19/*/Manually tagged datasets")[0]

R = pd.read_csv(f"{TAG}/promise-reclass.csv", encoding="latin1")
assert len(R) == 625 and (R.ProjectID.values == P.project.values).all() and (R.Class.values == P.cls.values).all(), \
    "relabelled PROMISE is not row-aligned with nfr.arff"
P["y_orig"] = (P.cls != "F").astype(int)                 # 1 = NFR  (classes sorted: FR=0, NFR=1, as before)
P["isF"], P["isQ"] = R.IsFunctional.values, R.IsQuality.values
P["y_reclass"] = P.isQ                                   # 1 = has a quality aspect

ext = []
for name in ["dronology", "reqview", "leeds", "wasp"]:
    d = pd.read_csv(f"{TAG}/{name}.csv", encoding="latin1")
    ext.append(pd.DataFrame(dict(dataset=name, text=d.RequirementText.astype(str).str.strip(),
                                 isF=d.IsFunctional.astype(int), isQ=d.IsQuality.astype(int))))
E = pd.concat(ext, ignore_index=True)
n_raw = len(E); E = E[(E.isF + E.isQ) > 0].reset_index(drop=True)   # drop items labelled neither F nor Q
E["kind"] = np.select([(E.isF == 1) & (E.isQ == 0), (E.isF == 0) & (E.isQ == 1)], ["onlyF", "onlyQ"], "FQ")

norm = lambda s: re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()
overlap = E.text.map(norm).isin(set(P.text.map(norm))).sum()
assert overlap == 0, f"{overlap} external texts also occur in PROMISE"

data_card = dict(promise=len(P), promise_classes=P.cls.value_counts().to_dict(),
                 reclass_counts={f"F{a}Q{b}": int(n) for (a, b), n in P.groupby(["isF", "isQ"]).size().items()},
                 external_raw=n_raw, external_used=len(E), external_dropped_neither=n_raw - len(E),
                 external_by_kind=E.groupby(["dataset", "kind"]).size().unstack(fill_value=0).to_dict(orient="index"),
                 text_overlap_with_promise=int(overlap))
json.dump(data_card, open(f"{OUT}/data_card.json", "w"), indent=1, default=int)
print(json.dumps(data_card, indent=1, default=int))
""")

code(r"""
# ---------------- Models (identical to rezz_bert_experiments.ipynb) ----------------
def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s); torch.cuda.manual_seed_all(s)

def finetune_predict(model_name, lr, tr_text, tr_y, te_text, n_cls, seed):
    set_seed(seed)
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=n_cls).to(dev)
    enc = lambda t: tok(list(t), truncation=True, max_length=MAX_LEN, padding=True, return_tensors="pt")
    Xtr, Xte = enc(tr_text), enc(te_text)
    ytr = torch.tensor(tr_y)
    counts = np.bincount(tr_y, minlength=n_cls).clip(min=1)
    w = torch.tensor(len(tr_y) / (n_cls * counts), dtype=torch.float, device=dev)
    lossf = torch.nn.CrossEntropyLoss(weight=w)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    steps = EPOCHS * int(np.ceil(len(tr_y) / BATCH))
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    model.train()
    for ep in range(EPOCHS):
        perm = torch.randperm(len(tr_y))
        for i in range(0, len(perm), BATCH):
            idx = perm[i:i + BATCH]
            out = model(input_ids=Xtr["input_ids"][idx].to(dev), attention_mask=Xtr["attention_mask"][idx].to(dev))
            loss = lossf(out.logits, ytr[idx].to(dev))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sch.step(); opt.zero_grad()
    model.eval(); logits = []
    with torch.no_grad():
        for i in range(0, len(te_text), 64):
            o = model(input_ids=Xte["input_ids"][i:i + 64].to(dev), attention_mask=Xte["attention_mask"][i:i + 64].to(dev))
            logits.append(o.logits.float().cpu())
    del model, opt
    if dev == "cuda": torch.cuda.empty_cache()
    return torch.cat(logits).numpy()

def svm_fit_predict(tr_text, tr_y, te_text):
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english")
    clf = LinearSVC(C=1, class_weight="balanced").fit(vec.fit_transform(tr_text), tr_y)
    Xte = vec.transform(te_text)
    return clf.predict(Xte), clf.decision_function(Xte)
""")

code(r"""
# ---------------- Experiment 1 + 2: train on all PROMISE, test on the external sets ----------------
def train_set(scheme):
    if scheme == "orig":
        return P.text.values, P.y_orig.values
    keep = (P.isF + P.isQ) > 0                         # drop the 13 PROMISE items labelled neither F nor Q
    return P.text.values[keep], P.y_reclass.values[keep]

for scheme in SCHEMES:
    tr_text, tr_y = train_set(scheme)
    for seed in SEEDS:
        for name in ["svm"] + list(MODELS):
            f = f"{OUT}/ext_{scheme}_{name}_{seed}.npz"
            if os.path.exists(f): continue
            t0 = time.time()
            if name == "svm":
                pred, score = svm_fit_predict(tr_text, tr_y, E.text.values)
                logits = np.stack([-score, score], 1).astype(np.float32)   # SVM margins, not probabilities
            else:
                mn, lr = MODELS[name]
                logits = finetune_predict(mn, lr, tr_text, tr_y, E.text.values, 2, seed)
                pred = logits.argmax(1)
            np.savez(f, pred=pred, logits=logits, isF=E.isF.values, isQ=E.isQ.values,
                     dataset=E.dataset.values, kind=E.kind.values, n_train=len(tr_y))
            m = E.kind != "FQ"
            mf1 = f1_score(E.isQ.values[m], pred[m], average="macro")
            print(f"{scheme:7s} | {name:10s} | seed {seed} | external macro-F1 (onlyF vs onlyQ) {mf1:.3f} | {time.time()-t0:.0f}s")
""")

code(r"""
# ---------------- Experiment 4: zero-shot LLM baseline ----------------
PROMPT_A = ("Classify the following software requirement.\n"
            "A) Functional: it describes a behaviour or function that the system must perform.\n"
            "B) Non-functional: it describes a quality or constraint of the system, such as performance, security, "
            "usability, availability, look and feel, legal, maintainability, portability, scalability, operability "
            "or fault tolerance.\n\nRequirement: \"{t}\"\n\nAnswer with the single letter A or B.")
PROMPT_B = ("Classify the following non-functional software requirement into one quality class.\n"
            "A) Operability: how the system is operated, installed, administered or supported in its environment.\n"
            "B) Performance: speed, response time, throughput, capacity or resource use.\n"
            "C) Security: access control, authentication, privacy, integrity or protection against misuse.\n"
            "D) Usability: ease of use, learnability, user satisfaction or accessibility for users.\n\n"
            "Requirement: \"{t}\"\n\nAnswer with the single letter A, B, C or D.")

def llm_scores(texts, template, letters, batch=8):
    tok = AutoTokenizer.from_pretrained(LLM_NAME); tok.padding_side = "left"
    if tok.pad_token is None: tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(LLM_NAME, torch_dtype=torch.float16 if dev == "cuda" else torch.float32).to(dev).eval()
    ids = [tok.encode(l, add_special_tokens=False)[0] for l in letters]
    assert len(set(ids)) == len(letters)
    out = []
    for i in range(0, len(texts), batch):
        msgs = [tok.apply_chat_template([{"role": "user", "content": template.format(t=t)}],
                                        tokenize=False, add_generation_prompt=True) for t in texts[i:i + batch]]
        x = tok(msgs, return_tensors="pt", padding=True, add_special_tokens=False).to(dev)
        pos = (x["attention_mask"].cumsum(-1) - 1).clamp(min=0)        # correct positions under left padding
        with torch.no_grad():
            try:
                lg = model(**x, position_ids=pos, logits_to_keep=1).logits[:, -1, :].float()
            except TypeError:                                          # older transformers
                lg = model(**x, position_ids=pos).logits[:, -1, :].float()
        out.append(lg[:, ids].cpu().numpy())
    del model
    if dev == "cuda": torch.cuda.empty_cache()
    return np.concatenate(out)        # scores over the option letters only (softmax -> probabilities)

if RUN_LLM and not os.path.exists(f"{OUT}/llm_zeroshot.npz"):
    lim = slice(None) if LLM_LIMIT is None else slice(0, LLM_LIMIT)
    B = P[P.cls.isin(["O", "PE", "SE", "US"])].reset_index(drop=True)      # classes sorted: O, PE, SE, US
    t0 = time.time()
    sA = llm_scores(list(P.text.values[lim]), PROMPT_A, ["A", "B"])
    sB = llm_scores(list(B.text.values[lim]), PROMPT_B, ["A", "B", "C", "D"])
    sE = llm_scores(list(E.text.values[lim]), PROMPT_A, ["A", "B"])
    yB = B.cls.map({"O": 0, "PE": 1, "SE": 2, "US": 3}).values[lim]
    np.savez(f"{OUT}/llm_zeroshot.npz", A_scores=sA, A_y=P.y_orig.values[lim], A_project=P.project.values[lim],
             B_scores=sB, B_y=yB, B_project=B.project.values[lim], E_scores=sE,
             E_isF=E.isF.values[lim], E_isQ=E.isQ.values[lim], E_dataset=E.dataset.values[lim], E_kind=E.kind.values[lim])
    print(f"LLM done in {time.time()-t0:.0f}s | Task A macro-F1 {f1_score(P.y_orig.values[lim], sA.argmax(1), average='macro'):.3f}"
          f" | Task B macro-F1 {f1_score(yB, sB.argmax(1), average='macro'):.3f}")
""")

code(r"""
# ---------------- Tables ----------------
def ext_metrics(pred, isF, isQ, kind, dataset=None):
    pred = np.asarray(pred).astype(int); m = kind != "FQ"
    r = dict(macroF1_onlyF_vs_onlyQ=f1_score(isQ[m], pred[m], average="macro", labels=[0, 1], zero_division=0),
             acc_onlyF_vs_onlyQ=(isQ[m] == pred[m]).mean(),
             qflag_P=precision_score(isQ, pred, zero_division=0), qflag_R=recall_score(isQ, pred, zero_division=0),
             qflag_F1=f1_score(isQ, pred, zero_division=0),
             FQ_flagged=pred[kind == "FQ"].mean() if (kind == "FQ").any() else np.nan,
             onlyF_flagged=pred[kind == "onlyF"].mean())
    return r

rec = []
for f in sorted(glob.glob(f"{OUT}/ext_*_*_*.npz")):
    _, scheme, name, seed = os.path.basename(f)[:-4].split("_")
    z = np.load(f, allow_pickle=True)
    rec.append(dict(scheme=scheme, model=name, seed=int(seed), **ext_metrics(z["pred"], z["isF"], z["isQ"], z["kind"])))
    for ds in np.unique(z["dataset"]):
        k = z["dataset"] == ds
        rec.append(dict(scheme=scheme, model=name, seed=int(seed), dataset=ds,
                        **ext_metrics(z["pred"][k], z["isF"][k], z["isQ"][k], z["kind"][k])))
X = pd.DataFrame(rec); X["dataset"] = X.get("dataset", pd.Series(dtype=object)).fillna("ALL")
X.to_csv(f"{OUT}/ext_per_seed.csv", index=False)

cols = ["macroF1_onlyF_vs_onlyQ", "acc_onlyF_vs_onlyQ", "qflag_P", "qflag_R", "qflag_F1", "FQ_flagged", "onlyF_flagged"]
agg = X[X.dataset == "ALL"].groupby(["scheme", "model"])[cols].agg(["mean", "std"]).round(3)
agg.to_csv(f"{OUT}/table_external.csv"); print("External test, all four sets (mean, SD over seeds):"); print(agg)

per_ds = X[X.dataset != "ALL"].groupby(["scheme", "model", "dataset"]).macroF1_onlyF_vs_onlyQ.agg(["mean", "std"]).round(3).unstack("dataset")
per_ds.to_csv(f"{OUT}/table_external_per_dataset.csv"); print("\nPer dataset, macro-F1 onlyF vs onlyQ:"); print(per_ds)

# LLM rows
if os.path.exists(f"{OUT}/llm_zeroshot.npz"):
    z = np.load(f"{OUT}/llm_zeroshot.npz", allow_pickle=True)
    llm = dict(model=LLM_NAME, n_A=len(z["A_y"]), n_B=len(z["B_y"]), n_E=len(z["E_isQ"]),
               taskA_macroF1=f1_score(z["A_y"], z["A_scores"].argmax(1), average="macro"),
               taskA_acc=(z["A_y"] == z["A_scores"].argmax(1)).mean(),
               taskB_macroF1=f1_score(z["B_y"], z["B_scores"].argmax(1), average="macro"),
               taskB_acc=(z["B_y"] == z["B_scores"].argmax(1)).mean(),
               **ext_metrics(z["E_scores"].argmax(1), z["E_isF"], z["E_isQ"], z["E_kind"]))
    pd.DataFrame([llm]).round(3).to_csv(f"{OUT}/table_llm_zeroshot.csv", index=False)
    print("\nZero-shot LLM:"); print(pd.Series(llm))
""")

code(r"""
# ---------------- Paired bootstrap vs SVM on the external sets (resampling within each dataset) ----------------
def macro_m(isQ, pred, kind):
    m = kind != "FQ"; return f1_score(isQ[m], pred[m], average="macro", labels=[0, 1], zero_division=0)

brow = []
z0 = np.load(glob.glob(f"{OUT}/ext_orig_svm_*.npz")[0], allow_pickle=True)
dsets, kind_all, isQ_all = z0["dataset"], z0["kind"], z0["isQ"]
by = {d: np.where(dsets == d)[0] for d in np.unique(dsets)}
rng = np.random.default_rng(0)
idx_boot = [np.concatenate([rng.choice(v, len(v), replace=True) for v in by.values()]) for _ in range(N_BOOT)]
for scheme in SCHEMES:
    for name in MODELS:
        pa = [np.load(f"{OUT}/ext_{scheme}_{name}_{s}.npz")["pred"] for s in SEEDS]
        pb = [np.load(f"{OUT}/ext_{scheme}_svm_{s}.npz")["pred"] for s in SEEDS]
        stat = lambda ii: np.mean([macro_m(isQ_all[ii], a[ii], kind_all[ii]) - macro_m(isQ_all[ii], b[ii], kind_all[ii])
                                   for a, b in zip(pa, pb)])
        obs = stat(np.arange(len(isQ_all))); d = np.array([stat(ii) for ii in idx_boot])
        lo, hi = np.percentile(d, [2.5, 97.5])
        brow.append(dict(scheme=scheme, model=name, diff_vs_svm=round(obs, 3), ci_low=round(lo, 3), ci_high=round(hi, 3),
                         excludes_zero=bool(lo > 0 or hi < 0)))
# orig vs reclass for the same model (does the label definition matter?)
if "reclass" in SCHEMES:
    for name in ["svm"] + list(MODELS):
        pa = [np.load(f"{OUT}/ext_reclass_{name}_{s}.npz")["pred"] for s in SEEDS]
        pb = [np.load(f"{OUT}/ext_orig_{name}_{s}.npz")["pred"] for s in SEEDS]
        for metric in ["macroF1", "qflag_F1"]:
            fn = (lambda q, p, k: macro_m(q, p, k)) if metric == "macroF1" else (lambda q, p, k: f1_score(q, p, zero_division=0))
            stat = lambda ii: np.mean([fn(isQ_all[ii], a[ii], kind_all[ii]) - fn(isQ_all[ii], b[ii], kind_all[ii]) for a, b in zip(pa, pb)])
            obs = stat(np.arange(len(isQ_all))); d = np.array([stat(ii) for ii in idx_boot]); lo, hi = np.percentile(d, [2.5, 97.5])
            brow.append(dict(scheme=f"reclass-minus-orig ({metric})", model=name, diff_vs_svm=round(obs, 3),
                             ci_low=round(lo, 3), ci_high=round(hi, 3), excludes_zero=bool(lo > 0 or hi < 0)))
boot = pd.DataFrame(brow); boot.to_csv(f"{OUT}/table_external_bootstrap.csv", index=False); boot
""")

code(r"""
# ---------------- Experiment 3: does the calibrated confidence gate transfer to new data? ----------------
def softmax(z, T=1.0):
    z = z / T; z = z - z.max(1, keepdims=True); e = np.exp(z); return e / e.sum(1, keepdims=True)
def ece(p, y, bins=15):
    conf, acc = p.max(1), (p.argmax(1) == y); edges, e = np.linspace(0, 1, bins + 1), 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any(): e += m.mean() * abs(acc[m].mean() - conf[m].mean())
    return e
def fit_T(z, y):
    return minimize_scalar(lambda T: -np.log(softmax(z, T)[np.arange(len(y)), y] + 1e-12).mean(), bounds=(0.05, 10), method="bounded").x
GRID = np.round(np.arange(0.50, 0.996, 0.005), 3)
def pick_tau(conf, ok, target=0.95, minn=20):
    for t in GRID:
        m = conf >= t
        if m.sum() >= minn and ok[m].mean() >= target: return t
    return None

crow = []
if BPR is None:
    print("Skipped: bert_paper_results not found.")
else:
    for name in MODELS:
        for seed in SEEDS:
            oof = np.load(f"{BPR}/A_project_{name}_{seed}.npz")
            T = fit_T(oof["logits"], oof["y"]); po = softmax(oof["logits"], T)
            tau = pick_tau(po.max(1), po.argmax(1) == oof["y"])
            z = np.load(f"{OUT}/ext_orig_{name}_{seed}.npz", allow_pickle=True); m = z["kind"] != "FQ"
            y, lg = z["isQ"][m], z["logits"][m]
            pr, pc = softmax(lg), softmax(lg, T); conf, ok = pc.max(1), pc.argmax(1) == y
            r = dict(model=name, seed=seed, T=round(T, 3), ECE_raw=ece(pr, y), ECE_cal=ece(pc, y),
                     tau_from_PROMISE=tau, PROMISE_cov_at_tau=(po.max(1) >= tau).mean() if tau else np.nan)
            for t in [0.80, 0.90] + ([tau] if tau else []):
                g = conf >= t; key = "tau" if (tau and t == tau) else f"{t:.2f}"
                r[f"ext_cov@{key}"] = g.mean(); r[f"ext_prec@{key}"] = ok[g].mean() if g.any() else np.nan
            crow.append(r)
    cal = pd.DataFrame(crow); cal.to_csv(f"{OUT}/table_external_calibration_per_seed.csv", index=False)
    print(cal.groupby("model").mean(numeric_only=True).round(3).T)
""")

code(r"""
# ---------------- Package results ----------------
import shutil
zipname = "paper_v2_results" + ("_QUICKTEST" if QUICK_TEST else "")
shutil.make_archive(zipname, "zip", OUT)
print("Created", zipname + ".zip with", len(os.listdir(OUT)), "files:", sorted(os.listdir(OUT)))
try:
    from google.colab import files
    files.download(zipname + ".zip")
except Exception as e:
    print("Download it from the Colab file panel (left) or from Drive:", OUT)
""")

md(r"""
## What to send back
Upload `paper_v2_results.zip` (or push the `paper_v2_results` folder to GitHub). I will check every number against the saved predictions before anything goes into the paper. Please do not edit, re-run selectively or delete files from the folder; if a run fails, send the error message instead.
""")

nb = nbf.v4.new_notebook(); nb["cells"] = cells
nb["metadata"] = {"accelerator": "GPU", "colab": {"provenance": []},
                  "kernelspec": {"name": "python3", "display_name": "Python 3"}}
nbf.write(nb, "/home/user/paper_v2_experiments.ipynb")
print("written", len(cells), "cells")
