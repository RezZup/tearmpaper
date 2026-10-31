# -*- coding: utf-8 -*-
"""Recompute every experimental number in the paper from the saved GPU predictions.

Inputs (produced on Google Colab GPUs by the two notebooks in notebooks/):
  results/bert_paper_results/{A,B}_{random,project}_{svm,distilbert,bert,roberta}_{42,43,44}.npz
      out-of-fold predictions on PROMISE NFR (rezz_bert_experiments.ipynb)
  results/paper_v2_results/ext_{orig,reclass}_{svm,distilbert,bert,roberta}_{42,43,44}.npz, llm_zeroshot.npz
      models trained on all of PROMISE, tested on the Dalpiaz et al. industrial sets (paper_v2_experiments.ipynb)
Outputs:
  outputs/results.json            every number used in the paper
  outputs/fig4_results.{pdf,png}  Fig. 4
The script also checks its numbers against the CSV tables the notebooks wrote and stops if any differ.
Usage:  python3 analyze.py
"""
import glob, json, os
import numpy as np, pandas as pd
from scipy.optimize import minimize_scalar
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix

HERE = os.path.dirname(os.path.abspath(__file__))
BPR = f"{HERE}/results/bert_paper_results"
V2 = f"{HERE}/results/paper_v2_results"
OUT = f"{HERE}/outputs"; os.makedirs(OUT, exist_ok=True)
SEEDS, MODELS, TR = [42, 43, 44], ["svm", "distilbert", "bert", "roberta"], ["distilbert", "bert", "roberta"]
CLASSES = {"A": ["FR", "NFR"], "B": ["O", "PE", "SE", "US"]}
R = {}

def softmax(z, T=1.0):
    z = np.asarray(z, float) / T; z = z - z.max(1, keepdims=True); e = np.exp(z); return e / e.sum(1, keepdims=True)
def ece(p, y, bins=15):
    conf, acc = p.max(1), (p.argmax(1) == y); edges, e = np.linspace(0, 1, bins + 1), 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any(): e += m.mean() * abs(acc[m].mean() - conf[m].mean())
    return float(e)
def fit_T(z, y):
    return minimize_scalar(lambda T: -np.log(softmax(z, T)[np.arange(len(y)), y] + 1e-12).mean(), bounds=(0.05, 10), method="bounded").x
def crossfit(z, y, fold):
    p = np.zeros_like(z, dtype=float)
    for k in np.unique(fold):
        m = fold == k; p[m] = softmax(z[m], fit_T(z[~m], y[~m]))
    return p
GRID = np.round(np.arange(0.50, 0.996, 0.005), 3)
def pick_tau(conf, ok, target=0.95, minn=20):
    for t in GRID:
        m = conf >= t
        if m.sum() >= minn and ok[m].mean() >= target: return float(t)
    return None
def mean_sd(v):
    v = np.asarray(v, float); return dict(mean=float(v.mean()), sd=float(v.std(ddof=1)) if len(v) > 1 else None, n=int(len(v)))

# ============================================================== Part 1: PROMISE out-of-fold predictions
def load(task, protocol, model, seed): return np.load(f"{BPR}/{task}_{protocol}_{model}_{seed}.npz")
runs = {}
for task in "AB":
    for protocol in ["random", "project"]:
        for model in MODELS:
            for seed in SEEDS:
                z = load(task, protocol, model, seed); y, pred = z["y"], z["pred"]
                if model != "svm": assert (z["logits"].argmax(1) == pred).all()
                P, Rr, F, _ = precision_score(y, pred, average=None, zero_division=0), recall_score(y, pred, average=None, zero_division=0), f1_score(y, pred, average=None, zero_division=0), None
                runs[f"{task}|{protocol}|{model}|{seed}"] = dict(
                    macro_F1=float(f1_score(y, pred, average="macro")), acc=float((y == pred).mean()),
                    per_class={c: dict(P=float(P[i]), R=float(Rr[i]), F1=float(F[i])) for i, c in enumerate(CLASSES[task])},
                    cm=confusion_matrix(y, pred).tolist(), n=int(len(y)),
                    n_test_folds=int(len(np.unique(z["fold"]))), fold_sizes=np.bincount(z["fold"]).tolist())
