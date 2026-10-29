# -*- coding: utf-8 -*-
"""Single content source for term_paper.tex and term_paper.docx.
Markup:
  {{k1;k2}}            numbered IEEE citation [n]        {{t:key}}  narrative: Author et al. [n]
  {{e.g.|k1;k2}}       parenthetical with prefix
  [[fig:x]] [[tab:x]] [[eq:x]] [[sec:x]]   cross-references
  *text*               italics
  ⟦latex¦docx⟧         inline math (docx part: _{sub} ^{sup})
  <<name>>             experiment numbers filled from exp/results_all.json
"""

TITLE = 'BERT-Based Requirement Classification for Agile Backlog Management'
AUTHOR = ('[NAME]', '[DEPARTMENT]', '[INSTITUTION]', '[CITY, COUNTRY]', '[EMAIL]')

ABSTRACT = (
    "Product backlogs mix feature requests, quality constraints, defects and chores, and few teams label them "
    "consistently. Quality requirements buried in this mix tend to surface late, when they are costly to fix. This paper "
    "asks whether BERT-family encoders can classify backlog items reliably enough to support backlog refinement. We synthesise 35 verified sources and propose a two-level framework whose confidence gate sends uncertain "
    "items to the Product Owner. In our replication on the PROMISE NFR dataset "
    "(625 requirements, 15 projects), we compared TF-IDF baselines with a partially frozen, CPU-trained DistilBERT under "
    "random 10-fold and project-held-out splits. <<ABSTRACT_RESULT>> Published BERT scores on PROMISE reach "
    "0.94\u20130.99 F1, but they rest on one small, dated corpus and mostly on random splits. We conclude that BERT "
    "classifiers suit refinement assistance better than autonomous labelling, and that results on unseen projects, not "
    "random folds, should guide adoption."
)
KEYWORDS = ('requirements classification, BERT, DistilBERT, non-functional requirements, agile, product backlog, '
            'user stories, PROMISE NFR')

B = []   # body blocks
def h1(t, lab=None): B.append(('h1', t, lab))
def h2(t, lab=None): B.append(('h2', t, lab))
def p(t): B.append(('p', t))
def fig(lab, path, cap, wide=False, width=3.4): B.append(('fig', lab, path, cap, wide, width))
def tab(lab, cap, head, rows, spec, widths, wide=False, size='footnotesize'): B.append(('tab', lab, cap, head, rows, spec, widths, wide, size))
def eq(lab, latex, docx): B.append(('eq', lab, latex, docx))
def items(lst, numbered=True): B.append(('list', lst, numbered))

# ------------------------------------------------------------------ I
h1('Introduction', 'sec:intro')
p("In Scrum the Product Backlog is the single, ordered source of work for a team, and the Product Owner is accountable "
  "for keeping it in order {{scrumguide2020}}. In practice the backlog is messier than that one sentence suggests. In a "
  "grounded-theory study of eight projects and 56 interviews at Pivotal, {{t:sedano2019}} found that the backlog acts as an "
  "informal model of the work still to be done, and that it serves as a boundary object shared by the different roles on a "
  "team rather than as a requirements specification. Most of its items are written as user stories; "
  "{{t:lucassen2016use}} surveyed 182 practitioners and interviewed 21 more, and found the Connextra template "
  "(\u201cAs a \u27e8role\u27e9, I want \u27e8goal\u27e9, so that \u27e8benefit\u27e9\u201d) to be the dominant format.")
p("Consider a typical story: \u201cAs a user, I want to reset my password through an e-mailed link so that I can regain "
  "access to my account.\u201d On the surface it is functional. Read carefully, it also carries security obligations: the "
  "link must expire, it must work only once, and the response must not reveal whether an e-mail address is registered. "
  "If the team tags the story only as a feature, those constraints are easily missed until a penetration test or an "
  "incident exposes them. {{t:dalpiaz2019}} formalised this observation by annotating requirements with separate "
  "functional and quality *aspects*, so that a single item can carry both. {{T:vancan2025}} analysed 1,636 backlog items "
  "from 14 projects and found that requirement-related content is labelled inconsistently and that one item often "
  "contains several requirements at different levels of granularity.")
p("Automatic classification of requirements text has a long history. It started with indicator-term classifiers trained on "
  "student specifications {{clelandhuang2007}} and moved through feature-engineered support vector machines "
  "{{kurtanovic2017;diascanedo2020}} and convolutional or recurrent networks {{rahman2019;rahimi2021}}. Since BERT appeared "
  "{{devlin2019}}, fine-tuned transformers have become the default, and NoRBERT showed that transfer learning helps most "
  "on projects not seen during training {{hey2020norbert;hey2022corrected}}. Yet three gaps remain. First, most results on "
  "FR/NFR classification come from the PROMISE NFR corpus {{promisenfr2007}}, 625 \u201cshall\u201d statements written for 15 student projects in the "
  "mid-2000s, or from its extensions, not from agile backlogs. Second, scores are reported under very different protocols, so a 0.99 in "
  "one paper and a 0.87 in another cannot be compared directly. Third, few of the studies we reviewed say what a team "
  "should *do* with a predicted label, or how to handle the predictions a model is unsure about.")
