# -*- coding: utf-8 -*-
"""Fill the experiment placeholders in content.py from repro/outputs/results.json.
results.json is produced by repro/analyze.py from the saved GPU predictions (our own runs only):
  PROMISE NFR out-of-fold predictions (rezz_bert_experiments.ipynb) and the external test (paper_v2_experiments.ipynb).
Every sentence whose wording depends on a pattern in the data has an assert in front of it."""
import json, numpy as np
RES = json.load(open('/home/user/repro/outputs/results.json'))
BPR = '/home/user/repro/results/bert_paper_results'
S, BOOT, CAL = RES['promise_summary'], RES['promise_bootstrap_vs_svm'], RES['promise_calibration']
ES, EB, EC, ER, LLM = RES['external_summary'], RES['external_bootstrap'], RES['external_calibration'], RES['external_runs'], RES['llm_zeroshot']
SEEDS, TR, ALL = [42, 43, 44], ['distilbert', 'bert', 'roberta'], ['svm', 'distilbert', 'bert', 'roberta']
NAME = {'svm': 'the SVM', 'distilbert': 'DistilBERT', 'bert': 'BERT', 'roberta': 'RoBERTa'}
f3 = lambda v: f'{v:.3f}'
f2 = lambda v: f'{v:.2f}'
pct = lambda v: f'{v * 100:.0f}%'
rng3 = lambda v: f3(min(v)) if f3(min(v)) == f3(max(v)) else f'{f3(min(v))}\u2013{f3(max(v))}'
rng2 = lambda v: f2(min(v)) if f2(min(v)) == f2(max(v)) else f'{f2(min(v))}\u2013{f2(max(v))}'
neg = lambda s: s.replace('-', '\u2212')
mf = lambda t, p, m: S[f'{t}|{p}|{m}']['macro_F1']['mean']
sd = lambda t, p, m: S[f'{t}|{p}|{m}']['macro_F1']['sd']
ms = lambda t, p, m: f'{f3(mf(t, p, m))} \u00b1 {f3(sd(t, p, m))}'
rec = lambda t, p, m, c: S[f'{t}|{p}|{m}']['recall'][c]['mean']
excl = lambda b: b['lo'] > 0 or b['hi'] < 0
nex = lambda t, p, m: sum(excl(BOOT[f'{t}|{p}|{m}|{s}']) for s in SEEDS)
F = {}

# ---------------------------------------------------------------- Table III (wide): macro-F1 mean ± SD over seeds
cols = [('A', 'random'), ('A', 'project'), ('B', 'random'), ('B', 'project'), ('ext', 'orig'), ('ext', 'reclass')]
def val(c, m):
    if c[0] == 'ext': e = ES[f'{c[1]}|{m}']['macroF1']; return e['mean'], f"{f3(e['mean'])} \u00b1 {f3(e['sd'])}"
    return mf(*c, m), ms(*c, m)
best = {c: max(val(c, m)[0] for m in ALL) for c in cols}
LAB = {'svm': 'TF-IDF+SVM', 'distilbert': 'DistilBERT', 'bert': 'BERT-base', 'roberta': 'RoBERTa-base'}
rows = []
for m in ALL:
    row = [LAB[m]]
    for c in cols:
        v, txt = val(c, m); row.append(f'**{txt}**' if round(v, 3) == round(best[c], 3) else txt)
    rows.append(row)
rows.append(['Qwen2.5-1.5B, zero-shot\u2021', '\u2013', f3(LLM['A_macroF1']), '\u2013', f3(LLM['B_macroF1']), f3(LLM['E_macroF1']), '\u2013'])
assert all(LLM[k] < best[c] for k, c in [('A_macroF1', ('A', 'project')), ('B_macroF1', ('B', 'project')), ('E_macroF1', ('ext', 'orig'))])
F['RES_ROWS'] = rows