R["promise_runs"] = runs
summ = {}
for task in "AB":
    for protocol in ["random", "project"]:
        for model in MODELS:
            rr = [runs[f"{task}|{protocol}|{model}|{s}"] for s in SEEDS]
            summ[f"{task}|{protocol}|{model}"] = dict(
                macro_F1=mean_sd([r["macro_F1"] for r in rr]), acc=mean_sd([r["acc"] for r in rr]),
                recall={c: mean_sd([r["per_class"][c]["R"] for r in rr]) for c in CLASSES[task]},
                f1={c: mean_sd([r["per_class"][c]["F1"] for r in rr]) for c in CLASSES[task]})
R["promise_summary"] = summ
# check against the notebook's per-seed CSV
ps = pd.read_csv(f"{BPR}/per_seed_results.csv")
for _, r in ps.iterrows():
    assert abs(r.macro_f1 - runs[f"{r.task}|{r.protocol}|{r.model}|{r.seed}"]["macro_F1"]) < 1e-9

# cluster bootstrap over projects (same procedure as the notebook: 1000 resamples, rng seed 0)
def cluster_boot(task, protocol, seed, model, n=1000):
    A, B = load(task, protocol, model, seed), load(task, protocol, "svm", seed)
    y, proj, pa, pb = A["y"], A["project"], A["pred"], B["pred"]
    labels, projs = np.unique(y), np.unique(proj); by = {p: np.where(proj == p)[0] for p in projs}
    rng = np.random.default_rng(0); d = []
    mac = lambda yy, pp: f1_score(yy, pp, average="macro", labels=labels, zero_division=0)
    for _ in range(n):
        ii = np.concatenate([by[p] for p in rng.choice(projs, len(projs), replace=True)]); d.append(mac(y[ii], pa[ii]) - mac(y[ii], pb[ii]))
    lo, hi = np.percentile(d, [2.5, 97.5]); return dict(diff=float(mac(y, pa) - mac(y, pb)), lo=float(lo), hi=float(hi))
boot = {}
for task in "AB":
    for protocol in ["random", "project"]:
        for model in TR:
            for seed in SEEDS: boot[f"{task}|{protocol}|{model}|{seed}"] = cluster_boot(task, protocol, seed, model)
R["promise_bootstrap_vs_svm"] = boot
bc = pd.read_csv(f"{BPR}/table_cluster_bootstrap.csv")
for _, r in bc.iterrows():
    b = boot[f"{r.task}|{r.protocol}|{r.model}|{r.seed}"]
    assert abs(round(b["diff"], 3) - r.diff_vs_svm) < 1e-9 and abs(round(b["lo"], 3) - r.ci_low) < 1e-9 and abs(round(b["hi"], 3) - r.ci_high) < 1e-9
assert len(bc) == len(boot)

# calibration and confidence gate (temperature cross-fitted on the other folds; tau also cross-fitted)
cal = {}
for task in "AB":
    for protocol in ["random", "project"]:
        for model in TR:
            for seed in SEEDS:
                z = load(task, protocol, model, seed); y, lg, fold = z["y"], z["logits"], z["fold"]
                pr, pc = softmax(lg), crossfit(lg, y, fold); conf, ok = pc.max(1), pc.argmax(1) == y
                g = {}
                for t in [0.80, 0.90, 0.95]:
                    m = conf >= t; g[f"{t:.2f}"] = dict(cov=float(m.mean()), prec=float(ok[m].mean()) if m.any() else None)
                    m = pr.max(1) >= t; g[f"raw{t:.2f}"] = dict(cov=float(m.mean()), prec=float((pr.argmax(1) == y)[m].mean()) if m.any() else None)
                sel = np.zeros(len(y), bool); taus = []
                for k in np.unique(fold):   # tau for fold k chosen on the other folds only
                    o = fold != k; t = pick_tau(conf[o], ok[o]); taus.append(t)
                    if t is not None: sel[fold == k] = conf[fold == k] >= t
                g["sel"] = dict(cov=float(sel.mean()), prec=float(ok[sel].mean()) if sel.any() else None, taus=taus)
                cal[f"{task}|{protocol}|{model}|{seed}"] = dict(ECE_raw=ece(pr, y), ECE_cal=ece(pc, y), gate=g)