p("This paper addresses those gaps with four contributions:")
items(["a critical synthesis of 35 sources, with the reported results collected in a single comparison table "
       "([[tab:lit]]) that keeps each study's dataset and protocol visible;",
       "a two-level classification framework (Figs. [[#fig:arch]]\u2013[[#fig:flow]]) that connects predicted labels to "
       "backlog refinement, the Definition of Done and sprint planning, and that routes uncertain items to a human through "
       "an explicit confidence gate;",
       "a small replication that we ran ourselves on PROMISE NFR, comparing DistilBERT with three TF-IDF baselines on "
       "identical random and project-held-out folds over three seeds, with every hyper-parameter and limitation stated "
       "and a script that reproduces every number;",
       "a discussion of deployment challenges and threats to validity, summarised in [[tab:chal]]."])
p("[[sec:rw]] reviews related work, [[sec:method]] presents the framework, [[sec:exp]] reports our experiment and the "
  "literature results separately, [[sec:disc]] discusses challenges and validity, and [[sec:concl]] concludes.")

# ------------------------------------------------------------------ II
h1('Related Work', 'sec:rw')
h2('Datasets and Label Schemes')
p("The PROMISE NFR dataset was created by {{t:clelandhuang2007}} and later shared through the PROMISE repository "
  "{{promisenfr2007}}. It contains 255 functional requirements and 370 non-functional ones, the latter spread over eleven "
  "quality classes ranging from usability (67 items) to portability (one item). {{t:lima2019}} enlarged it to 969 "
  "requirements (444 functional, 525 non-functional) in PROMISE_exp, but kept the same style of text. {{t:dalpiaz2019}} "
  "relabelled more than 1,500 requirements from PROMISE and seven industrial documents with independent functional and "
  "quality aspects. That relabelling matters. It shows that the binary FR/NFR split, which most papers take for granted, "
  "forces an annotator to discard information whenever a requirement constrains behaviour and quality at the same time.")
h2('Classical and Deep-Learning Classifiers')
p("{{t:kurtanovic2017}} combined lexical and syntactic features with a support vector machine and used under- and "
  "over-sampling to counter class imbalance. They reported precision and recall of up to about 92% for the FR/NFR "
  "distinction on PROMISE NFR, with security and performance among the best-recognised quality classes. "
  "{{t:dalpiaz2019}} replaced the large feature space with 17 interpretable features derived from dependency parsing. "
  "Their classifier fitted the training data slightly less well than a reconstruction of the Kurtanovi\u0107 and Maalej "
  "model, but it generalised better to other datasets and its decisions could be explained. To us this is the more useful "
  "result for practice, because a Product Owner is more likely to trust a tag whose cause can be shown. "
  "{{T:diascanedo2020}} compared bag-of-words, TF-IDF and chi-squared features with logistic regression, SVM, "
  "multinomial Naive Bayes and k-nearest neighbours on PROMISE_exp. TF-IDF with logistic regression gave the best "
  "F-measure: 0.91 for FR/NFR (tied with the SVM), 0.74 for the NFR classes and 0.78 overall. These are the same feature "
  "and model families as our baselines in [[sec:exp]].")
p("Neural models followed. {{t:rahman2019}} compared recurrent variants on PROMISE NFR and reported that an LSTM "
  "reached a validation precision of 0.973, recall of 0.967 and F1 of 0.966, ahead of GRU and CNN models. "
  "{{t:rahimi2021}} combined LSTM, BiLSTM, GRU and CNN models in an ensemble on a 17-class PROMISE variant that also "
  "labels functional subtypes, and reported 92.56% accuracy for one-phase classification. Their two-phase variant "
  "reached 95.7% for the binary step and 93.4% for the multi-class step. Two reviews put this stream in context: "
  "{{t:binkhonain2019}} catalogued machine-learning methods for identifying non-functional requirements, and "
  "{{t:zhao2022nlp4re}} mapped the wider NLP-for-RE field and documented the gap between research prototypes and tools "
  "that practitioners actually use.")
p("A pattern runs through these numbers. The highest scores tend to come from the smallest evaluation sets and the least "
  "clearly described splits. An F1 of 0.966 on roughly 370 short sentences is plausible under random cross-validation, "
  "where requirements from the same project, often with near-identical wording, fall on both sides of a split. It says "
  "little about how the same model would label a new team's backlog.")
h2('BERT and Its Variants in Requirements Engineering')
p("BERT pre-trains a bidirectional transformer encoder with masked-language-model and next-sentence objectives, and is "
  "then adapted to a downstream task by adding a single output layer and fine-tuning all weights {{devlin2019}}. "
  "RoBERTa keeps the architecture but trains longer on more data, drops the next-sentence objective and masks tokens "
  "dynamically {{liu2019roberta}}. DistilBERT applies knowledge distillation to obtain a model about 40% smaller and 60% "
  "faster that keeps 97% of BERT's language-understanding performance {{sanh2019distilbert}}, which makes it a realistic "
  "choice for a team without GPUs. {{t:sun2019finetune}} studied fine-tuning choices such as layer selection, learning "
  "rates and further pre-training, and their recommendations inform the settings in [[sec:exp]].")
