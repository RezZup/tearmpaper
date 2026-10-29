# Viva preparation: BERT-Based Requirement Classification for Agile Backlog Management

All numbers are from our own runs (`repro/outputs/results.json`) unless a reference is named. Literature numbers are the authors' own figures.

## Part 1. The method in plain language

**The question.** Backlog items are a mix of features ("the user can reset a password") and quality concerns ("pages load within 2 s", "failed logins are logged"). Quality concerns that nobody tags tend to surface late. We asked whether a pre-trained language model such as BERT can tag these items well enough to help a Scrum team during refinement.

**The data.** PROMISE NFR is a public set of 625 requirement sentences from 15 student projects (around 2007). Each sentence carries one label: functional (F) or one of 11 quality types. It is the standard benchmark in this field, but it is small, old and written as "The system shall…" sentences, not user stories.

**Two tasks.**
- *Task A:* is an item functional or non-functional? (625 items, 255 F and 370 NFR.)
- *Task B:* for the four most common quality types (usability, security, operability, performance; 249 items), which type is it? The other seven quality types have too few examples to test reliably.

**Four models.**
- *Three classical baselines.* Each turns a sentence into a weighted word and word-pair count vector (TF-IDF) and feeds it to a simple classifier: Naive Bayes, logistic regression or a linear SVM.
- *DistilBERT.* A smaller, faster version of BERT. It has already learned English from large text collections, and we *fine-tune* it, meaning we continue training it on our labelled sentences.
  - Our sandbox had 2 CPU cores and about 2 GB of RAM, so we *froze* the word-embedding layer and the first 2 of its 6 layers. Frozen layers are not updated, which saves memory.
  - The loss gives rare classes more weight so that the model does not simply favour the majority class.

**How we tested: two protocols.**
1. *Random 10-fold cross-validation.* Shuffle all items, cut them into 10 parts, train on 9 and test on the 10th, and rotate. Every item is tested exactly once. Items from the same project end up in both training and test data, and items from one project often share wording, so this is an optimistic test.
2. *Project-held-out 5-fold.* Whole projects are kept together, so the model is always tested on projects it has never seen. This is closer to what happens when a team adopts a model trained elsewhere.

We repeated each protocol with three random seeds (42, 43, 44) and report the mean and standard deviation. The exception is random-fold DistilBERT, which ran for one seed only because of CPU time. No model was tuned on the test data.

**Measures.**
- *Macro-F1* is the F1 score (the balance of precision and recall) computed for each class separately and then averaged with equal weight. A model therefore cannot score well by getting only the big class right.
- *McNemar's test* compares two models on the same items. It looks only at items where exactly one model was right and asks whether that split is more lopsided than chance.

