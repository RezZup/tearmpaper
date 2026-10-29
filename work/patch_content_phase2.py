# -*- coding: utf-8 -*-
"""Phase 2 text fixes from the reference audit (reference_audit.md) and the claim check.
Each pair must match exactly once."""
import shutil
P = '/home/user/work/content.py'
shutil.copy(P, '/home/user/work/content_phase1.py')
s = open(P, encoding='utf-8').read()

R = [
# --- markup doc + author placeholders
("  {{k1;k2}}            parenthetical APA citation       {{t:key}}  narrative citation",
 "  {{k1;k2}}            numbered IEEE citation [n]        {{t:key}}  narrative: Author et al. [n]"),
("AUTHOR = ('[Author Name]', '[Department, Institution]', '[City, Country] \\u00b7 [e-mail]')",
 "AUTHOR = ('[NAME]', '[DEPARTMENT]', '[INSTITUTION]', '[CITY, COUNTRY]', '[EMAIL]')"),
# --- Introduction
("{{kurtanovic2017}} and convolutional or recurrent networks {{navarro2017;rahman2019}}.",
 "{{kurtanovic2017;diascanedo2020}} and convolutional or recurrent networks {{rahman2019;rahimi2021}}."),
("on projects not seen during training {{hey2020norbert}}. Yet three gaps remain. First, almost every result comes from \"\n  \"the PROMISE NFR corpus,",
 "on projects not seen during training {{hey2020norbert;hey2022corrected}}. Yet three gaps remain. First, most results on \"\n  \"FR/NFR classification come from the PROMISE NFR corpus or its extensions,"),
("Third, few studies say what a team should *do* with a \"\n  \"predicted label,",
 "Third, few of the studies we reviewed say what a team \"\n  \"should *do* with a predicted label,"),
# --- Related work: classical
("model, but it generalised better to other datasets and its decisions could be explained. To us this is the more useful \"\n  \"result for practice, because a Product Owner is more likely to trust a tag whose cause can be shown.\")",
 "model, but it generalised better to other datasets and its decisions could be explained. To us this is the more useful \"\n  \"result for practice, because a Product Owner is more likely to trust a tag whose cause can be shown. \"\n  \"{{T:diascanedo2020}} compared bag-of-words, TF-IDF and chi-squared features with logistic regression, SVM, \"\n  \"multinomial Naive Bayes and k-nearest neighbours on PROMISE_exp. TF-IDF with logistic regression gave the best \"\n  \"F-measure: 0.91 for FR/NFR (tied with the SVM), 0.74 for the NFR classes and 0.78 overall. These are the same feature \"\n  \"and model families as our baselines in [[sec:exp]].\")"),
("p(\"Neural models followed. {{t:winkler2016}} used a convolutional network to separate requirements from explanatory \"\n  \"text in industrial specifications and reached a precision of 0.73 and a recall of 0.89. {{t:navarro2017}} applied a \"\n  \"CNN with word embeddings to the twelve PROMISE classes and obtained a precision of 0.80, a recall of 0.785 and an F1 \"\n  \"of 0.77. {{t:rahman2019}} compared recurrent variants on PROMISE NFR and reported that an LSTM reached a precision of \"\n  \"0.973, a recall of 0.967 and an F1 of 0.966, ahead of GRU and CNN models. {{t:rahimi2021}} stacked LSTM, BiLSTM, GRU \"\n  \"and CNN models into an ensemble and reported 92.56% accuracy for one-phase classification.",
 "p(\"Neural models followed. {{t:rahman2019}} compared recurrent variants on PROMISE NFR and reported that an LSTM \"\n  \"reached a validation precision of 0.973, recall of 0.967 and F1 of 0.966, ahead of GRU and CNN models. \"\n  \"{{t:rahimi2021}} combined LSTM, BiLSTM, GRU and CNN models in an ensemble on a 17-class PROMISE variant that also \"\n  \"labels functional subtypes, and reported 92.56% accuracy for one-phase classification."),
# --- NoRBERT
("p(\"NoRBERT was the first systematic use of BERT for requirements classification {{hey2020norbert}}. On PROMISE NFR it \"\n  \"reached an F1 of up to 94% for FR/NFR, an average F1 of 87% on the most frequent quality classes, and gains of up to \"\n  \"15 percentage points over earlier work when tested on unseen projects. The authors later reported a bug that made \"\n  \"their project-specific folds not strictly project-specific; corrected scores were about five points lower, although \"\n  \"the advantage on unseen projects held {{hey2020supp}}. We regard this correction as one of the most instructive \"\n  \"episodes in the field. It shows how easily leakage between folds can inflate results, and it was disclosed openly.\")",
 "p(\"NoRBERT was an early and widely cited application of BERT fine-tuning to requirements classification \"\n  \"{{hey2020norbert}}. On PROMISE NFR it reached an F1 of up to 94% for FR/NFR and an average F1 of 87% on the most \"\n  \"frequent quality classes. In an unseen-project setup on a relabelled version of PROMISE it reported an improvement of \"\n  \"15 percentage points over earlier approaches. The authors later released a corrected version, citing a bug in part of \"\n  \"the evaluation, in which that improvement is ten percentage points {{hey2022corrected}}. We regard this correction as \"\n  \"one of the most instructive episodes in the field. It shows how much the split protocol can change a headline number, \"\n  \"and it was disclosed openly.\")"),
# --- later studies
("(PRCBERT) and, with self-learning, reached zero-shot F1 scores of 53.27% on NFR-Review and 72.96% on NFR-SO. \"\n  \"Domain-specific work includes aeroBERT, which classified 310 aerospace requirements with an average F1 of 0.83 \"\n  \"{{tikayatray2023}},",
 "(PRCBERT). A model fine-tuned on PROMISE and transferred without labels, with self-learning, reached weighted F1 \"\n  \"scores of 53.27% on NFR-Review and 72.96% on NFR-SO. Domain-specific work includes aeroBERT, fine-tuned on a corpus \"\n  \"of 310 aerospace requirements, which reached an average F1 of 0.83 on a 31-item test set {{tikayatray2023}},"),
("while {{t:eltahier2025}} reported an F1 of 0.99 on PROMISE and 0.97 on the FR_NFR dataset after \"\n  \"varying model components and training-set size.",
 "while {{t:eltahier2025}} reported an average F1 of 0.99 on PROMISE and 0.97 on the FR_NFR dataset. \"\n  \"Their protocol is stratified 10-fold cross-validation with weighted F1, and hyper-parameters were chosen by ablation \"\n  \"on the same data."),
# --- zero/few shot
("contrastively fine-tunes a sentence transformer on a handful of pairs; with only eight labelled examples per class it was \"\n  \"competitive with fully fine-tuned RoBERTa-Large on a sentiment benchmark {{tunstall2022setfit}}. To our knowledge it has \"\n  \"not yet been evaluated on PROMISE, which makes it a natural next step.",
 "contrastively fine-tunes a sentence transformer on pairs of labelled examples; with eight labelled examples per class \"\n  \"on the Customer Reviews sentiment dataset it was competitive with RoBERTa-Large fine-tuned on the full training set \"\n  \"{{tunstall2022setfit}}. {{T:petrillo2025}} applied SetFit and fine-tuned transformers to security-requirements \"\n  \"classification on the SecReq dataset. We did not find a study that applies SetFit to PROMISE NFR, although our search \"\n  \"was not systematic."),
# --- agile backlog support
("{{t:mejia2026loona}} built LOONA, an LLM assistant for the quality assurance of Spanish user stories, and reported a \"\n  \"\\u03ba of 0.76 in an evaluation on 100 stories.",
 "{{t:mejia2026loona}} built LOONA for the quality assurance of Spanish user stories: a fine-tuned Spanish BERT \"\n  \"classifier flags defective stories, and a confidence threshold decides when a generative model proposes a rewrite. \"\n  \"The classifier reached an F1 of 0.91 in 5-fold cross-validation on expert-labelled stories."),
("None of \"\n  \"these studies feeds requirement-type labels into prioritisation or refinement,",
 "None of \"\n  \"the studies cited in this subsection feeds requirement-type labels into prioritisation or refinement,"),
# --- Table I
("    ['{{winkler2016}}', 'Industrial specifications', 'CNN (requirement vs. information)', 'P 0.73, R 0.89', 'Different task'],\n"
 "    ['{{navarro2017}}', 'PROMISE, 12 classes', 'CNN + word embeddings', 'P 0.80, R 0.785, F1 0.77', 'Includes rare classes'],\n"
 "    ['{{rahman2019}}', 'PROMISE NFR', 'LSTM / GRU / CNN', 'LSTM: P 0.973, R 0.967, F1 0.966', 'Split protocol limits comparison'],\n"
 "    ['{{rahimi2021}}', 'PROMISE', 'Ensemble of DL models', 'Acc. 95.7% (binary), 93.4% (multi-class), two-phase', 'Accuracy only'],\n"
 "    ['{{hey2020norbert}}', 'PROMISE NFR', 'NoRBERT (BERT fine-tuning)', 'FR/NFR F1 up to 94%; frequent NFR avg. F1 87%', 'Corrected folds \\u2248 5 pp lower {{hey2020supp}}'],",
 "    ['{{diascanedo2020}}', 'PROMISE_exp (969)', 'TF-IDF / BoW / CHI2 + LR, SVM, MNB, kNN', 'TF-IDF+LR F 0.91 (FR/NFR, tie with SVM); 0.74 (NFR classes)', 'Same model families as our baselines'],\n"
 "    ['{{rahman2019}}', 'PROMISE NFR', 'LSTM / GRU / CNN', 'LSTM (validation): P 0.973, R 0.967, F1 0.966', 'Split protocol limits comparison'],\n"
 "    ['{{rahimi2021}}', 'PROMISE, 17-class variant', 'Ensemble of DL models', 'Acc. 95.7% (binary), 93.4% (multi-class), two-phase', 'Accuracy only'],\n"
 "    ['{{hey2020norbert}}', 'PROMISE NFR', 'NoRBERT (BERT fine-tuning)', 'FR/NFR F1 up to 94%; frequent NFR avg. F1 87%', 'Unseen-project gain 15 pp, corrected to 10 pp {{hey2022corrected}}'],"),
("    ['{{luo2022prcbert}}', 'NFR-Review, NFR-SO', 'PRCBERT prompt learning', 'Zero-shot F1 53.27% / 72.96%', 'Non-SRS text'],",
 "    ['{{luo2022prcbert}}', 'NFR-Review, NFR-SO', 'PRCBERT prompt learning', 'Transferred, no labels: weighted F1 53.27% / 72.96%', 'Non-SRS text'],"),
("    ['{{tikayatray2023}}', '310 aerospace requirements', 'aeroBERT-Classifier', 'Average F1 0.83', 'Domain-specific'],",
 "    ['{{tikayatray2023}}', '310 aerospace requirements', 'aeroBERT-Classifier', 'Average F1 0.83', '31-item test set'],\n"
 "    ['{{petrillo2025}}', 'SecReq (623, 3 specifications)', 'Fine-tuned transformers; SetFit', 'Best: Acc. 0.94, F1 0.90', 'Security vs. other only'],"),
("    ['{{eltahier2025}}', 'PROMISE; FR_NFR', 'BERT fine-tuning variants', 'F1 0.99 (PROMISE), 0.97 (FR_NFR)', 'Near ceiling; needs scrutiny'],",
 "    ['{{eltahier2025}}', 'PROMISE; FR_NFR', 'BERT fine-tuning variants', 'Weighted F1 0.99 (PROMISE), 0.97 (FR_NFR)', 'Tuned on the evaluation data'],"),
# --- method: imbalance
("The training loss \"\n  \"therefore weights each class by its inverse frequency, which is a standard algorithm-level remedy for imbalance \"\n  \"{{johnson2019}}:\")",
 "The training loss \"\n  \"therefore weights each class by its inverse frequency, a common algorithm-level remedy for imbalance that is \"\n  \"implemented through a weight or cost scheme {{johnson2019}}:\")"),
# --- challenges
("*Imbalance* is structural: some quality classes will always be rare, and a macro-averaged score is the \"\n  \"honest way to report it {{johnson2019}}.",
 "*Imbalance* is structural: some quality classes will always be rare, and accuracy can mislead on \"\n  \"imbalanced data {{johnson2019}}, which is why we report macro-averaged scores."),
("    ['Leakage and optimistic splits', '{{hey2020supp}}', 'Project- or time-based evaluation before roll-out'],",
 "    ['Optimistic random splits', '{{hey2022corrected}}; our [[sec:ownexp]]', 'Project-held-out or time-based evaluation before roll-out'],"),
]
for a, b in R:
    n = s.count(a)
    assert n == 1, (n, a[:90])
    s = s.replace(a, b)
open(P, 'w', encoding='utf-8').write(s)
print('applied', len(R), 'replacements')