p("NoRBERT was an early and widely cited application of BERT fine-tuning to requirements classification "
  "{{hey2020norbert}}. On PROMISE NFR it reached an F1 of up to 94% for FR/NFR and an average F1 of 87% on the most "
  "frequent quality classes. In an unseen-project setup on a relabelled version of PROMISE it reported an improvement of "
  "15 percentage points over earlier approaches. The authors later released a corrected version, citing a bug in part of "
  "the evaluation, in which that improvement is ten percentage points {{hey2022corrected}}. We regard this correction as "
  "one of the most instructive episodes in the field. It shows how much the split protocol can change a headline number, "
  "and it was disclosed openly.")
p("Later studies widened the scope. {{t:kici2021}} found that DistilBERT outperformed LSTM and BiLSTM baselines on "
  "several requirements datasets. {{t:luo2022prcbert}} reformulated classification as prompt-based cloze filling "
  "(PRCBERT). A model fine-tuned on PROMISE and transferred without labels, with self-learning, reached weighted F1 "
  "scores of 53.27% on NFR-Review and 72.96% on NFR-SO. Domain-specific work includes aeroBERT, fine-tuned on a corpus "
  "of 310 aerospace requirements, which reached an average F1 of 0.83 on a 31-item test set {{tikayatray2023}}, and BERTurk fine-tuned on newly created Turkish requirements, which reached an F-score of about "
  "95% {{yucalar2023}}. {{t:alsanoosy2026}} assembled 4,908 requirements and reported a binary F1 of 86.93% for a "
  "BERT+LSTM hybrid, while {{t:eltahier2025}} reported an average F1 of 0.99 on PROMISE and 0.97 on the FR_NFR dataset. "
  "Their protocol is stratified 10-fold cross-validation with weighted F1, and hyper-parameters were chosen by ablation "
  "on the same data. Read side by side, these results show that the dataset and the split "
  "protocol explain more of the variation than the choice of encoder. A score of 0.99 on PROMISE and 0.87 on a corpus "
  "eight times larger do not show that one method is better than the other.")
h2('Zero-Shot, Few-Shot and Large Language Models')
p("Labelling is expensive, so learning from few or no labelled examples is attractive. {{t:alhoshan2023}} tested "
  "zero-shot classification with pre-trained sentence embeddings and label descriptions. Their best zero-shot F1 was "
  "0.66 for functional and 0.65 for non-functional requirements, against 0.93 for the supervised Kurtanovi\u0107\u2013Maalej "
  "model on FR and 0.93 for NoRBERT on NFR. The gap is large but so is the saving: no labelled data at all. SetFit "
  "contrastively fine-tunes a sentence transformer on pairs of labelled examples; with eight labelled examples per class "
  "on the Customer Reviews sentiment dataset it was competitive with RoBERTa-Large fine-tuned on the full training set "
  "{{tunstall2022setfit}}. {{T:petrillo2025}} applied SetFit and fine-tuned transformers to security-requirements "
  "classification on the SecReq dataset. We did not find a study that applies SetFit to PROMISE NFR, although our search "
  "was not systematic. The broader shift towards large language models is "
  "documented in the review by {{t:hou2024llm4se}}. For backlogs specifically, {{t:vancan2025}} found that fine-tuned "
  "encoder-only models were better suited than prompted generative models to locating requirements in backlog items. This "
  "is a useful corrective to the assumption that the largest model is always the right one.")
h2('Agile Backlog Support')
p("Other work automates neighbouring backlog tasks. {{t:lucassen2016qus}} proposed the Quality User Story framework, "
  "with 13 criteria, and the AQUSA tool for detecting defects in story text. {{t:choetkiertikul2019}} estimated story "
  "points with an LSTM and a recurrent highway network trained on 23,313 issues from 16 open-source projects. "
  "{{t:mejia2026loona}} built LOONA for the quality assurance of Spanish user stories: a fine-tuned Spanish BERT "
  "classifier flags defective stories, and a confidence threshold decides when a generative model proposes a rewrite. "
  "The classifier reached an F1 of 0.91 in 5-fold cross-validation on expert-labelled stories. Prioritisation is the step that ultimately consumes any label, and "
  "{{t:hujainah2018}} reviewed the techniques, stakeholders and open challenges of requirements prioritisation. None of "
  "the studies cited in this subsection feeds requirement-type labels into prioritisation or refinement, and that is the link our framework is "
  "meant to provide.")

