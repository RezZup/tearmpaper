"""Evaluate DistilBERT pooled out-of-fold predictions in the same format as results_baselines.json,
and run exact McNemar tests (DistilBERT vs. each baseline) on the pooled predictions."""
import json, numpy as np, pandas as pd
from math import comb
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix

F = json.load(open('/home/user/work/exp/folds.json'))
base = json.load(open('/home/user/work/exp/results_baselines.json'))
SEED = 42
models = {
    'TF-IDF + MNB': lambda: MultinomialNB(alpha=0.1),
    'TF-IDF + LinearSVM': lambda: LinearSVC(C=1.0, class_weight='balanced', random_state=SEED),
    'TF-IDF + LogReg': lambda: LogisticRegression(C=10, max_iter=2000, class_weight='balanced'),
}

def metrics(y, pred, labels):
    p, r, f, s = precision_recall_fscore_support(y, pred, labels=labels, zero_division=0)
    mp, mr, mf, _ = precision_recall_fscore_support(y, pred, labels=labels, average='macro', zero_division=0)
    wf = precision_recall_fscore_support(y, pred, labels=labels, average='weighted', zero_division=0)[2]
    return {'per_class': {l: {'P': float(p[i]), 'R': float(r[i]), 'F1': float(f[i]), 'n': int(s[i])} for i, l in enumerate(labels)},
            'macro_P': float(mp), 'macro_R': float(mr), 'macro_F1': float(mf), 'weighted_F1': float(wf),
            'acc': float(accuracy_score(y, pred)), 'cm': confusion_matrix(y, pred, labels=labels).tolist()}

def mcnemar_exact(c_a, c_b):
    """c_a: A right & B wrong; c_b: A wrong & B right. Two-sided exact binomial p."""
    n = c_a + c_b; k = min(c_a, c_b)
    if n == 0: return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)

out = {}
for t in ['A', 'B']:
    d = F[t]; X = np.array(d['texts'], dtype=object); y = np.array(d['y']); labels = d['labels']
    preds = {}
    for name, mk in models.items():   # recompute baseline OOF predictions (deterministic) for paired tests
        pr = np.empty(len(y), dtype=object)
        for tr, te in d['folds']:
            vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1, stop_words='english')
            clf = mk().fit(vec.fit_transform(X[tr]), y[tr]); pr[te] = clf.predict(vec.transform(X[te]))
        preds[name] = pr
        assert abs(metrics(y, pr, labels)['macro_F1'] - base[f'{t}|{name}']['macro_F1']) < 1e-9
    st = json.load(open(f'/home/user/work/exp/bert_preds_{t}.json'))
    assert len(st['done']) == 10 and None not in st['pred'], f'task {t} incomplete'
    bp = np.array(st['pred'], dtype=object); preds['DistilBERT'] = bp
    m = metrics(y, bp, labels); m['secs_per_fold'] = float(np.mean(st['secs']))
    m['fold_acc'] = [float((bp[te] == y[te]).mean()) for tr, te in d['folds']]
    out[f'{t}|DistilBERT'] = m
    for name in models:
        b_ok = bp == y; s_ok = preds[name] == y
        c1 = int((b_ok & ~s_ok).sum()); c2 = int((~b_ok & s_ok).sum())
        out[f'{t}|mcnemar|DistilBERT_vs_{name}'] = {'bert_only': c1, 'base_only': c2, 'p': mcnemar_exact(c1, c2)}
    for name in models:
        out[f'{t}|{name}'] = dict(base[f'{t}|{name}'], fold_acc=[float((preds[name][te] == y[te]).mean()) for tr, te in d['folds']])
json.dump(out, open('/home/user/work/exp/results_all.json', 'w'), indent=1)
for k, v in out.items():
    if 'mcnemar' in k: print(k, v)
    else: print(k, 'mP %.3f mR %.3f mF1 %.3f wF1 %.3f acc %.3f' % (v['macro_P'], v['macro_R'], v['macro_F1'], v['weighted_F1'], v['acc']),
               {l: round(c['F1'], 3) for l, c in v['per_class'].items()}, 'foldacc sd %.3f' % np.std(v['fold_acc']))