# ---------------------------------------------------------------- random folds
aR = [mf('A', 'random', m) for m in ALL]
assert max(aR) - min(aR) < 0.01 and all(nex('A', 'random', m) == 0 for m in TR)
F['A_RND_RANGE'] = rng3(aR)
bR = {m: mf('B', 'random', m) for m in ALL}
assert bR['roberta'] > bR['distilbert'] > bR['bert'] > bR['svm']
assert (nex('B', 'random', 'roberta'), nex('B', 'random', 'distilbert'), nex('B', 'random', 'bert')) == (3, 2, 0)
F['RESULTS_PARA_RANDOM'] = (
    f"*Random folds.* On Task A the four models are statistically tied: their mean macro-F1 ranges from {f3(min(aR))} to {f3(max(aR))}, "
    f"and none of the nine project-bootstrap intervals for a transformer minus the SVM excludes zero. On Task B the "
    f"transformers pull ahead. RoBERTa reaches {ms('B', 'random', 'roberta')} and DistilBERT {ms('B', 'random', 'distilbert')}, "
    f"against {ms('B', 'random', 'svm')} for the SVM; their intervals exclude zero in three and two of three seeds respectively. "
    f"BERT ({ms('B', 'random', 'bert')}) is ahead of the SVM on average, but none of its intervals excludes zero.")

# ---------------------------------------------------------------- project-held-out folds
drop = lambda t, m: mf(t, 'random', m) - mf(t, 'project', m)
dA = {m: drop('A', m) for m in ALL}; dB = {m: drop('B', m) for m in ALL}
assert dA['svm'] > max(dA[m] for m in TR)
exA = {m: nex('A', 'project', m) for m in TR}; assert sum(exA.values()) == 8 and exA['distilbert'] == 2
miss = [s for s in SEEDS if not excl(BOOT[f'A|project|distilbert|{s}'])]; assert miss == [42]
bm = BOOT['A|project|distilbert|42']
frA = {m: rec('A', 'project', m, 'FR') for m in ALL}; nfrA = [rec('A', 'project', m, 'NFR') for m in ALL]
assert frA['svm'] < 0.3 and max(frA[m] for m in TR) < 0.7 and min(nfrA) > 0.9
exB = {m: nex('B', 'project', m) for m in TR}; assert exB == {'distilbert': 3, 'bert': 0, 'roberta': 3}
bP = {m: mf('B', 'project', m) for m in ALL}; assert bP['distilbert'] > bP['roberta'] > bP['bert'] > bP['svm']
# fold sizes and training-set sizes, from the saved fold ids
sizes = {}
for t, n in [('A', 625), ('B', 249)]:
    for p in ['random', 'project']:
        fs = [np.bincount(np.load(f'{BPR}/{t}_{p}_svm_{s}.npz')['fold']) for s in SEEDS]
        sizes[(t, p)] = (min(min(f) for f in fs), max(max(f) for f in fs), float(np.mean([n - k for f in fs for k in f])) / n,
                         min(n - max(f) for f in fs), max(n - min(f) for f in fs), round(float(np.mean([n - k for f in fs for k in f]))))
assert abs(sizes[('A', 'random')][2] - 0.9) < 0.005 and abs(sizes[('A', 'project')][2] - 0.8) < 0.005
z = np.load(f'{BPR}/A_project_svm_42.npz'); noF = sorted(set(z['project']) - set(z['project'][z['y'] == 0]))
assert noF == [11, 12, 13, 14, 15]
aP = sizes[('A', 'project')]
F['RESULTS_PARA_PROJECT'] = (
    f"*Project-held-out folds.* Holding out whole projects lowers every score (right-hand columns of [[tab:res]] and "
    f"[[fig:res]]), but not equally. On Task A the SVM loses {dA['svm'] * 100:.0f} points of macro-F1 and ends at "
    f"{ms('A', 'project', 'svm')}, whereas the transformers lose {min(dA[m] for m in TR) * 100:.0f}\u2013"
    f"{max(dA[m] for m in TR) * 100:.0f} points: DistilBERT reaches {ms('A', 'project', 'distilbert')}, BERT "
    f"{ms('A', 'project', 'bert')} and RoBERTa {ms('A', 'project', 'roberta')}. Eight of the nine project-bootstrap intervals "
    f"exclude zero; the exception is DistilBERT with seed 42 (difference {f3(bm['diff'])}, 95% interval {neg(f3(bm['lo']))} to "
    f"{f3(bm['hi'])}). Most of the loss is in the functional class. Averaged over seeds, functional recall falls to "
    f"{f2(frA['svm'])} for the SVM, {f2(frA['distilbert'])} for DistilBERT, {f2(frA['bert'])} for BERT and "
    f"{f2(frA['roberta'])} for RoBERTa, while non-functional recall stays at {f2(min(nfrA))} or above for every model. On an "
    f"unseen project the models therefore label many functional requirements as non-functional; even the best model "
    f"finds only about two thirds of them. A likely but untested reason is that functional requirements are written in each "
    f"project's domain vocabulary, whereas quality requirements reuse phrases such as \u201cshall be available\u201d or "
    f"\u201cwithin 2 seconds\u201d across projects. Task B loses less: the SVM drops to {ms('B', 'project', 'svm')}, "
    f"DistilBERT reaches {ms('B', 'project', 'distilbert')} and RoBERTa {ms('B', 'project', 'roberta')}, and both are "
    f"ahead of the SVM in every seed. BERT ({ms('B', 'project', 'bert')}) is again ahead on average without any interval "
    f"excluding zero. The drop should not be read as the effect of unseen projects alone, because the protocols differ in "
    f"other ways. Five project-held-out folds train on about 80% of the items, against 90% for ten random folds (on Task A, "
    f"{aP[3]}\u2013{aP[4]} training items per fold instead of about {sizes[('A', 'random')][5]}). The folds are also uneven, "
    f"because PROMISE projects differ in size and content: Task A test folds hold between {aP[0]} and {aP[1]} items, and "
    f"projects 11\u201315 contain no functional requirements at all.")