LIT_HEAD = ['Study', 'Data', 'Approach', 'Result as reported by the authors', 'Our remark']
LIT_ROWS = [
    ['{{kurtanovic2017}}', 'PROMISE NFR', 'SVM, lexical + syntactic features, sampling', 'FR/NFR P and R up to \u224892%', 'Strong classical baseline'],
    ['{{dalpiaz2019}}', 'PROMISE + 7 industrial sets (>1,500 items), F/Q aspects', 'Dependency-parse features (17)', 'Generalises better than K&M reconstruction', 'Interpretable; multi-aspect labels'],
    ['{{diascanedo2020}}', 'PROMISE_exp (969)', 'TF-IDF / BoW / CHI2 + LR, SVM, MNB, kNN', 'TF-IDF+LR F 0.91 (FR/NFR, tie with SVM); 0.74 (NFR classes)', 'Same model families as our baselines'],
    ['{{rahman2019}}', 'PROMISE NFR', 'LSTM / GRU / CNN', 'LSTM (validation): P 0.973, R 0.967, F1 0.966', 'Split protocol limits comparison'],
    ['{{rahimi2021}}', 'PROMISE, 17-class variant', 'Ensemble of DL models', 'Acc. 95.7% (binary), 93.4% (multi-class), two-phase', 'Accuracy only'],
    ['{{hey2020norbert}}', 'PROMISE NFR', 'NoRBERT (BERT fine-tuning)', 'FR/NFR F1 up to 94%; frequent NFR avg. F1 87%', 'Unseen-project gain 15 pp, corrected to 10 pp {{hey2022corrected}}'],
    ['{{kici2021}}', 'PROMISE NFR and others', 'DistilBERT', 'Outperformed LSTM and BiLSTM', 'Light model'],
    ['{{luo2022prcbert}}', 'NFR-Review, NFR-SO', 'PRCBERT prompt learning', 'Transferred, no labels: weighted F1 53.27% / 72.96%', 'Non-SRS text'],
    ['{{alhoshan2023}}', 'PROMISE NFR and others', 'Zero-shot embeddings', 'Best F1 0.66 (FR), 0.65 (NFR)', 'No labels needed'],
    ['{{tikayatray2023}}', '310 aerospace requirements', 'aeroBERT-Classifier', 'Average F1 0.83', '31-item test set'],
    ['{{petrillo2025}}', 'SecReq (623, 3 specifications)', 'Fine-tuned transformers; SetFit', 'Best few-shot (SetFit, BERT body, augmented data): Acc. 0.94, F1 0.90', 'Security vs. other only'],
    ['{{yucalar2023}}', 'New Turkish requirements', 'BERTurk', 'F-score \u2248 95%', 'Non-English'],
    ['{{alsanoosy2026}}', '4,908 requirements', 'BERT + LSTM', 'Binary F1 86.93%', 'Largest corpus here'],
    ['{{eltahier2025}}', 'PROMISE; FR_NFR', 'BERT fine-tuning variants', 'Weighted F1 0.99 (PROMISE), 0.97 (FR_NFR)', 'Tuned on the evaluation data'],
    ['{{vancan2025}}', '1,636 backlog items, 14 projects', 'Encoders vs. generative LLMs', 'Encoder-only models most suitable', 'Closest to backlogs'],
]
tab('tab:lit', 'Reported results from the literature (not our experiments). Scores are copied as published; datasets and protocols differ, so rows are not directly comparable.',
    LIT_HEAD, LIT_ROWS, r'p{2.3cm}p{3.0cm}p{3.1cm}p{4.3cm}p{3.6cm}', [1.15, 1.45, 1.45, 1.95, 1.5], wide=True)

# ------------------------------------------------------------------ III
h1('Methodology and Proposed Framework', 'sec:method')
h2('Research Approach')
p("The study combines a structured, but not systematic, literature review with a small experiment. In "
  "October 2026 we searched IEEE Xplore, the ACM Digital Library, SpringerLink, ScienceDirect, MDPI and "
  "arXiv through web search. We used combinations of *requirements classification*, *non-functional*, *BERT*, "
  "*user story*, *product backlog*, *zero-shot* and *class imbalance*. We screened around 60 candidate records and "
  "kept 35. A source was kept if it reported a classifier for natural-language requirements, contributed a dataset or model "
  "that such work depends on, or described agile backlog practice. Every DOI was checked against Crossref, DataCite or "
  "arXiv metadata. Because we did not follow a registered protocol, did not double-screen, and did not snowball "
  "exhaustively, we do not claim the coverage of a systematic literature review.")
h2('Framework Overview')
p("[[fig:arch]] shows the proposed framework. Items enter from the team's tracker (for example Jira), from a story-writing "
  "workshop or from user feedback. A pre-processing step normalises each item: it splits a Connextra story into role, "
  "goal and benefit, keeps the \u201cso that\u201d clause because it often signals the quality concern, separates acceptance "
  "criteria, and removes personal names. Classification then proceeds in two levels. Level 1 decides whether an item "
  "contains a quality concern: FR versus NFR, or F+Q when both aspects are present, as proposed by "
  "{{t:dalpiaz2019}}. "
  "Level 2 assigns the quality class, such as security (SE), performance (PE), usability (US) or operability (O), and is "
  "run only for items that Level 1 flags.")
