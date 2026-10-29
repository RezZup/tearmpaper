"""Item 2 audit: numbers in abstract, Tables III-IV, IV-A, IV-B, V-A, V-D, VI (docx) and viva_prep.md
(1) every number is derived from repro/outputs or is a documented setup/literature constant;
(2) key quantities are stated identically wherever they appear (matrix)."""
import json, re, docx, numpy as np, pandas as pd
exec(open('numaudit.py').read().split("d = docx.Document")[0])        # reuse the derived-value set `ok`
d = docx.Document('/home/user/term_paper.docx'); P = [p.text for p in d.paragraphs]
idx = lambda pref: next(i for i, t in enumerate(P) if t.startswith(pref))
sec = {
 'Abstract': P[idx('Abstract')],
 'IV-A': ' '.join(P[idx('A. Our Comparative Experiment'):idx('TABLE III')]),
 'IV-B': ' '.join(P[idx('B. Reported Results'):idx('V. Discussion')]),
 'V-A': ' '.join(P[idx('A. What the Evidence'):idx('B. Implications')]),
 'V-D': ' '.join(P[idx('D. Threats'):idx('E. Ethical')]),
 'VI': ' '.join(P[idx('VI. Conclusion'):idx('References')]),
 'viva_prep.md': open('/home/user/viva_prep.md').read(),
}
tabs = {t.rows[0].cells[0].text.strip() + '|' + t.rows[0].cells[-1].text.strip(): t for t in d.tables}
sec['Table III'] = ' '.join(c.text for r in tabs['Model|B project'].rows for c in r.cells)
sec['Table IV'] = ' '.join(c.text for r in tabs['Task|Bonferroni p'].rows for c in r.cells)
# setup constants (hyper-parameters, dataset facts, seeds) and literature numbers, each with its source
SETUP = {'42','43','44','625','249','255','370','15','10','5','3','2','6','4','1','11','18','7','9','8','64','21','54','67','16','0.95','0.99','0.05',
         '2e-5','5e-5','0.1','0.01','1.5','90','80','100','2007','2020','2016','236','88','13','12','26','14','17','20','22','30','32','40','60','97','59','0.37','2.0','0.0','0.4'}
LIT = {'0.94','0.99','0.97','94','87','0.92','92','0.91','0.87','86.93','0.93','0.66','0.65','0.966','0.70','0.83','31','310','95','969','444','525','1,500','4,908','182','56','2,595','2,313','404','130','1,636','623','0.74','0.78','0.76','0.82'}
def nums(t): return re.findall(r'(?<![\w.])\d(?:[\d]|,(?=\d{3}))*(?:\.\d+)?(?:e-\d+)?', t.replace('\u2013', ' ').replace('\u2212', '-'))
print('== (1) numbers not derived from results.json / CSVs, by section ==')
for k, t in sec.items():
    n = nums(t); un = sorted({x for x in n if x not in ok and x not in SETUP and x not in LIT})
    print(f'{k:13s} {len(n):4d} numbers; not derived and not a listed constant: {un}')
print('\n== (2) key quantities: where stated (✓) ==')
KEY = {
 'A rnd s42 SVM 0.916 / DB 0.901': [r'0\.916', r'0\.901'], 'B rnd s42 DB 0.919 / SVM 0.832': [r'0\.919', r'0\.832'],
 'A rnd SVM mean 0.912': [r'0\.912'], 'B rnd means .824/.819/.791': [r'0\.824', r'0\.819', r'0\.791'],
 'A proj DB 0.751': [r'0\.751'], 'A proj baselines 0.589–0.638': [r'0\.589', r'0\.638'],
 'B proj DB 0.813': [r'0\.813'], 'B proj baselines 0.696–0.718': [r'0\.696', r'0\.718'],
 'F recall DB 0.56 / 56%': [r'0\.56\b|56%'], 'F recall SVM 0.28': [r'0\.28\b'],
 'max p 0.017': [r'0\.017'], 'Bonferroni 0.051': [r'0\.051'], 'train 80% vs 90%': [r'80%', r'90%'],
 'Task A folds 25–216': [r'\b25\b.{0,8}216'], 'gate 89% / 0.81': [r'89%', r'0\.81\b'], 'gate B 22% / 0.99': [r'22%'],
 'drops A 15–32 / B 9–11': [r'15\u201332|15–32', r'9\u201311|9–11'], 'rnd McNemar A p=0.35': [r'0\.35\b'],
}
cols = list(sec); print('quantity'.ljust(34) + ' '.join(c[:6].ljust(6) for c in cols))
for q, pats in KEY.items():
    print(q.ljust(34) + ' '.join(('✓' if all(re.search(p, sec[c]) for p in pats) else ('~' if any(re.search(p, sec[c]) for p in pats) else '·')).ljust(6) for c in cols))
# contradiction scan: alternative values that would conflict with the canonical ones
BAD = [r'0\.57\b.{0,40}functional', r'p ?≤ ?0\.01[0-689]', r'0\.05[02-9]\b.{0,20}[Bb]onferroni', r'85%.{0,20}train', r'0\.75\b(?!1)', r'0\.92[0-9].{0,30}DistilBERT']
print('\nconflicting variants found:', [(c, p) for c in cols for p in BAD if re.search(p, sec[c])])