R["promise_calibration"] = cal
tc = pd.read_csv(f"{BPR}/table_calibration.csv")
for _, r in tc.iterrows():
    a = np.mean([cal[f"{r.task}|{r.protocol}|{r.model}|{s}"]["ECE_raw"] for s in SEEDS]); b = np.mean([cal[f"{r.task}|{r.protocol}|{r.model}|{s}"]["ECE_cal"] for s in SEEDS])
    assert abs(round(a, 3) - r.ECE_raw) < 1e-9 and abs(round(b, 3) - r.ECE_calibrated) < 2e-3, (r.to_dict(), a, b)

# ============================================================== Part 2: external test (Dalpiaz et al. industrial sets)
def ext_metrics(pred, isQ, kind):
    pred = np.asarray(pred).astype(int); m = kind != "FQ"
    return dict(macroF1=float(f1_score(isQ[m], pred[m], average="macro", labels=[0, 1], zero_division=0)), acc=float((isQ[m] == pred[m]).mean()),
                qflag_P=float(precision_score(isQ, pred, zero_division=0)), qflag_R=float(recall_score(isQ, pred, zero_division=0)),
                qflag_F1=float(f1_score(isQ, pred, zero_division=0)), FQ_flagged=float(pred[kind == "FQ"].mean()),
                onlyF_flagged=float(pred[kind == "onlyF"].mean()), onlyQ_flagged=float(pred[kind == "onlyQ"].mean()))
ext, z0 = {}, np.load(f"{V2}/ext_orig_svm_42.npz", allow_pickle=True)
dsets, kind_all, isQ_all = z0["dataset"], z0["kind"], z0["isQ"]
for scheme in ["orig", "reclass"]:
    for model in MODELS:
        for seed in SEEDS:
            z = np.load(f"{V2}/ext_{scheme}_{model}_{seed}.npz", allow_pickle=True)
            assert (z["dataset"] == dsets).all() and (z["isQ"] == isQ_all).all() and (z["kind"] == kind_all).all()
            if model != "svm": assert (z["logits"].argmax(1) == z["pred"]).all()
            e = ext_metrics(z["pred"], isQ_all, kind_all)
            e["per_dataset"] = {d: ext_metrics(z["pred"][dsets == d], isQ_all[dsets == d], kind_all[dsets == d])["macroF1"] for d in np.unique(dsets)}
            e["n_train"] = int(z["n_train"]); ext[f"{scheme}|{model}|{seed}"] = e
R["external_runs"] = ext
R["external_counts"] = dict(total=int(len(dsets)), by_kind={k: int((kind_all == k).sum()) for k in ["onlyF", "onlyQ", "FQ"]},
                            by_dataset={d: {k: int(((dsets == d) & (kind_all == k)).sum()) for k in ["onlyF", "onlyQ", "FQ"]} for d in np.unique(dsets)})
R["external_summary"] = {f"{s}|{m}": {k: mean_sd([ext[f"{s}|{m}|{x}"][k] for x in SEEDS]) for k in
                          ["macroF1", "acc", "qflag_P", "qflag_R", "qflag_F1", "FQ_flagged", "onlyF_flagged", "onlyQ_flagged"]}
                         for s in ["orig", "reclass"] for m in MODELS}
te = pd.read_csv(f"{V2}/table_external.csv", header=[0, 1], index_col=[0, 1])
for (s, m), row in te.iterrows():
    assert abs(round(R["external_summary"][f"{s}|{m}"]["macroF1"]["mean"], 3) - row[("macroF1_onlyF_vs_onlyQ", "mean")]) < 1e-9
    assert abs(round(R["external_summary"][f"{s}|{m}"]["qflag_F1"]["mean"], 3) - row[("qflag_F1", "mean")]) < 1e-9