# ---------------------------------------------------------------- calibration and gate (PROMISE)
def cm(t, p, m, key, field):
    v = [CAL[f'{t}|{p}|{m}|{s}']['gate'][key][field] for s in SEEDS]; v = [x for x in v if x is not None]
    return (float(np.mean(v)), len(v)) if v else (None, 0)
eceA = [np.mean([CAL[f'A|project|{m}|{s}'][k] for s in SEEDS]) for m in TR for k in ['ECE_raw']]
eceAc = [np.mean([CAL[f'A|project|{m}|{s}']['ECE_cal'] for s in SEEDS]) for m in TR]
eceBb = [np.mean([CAL[f'B|{p}|bert|{s}']['ECE_raw'] for s in SEEDS]) for p in ['random', 'project']]
eceBo = [np.mean([CAL[f'B|{p}|{m}|{s}']['ECE_raw'] for s in SEEDS]) for p in ['random', 'project'] for m in ['distilbert', 'roberta']]
assert min(eceBb) > 0.25 and max(eceBo) < 0.12
rawA = [cm('A', 'project', m, 'raw0.95', f)[0] for m in TR for f in ['cov']]; rawAp = [cm('A', 'project', m, 'raw0.95', 'prec')[0] for m in TR]
assert min(rawA) > 0.8 and max(rawAp) < 0.86
assert all(cm('A', 'project', m, '0.95', 'cov')[0] == 0 for m in TR)
selA = {m: (cm('A', 'project', m, 'sel', 'cov')[0], cm('A', 'project', m, 'sel', 'prec')[0]) for m in TR}
assert max(v[0] for v in selA.values()) == selA['roberta'][0] and selA['roberta'][1] < 0.9 and selA['roberta'][0] < 0.25
selB = {m: (cm('B', 'project', m, 'sel', 'cov')[0], cm('B', 'project', m, 'sel', 'prec')[0]) for m in TR}
assert all(cm('B', 'project', m, 'sel', 'prec')[1] == 3 for m in TR)
selAr = [cm('A', 'random', m, 'sel', 'cov')[0] for m in TR]; selArp = [cm('A', 'random', m, 'sel', 'prec')[0] for m in TR]
F['RESULTS_PARA_CAL'] = (
    f"*Calibration and the confidence gate.* The raw softmax scores were over-confident on unseen projects. On Task A "
    f"project-held-out folds the expected calibration error (ECE) of the three transformers was {rng2(eceA)}, and a "
    f"threshold of 0.95 on the raw scores would have auto-labelled {pct(min(rawA))}\u2013{pct(max(rawA))} of the items at a "
    f"precision of only {rng2(rawAp)}. BERT was badly calibrated on Task B as well (ECE {rng2(eceBb)}, against "
    f"{f2(max(eceBo))} or less for DistilBERT and RoBERTa). Cross-fitted temperature scaling reduced the Task A "
    f"project-held-out ECE to {rng2(eceAc)}, but it also showed how little of that task can be automated safely: after "
    f"scaling, no Task A item of an unseen project reached a confidence of 0.95, and the cross-fitted threshold "
    f"auto-labelled at most {pct(selA['roberta'][0])} of the items (RoBERTa), at a precision of {f2(selA['roberta'][1])}, "
    f"short of the 0.95 target. Task B behaved better. With the cross-fitted threshold, DistilBERT auto-labelled "
    f"{pct(selB['distilbert'][0])} of the unseen-project items at a precision of {f2(selB['distilbert'][1])}, RoBERTa "
    f"{pct(selB['roberta'][0])} at {f2(selB['roberta'][1])} and BERT {pct(selB['bert'][0])} at {f2(selB['bert'][1])}; the "
    f"remaining items would go to review. Under random folds the same procedure auto-labelled about "
    f"{pct(np.mean(selAr))} of Task A items at a precision of {rng2(selArp)}, which again shows how optimistic random "
    f"splits are.")