fig('fig:arch', 'fig1_architecture', 'Proposed framework. Items are normalised, encoded by a fine-tuned BERT-family model and classified at two levels. A confidence gate decides whether a label is applied automatically or sent to the Product Owner, whose corrections feed periodic re-training.', wide=True, width=6.6)
h2('Encoder and Training Objective')
p("Any BERT-family encoder fits the framework. We use DistilBERT in [[sec:exp]] because it runs on a laptop CPU. "
  "[[fig:ft]] traces the running example through the model. The text is tokenised into WordPiece units, the final hidden "
  "state of the [CLS] token passes through a small classification head, and a softmax gives a probability for each of the "
  "⟦K¦K⟧ labels. PROMISE NFR is imbalanced: usability has 67 examples and fault tolerance has 10. The training loss "
  "therefore weights each class by its inverse frequency, a common algorithm-level remedy for imbalance that is "
  "implemented through a weight or cost scheme {{johnson2019}}:")
eq('eq:wce', r'\mathcal{L} = -\frac{1}{N}\sum_{i=1}^{N} w_{y_i}\,\log p_\theta(y_i \mid x_i), \qquad w_c = \frac{N}{K\,N_c}',
   'ℒ = −(1/N) Σ_{i=1}^{N} w_{yi} log p_{θ}(y_{i} | x_{i}),     w_{c} = N / (K · N_{c})')
p("Here ⟦N¦N⟧ is the number of training items, ⟦N_c¦N_{c}⟧ the number of items in class ⟦c¦c⟧ and ⟦K¦K⟧ the number of "
  "classes. Re-sampling, as used by {{t:kurtanovic2017}}, is an alternative. We prefer weighting because it leaves the "
  "data untouched and adds no duplicated sentences that could appear in both training and test folds.")
fig('fig:ft', 'fig2_finetune', 'Fine-tuning pipeline for one backlog item. Grey blocks were frozen in our CPU experiment; the dashed path is used only during training.', width=3.3)
h2('Confidence Gate', 'sec:gate')
p("A classifier that is wrong 8% of the time and gives no warning will gradually erode the team's trust in the backlog. "
  "The framework therefore applies a label automatically only when the model is confident:")
eq('eq:gate', r'\mathrm{route}(x) = \begin{cases} \text{auto-label } \hat{y}, & \max_c p_\theta(c \mid x) \ge \tau \\ \text{Product Owner review}, & \text{otherwise} \end{cases}',
   'route(x) = auto-label ŷ if max_{c} p_{θ}(c | x) ≥ τ, else PO review')
p("The threshold ⟦\\tau¦τ⟧ in [[eq:gate]] is set on held-out data so that the automatically applied labels reach a precision the team "
  "agrees on, for example 0.95. Softmax probabilities from fine-tuned transformers are often over-confident, so a team "
  "should check calibration before relying on ⟦\\tau¦τ⟧. Items below the threshold appear in the refinement queue with the "
  "two most likely labels shown, which turns a silent error into a one-click decision.")
h2('Integration with the Backlog Workflow')
p("[[fig:flow]] places the classifier in the Scrum cycle. When an item is created or edited, the tracker sends it to the "
  "service, which writes back a label and a confidence value. During refinement the team reviews the low-confidence queue "
  "and also checks the high-confidence quality labels, because these carry consequences. A security label, for instance, "
  "adds the team's security checklist to the item's acceptance criteria. A performance label prompts the team to state a "
  "measurable target, such as \u201csearch results appear within 2 s for 95% of queries.\u201d Usability items get an "
  "accessibility check. Before sprint planning, the Product Owner can filter the ordered backlog by label and see, for "
  "example, that the next three sprints contain no operability work. Ordering stays with the Product Owner "
  "{{scrumguide2020}}; the classifier makes quality work visible but never reorders the backlog.")
fig('fig:flow', 'fig3_workflow', 'Classifier-in-the-loop backlog workflow. Corrections made during refinement are logged and used for re-training at release boundaries.', wide=True, width=6.9)
h2('Human Feedback and Re-Training')
p("Every label the Product Owner confirms or changes is stored together with the item text, the model version and the "
  "confidence. The model is re-trained at release boundaries rather than continuously, so that its behaviour stays "
  "stable within a sprint. Two signals tell the team when re-training is due: the share of items routed to review rising "
  "above an agreed level, and the precision of automatic labels, measured on a small random audit sample, falling below "
  "the target.")

# ------------------------------------------------------------------ IV
h1('Experimental Setup and Results', 'sec:exp')
p("This section has two parts. [[sec:ownexp]] reports an experiment that *we ran ourselves*. [[sec:litres]] "
  "summarises results *reported in the literature*, which we did not reproduce. The two are kept separate throughout, and no literature "
  "number appears in our results table.")
