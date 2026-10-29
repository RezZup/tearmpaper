"""Classical baselines on PROMISE NFR (Cleland-Huang et al., Zenodo 10.5281/zenodo.268542).
Task A: FR vs NFR (625 requirements). Task B: four most frequent NFR classes (US, SE, O, PE; 249 requirements).
Stratified 10-fold CV, seed 42. Folds are saved so the DistilBERT run uses identical splits."""
import json, numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix

SEED = 42
df = pd.read_csv('/home/user/work/data/promise_nfr.csv')
tasks = {
    'A': (df.assign(y=np.where(df.label == 'F', 'F', 'NFR')), ['F', 'NFR']),
    'B': (df[df.label.isin(['US', 'SE', 'O', 'PE'])].assign(y=lambda d: d.label), ['US', 'SE', 'O', 'PE']),
}
models = {
    'TF-IDF + MNB': lambda: MultinomialNB(alpha=0.1),
    'TF-IDF + LinearSVM': lambda: LinearSVC(C=1.0, class_weight='balanced', random_state=SEED),
    'TF-IDF + LogReg': lambda: LogisticRegression(C=10, max_iter=2000, class_weight='balanced'),
}
results, folds_out = {}, {}
for t, (d, labels) in tasks.items():
    d = d.reset_index(drop=True)
    X, y = d.text.values, d.y.values
    skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=SEED)
    folds = [(tr.tolist(), te.tolist()) for tr, te in skf.split(X, y)]
    folds_out[t] = {'texts': X.tolist(), 'y': y.tolist(), 'labels': labels, 'folds': folds}
    for name, mk in models.items():
        pred = np.empty(len(y), dtype=object)
        for tr, te in folds:
            vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1, stop_words='english')
            Xtr = vec.fit_transform(X[tr]); Xte = vec.transform(X[te])
            clf = mk().fit(Xtr, y[tr]); pred[te] = clf.predict(Xte)
        p, r, f, s = precision_recall_fscore_support(y, pred, labels=labels, zero_division=0)
        mp, mr, mf, _ = precision_recall_fscore_support(y, pred, labels=labels, average='macro', zero_division=0)
        wf = precision_recall_fscore_support(y, pred, labels=labels, average='weighted', zero_division=0)[2]
        results[f'{t}|{name}'] = {
            'per_class': {l: {'P': float(p[i]), 'R': float(r[i]), 'F1': float(f[i]), 'n': int(s[i])} for i, l in enumerate(labels)},
            'macro_P': float(mp), 'macro_R': float(mr), 'macro_F1': float(mf), 'weighted_F1': float(wf),
            'acc': float(accuracy_score(y, pred)),
            'cm': confusion_matrix(y, pred, labels=labels).tolist()}
        print(t, name, 'macroF1=%.3f wF1=%.3f acc=%.3f' % (mf, wf, accuracy_score(y, pred)),
              {l: round(float(f[i]), 3) for i, l in enumerate(labels)})
json.dump(folds_out, open('/home/user/work/exp/folds.json', 'w'))
json.dump(results, open('/home/user/work/exp/results_baselines.json', 'w'), indent=1)
