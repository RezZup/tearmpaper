# -*- coding: utf-8 -*-
"""Phase 3: user's corrections 1-12 (text side). Works on the joined-string form of content.py."""
import re
P = '/home/user/work/content.py'
s = re.sub(r'"\s*\n\s*"', '', open(P, encoding='utf-8').read())
R = [
# item 9, 10, 2 (abstract)
("We synthesise 35 verified sources and propose", "We synthesise 35 sources and propose"),
("In our replication on the PROMISE NFR dataset (625 requirements, 15 projects), we compared TF-IDF baselines with a partially frozen, CPU-trained DistilBERT under",
 "In a comparative experiment on the PROMISE NFR dataset (625 requirements, 15 projects), we compared TF-IDF baselines with a partially frozen DistilBERT under"),
("but they rest on one small, dated corpus and mostly on random splits. We conclude that BERT classifiers suit refinement assistance better than autonomous labelling, and that results on unseen projects, not random folds, should guide adoption.",
 "but they rest on one small, dated corpus, often without project-level splits. We conclude that BERT classifiers suit refinement assistance better than autonomous labelling."),
# item 10 (contribution 3, heading, conclusion)
("\"a small replication that we ran ourselves on PROMISE NFR,", "\"a small comparative experiment that we ran ourselves on PROMISE NFR,"),
("h2('Our Replication on PROMISE NFR', 'sec:ownexp')", "h2('Our Comparative Experiment on PROMISE NFR', 'sec:ownexp')"),
("Our own small replication found that <<CONCL_RESULT>>", "Our own small comparative experiment found that <<CONCL_RESULT>>"),
# item 11
("We screened around 60 candidate records and kept 35.", "We screened the candidate records and kept 35."),
# item 12
("Most of its items are written as user stories; {{t:lucassen2016use}} surveyed",
 "User stories are an increasingly popular way to write these items; {{t:lucassen2016use}} surveyed"),
# item 7 (II-B pattern paragraph, Rahman)
("A pattern runs through these numbers. The highest scores tend to come from the smallest evaluation sets and the least clearly described splits. An F1 of 0.966 on roughly 370 short sentences is plausible under random cross-validation, where requirements from the same project, often with near-identical wording, fall on both sides of a split. It says little about how the same model would label a new team's backlog.",
 "A pattern runs through several of these numbers, although not all of them. Some of the highest scores come from small evaluation sets, from validation rather than test data, or from briefly described splits. The F1 of 0.966 reported by {{t:rahman2019}} is an average over cross-validation folds of PROMISE NFR's roughly 370 non-functional requirements; on a separately selected test set, the same LSTM averaged an F1 of 0.70. Under random cross-validation, requirements from the same project, often with near-identical wording, fall on both sides of a split. Not every high score fits this pattern, however: {{t:eltahier2025}} also report 0.97 on a second dataset, FR_NFR. A high random-fold score says little about how the same model would label a new team's backlog."),
("'LSTM (validation): P 0.973, R 0.967, F1 0.966', 'Split protocol limits comparison'",
 "'LSTM (validation): P 0.973, R 0.967, F1 0.966', 'Test-set F1 0.70'"),
# item 7 (II-D, Alhoshan)
("against 0.93 for the supervised Kurtanovi\\u0107\\u2013Maalej model on FR and 0.93 for NoRBERT on NFR.",
 "against supervised F1 scores of 0.93 for the Kurtanovi\\u0107\\u2013Maalej SVM on FR and 0.93 for NoRBERT on NFR, which they took from the original studies."),
# item 1 and 5 (IV-B)
("our own project-held-out runs in [[tab:res]] show how much such folds add on PROMISE.",
 "on PROMISE our own project-held-out runs in [[tab:res]] score well below our random-fold runs, although that gap also reflects smaller training sets."),
("both above our <<A_BERT>>.", "both above our seed-42 <<A_BERT>>."),
("our DistilBERT macro-F1 of <<B_BERT>> is higher", "our seed-42 DistilBERT macro-F1 of <<B_BERT>> is higher"),
("Our random-fold TF-IDF+SVM macro-F1 of <<A_SVM>> on Task A is close",
 "Our seed-42 random-fold TF-IDF+SVM macro-F1 of <<A_SVM>> on Task A (three-seed mean <<A_SVM_MEAN>>) is close"),
# item 5 (threats, external validity)
("Our project-held-out runs measure how much this inflates scores on PROMISE, but they cover only 15 projects of one corpus, with uneven fold sizes and no time order.",
 "Our project-held-out runs show how much lower the scores are when this is prevented, but the gap is not a pure measure of that leakage: the project-held-out models also train on less data (about 80% of the items instead of 90%), and their test folds differ in size and class mix, with projects 11\\u201315 contributing no functional requirements. The runs also cover only 15 projects of one corpus, with no time order."),
# item 6 (threats, conclusion validity)
("We therefore report pooled scores, spread over seeds and paired McNemar tests rather than claiming small differences.",
 "We therefore report pooled scores, spread over seeds and paired McNemar tests rather than claiming small differences. McNemar's test assumes independent items, but requirements from the same project share authors, vocabulary and templates, so our p-values are likely optimistic."),
]
for old, new in R:
    n = s.count(old); assert n == 1, (n, old[:90]); s = s.replace(old, new)
open(P, 'w', encoding='utf-8').write(s)
print('applied', len(R))