h2('Our Replication on PROMISE NFR', 'sec:ownexp')
p("*Data.* We downloaded the PROMISE NFR dataset from its Zenodo record {{promisenfr2007}} and parsed the ARFF file into "
  "625 labelled requirements from 15 projects. [[tab:data]] gives the class distribution, together with an agile-style "
  "example that we wrote for each class to show what the label means in a backlog. The PROMISE items themselves are "
  "\u201cshall\u201d statements, not user stories. We defined two tasks. Task A separates functional (255) from "
  "non-functional (370) requirements. Task B classifies the four most frequent quality classes: usability (67), security "
  "(66), operability (62) and performance (54), 249 items in total. The seven remaining quality classes have between 1 and "
  "38 examples, too few for a reliable per-class estimate, so we left them out.")
DATA_HEAD = ['Code', 'Class', 'n', 'Task', 'Illustrative agile item (written by us, not from PROMISE)']
DATA_ROWS = [
    ['F', 'Functional', '255', 'A', '\u201cAs a user, I want to reset my password via an e-mailed link so that I can regain access.\u201d (F; also carries a security aspect)'],
    ['US', 'Usability', '67', 'A, B', '\u201cAs a screen-reader user, I want every form field to have a label so that I can complete checkout.\u201d'],
    ['SE', 'Security', '66', 'A, B', '\u201cAs an administrator, I want failed login attempts logged with time and IP so that I can spot attacks.\u201d (F+SE)'],
    ['O', 'Operability', '62', 'A, B', '\u201cAs an operator, I want to change the backup schedule without a redeploy.\u201d'],
    ['PE', 'Performance', '54', 'A, B', '\u201cAs a shopper, I want search results within 2 s so that I do not abandon the search.\u201d'],
    ['LF', 'Look and feel', '38', 'A', '\u201cAs a marketer, I want pages to use the corporate colour palette.\u201d'],
    ['A', 'Availability', '21', 'A', '\u201cAs a customer, I want the shop to be reachable 99.9% of the time.\u201d'],
    ['SC', 'Scalability', '21', 'A', '\u201cAs the business, we want to serve 10,000 concurrent users at launch.\u201d'],
    ['MN', 'Maintainability', '17', 'A', '\u201cAs a developer, I want tax rules in configuration rather than in code.\u201d'],
    ['L', 'Legal', '13', 'A', '\u201cAs a data-protection officer, I want users to be able to export their personal data.\u201d'],
    ['FT', 'Fault tolerance', '10', 'A', '\u201cAs a user, I want my cart preserved if the payment service fails.\u201d'],
    ['PO', 'Portability', '1', 'A', '\u201cAs a user, I want the app to run on Android 12 and later.\u201d'],
]
tab('tab:data', 'PROMISE NFR class distribution (625 requirements, 15 projects) and illustrative backlog items.',
    DATA_HEAD, DATA_ROWS, r'p{0.7cm}p{1.9cm}p{0.6cm}p{0.8cm}p{11.2cm}', [0.45, 1.0, 0.35, 0.45, 5.05], wide=True)
p("*Protocol.* We used two protocols, and within each one all models share the same splits. *Random*: stratified "
  "10-fold cross-validation (scikit-learn), in which requirements from one project fall on both sides of a split. "
  "*Project-held-out*: five folds built with StratifiedGroupKFold using the PROMISE project identifier as the group, so "
  "no project contributes to both training and test data. Each protocol was run with seeds 42, 43 and 44, except that "
  "random-fold DistilBERT was trained for seed 42 only because of the CPU budget. For each run we pool the out-of-fold "
  "predictions and compute per-class precision, recall and F1, their macro averages and accuracy; [[tab:res]] reports "
  "macro-F1 as mean \u00b1 standard deviation over seeds. Paired comparisons use exact McNemar tests on the pooled "
  "predictions of one seed. We did no hyper-parameter search for any model: the baselines use common defaults and "
  "DistilBERT uses the settings below. Tuning on the same folds would have made the comparison look better without "
  "making it more honest. Code, splits and every model's out-of-fold predictions are in our reproducibility package.")
p("*Baselines.* Each baseline uses TF-IDF features over word unigrams and bigrams, with sublinear term frequency and "
  "English stop-word removal, fitted inside each training fold. On top of these features we trained multinomial Naive "
  "Bayes (\u03b1 = 0.1), a linear SVM (C = 1, class-balanced weights) and logistic regression (C = 10, class-balanced "
  "weights).")
p("*DistilBERT.* We fine-tuned distilbert-base-uncased {{sanh2019distilbert}} with the Hugging Face Transformers library. "
  "Settings: maximum length 64 WordPiece tokens (median item length is 21 tokens; 7 of 625 items were truncated), batch "
  "size 8, AdamW with learning rate 5\u00d710\u207b\u2075 and weight decay 0.01, 10% linear warm-up followed by linear "
  "decay, gradient clipping at 1.0, five epochs, and the class-weighted loss of [[eq:wce]]. The sandbox had two CPU cores "
  "and about 2 GB of RAM, so we froze the embedding layer and the first two of the six transformer blocks, which reduced "
  "optimiser memory. This departs from full fine-tuning {{devlin2019}}, and the numbers below should be read as a lower "
  "bound for what DistilBERT can do on this data. One fold took about <<A_SECS>> s to train for Task A and <<B_SECS>> s "
  "for Task B.")