**What we found.**
- *Random folds (seed 42, the only DistilBERT seed under this protocol):*
  - On Task A all four models scored within 1.5 points of each other (SVM 0.916, DistilBERT 0.901 macro-F1; McNemar p = 0.35, not significant).
  - On Task B DistilBERT was clearly better (0.919 vs. 0.832 for the SVM on seed 42; the SVM's three-seed mean is 0.824; p < 0.001 against every baseline).
- *Project-held-out:*
  - Every model dropped. On Task A the baselines fell to 0.59–0.64 and DistilBERT to 0.751. On Task B the baselines fell to 0.70–0.72 and DistilBERT to 0.813.
  - So on unseen projects DistilBERT beat every baseline on *both* tasks (McNemar p ≤ 0.017 in every seed; one comparison fails a Bonferroni correction, and the test's independence assumption makes p-values optimistic). The Task A tie under random folds becomes a clear DistilBERT lead.
  - The main failure is functional items from an unseen project being labelled non-functional (functional recall averaged 0.28 for the SVM and only 0.56 for DistilBERT). DistilBERT is better, but still weak in absolute terms.
  - The drop is not leakage alone: project-held-out folds also train on less data (about 80% vs. 90% of items) and differ in class mix.

**What we conclude.** Scores from random folds overstate how well these models work on a new project. A classifier is best used as a *refinement assistant*: it suggests labels, and uncertain items go to the Product Owner through a confidence threshold. It should not label silently, and it should be checked on the team's own items before anyone trusts it.

## Part 2. Likely examiner questions with short answers

1. **Why did you use random folds at all, if they are optimistic?**
   They are what most published PROMISE results use, so they make our numbers comparable with the literature and show that our baselines are reproduced (SVM 0.916 on seed 42, mean 0.912 over three seeds, vs. about 0.92 reported by Kurtanović and Maalej). We then added project-held-out folds, on which every model scores much lower. Reporting both makes the gap visible. The gap is not a pure leakage measure, though (see Q2).

2. **What exactly is "leakage" here?**
   Requirements from the same project share vocabulary, product names and phrasing. With random folds a near-duplicate of a test sentence is often in the training data, so the model is partly tested on things it has effectively seen. Holding out whole projects removes this. But the drop from random to project-held-out scores is not caused by leakage alone. The two protocols also differ in training size: 10 folds train on 90% of the items, 5 folds on about 80% (409–600 items per Task A fold). They also differ in the test folds, which range from 25 to 216 items, and projects 11–15 contain no functional requirements at all.

3. **Why did you freeze part of DistilBERT?**
   Memory. Full fine-tuning keeps optimiser state for every weight, and with about 2 GB of RAM the run crashed. Freezing the embeddings and 2 of the 6 layers made it fit. The cost is that the model adapts less, so our DistilBERT numbers are a lower bound for what full fine-tuning would give, and we say so in the paper.

4. **Why DistilBERT and not BERT-base or RoBERTa?**
   It has about 40% fewer parameters and runs about 60% faster than BERT-base (Sanh et al.), which made CPU training feasible: about 4 minutes per fold on Task A. Comparing full BERT and RoBERTa under the same protocol is listed as future work.

5. **What does McNemar's test tell you, and why not a t-test?**
   Both models predict the same items, so the data are paired. McNemar counts the items where only model 1 is right (b) and only model 2 is right (c) and tests whether b and c differ more than chance would allow. We used the exact binomial version. A t-test over fold scores would rest on only 10 or 5 dependent numbers and would ignore the pairing at item level. Limitation: McNemar assumes the items are independent. Requirements from the same project share authors, vocabulary and templates, so they are not, and our p-values are likely optimistic. One of the 18 project-held-out comparisons (Task B, seed 43, vs. logistic regression, p = 0.017) would also fail a Bonferroni correction for three baselines (corrected p = 0.051).

6. **What does macro-F1 mean, and why not accuracy?**
   Macro-F1 averages the per-class F1 scores with equal weight. In Task A, 59% of the items are NFR, so a model that always says NFR gets 59% accuracy but a macro-F1 of only about 0.37. Accuracy hides failure on the smaller class; macro-F1 exposes it. We still publish accuracy in the reproducibility package.

7. **Why did the SVM match BERT on Task A?**
   In PROMISE, the functional/non-functional split is carried largely by surface words: action verbs for functional items, quality adjectives and numbers ("within 2 seconds", "99%") for NFR. Word and word-pair counts capture these cues well, and with only 625 short sentences there is little left for a pre-trained model to add. Our DistilBERT was also partially frozen and untuned. This is an explanation we did not test directly. Important follow-up: the tie holds only under random folds. On unseen projects DistilBERT was clearly better on Task A (0.751 vs. 0.589–0.638 for the three baselines), significantly better than each baseline in every seed (largest p 0.003). It still found only 56% of functional requirements, so it is better but not good. One plausible reading, which we did not test, is that the SVM's random-fold score relied on project-specific words that do not transfer.

8. **Then why did BERT win clearly on Task B?**
   Usability, security, operability and performance share most of their surface words ("user", "system", "shall"), and each class has only 54–67 examples. Pre-trained representations carry meaning that lets the model separate, say, "log failed logins" (security) from "change the backup schedule" (operability) without many examples.

9. **Why did scores drop so much on unseen projects, especially on Task A?**
   Mostly through the functional class: averaged over seeds, SVM functional recall fell to 0.28 (DistilBERT 0.56) while baseline NFR recall stayed at 0.93 or above. Functional requirements are written in each project's domain language ("dispute case", "meeting room"), which a new project does not share, whereas quality requirements reuse generic phrases. Projects 11–15 contain no functional items at all, and fold sizes range from 25 to 216 items. This explanation is plausible but untested. Part of the drop may also come from the smaller training sets of 5-fold project-held-out splits (about 80% of the items, against 90%).

10. **Is the comparison with NoRBERT or the 0.99 F1 of Eltahier et al. fair?**
    No, and the paper says so. Datasets, class sets, metrics (weighted vs. macro F1) and split protocols differ. NoRBERT's own corrected report lowered its unseen-project gain from 15 to 10 percentage points after a bug fix, which shows how sensitive such numbers are. We keep literature numbers in Table I and our own in Table III, never mixed.

11. **Why three seeds, and is the standard deviation meaningful?**
    The seeds change the fold assignment and DistilBERT's initialisation. Three seeds show whether a result depends on one lucky split. A standard deviation from three values is only a rough estimate, which we state as a limitation. Random-fold DistilBERT has one seed because of the CPU budget.

12. **Why no hyper-parameter tuning?**
    Tuning on the same folds we report would inflate the scores. A fair alternative is nested cross-validation, which would have multiplied the compute. We used common defaults for every model and stated them all, so the comparison is untuned but equal.

13. **How would the confidence gate work in practice, and how do you set the threshold?**
    The model applies a label automatically only if its top probability is at least τ; otherwise the item goes to the Product Owner with the two most likely labels shown. τ is chosen on held-out data so that the automatic labels reach an agreed precision (e.g., 0.95). Fine-tuned transformers tend to be over-confident, so calibration should be checked first. Our own runs show why calibration matters. On unseen projects, a threshold of 0.95 would have auto-labelled 89% of Task A items at only 0.81 precision, which is over-confident. On Task B it reached 0.99 precision but auto-labelled only 22%. We propose the gate but have not evaluated it with a team.

14. **Do your results apply to real user stories?**
    Not directly. PROMISE contains "The system shall…" sentences from student projects. Real backlogs contain terse stories, bugs and chores, often with several requirements in one item (van Can and Dalpiaz). Our project-held-out results suggest that performance on a new team's backlog could be much lower than random-fold scores imply. A labelled corpus of real backlog items is our first future-work item.

15. **How did you make sure the references and numbers are real?**
    Every DOI was resolved against Crossref, DataCite or arXiv. Numbers attributed to a source were checked against the source, with two honest exceptions. Navarro-Almanza et al.'s numbers could not be checked in the primary source: the abstract gives none and the full text is paywalled, so we removed that reference. Lima et al.'s PROMISE_exp counts (969 = 444 F + 525 NFR) were checked only through two secondary sources, because the full text is paywalled. Two other references were replaced for different reasons. Winkler and Vogelsang was correct but addressed a different task. The Zenodo note on NoRBERT was superseded by the corrected KIT report, which discloses the bug and gives the corrected 10-point figure (see `reference_audit.md`). Our own numbers are produced by one script (`repro/reproduce.py`), and the out-of-fold predictions of every model are published as CSV files. The literature synthesis is not a systematic review, and we say so.

**Spare questions worth preparing:**
- Why were seven quality classes left out of Task B?
- What is class weighting doing in Eq. (1)?
- Why did you not try an LLM such as GPT?
  - Privacy and cost for backlogs, a fair-comparison budget, and recent work already exists (Hou et al. survey). This is future work.