# paired bootstrap vs SVM, resampling within each dataset (same procedure as the notebook: 2000 resamples, rng seed 0)
def macro_m(q, p, k): m = k != "FQ"; return f1_score(q[m], p[m], average="macro", labels=[0, 1], zero_division=0)
by = {d: np.where(dsets == d)[0] for d in np.unique(dsets)}; rng = np.random.default_rng(0)
idx_boot = [np.concatenate([rng.choice(v, len(v), replace=True) for v in by.values()]) for _ in range(2000)]
eb = {}
def boot_stat(pa, pb, fn):
    stat = lambda ii: np.mean([fn(isQ_all[ii], a[ii], kind_all[ii]) - fn(isQ_all[ii], b[ii], kind_all[ii]) for a, b in zip(pa, pb)])
    obs = stat(np.arange(len(isQ_all))); d = np.array([stat(ii) for ii in idx_boot]); lo, hi = np.percentile(d, [2.5, 97.5])
    return dict(diff=float(obs), lo=float(lo), hi=float(hi))
pred = lambda s, m: [np.load(f"{V2}/ext_{s}_{m}_{x}.npz")["pred"] for x in SEEDS]
for s in ["orig", "reclass"]:
    for m in TR: eb[f"{s}|{m}|vs_svm"] = boot_stat(pred(s, m), pred(s, "svm"), macro_m)
for m in MODELS:
    eb[f"reclass_minus_orig|{m}|macroF1"] = boot_stat(pred("reclass", m), pred("orig", m), macro_m)
    eb[f"reclass_minus_orig|{m}|qflag_F1"] = boot_stat(pred("reclass", m), pred("orig", m), lambda q, p, k: f1_score(q, p, zero_division=0))
R["external_bootstrap"] = eb
tb = pd.read_csv(f"{V2}/table_external_bootstrap.csv")
for _, r in tb.iterrows():
    key = (f"{r.scheme}|{r.model}|vs_svm" if not r.scheme.startswith("reclass-minus") else
           f"reclass_minus_orig|{r.model}|{'macroF1' if 'macroF1' in r.scheme else 'qflag_F1'}")
    b = eb[key]; assert all(abs(round(b[k], 3) - r[c]) < 1e-9 for k, c in [("diff", "diff_vs_svm"), ("lo", "ci_low"), ("hi", "ci_high")]), key

# calibration transfer: T and tau chosen on PROMISE Task A project-held-out out-of-fold logits, applied unchanged
ct = {}
for m in TR:
    for seed in SEEDS:
        oof = load("A", "project", m, seed); T = fit_T(oof["logits"], oof["y"]); po = softmax(oof["logits"], T)
        tau = pick_tau(po.max(1), po.argmax(1) == oof["y"])
        z = np.load(f"{V2}/ext_orig_{m}_{seed}.npz", allow_pickle=True); k = z["kind"] != "FQ"; y, lg = z["isQ"][k], z["logits"][k]
        prw, pc = softmax(lg), softmax(lg, T); conf, ok = pc.max(1), pc.argmax(1) == y
        r = dict(T=float(T), ECE_raw=ece(prw, y), ECE_cal=ece(pc, y), tau=tau)
        if tau is not None:
            g = conf >= tau; r.update(cov=float(g.mean()), n_auto=int(g.sum()), prec=float(ok[g].mean()) if g.any() else None)
        ct[f"{m}|{seed}"] = r
R["external_calibration"] = ct
tcs = pd.read_csv(f"{V2}/table_external_calibration_per_seed.csv")
for _, r in tcs.iterrows():
    c = ct[f"{r.model}|{r.seed}"]; assert abs(c["ECE_raw"] - r.ECE_raw) < 1e-6 and abs(c["ECE_cal"] - r.ECE_cal) < 2e-3