p("*Results.* [[tab:res]] and [[fig:res]] give the results. <<RESULTS_PARA_1>>")
p("<<RESULTS_PARA_G>>")
p("<<RESULTS_PARA_2>>")
RES_HEAD = ['Model', 'A random', 'A project', 'B random', 'B project']
tab('tab:res', 'Our experiment: macro-F1 on PROMISE NFR, mean \u00b1 SD over seeds 42\u201344 of pooled out-of-fold predictions. Random = stratified 10-fold; project = project-held-out 5-fold. Task A: FR vs. NFR (n = 625); Task B: US/SE/O/PE (n = 249). NB = multinomial Naive Bayes; DistilBERT has 2 of 6 blocks frozen. \u2020 One seed (42). Best mean per column in bold. Accuracies are in the reproducibility package.',
    RES_HEAD, '<<RES_ROWS>>', r'@{}lcccc@{}', [0.95, 0.64, 0.64, 0.64, 0.64], size='scriptsize')
fig('fig:res', 'fig4_results', 'Our experiment: macro-F1 under random 10-fold and project-held-out 5-fold splits, mean over seeds 42\u201344 with SD error bars (random-fold DistilBERT: seed 42 only). The y-axis starts at 0.4.', width=3.4)
h2('Reported Results from the Literature', 'sec:litres')
p("[[tab:lit]] lists the results reported in the literature. These are the authors' numbers, not ours. On PROMISE NFR "
  "the published results bracket our own. For the FR/NFR decision, NoRBERT reports an F1 of up to 94% "
  "{{hey2020norbert}} and Eltahier et al. report 0.99 {{eltahier2025}}, both above our <<A_BERT>>. For the frequent "
  "quality classes, our DistilBERT macro-F1 of <<B_BERT>> is higher than the 87% average F1 that NoRBERT reports. We do "
  "not read this as DistilBERT beating NoRBERT. The protocols differ: we used random stratified folds over four classes, "
  "and our own project-held-out runs in [[tab:res]] show how much such folds add on PROMISE. NoRBERT's corrected "
  "report also lowers its unseen-project improvement from 15 to 10 percentage points {{hey2022corrected}}, another sign "
  "that headline numbers depend on the split. Model capacity differs in the opposite "
  "direction: NoRBERT fine-tuned full-size BERT models (base and large) with all layers trainable, whereas we used a "
  "distilled model with a third of its blocks frozen. Our random-fold TF-IDF+SVM macro-F1 of <<A_SVM>> on Task A is "
  "close to the roughly 92% precision and recall reported by {{t:kurtanovic2017}} and to the F-measure of 0.91 that "
  "{{t:diascanedo2020}} report for TF-IDF models on the larger PROMISE_exp, so the classical baseline appears to be "
  "reasonably reproduced. The 0.99 reported by Eltahier et al. cannot be placed on the same protocol as ours from the "
  "information we used.")

# ------------------------------------------------------------------ V
h1('Discussion', 'sec:disc')
h2('What the Evidence Supports')
p("Taken together, the sources support three claims and leave a fourth open. First, fine-tuned transformers are at least "
  "as good as feature-engineered models on PROMISE-style text and are better at transferring to unseen projects "
  "{{hey2020norbert;hey2022corrected}}. Second, the FR/NFR boundary is not crisp: an item can carry both aspects "
  "{{dalpiaz2019}}, and backlog items mix several requirements in one entry {{vancan2025}}. Third, label-free approaches "
  "are possible but still well behind supervised ones {{alhoshan2023;luo2022prcbert}}. Our own results "
  "sharpen this picture. <<DISC_RESULT>> The open question is how "
  "well any of these models works on genuine backlog text, where items are terse, informal and full of project jargon.")
h2('Implications for Backlog Management')
p("For a Scrum team the value lies less in the label itself than in the conversation it starts. Picture a team "
  "refining twenty new stories before sprint planning. The classifier tags fourteen with high confidence. It flags "
  "\u201cAs an administrator, I want to see a log of all login attempts\u201d as functional with a security concern, and "
  "it sends three ambiguous items to the review queue. The Product Owner confirms the security tag, so the team adds "
  "retention and access rules to the acceptance criteria before the work starts, not after a later audit. Used this way, "
  "the classifier supports the Definition of Done and leaves responsibility for ordering and scope with the Product "
  "Owner {{scrumguide2020}}. It also complements story-quality checks such as QUS {{lucassen2016qus}}: one tool asks "
  "whether a story is well formed, the other asks what kind of concern it raises.")
