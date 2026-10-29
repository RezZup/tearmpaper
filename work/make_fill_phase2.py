# -*- coding: utf-8 -*-
"""Fill experiment placeholders in content.py from repro/outputs/results.json (our own runs only).
Random protocol: stratified 10-fold; baselines seeds 42-44, DistilBERT seed 42 only.
Grouped protocol: project-held-out 5-fold (StratifiedGroupKFold by project), seeds 42-44 for all models."""
import json, numpy as np, pandas as pd
RES = json.load(open('/home/user/repro/outputs/results.json'))
PRED = '/home/user/repro/outputs/predictions'
S, RUN, MC = RES['summary'], RES['runs'], RES['mcnemar']
SEEDS = [42, 43, 44]
NB, LR, SVM, DB = 'MNB', 'LogReg', 'LinearSVM', 'DistilBERT'
BASE = [NB, LR, SVM]
f3 = lambda v: f'{v:.3f}'
f2 = lambda v: f'{v:.2f}'
def pfmt(p): return 'p < 0.001' if p < 0.001 else f'p = {p:.2f}'
def sm(t, pr, m): return S.get(f'{t}|{pr}|{m}')
def mf(t, pr, m): return sm(t, pr, m)['macro_F1_mean']
def run(t, pr, s, m): return RUN[f'{t}|{pr}|{s}|{m}']
def mc(t, pr, s, m): return MC[f'{t}|{pr}|{s}|DistilBERT_vs_{m}']
COMPLETE = sm('A', 'grouped', DB) is not None and sm('B', 'grouped', DB) is not None \
    and sm('A', 'grouped', DB)['n_seeds'] == 3 and sm('B', 'grouped', DB)['n_seeds'] == 3
PEND = 'PEND'

# ---------------------------------------------------------------- random protocol (seed 42 = DistilBERT split)
A_db, A_svm, B_db, B_svm = run('A', 'random', 42, DB), run('A', 'random', 42, SVM), run('B', 'random', 42, DB), run('B', 'random', 42, SVM)
mA, mB = mc('A', 'random', 42, SVM), mc('B', 'random', 42, SVM)
assert max(mc('B', 'random', 42, m)['p'] for m in BASE) * 3 < 0.05     # Bonferroni claim
assert all(mc('A', 'random', 42, m)['p'] > 0.05 for m in BASE)
fa = B_db['fold_acc']; cmA = A_db['cm']
assert all(abs(run(t, 'random', 42, m)['macro_F1'] - mf(t, 'random', m)) < 0.01 for t in 'AB' for m in BASE)
assert max(run('A', 'random', 42, m)['macro_F1'] for m in BASE + [DB]) - min(run('A', 'random', 42, m)['macro_F1'] for m in BASE + [DB]) < 0.015

F = {'COMPLETE': COMPLETE}
F['A_BERT'] = f3(A_db['macro_F1']); F['B_BERT'] = f3(B_db['macro_F1']); F['A_SVM'] = f3(A_svm['macro_F1'])
F['A_SECS'] = f"{A_db['secs_per_fold']:.0f}"; F['B_SECS'] = f"{B_db['secs_per_fold']:.0f}"

F['RESULTS_PARA_1'] = (
    f"*Random folds.* We first describe the seed-42 split, the one on which DistilBERT was trained. On Task A the four "
    f"models finish within 1.5 points of each other. The linear SVM has the highest macro-F1 ({f3(A_svm['macro_F1'])}) "
    f"and DistilBERT the lowest ({f3(A_db['macro_F1'])}). DistilBERT recognises non-functional requirements well (recall "
    f"{f3(A_db['per_class']['NFR']['R'])}) but misses more functional ones (recall {f3(A_db['per_class']['F']['R'])}; "
    f"{cmA[0][1]} of {sum(cmA[0])} were labelled NFR). An exact McNemar test on the pooled predictions finds no significant "
    f"difference between DistilBERT and the SVM ({mA['bert_only']} items only DistilBERT got right, {mA['base_only']} only "
    f"the SVM; {pfmt(mA['p'])}). Task B tells a different story. DistilBERT reaches a macro-F1 of {f3(B_db['macro_F1'])}, "
    f"against {f3(B_svm['macro_F1'])} for the SVM, {f3(run('B', 'random', 42, LR)['macro_F1'])} for logistic regression and "
    f"{f3(run('B', 'random', 42, NB)['macro_F1'])} for Naive Bayes, and its F1 is at least "
    f"{min(c['F1'] for c in B_db['per_class'].values()):.2f} for every class. Here the McNemar tests are significant against "
    f"all three baselines ({mB['bert_only']} versus {mB['base_only']} discordant items against the SVM; p < 0.001 in each "
    f"case), and the differences remain significant after a Bonferroni correction for three comparisons. Over seeds 42\u201344 "
    f"the baseline means in [[tab:res]] are within 0.01 of these seed-42 values.")