# ---------------------------------------------------------------- external test
cnt = RES['external_counts']; bk, bd = cnt['by_kind'], cnt['by_dataset']
assert cnt['total'] == 327 and RES['data_card_v2']['external_dropped_neither'] == 4
nd = {d: sum(v.values()) for d, v in bd.items()}
F.update(EXT_N=str(cnt['total']), EXT_ONLYF=str(bk['onlyF']), EXT_ONLYQ=str(bk['onlyQ']), EXT_FQ=str(bk['FQ']),
         EXT_M=str(bk['onlyF'] + bk['onlyQ']), EXT_DRON=str(nd['dronology']), EXT_LEEDS=str(nd['leeds']),
         EXT_REQV=str(nd['reqview']), EXT_WASP=str(nd['wasp']), EXT_DRON_Q=str(bd['dronology']['onlyQ']), EXT_WASP_Q=str(bd['wasp']['onlyQ']),
         RECLASS_N=str(ER['reclass|svm|42']['n_train']))
assert ER['reclass|svm|42']['n_train'] == 612 and RES['data_card_v2']['text_overlap_with_promise'] == 0
em = lambda s, m, k='macroF1': ES[f'{s}|{m}'][k]['mean']
ems = lambda s, m: f"{f3(em(s, m))} \u00b1 {f3(ES[f'{s}|{m}']['macroF1']['sd'])}"
s44 = [ER[f'orig|{m}|44']['macroF1'] for m in TR]; oth = [ER[f'orig|{m}|{s}']['macroF1'] for m in TR for s in (42, 43)]
assert max(s44) < min(oth)
vs = {s: [EB[f'{s}|{m}|vs_svm'] for m in TR] for s in ['orig', 'reclass']}
assert all(excl(b) and b['diff'] > 0 for v in vs.values() for b in v)
rmo = {m: EB[f'reclass_minus_orig|{m}|macroF1'] for m in ALL}
assert excl(rmo['roberta']) and not any(excl(rmo[m]) for m in ['svm', 'distilbert', 'bert'])
qf = [em(s, m, 'qflag_F1') for s in ['orig', 'reclass'] for m in ALL]
oF = {m: em('orig', m, 'onlyF_flagged') for m in ALL}; fq = [em('orig', m, 'FQ_flagged') for m in TR]
assert oF['svm'] > 0.44 and max(oF[m] for m in TR) < 0.35
pdR = {d: float(np.mean([ER[f'orig|roberta|{s}']['per_dataset'][d] for s in SEEDS])) for d in bd}
assert pdR['leeds'] > 0.75 and pdR['reqview'] > 0.75 and pdR['dronology'] < 0.5 and pdR['wasp'] < 0.5
rc = em('reclass', 'roberta', 'onlyF_flagged')
F['RESULTS_PARA_EXT'] = (
    f"*External test.* Trained on all of PROMISE with its original labels and applied to the {cnt['total']} industrial "
    f"requirements, the SVM reached a macro-F1 of {f3(em('orig', 'svm'))} on the {bk['onlyF'] + bk['onlyQ']} items that have "
    f"only a functional or only a quality aspect. The transformers reached {ems('orig', 'distilbert')} (DistilBERT), "
    f"{ems('orig', 'bert')} (BERT) and {ems('orig', 'roberta')} (RoBERTa), and the within-document bootstrap put their "
    f"seed-averaged advantage over the SVM at +{f3(min(b['diff'] for b in vs['orig']))} to +{f3(max(b['diff'] for b in vs['orig']))}, "
    f"with every interval excluding zero. The large standard deviations come mostly from seed 44, which gave "
    f"{rng3(s44)} for all three transformers against {rng3(oth)} for seeds 42 and 43. Training on the relabelled PROMISE "
    f"instead changed little for the SVM, DistilBERT and BERT (all intervals for the difference include zero), but it "
    f"raised RoBERTa to {ems('reclass', 'roberta')}, a gain of {f3(rmo['roberta']['diff'])} (95% interval "
    f"{f3(rmo['roberta']['lo'])} to {f3(rmo['roberta']['hi'])}). As a quality flag over all {cnt['total']} items, every "
    f"model reached an F1 between {f2(min(qf))} and {f2(max(qf))}. The errors differ, however: with the original labels the "
    f"transformers flagged {pct(min(oF[m] for m in TR))}\u2013{pct(max(oF[m] for m in TR))} of the purely functional items "
    f"as having a quality aspect, against {pct(oF['svm'])} for the SVM, and flagged {pct(min(fq))}\u2013{pct(max(fq))} of "
    f"the mixed F+Q items. Results also varied by document. RoBERTa reached {f2(pdR['leeds'])} on Leeds and "
    f"{f2(pdR['reqview'])} on ReqView, but only {f2(pdR['dronology'])} on Dronology and {f2(pdR['wasp'])} on WASP, where "
    f"only {bd['dronology']['onlyQ']} and {bd['wasp']['onlyQ']} items are purely quality requirements, so those two "
    f"values rest on very few items.")

