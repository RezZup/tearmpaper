"""Phase 13 number audit.

Every number in the passages that report OUR experiments (abstract, Section IV-A incl. Table III,
our-number sentences of IV-B, Discussion V-A, Threats, Conclusion) of term_paper.docx is checked
against values derived from repro/outputs/results.json (built from the GPU prediction files), or
against an explicit list of design constants / dataset facts, each with its source.
Prints every unmatched number and exits 1 if there is any.
"""
import json, re, sys, itertools
import numpy as np, pandas as pd, docx

R = json.load(open('/home/user/repro/outputs/results.json'))
ok = set()

def add(v):
    v = float(v)
    for d in (2, 3): ok.add(f'{v:.{d}f}'); ok.add(f'{-v:.{d}f}')
    ok.add(f'{v * 100:.0f}'); ok.add(f'{abs(v) * 100:.0f}')
    if v == int(v): ok.add(str(int(v)))

def walk(o):
    if isinstance(o, dict): [walk(v) for v in o.values()]
    elif isinstance(o, list): [walk(v) for v in o]
    elif isinstance(o, (int, float)) and not isinstance(o, bool): add(o)
walk(R)

PS, MODELS = R['promise_summary'], ['svm', 'distilbert', 'bert', 'roberta']
# drop random -> project, in macro-F1 points
for t in 'AB':
    for m in MODELS:
        add((PS[f'{t}|random|{m}']['macro_F1']['mean'] - PS[f'{t}|project|{m}']['macro_F1']['mean']))
# seed-averaged per-document external scores and seed-averaged calibration quantities
ER = R['external_runs']
for lab in ('orig', 'reclass'):
    for m in MODELS:
        runs = [ER[f'{lab}|{m}|{s}'] for s in (42, 43, 44)]
        for ds in runs[0]['per_dataset']: add(np.mean([r['per_dataset'][ds] for r in runs]))
PC = R['promise_calibration']
for k in {k.rsplit('|', 1)[0] for k in PC}:
    runs = [PC[f'{k}|{s}'] for s in (42, 43, 44)]
    add(np.mean([r['ECE_raw'] for r in runs])); add(np.mean([r['ECE_cal'] for r in runs]))
    for g in [g for g in runs[0]['gate'] if g != 'sel']:
        for q in ('cov', 'prec'):
            vals = [r['gate'][g][q] for r in runs if r['gate'][g].get(q) is not None]
            if vals: add(np.mean(vals))
    for q in ('cov', 'prec'):
        key = 'sel' if 'sel' in runs[0]['gate'] else None
        if key:
            vals = [r['gate'][key][q] for r in runs if r['gate'][key].get(q) is not None]
            if vals: add(np.mean(vals))
# fold-level accuracies and training-set sizes from the prediction files
for t, n in (('A', 625), ('B', 249)):
    for pr in ('random', 'project'):
        for s in (42, 43, 44):
            z = np.load(f'/home/user/repro/results/bert_paper_results/{t}_{pr}_distilbert_{s}.npz')
            for f in np.unique(z['fold']):
                msk = z['fold'] == f
                add((z['y'][msk] == z['pred'][msk]).mean()); add(msk.sum()); add(n - msk.sum())

# design constants and dataset facts (value -> source)
CONST = {
    '625': 'PROMISE size', '15': 'PROMISE projects', '255': 'FR count', '370': 'NFR count', '249': 'Task B size',
    '67': 'US', '66': 'SE', '62': 'O', '54': 'PE', '38': 'LF (largest dropped class)', '1': 'PO / misc',
    '42': 'seed', '43': 'seed', '44': 'seed', '10': '10-fold', '5': '5-fold', '64': 'max_len', '16': 'batch',
    '0.01': 'weight decay', '1.0': 'grad clip', '1,000': 'cluster bootstrap n', '2,000': 'within-doc bootstrap n',
    '0.50': 'tau grid start', '0.995': 'tau grid end', '0.005': 'tau grid step', '20': 'min items at tau',
    '0.95': 'target precision', '2.5': 'percentile', '97.5': 'percentile', '95': '95% interval / precision',
    '80': 'project folds train on ~80%', '90': 'random folds train on 90%', '11': 'projects 11-15 no FR',
    '21': 'median tokens (bert)', '22': 'median tokens (roberta)', '6': 'items >64 tok (bert)', '9': 'items >64 tok (roberta)',
    '4': 'external dropped / documents', '3': 'seeds / models', '2': 'Dronology onlyQ / two annotators',
    '242': 'story pilot size', '0.002': 'story pilot kappa', '59': '370/625 NFR share and onlyQ count',
    '0.87': 'NoRBERT literature (IV-B)', '0.99': 'Eltahier literature', '94': 'NoRBERT literature', '87': 'NoRBERT literature',
    '92': 'Kurtanovic literature', '0.91': 'Dias Canedo literature', '0.83': 'aeroBERT literature', '19': '15 + 4 projects',
    '12': 'Table/section numbering', '13': 'Table/section numbering', '7': 'seven remaining classes',
    '35': 'number of sources', '0.4': 'Fig. 4 y-axis start', '2007': 'PROMISE creation year', '327': 'external items', '246': 'external single-aspect items',
}
assert round(370 / 625 * 100) == 59
ok |= set(CONST)

d = docx.Document('/home/user/term_paper.docx')
paras = [p.text for p in d.paragraphs]
for t in d.tables:
    for row in t.rows: paras.append(' | '.join(c.text for c in row.cells))
full = '\n'.join(paras)
def between(a, b):
    i = full.index(a); return full[i:full.index(b, i)]
parts = {
    'abstract': between('Product backlogs mix', 'Index Terms') if 'Index Terms' in full else full[:full.index('Product backlogs mix') + 1500],
    'IV-A': between('Our Comparative Experiment', 'Reported Results from the Literature'),
    'IV-B': between('Reported Results from the Literature', 'What the Evidence Supports'),
    'V-A': between('Our own results sharpen this picture.', 'Implications for Backlog Management'),
    'threats': between('Construct validity.', 'Ethical and Practical Considerations'),
    'concl': between('Our own comparative experiments found that', 'Four steps would make'),
    'tableIII': '\n'.join(p for p in paras if p.startswith(('TF-IDF+SVM |', 'DistilBERT |', 'BERT-base |', 'RoBERTa-base |', 'Qwen2.5'))),
}
NUM = re.compile(r'(?<![\w.])[\u2212-]?\d{1,3}(?:,\d{3})+(?![\d])|(?<![\w.])[\u2212-]?\d+(?:\.\d+)?')
SKIP = re.compile(r'Qwen2\.5-1\.5B|F1|10\u207b\u2075|\u00d710|Table [IVX]+|Section [IVX]+-?[A-Z]?|Fig\. \d|\(\d\)|\[\d+(?:\]\u2013\[\d+)?\]|seeds? 4[234]|A100|PROMISE_exp|[A-Z]{1,2}\d|\d+\u2013\d+ tokens')
bad, n = [], 0
for name, txt in parts.items():
    clean = SKIP.sub(' ', txt.replace('\u2212', '-'))
    for m in NUM.finditer(clean):
        tok = m.group(0); n += 1
        if tok in ok or tok.lstrip('-') in ok: continue
        bad.append((name, tok, clean[max(0, m.start() - 50):m.end() + 30].replace('\n', ' ')))
print('numbers checked:', n, '| unmatched:', len(bad))
for b in bad: print('  ', b)
sys.exit(1 if bad else 0)