# ---------------------------------------------------------------- grouped protocol
def frec(t, m, cls):   # mean recall of one class over seeds, grouped protocol
    v = [run(t, 'grouped', s, m)['per_class'][cls]['R'] for s in SEEDS if f'{t}|grouped|{s}|{m}' in RUN]
    return float(np.mean(v)) if v else None
foldn = []
for s in SEEDS:
    df = pd.read_csv(f'{PRED}/A_grouped_seed{s}.csv'); foldn += list(df.groupby('fold').size())
gb = lambda t, m: mf(t, 'grouped', m)
base_rng = lambda t: f"{f3(min(gb(t, m) for m in BASE))}\u2013{f3(max(gb(t, m) for m in BASE))}"
dropA_base = min(mf('A', 'random', m) - gb('A', m) for m in BASE)
dropB_base = [mf('B', 'random', m) - gb('B', m) for m in BASE]
if COMPLETE:
    dA, dB = sm('A', 'grouped', DB), sm('B', 'grouped', DB)
    dbA = f"{f3(dA['macro_F1_mean'])} \u00b1 {f3(dA['macro_F1_sd'])}"; dbB = f"{f3(dB['macro_F1_mean'])} \u00b1 {f3(dB['macro_F1_sd'])}"
    def mcn_sentence(t):
        rows = [mc(t, 'grouped', s, SVM) for s in SEEDS]
        win = sum(r['bert_only'] > r['base_only'] and r['p'] < 0.05 for r in rows)
        lose = sum(r['bert_only'] < r['base_only'] and r['p'] < 0.05 for r in rows)
        ps = ', '.join('<0.001' if r['p'] < 0.001 else f"{r['p']:.3f}" for r in rows)
        if win == 3: verdict = 'DistilBERT is significantly better than the SVM in all three seeds'
        elif lose == 3: verdict = 'the SVM is significantly better than DistilBERT in all three seeds'
        elif win == 0 and lose == 0: verdict = 'DistilBERT and the SVM do not differ significantly in any seed'
        else: verdict = f'DistilBERT is significantly better than the SVM in {win} and significantly worse in {lose} of three seeds'
        return f"{verdict} (exact McNemar p per seed: {ps})"
    mcA, mcB = mcn_sentence('A'), mcn_sentence('B')
    db_fr = f2(frec('A', DB, 'F'))
else:
    dbA = dbB = mcA = mcB = db_fr = PEND
def gate(t, tau):
    g = [RES['gate'].get(f'{t}|grouped|{s}', {}).get(str(tau)) for s in SEEDS]
    g = [x for x in g if x]
    return (float(np.mean([x['coverage'] for x in g])), float(np.mean([x['precision_auto'] for x in g]))) if len(g) == 3 else None
if COMPLETE and gate('A', 0.95):
    cA, pA = gate('A', 0.95); cB, pB = gate('B', 0.95)
    assert pA < 0.9 and pB >= 0.95 and cB < 0.5     # wording below depends on this pattern
    GATE_S = (f" DistilBERT's confidence scores behaved differently on the two tasks. Averaged over seeds, a threshold of "
              f"0.95 would have auto-labelled {cA * 100:.0f}% of Task A items with a precision of only {f2(pA)}, well "
              f"short of the 0.95 target used as an example in [[sec:gate]]; on unseen projects the Task A scores were "
              f"over-confident. On Task B the same threshold met the target (precision {f2(pB)}) but auto-labelled only "
              f"{cB * 100:.0f}% of the items and sent the rest to review.")
else:
    GATE_S = ' ' + PEND + '.'