# zero-shot LLM
z = np.load(f"{V2}/llm_zeroshot.npz", allow_pickle=True)
pA, pB, pE = z["A_scores"].argmax(1), z["B_scores"].argmax(1), z["E_scores"].argmax(1)
R["llm_zeroshot"] = dict(model="Qwen/Qwen2.5-1.5B-Instruct", A_macroF1=float(f1_score(z["A_y"], pA, average="macro")), A_acc=float((z["A_y"] == pA).mean()),
                         A_share_pred_NFR=float(pA.mean()), B_macroF1=float(f1_score(z["B_y"], pB, average="macro")), B_acc=float((z["B_y"] == pB).mean()),
                         **{f"E_{k}": v for k, v in ext_metrics(pE, z["E_isQ"], z["E_kind"]).items()})
tl = pd.read_csv(f"{V2}/table_llm_zeroshot.csv").iloc[0]
assert abs(round(R["llm_zeroshot"]["A_macroF1"], 3) - tl.taskA_macroF1) < 1e-9 and abs(round(R["llm_zeroshot"]["B_macroF1"], 3) - tl.taskB_macroF1) < 1e-9
R["environment_v2"] = json.load(open(f"{V2}/environment.json")); R["data_card_v2"] = json.load(open(f"{V2}/data_card.json"))
json.dump(R, open(f"{OUT}/results.json", "w"), indent=1)

# ============================================================== Fig. 4
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"], "font.size": 8})
lab = {"svm": "TF-IDF+SVM", "distilbert": "DistilBERT", "bert": "BERT", "roberta": "RoBERTa"}
col = {"svm": "#bdbdbd", "distilbert": "#6baed6", "bert": "#2171b5", "roberta": "#08306b"}
fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.2), gridspec_kw=dict(width_ratios=[1, 1, 1]))
w = 0.2
for ax, task in zip(axes[:2], "AB"):
    for i, m in enumerate(MODELS):
        mu = [summ[f"{task}|{p}|{m}"]["macro_F1"]["mean"] for p in ["random", "project"]]
        sd = [summ[f"{task}|{p}|{m}"]["macro_F1"]["sd"] for p in ["random", "project"]]
        ax.bar(np.arange(2) + (i - 1.5) * w, mu, w, yerr=sd, capsize=1.5, color=col[m], edgecolor="black", linewidth=0.3, label=lab[m], error_kw=dict(lw=0.6))
    ax.set_xticks(range(2)); ax.set_xticklabels(["Random", "Project-held-out"])
    ax.set_title(f"({'a' if task == 'A' else 'b'}) Task {task}" + (": FR vs. NFR" if task == "A" else ": US/SE/O/PE"), fontsize=8)
for i, m in enumerate(MODELS):
    mu = [R["external_summary"][f"{s}|{m}"]["macroF1"]["mean"] for s in ["orig", "reclass"]]
    sd = [R["external_summary"][f"{s}|{m}"]["macroF1"]["sd"] for s in ["orig", "reclass"]]
    axes[2].bar(np.arange(2) + (i - 1.5) * w, mu, w, yerr=sd, capsize=1.5, color=col[m], edgecolor="black", linewidth=0.3, error_kw=dict(lw=0.6))
axes[2].set_xticks(range(2)); axes[2].set_xticklabels(["Original", "Relabelled"])
axes[2].set_title("(c) External sets", fontsize=8)
for ax in axes:
    ax.set_ylim(0.4, 1.0); ax.grid(axis="y", lw=0.3, alpha=0.6); ax.set_axisbelow(True)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
axes[0].set_ylabel("Macro-F1")
axes[0].legend(loc="upper center", bbox_to_anchor=(1.75, -0.16), ncol=4, frameon=False, fontsize=7.5)
fig.subplots_adjust(left=0.07, right=0.995, top=0.88, bottom=0.25, wspace=0.28)
for ext_ in ["pdf", "png"]: fig.savefig(f"{OUT}/fig4_results.{ext_}", dpi=300, bbox_inches="tight")
print("All checks against the notebooks' CSV tables passed. Wrote outputs/results.json and outputs/fig4_results.{pdf,png}")