# calibration transfer
taus = {k: v for k, v in EC.items() if v['tau'] is not None}
assert len(taus) == 8 and 'distilbert|43' not in taus
met = [k for k, v in taus.items() if v['prec'] >= 0.95]; fail = sorted(set(taus) - set(met))
assert len(met) == 5 and all(k.endswith('|44') for k in fail) and len(fail) == 3
er = [v['ECE_raw'] for v in EC.values()]; ecl = [v['ECE_cal'] for v in EC.values()]
cov = [v['cov'] for v in taus.values()]; na = [v['n_auto'] for v in taus.values()]; pr = [v['prec'] for v in taus.values()]
F['RESULTS_PARA_TRANSFER'] = (
    f"The calibration did not transfer well. With the temperature fitted on the PROMISE out-of-fold predictions of the "
    f"same model and seed, the external ECE fell from {rng2(er)} to {rng2(ecl)}, so the scores stayed miscalibrated. A "
    f"threshold for 0.95 precision could be set on PROMISE in eight of the nine runs. Applied unchanged to the external "
    f"items, it auto-labelled {pct(min(cov))}\u2013{pct(max(cov))} of them ({min(na)}\u2013{max(na)} items) at a precision "
    f"of {rng2(pr)}, and met the target in only {len(met)} of the {len(taus)} runs; the three failures were the seed-44 "
    f"runs of all three transformers.")

# zero-shot LLM
assert LLM['A_share_pred_NFR'] < 0.1 and LLM['E_qflag_R'] < 0.05 and abs(LLM['B_macroF1'] - mf('B', 'project', 'svm')) < 0.01
F['RESULTS_PARA_LLM'] = (
    f"*Zero-shot LLM.* Without any training, Qwen2.5-1.5B-Instruct reached a macro-F1 of {f3(LLM['A_macroF1'])} on Task A, "
    f"because it called only {pct(LLM['A_share_pred_NFR'])} of the requirements non-functional although {pct(370 / 625)} are. "
    f"On Task B it reached {f3(LLM['B_macroF1'])}, about the same as the SVM on unseen projects. On the external items it "
    f"flagged only {pct(LLM['E_qflag_R'])} of the items with a quality aspect (macro-F1 {f3(LLM['E_macroF1'])}). A "
    f"model of this size with one fixed prompt is a weak baseline, and larger models or few-shot prompts may do much "
    f"better; we did not test them.")