F['RESULTS_PARA_G'] = (
    f"*Project-held-out folds.* Holding out whole projects lowers every score (right-hand columns of [[tab:res]], and "
    f"[[fig:res]]). On Task A each baseline loses at least {dropA_base * 100:.0f} points of macro-F1 and ends at "
    f"{base_rng('A')}; DistilBERT reaches {dbA}. Most of the loss is in the functional class. Averaged over the three "
    f"seeds, functional recall falls to {f2(frec('A', SVM, 'F'))} for the SVM, {f2(frec('A', NB, 'F'))} for Naive Bayes "
    f"and {db_fr} for DistilBERT, while non-functional recall stays at "
    f"{f2(min(frec('A', m, 'NFR') for m in BASE))} or above for the baselines. On an unseen project the models therefore label "
    f"many functional requirements as non-functional. A plausible reason, which we did not test, is that functional "
    f"requirements are written in each project's domain vocabulary, whereas quality requirements reuse phrases such as "
    f"\u201cshall be available\u201d or \u201cwithin 2 seconds\u201d across projects. On Task A, {mcA}. Task B loses less: "
    f"the baselines drop by {min(dropB_base) * 100:.0f}\u2013{max(dropB_base) * 100:.0f} points to {base_rng('B')}, and "
    f"DistilBERT reaches {dbB}; {mcB}. The project-held-out folds are uneven because PROMISE projects differ in size: "
    f"Task A test folds hold between {min(foldn)} and {max(foldn)} items, and projects 11\u201315 contain no functional "
    f"requirements at all.{GATE_S}")

F['RESULTS_PARA_2'] = (
    "We read the random-fold contrast between the tasks as follows, although we did not test this explanation. In PROMISE "
    "the FR/NFR split is carried largely by surface cues, such as verbs of action versus adjectives of quality, and a bag "
    "of n-grams captures these well. Telling usability from operability or security is harder: words such as "
    "\u201cuser\u201d, \u201csystem\u201d and \u201cshall\u201d appear in every class, and each class has only 54\u201367 "
    "examples. This is the situation in which pre-trained representations are expected to help most. The errors also "
    "support the F+Q view of {{t:dalpiaz2019}}. Several Task A \u201cerrors\u201d are debatable. One item requires that all "
    "changes to a dispute case be \u201crecorded in the case history\u201d; PROMISE labels it NFR, the model predicted F, "
    "and it reads like our audit-log example in [[tab:data]]. In Task B, a requirement to conform to the Americans with "
    "Disabilities Act is labelled usability but was predicted security, and arguably it is a legal requirement as well. "
    f"Fold-level accuracy varied widely (DistilBERT on random Task B folds: {min(fa):.2f} to {max(fa):.2f} over test folds "
    "of about 25 items), which is why we report pooled scores.")

# ---------------------------------------------------------------- summary sentences
if COMPLETE:
    gA = [gb('A', m) for m in BASE]; gB = [gb('B', m) for m in BASE]
    leadA = all(mc('A', 'grouped', s, m)['bert_only'] > mc('A', 'grouped', s, m)['base_only'] and mc('A', 'grouped', s, m)['p'] < 0.05 for s in SEEDS for m in BASE)
    F['LEAD_A'] = leadA
    rng = lambda v: f"{f3(min(v))}\u2013{f3(max(v))}"
    F['ABSTRACT_RESULT'] = (
        f"With random folds, DistilBERT matched a linear SVM on functional versus non-functional classification "
        f"(macro-F1 {f3(A_db['macro_F1'])} vs. {f3(A_svm['macro_F1'])}, not significant) and beat it on the four most "
        f"frequent quality classes ({f3(B_db['macro_F1'])} vs. {f3(B_svm['macro_F1'])}). On unseen projects every score "
        f"fell{', and DistilBERT led clearly' if leadA else ''}: {f3(gb('A', DB))} versus {rng(gA)} for the baselines on the "
        f"first task, {f3(gb('B', DB))} versus {rng(gB)} on the second.")
    F['CONCL_RESULT'] = (
        f"with random folds a CPU-trained DistilBERT was no better than a linear SVM at separating functional from "
        f"non-functional requirements (macro-F1 {f3(A_db['macro_F1'])} vs. {f3(A_svm['macro_F1'])}) but clearly better at "
        f"telling the four most frequent quality classes apart ({f3(B_db['macro_F1'])} vs. {f3(B_svm['macro_F1'])}). When "
        f"whole projects were held out, every model lost ground"
        + (f", and the picture for the first task reversed: DistilBERT reached {f3(gb('A', DB))} against {rng(gA)} for "
           f"the baselines" if leadA else f": DistilBERT reached {f3(gb('A', DB))} against {rng(gA)} for the baselines")
        + f", and {f3(gb('B', DB))} against {rng(gB)} on the second task. Its confidence scores, however, were "
          f"over-confident on unseen projects for the first task, so a confidence gate needs calibration on the team's "
          f"own items before it can be trusted.")
