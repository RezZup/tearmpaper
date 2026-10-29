# -*- coding: utf-8 -*-
"""Phase 2, part b: project-held-out protocol, new Table III / Fig. 4, Sections IV-VI and abstract."""
P = '/home/user/work/content.py'
s = open(P, encoding='utf-8').read()
R = [
# --- abstract (kept within 150-200 words; the result sentence is filled from results.json)
("    \"planning. We synthesise 35 verified sources on classical, deep-learning, transformer and zero-shot classifiers, and \"\n"
 "    \"propose a two-level framework whose confidence gate sends uncertain items to the Product Owner rather than labelling \"\n"
 "    \"them silently. In our own replication on the PROMISE NFR dataset (625 requirements), TF-IDF baselines and a \"\n"
 "    \"partially frozen, CPU-trained DistilBERT shared identical stratified 10-fold splits. <<ABSTRACT_RESULT>> Published \"\n"
 "    \"BERT scores on PROMISE reach 0.94\\u20130.99 F1, but, like ours, they rest on one small, dated corpus and mostly on \"\n"
 "    \"random rather than project-level splits. We conclude that BERT classifiers suit refinement assistance better than \"\n"
 "    \"autonomous labelling, and we list the evidence still missing for real backlogs.\"",
 "    \"planning. We synthesise 35 verified sources and propose a two-level framework whose confidence gate sends uncertain \"\n"
 "    \"items to the Product Owner rather than labelling them silently. In our own replication on the PROMISE NFR dataset \"\n"
 "    \"(625 requirements, 15 projects), we compared TF-IDF baselines with a partially frozen, CPU-trained DistilBERT under \"\n"
 "    \"random 10-fold and project-held-out splits. <<ABSTRACT_RESULT>> Published BERT scores on PROMISE reach \"\n"
 "    \"0.94\\u20130.99 F1, but they rest on one small, dated corpus and mostly on random splits. We conclude that BERT \"\n"
 "    \"classifiers suit refinement assistance better than autonomous labelling, and that results on unseen projects, not \"\n"
 "    \"random folds, should guide adoption.\""),
# --- contributions
("\"a small replication that we ran ourselves on PROMISE NFR, comparing DistilBERT with three TF-IDF baselines on \"\n"
 "       \"identical folds, with every hyper-parameter and limitation stated;\",",
 "\"a small replication that we ran ourselves on PROMISE NFR, comparing DistilBERT with three TF-IDF baselines on \"\n"
 "       \"identical random and project-held-out folds over three seeds, with every hyper-parameter and limitation stated \"\n"
 "       \"and a script that reproduces every number;\","),
# --- data paragraph: 10-fold wording
("too few for a 10-fold estimate, so we left them out.",
 "too few for a reliable per-class estimate, so we left them out."),
# --- protocol
("p(\"*Protocol.* All models share the same stratified 10-fold splits (scikit-learn, seed 42). We pool the out-of-fold \"\n"
 "  \"predictions and report per-class precision, recall and F1, their macro averages and accuracy. We used random rather \"\n"
 "  \"than project-held-out folds. [[sec:disc]] explains why this flatters every model, including ours. We did no \"\n"
 "  \"hyper-parameter search for any model: the baselines use common defaults and DistilBERT uses the settings below. \"\n"
 "  \"Tuning on the same folds would have made the comparison look better without making it more honest.\")",
 "p(\"*Protocol.* We used two protocols, and within each one all models share the same splits. *Random*: stratified \"\n"
 "  \"10-fold cross-validation (scikit-learn), in which requirements from one project fall on both sides of a split. \"\n"
 "  \"*Project-held-out*: five folds built with StratifiedGroupKFold using the PROMISE project identifier as the group, so \"\n"
 "  \"no project contributes to both training and test data. Each protocol was run with seeds 42, 43 and 44, except that \"\n"
 "  \"random-fold DistilBERT was trained for seed 42 only because of the CPU budget. For each run we pool the out-of-fold \"\n"
 "  \"predictions and compute per-class precision, recall and F1, their macro averages and accuracy; [[tab:res]] reports \"\n"
 "  \"macro-F1 as mean \\u00b1 standard deviation over seeds. Paired comparisons use exact McNemar tests on the pooled \"\n"
 "  \"predictions of one seed. We did no hyper-parameter search for any model: the baselines use common defaults and \"\n"
 "  \"DistilBERT uses the settings below. Tuning on the same folds would have made the comparison look better without \"\n"
 "  \"making it more honest. Code, splits and every model's out-of-fold predictions are in our reproducibility package.\")"),
# --- results paragraphs, table, figure
("p(\"*Results.* [[tab:res]] and [[fig:res]] give the results. <<RESULTS_PARA_1>>\")\np(\"<<RESULTS_PARA_2>>\")\n"
 "RES_HEAD = ['Model', 'A: mF1', 'A: Acc.', 'B: mF1', 'B: Acc.']\n"
 "tab('tab:res', 'Our experiment: pooled 10-fold results on PROMISE NFR (Task A: FR vs. NFR, n = 625; Task B: US/SE/O/PE, n = 249). mF1 = macro-F1; best value per column in bold.',\n"
 "    RES_HEAD, '<<RES_ROWS>>', r'p{2.9cm}cccc', [1.3, 0.55, 0.5, 0.55, 0.5], size='footnotesize')\n"
 "fig('fig:res', 'fig4_results', 'Our experiment: per-class F1 on Task B (top) and macro-F1 on both tasks (bottom), pooled over the same 10 folds for every model. Note that the y-axes do not start at zero.', width=3.4)",
 "p(\"*Results.* [[tab:res]] and [[fig:res]] give the results. <<RESULTS_PARA_1>>\")\np(\"<<RESULTS_PARA_G>>\")\np(\"<<RESULTS_PARA_2>>\")\n"
 "RES_HEAD = ['Model', 'A random', 'A project', 'B random', 'B project']\n"
 "tab('tab:res', 'Our experiment: macro-F1 on PROMISE NFR, mean \\u00b1 SD over seeds 42\\u201344 of pooled out-of-fold predictions. Random = stratified 10-fold; project = project-held-out 5-fold. Task A: FR vs. NFR (n = 625); Task B: US/SE/O/PE (n = 249). \\u2020 One seed (42). Best mean per column in bold. Accuracies are in the reproducibility package.',\n"
 "    RES_HEAD, '<<RES_ROWS>>', r'p{1.75cm}cccc', [1.05, 0.62, 0.62, 0.62, 0.62], size='scriptsize')\n"
 "fig('fig:res', 'fig4_results', 'Our experiment: macro-F1 under random 10-fold and project-held-out 5-fold splits, mean over seeds 42\\u201344 with SD error bars (random-fold DistilBERT: seed 42 only). The y-axis starts at 0.4.', width=3.4)"),
# --- literature results paragraph
("not read this as DistilBERT beating NoRBERT. The protocols differ: we used random stratified folds over four classes, \"\n"
 "  \"while NoRBERT's corrected project-level scores are about five points below its originally reported ones \"\n"
 "  \"{{hey2020supp}}, which indicates how much random or leaky splits can add. Model capacity differs in the opposite \"",
 "not read this as DistilBERT beating NoRBERT. The protocols differ: we used random stratified folds over four classes, \"\n"
 "  \"and our own project-held-out runs in [[tab:res]] show how much such folds add on PROMISE. NoRBERT's corrected \"\n"
 "  \"report also lowers its unseen-project improvement from 15 to 10 percentage points {{hey2022corrected}}, another sign \"\n"
 "  \"that headline numbers depend on the split. Model capacity differs in the opposite \""),
("distilled model with a third of its blocks frozen. Our TF-IDF+SVM macro-F1 of <<A_SVM>> on Task A is close to the \"\n"
 "  \"roughly 92% precision and recall reported by {{t:kurtanovic2017}}, so the classical baseline appears to be \"\n"
 "  \"reasonably reproduced.",
 "distilled model with a third of its blocks frozen. Our random-fold TF-IDF+SVM macro-F1 of <<A_SVM>> on Task A is \"\n"
 "  \"close to the roughly 92% precision and recall reported by {{t:kurtanovic2017}} and to the F-measure of 0.91 that \"\n"
 "  \"{{t:diascanedo2020}} report for TF-IDF models on the larger PROMISE_exp, so the classical baseline appears to be \"\n"
 "  \"reasonably reproduced."),
# --- discussion
("as good as feature-engineered models on PROMISE-style text and are better at transferring to unseen projects \"\n"
 "  \"{{hey2020norbert;hey2020supp}}.",
 "as good as feature-engineered models on PROMISE-style text and are better at transferring to unseen projects \"\n"
 "  \"{{hey2020norbert;hey2022corrected}}."),
("Our own results \"\n"
 "  \"sharpen this picture. For the coarse FR/NFR decision a linear TF-IDF model was as good as DistilBERT, whereas for \"\n"
 "  \"separating quality classes the transformer was clearly better. For a team, this suggests that a transformer pays off \"\n"
 "  \"mainly at Level 2 of the framework, and that a cheap linear model may be enough at Level 1.",
 "Our own results \"\n"
 "  \"sharpen this picture. <<DISC_RESULT>>"),
# --- threats
("*Internal validity.* We used one random seed per fold, no hyper-parameter search, and \"\n"
 "  \"a partially frozen encoder.",
 "*Internal validity.* We used three seeds per protocol, except for random-fold DistilBERT \"\n"
 "  \"(one seed), no hyper-parameter search, and a partially frozen encoder."),
("*External validity.* Random 10-fold \"\n"
 "  \"splits put requirements from the same project into both training and test data, which inflates all scores; \"\n"
 "  \"{{t:hey2020supp}} quantified a drop of about five points when folds were made properly project-specific. PROMISE \"\n"
 "  \"contains English \\u201cshall\\u201d statements,",
 "*External validity.* Random 10-fold \"\n"
 "  \"splits put requirements from the same project into both training and test data. Our project-held-out runs measure \"\n"
 "  \"how much this inflates scores on PROMISE, but they cover only 15 projects of one corpus, with uneven fold sizes and \"\n"
 "  \"no time order. PROMISE contains English \\u201cshall\\u201d statements,"),
("*Conclusion validity.* With 249 items in Task B, each test fold holds about 25 items, so fold-level accuracies vary \"\n"
 "  \"considerably. We therefore report pooled scores and paired McNemar tests rather than claiming small differences.",
 "*Conclusion validity.* With 249 items in Task B, random test folds hold about 25 items, so fold-level accuracies \"\n"
 "  \"vary considerably. We therefore report pooled scores, spread over seeds and paired McNemar tests rather than claiming \"\n"
 "  \"small differences. The spread over three seeds is itself only a rough estimate."),
# --- conclusion
("(2) Evaluate with project-held-out and \"\n"
 "  \"time-ordered splits as standard.",
 "(2) Make project-held-out and time-ordered \"\n"
 "  \"splits the standard; our project-held-out runs are a first step, but they cover 15 PROMISE projects and no time \"\n"
 "  \"order."),
]
for a, b in R:
    n = s.count(a)
    assert n == 1, (n, a[:100])
    s = s.replace(a, b)
open(P, 'w', encoding='utf-8').write(s)
print('applied', len(R))
