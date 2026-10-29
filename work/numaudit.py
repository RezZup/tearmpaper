"""Phase 3 number audit: every number in our-experiment passages of the docx vs values derived from repro/outputs."""
import json, re, docx, numpy as np, pandas as pd
R = json.load(open('/home/user/repro/outputs/results.json'))
ok = set()
def add(v):
    for d in (2, 3): ok.add(f'{v:.{d}f}')
    ok.add(f'{v*100:.0f}'); ok.add(f'{v*100:.1f}')
def walk(o):
    if isinstance(o, dict): [walk(v) for v in o.values()]
    elif isinstance(o, list): [walk(v) for v in o]
    elif isinstance(o, (int, float)) and not isinstance(o, bool): add(float(o)); ok.add(str(o))
walk(R)
S = R['summary']; B = ['MNB', 'LogReg', 'LinearSVM', 'DistilBERT']
for t in 'AB':                                   # drops random -> grouped (points)
    for m in B: add(S[f'{t}|random|{m}']['macro_F1_mean'] - S[f'{t}|grouped|{m}']['macro_F1_mean'])
for t in 'AB':                                   # mean per-class recall over seeds, grouped; gate means
    for m in B:
        for c in R['runs'][f'{t}|grouped|42|{m}']['per_class']:
            add(np.mean([R['runs'][f'{t}|grouped|{s}|{m}']['per_class'][c]['R'] for s in (42, 43, 44)]))
    for tau in ('0.95', '0.99'):
        g = [R['gate'][f'{t}|grouped|{s}'][tau] for s in (42, 43, 44)]
        add(np.mean([x['coverage'] for x in g])); pa = [x['precision_auto'] for x in g if x['precision_auto'] is not None]; add(np.mean(pa)) if pa else None
        for x in g: add(x['coverage']); add(x['precision_auto']) if x['precision_auto'] is not None else None
for k, v in R['mcnemar'].items(): add(3 * v['p'])
for t, n in [('A', 625), ('B', 249)]:            # fold and training sizes
    for pr in ('random', 'grouped'):
        for s in (42, 43, 44):
            sz = pd.read_csv(f'/home/user/repro/outputs/predictions/{t}_{pr}_seed{s}.csv').groupby('fold').size()
            for k in sz: ok.add(str(k)); ok.add(str(n - k))
            ok.add(str(round(float(np.mean(n - sz)))))
d = docx.Document('/home/user/term_paper.docx')
paras = [p.text for p in d.paragraphs]
start = next(i for i, p in enumerate(paras) if p.startswith('Results.'))
txt = {'abstract': next(p for p in paras if 'Product backlogs mix' in p),
       'IV-A results': ' '.join(paras[start:start + 3]),
       'V-A': next(p for p in paras if p.startswith('Taken together')),
       'VI': next(p for p in paras if p.startswith('We set out to judge'))}
res = [t for t in d.tables if t.rows[0].cells[0].text.strip() == 'Model'][0]
txt['Table III'] = ' '.join(c.text for r in res.rows for c in r.cells)
CONST = {'42', '43', '44', '10', '5', '3', '1', '2', '4', '15', '11', '18', '625', '249', '255', '0.95', '0.05', '35', '90', '80',
         '2', '0.94', '0.99', '54', '67', '87', '94', '0.97', '0.21', '1.5', '0.01'}
for name, t in txt.items():
    nums = re.findall(r'(?<![\w.])\d+(?:\.\d+)?', t.replace('\u2013', ' ').replace('\u2212', '-'))
    bad = [x for x in nums if x not in ok and x not in CONST]
    print(f'{name:13s} {len(nums):3d} numbers; unmatched: {bad}')