else:
    F['ABSTRACT_RESULT'] = F['CONCL_RESULT'] = PEND + '.'

def disc():
    head = ("Under random folds, a linear TF-IDF model was as good as DistilBERT for the coarse FR/NFR decision, whereas the "
            "transformer was clearly better at separating quality classes. ")
    if not COMPLETE: return head + PEND + '.'
    def rel(t):
        d = gb(t, DB) - gb(t, SVM); r = [mc(t, 'grouped', s, SVM) for s in SEEDS]
        sig = sum(x['p'] < 0.05 for x in r)
        if abs(d) < 0.01 or sig == 0: return f"level with the SVM ({f3(gb(t, DB))} vs. {f3(gb(t, SVM))})"
        return f"{'ahead of' if d > 0 else 'behind'} the SVM ({f3(gb(t, DB))} vs. {f3(gb(t, SVM))})"
    drA = [mf('A', 'random', m) - gb('A', m) for m in BASE + [DB]]; drB = [mf('B', 'random', m) - gb('B', m) for m in BASE + [DB]]
    both = rel('A').startswith('ahead') and rel('B').startswith('ahead')
    where = (f"ahead of the SVM on both tasks ({f3(gb('A', DB))} vs. {f3(gb('A', SVM))} and {f3(gb('B', DB))} vs. {f3(gb('B', SVM))})"
             if both else f"{rel('A')} on Task A and {rel('B')} on Task B")
    return head + (f"Holding out whole projects cost every model {min(drA) * 100:.0f}\u2013{max(drA) * 100:.0f} points of "
            f"macro-F1 on Task A and {min(drB) * 100:.0f}\u2013{max(drB) * 100:.0f} points on Task B; DistilBERT ended "
            f"{where}. "
            + ("The transformer's advantage is therefore largest where it matters for adoption, on projects it has not "
               "seen, which agrees with the unseen-project results of NoRBERT {{hey2020norbert;hey2022corrected}}. For a "
               "team, this suggests that a cheap linear model is a reasonable Level 1 classifier only if it is trained on "
               "the team's own items, and that any model should be checked on those items before its labels are trusted, "
               "because random-fold scores overstate how well it will do on a new project."
               if gb('A', DB) - gb('A', SVM) > 0.05 else
               "For a team, this suggests that a transformer pays off mainly at Level 2 of the framework, and that any "
               "model should be checked on the team's own items before its labels are trusted, because random-fold scores "
               "overstate how well it will do on a new project."))
F['DISC_RESULT'] = disc()

# ---------------------------------------------------------------- Table III
order = [(NB, 'TF-IDF+NB'), (LR, 'TF-IDF+LogReg'), (SVM, 'TF-IDF+SVM'), (DB, 'DistilBERT')]
cols = [('A', 'random'), ('A', 'grouped'), ('B', 'random'), ('B', 'grouped')]
def cell(t, pr, m):
    s = sm(t, pr, m)
    if s is None or (pr == 'grouped' and m == DB and not COMPLETE): return None, PEND
    if s['macro_F1_sd'] is None: return round(s['macro_F1_mean'], 3), f"{s['macro_F1_mean']:.3f}\u2020"
    return round(s['macro_F1_mean'], 3), f"{s['macro_F1_mean']:.3f} \u00b1 {s['macro_F1_sd']:.3f}"
best = {c: max(v for v, _ in (cell(*c, m) for m, _ in order) if v is not None) for c in cols}
rows = []
for m, lab in order:
    row = [lab]
    for c in cols:
        v, txt = cell(*c, m); row.append(f'**{txt}**' if v is not None and v == best[c] else txt)
    rows.append(row)
F['RES_ROWS'] = rows
json.dump(F, open('/home/user/work/fill.json', 'w'), indent=1, ensure_ascii=False)
for k, v in F.items(): print(k, ':', v)