# fold-level spread (DistilBERT, random Task B) for the pooled-score remark
zb = np.load(f'{BPR}/B_random_distilbert_42.npz')
facc = [float((zb['pred'][zb['fold'] == k] == zb['y'][zb['fold'] == k]).mean()) for k in np.unique(zb['fold'])]
F['FOLD_ACC'] = f'{min(facc):.2f} to {max(facc):.2f}'
F['B_FOLD_N'] = str(round(249 / 10))

# ---------------------------------------------------------------- literature comparison numbers (Section IV-B)
F['A_SVM_RND'] = f3(mf('A', 'random', 'svm')); F['A_TR_RND'] = rng3([mf('A', 'random', m) for m in TR])
F['B_ROB_RND'] = f3(mf('B', 'random', 'roberta')); F['B_RND_TR'] = rng3([mf('B', 'random', m) for m in TR])

# ---------------------------------------------------------------- abstract, discussion, conclusion
trA = [mf('A', 'project', m) for m in TR]
F['ABSTRACT_RESULT'] = (
    f"On random folds all models tied on functional versus non-functional classification (macro-F1 {rng3(aR)}). On unseen "
    f"projects every score fell, but the transformers fell less ({rng3(trA)} versus {f3(mf('A', 'project', 'svm'))} for the "
    f"SVM; project-bootstrap intervals excluded zero in eight of nine runs). On the industrial requirements they led the SVM "
    f"by {f3(min(b['diff'] for b in vs['orig']))}\u2013{f3(max(b['diff'] for b in vs['orig']))} macro-F1, but confidence "
    f"thresholds set on PROMISE met their precision target in only {len(met)} of {len(taus)} runs.")
F['DISC_RESULT'] = (
    f"Under random folds a linear TF-IDF model was as good as any transformer for the coarse FR/NFR decision, whereas "
    f"RoBERTa and DistilBERT were clearly better at separating quality classes. Moving to project-held-out folds cost the "
    f"SVM {dA['svm'] * 100:.0f} points of macro-F1 on Task A but the transformers only {min(dA[m] for m in TR) * 100:.0f}\u2013"
    f"{max(dA[m] for m in TR) * 100:.0f}, part of which may come from smaller training sets and uneven test folds rather "
    f"than from unseen projects alone. The transformers' advantage is therefore largest where it matters for adoption, on "
    f"projects they have not seen, which agrees with the unseen-project results of NoRBERT {{{{hey2020norbert;hey2022corrected}}}}. "
    f"The external test points the same way, with a smaller margin: on documents written by other teams and labelled by "
    f"other researchers, the transformers stayed ahead of the SVM, but their scores ({rng3([em('orig', m) for m in TR])}) "
    f"were far below the random-fold numbers and varied strongly with the seed and the document. Two cautions follow. BERT-base, "
    f"the original model of the family, was the weakest transformer on Task B and the worst calibrated, so the choice of "
    f"encoder matters even within one family. And calibration is not portable: temperature scaling fixed most of the "
    f"miscalibration on held-out PROMISE folds, but a threshold chosen on PROMISE missed its precision target on the "
    f"external documents in {len(taus) - len(met)} of {len(taus)} runs. For a team, the practical consequence is that any "
    f"model, and especially its confidence threshold, should be re-checked on the team's own items before its labels are "
    f"trusted.")
F['CONCL_RESULT'] = (
    f"on random folds the fully fine-tuned DistilBERT, BERT and RoBERTa were no better than a linear SVM at separating "
    f"functional from non-functional requirements (macro-F1 {rng3(aR)}), but RoBERTa and DistilBERT were clearly better at "
    f"telling the four most frequent quality classes apart. When whole projects were held out, every model lost ground, "
    f"and the first task changed from a statistical tie to a clear transformer lead ({rng3(trA)} against "
    f"{f3(mf('A', 'project', 'svm'))}). On {cnt['total']} industrial requirements from four other projects the "
    f"transformers kept a smaller lead over the SVM, and its bootstrap intervals excluded zero. Even so, the best model found only about two thirds of "
    f"the functional requirements of an unseen project, and confidence thresholds did not carry over from PROMISE to "
    f"new documents, so a confidence gate needs calibration on the team's own items before it can be trusted.")
json.dump(F, open('/home/user/work/fill.json', 'w'), indent=1, ensure_ascii=False)
for k, v in F.items(): print(k, ':', v if k != 'RES_ROWS' else '\n  ' + '\n  '.join(' | '.join(r) for r in v))