h2('Challenges')
p("[[tab:chal]] summarises the main deployment challenges and how the framework addresses each one. Three need further "
  "comment. *Imbalance* is structural: some quality classes will always be rare, and accuracy can mislead on "
  "imbalanced data {{johnson2019}}, which is why we report macro-averaged scores. *Format shift* is the largest unknown: models trained on \u201cThe system "
  "shall\u2026\u201d sentences meet \u201cAs a \u27e8role\u27e9\u2026\u201d stories, bug reports and one-line chores in a real "
  "tracker {{vancan2025}}. *Label drift* follows from the backlog being an informal and evolving model of the work "
  "{{sedano2019}}: a team's notion of \u201coperability\u201d may change as its product matures.")
CHAL_HEAD = ['Challenge', 'Evidence', 'Mitigation in the framework']
CHAL_ROWS = [
    ['Class imbalance (PO: 1 item; FT: 10)', '{{johnson2019}}', 'Weighted loss (Eq. 1); macro-F1; merge rare classes'],
    ['FR/NFR ambiguity, mixed items', '{{dalpiaz2019;vancan2025}}', 'F+Q label; split multi-requirement items'],
    ['SRS-to-story format shift', '{{lucassen2016use;vancan2025}}', 'Parse role/goal/benefit; fine-tune on team data'],
    ['Over-confident predictions', 'Our [[sec:ownexp]] (gate analysis)', 'Confidence gate with calibration check; audit sample'],
    ['Optimistic random splits', '{{hey2022corrected}}; our [[sec:ownexp]]', 'Project-held-out or time-based evaluation before roll-out'],
    ['Scarce labelled data', '{{alhoshan2023;tunstall2022setfit}}', 'Zero-/few-shot start; active labelling in review'],
    ['Compute and privacy limits', '{{sanh2019distilbert}}', 'Distilled model on-premise; no external API'],
]
tab('tab:chal', 'Deployment challenges, supporting evidence and mitigations.', CHAL_HEAD, CHAL_ROWS,
    r'p{2.35cm}p{2.0cm}p{3.2cm}', [1.2, 0.95, 1.35], size='scriptsize')
h2('Threats to Validity', 'sec:threats')
p("*Construct validity.* PROMISE labels were assigned by students around 2007 {{clelandhuang2007}}, and the FR/NFR "
  "boundary itself is contested {{dalpiaz2019}}. A model that agrees with these labels has learned one annotation "
  "convention, not a ground truth. *Internal validity.* We used three seeds per protocol, except for random-fold DistilBERT "
  "(one seed), no hyper-parameter search, and a partially frozen encoder. A different configuration could change the random-fold Task A ranking, where the difference was not "
  "significant, and could narrow or widen the other gaps. The "
  "baselines and DistilBERT did, however, share identical folds and pre-processing. *External validity.* Random 10-fold "
  "splits put requirements from the same project into both training and test data. Our project-held-out runs measure "
  "how much this inflates scores on PROMISE, but they cover only 15 projects of one corpus, with uneven fold sizes and "
  "no time order. PROMISE contains English \u201cshall\u201d statements, so our results say nothing direct about user stories or other languages. "
  "*Conclusion validity.* With 249 items in Task B, random test folds hold about 25 items, so fold-level accuracies "
  "vary considerably. We therefore report pooled scores, spread over seeds and paired McNemar tests rather than claiming "
  "small differences. The spread over three seeds is itself only a rough estimate. "
  "Finally, the literature synthesis is not a systematic review, and relevant studies may have been missed.")
h2('Ethical and Practical Considerations')
p("Backlogs can contain customer names, contract details and security weaknesses. Sending them to an external API may "
  "breach confidentiality, which is a practical argument for small models that run on-premise. Automation bias is the "
  "other risk: if a high-confidence label is never questioned, the team may stop thinking about quality at all. Keeping "
  "the label visible but editable, and auditing a sample every release, limits that risk.")

# ------------------------------------------------------------------ VI
h1('Conclusion and Future Work', 'sec:concl')
p("We set out to judge whether BERT-family classifiers can support agile backlog management. The literature shows steady "
  "progress on PROMISE-style text, from indicator terms to NoRBERT, but also a habit of reporting near-ceiling scores "
  "under protocols that cannot be compared. Our own small replication found that <<CONCL_RESULT>> We therefore propose "
  "using such models as refinement assistants: they surface quality concerns early and route uncertain items to a person, "
  "while ordering and scope remain with the Product Owner.")
p("Four steps would make the evidence stronger. (1) Build an openly licensed corpus of real user stories and backlog "
  "items with F/Q aspect labels, so that results stop depending on PROMISE. (2) Make project-held-out and time-ordered "
  "splits the standard; our project-held-out runs are a first step, but they cover 15 PROMISE projects and no time "
  "order. (3) Compare fully fine-tuned BERT and RoBERTa with few-shot SetFit and zero-shot "
  "baselines under one protocol, using label budgets a real team could afford. (4) Run a field study in which a team uses "
  "the confidence-gated classifier during refinement, and measure whether quality issues are found earlier.")
