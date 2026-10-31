# Reference audit (Step 1)

Checked 24 Oct 2026.

**How each item was checked**
- **Metadata:** title, authors, year and venue were compared against Crossref, DataCite (Zenodo, KIT) or the arXiv API using `work/verify_refs.py`, with output in `work/verify_refs.json`.
- **Numbers:** every number or specific claim the paper attributes to a source was compared with the source itself. Sources used were the full text where it is open, the publisher abstract page, or (stated explicitly) a secondary source when the primary was paywalled.

**Status key**
- **OK**: the claim matches the source.
- **FIX**: the source is valid, but the wording or number in our paper must change.
- **REMOVE**: the reference leaves the list, with the reason given.

"DOI ✔" means the DOI resolves and its metadata match our bibliography entry.

## Peer-reviewed / primary sources

| # | Reference (key) | DOI resolves? | Claim in paper (Phase 1 text) | What the source says | Status |
|---|---|---|---|---|---|
| 1 | Devlin et al. 2019 (devlin2019) | ✔ 10.18653/v1/N19-1423 | BERT is pre-trained with masked-LM and next-sentence objectives; fine-tuned with one extra output layer | Abstract: "fine-tuned with just one additional output layer". MLM and NSP are described in Sec. 3.1 (PDF) | OK |
| 2 | Liu et al. 2019, RoBERTa (liu2019roberta) | ✔ arXiv 1907.11692 | Dynamic masking, NSP removed, longer training on more data | PDF: dynamic masking, removing NSP, bigger batches and longer training, 160 GB of text | OK |
| 3 | Sanh et al. 2019, DistilBERT (sanh2019distilbert) | ✔ arXiv 1910.01108 | About 40% smaller, 60% faster, keeps 97% of language understanding | Abstract gives the same three figures | OK |
| 4 | Sun et al. 2019 (sun2019finetune) | ✔ 10.1007/978-3-030-32381-3_16 | Studied layer selection, learning rates and further pre-training | PDF: sections on features from different layers, "layer-wise decreasing layer rate", catastrophic forgetting and further pre-training | REMOVE (Phase 13; see below) |
| 5 | Cleland-Huang et al. 2007 (clelandhuang2007) | ✔ 10.1007/s00766-007-0045-1 | Indicator-term classifier trained on student specifications; origin of PROMISE NFR | Abstract: 30 specifications from MS-student term projects at DePaul. Body: weighted "indicator terms" per NFR type | OK |
| 6 | PROMISE NFR dataset, Zenodo (promisenfr2007) | ✔ 10.5281/zenodo.268542 (DataCite lists the creator as "Huang Liguo") | 625 requirements: 255 F, 370 NFR, 11 NFR classes, 15 projects | Counted from the downloaded file (md5 c3e68d6c…). Dalpiaz 2019 also describes it as 625 requirements from 15 projects | OK |
| 7 | Lima et al. 2019 (lima2019) | ✔ 10.1145/3350768.3350776 | PROMISE_exp: 969 requirements (444 F / 525 NFR) | ACM full text is paywalled. Two independent secondary sources (the Mitrevski PROMISE_exp repository and Dias Canedo & Cordeiro Mendes 2020) give 969 = 444 F + 525 NFR | OK (via secondary sources) |
| 8 | Kurtanović & Maalej 2017 (kurtanovic2017) | ✔ 10.1109/RE.2017.82 | SVM with lexical and syntactic features plus sampling; P/R up to about 92% (FR/NFR); security and performance best | IEEE abstract: "precision and recall up to ~92%" for FR/NFR; security and performance "~92% precision and ~90% recall"; under- and over-sampling | OK |
| 9 | Dalpiaz et al. 2019 (dalpiaz2019) | ✔ 10.1109/RE.2019.00025 | More than 1,500 requirements from PROMISE plus 7 industrial sets, with F/Q aspects; 17 features; generalises better | PDF: "1,500+ requirements" (Table II total 1,502) from PROMISE and seven other projects; 17 dependency features; "performs generally better on validation datasets" | OK |
| 10 | Navarro-Almanza et al. 2017 (navarro2017) | ✔ 10.1109/CONISOFT.2017.00021 | CNN on 12 PROMISE classes; P 0.80, R 0.785, F1 0.77 | The abstract confirms a CNN and 12 classes but gives **no numbers**. The full text is paywalled. The numbers appear only second-hand, in Rahimi et al. 2021 Table 3 | **REMOVE**: the attributed numbers cannot be checked in the primary source. Replaced by Dias Canedo & Cordeiro Mendes 2020 (row N1) |
| 11 | Winkler & Vogelsang 2016 (winkler2016) | ✔ 10.1109/REW.2016.021 | CNN separates requirements from information; P 0.73, R 0.89 | IEEE abstract: the same figures, on an automotive specification | Claim OK, but **REMOVE**: a different task, from 2016. The slot goes to Petrillo et al. 2025 (row N2) to raise the 2018–2026 share |
| 12 | Rahman et al. 2019 (rahman2019) | ✔ 10.1145/3340482.3342745 | LSTM P 0.973, R 0.967, F1 0.966, ahead of GRU and CNN | ACM abstract: "precision, recall, and f1-score of LSTM validation are 0.973, 0.967 and 0.966", higher than CNN and GRU. **Phase 3 check (ACM full text, now open access):** PROMISE 625 items, 370 NFR in 11 classes, the one-item class removed (10 classes); 0.966 is the mean over 10-fold validation folds; on a separately selected test set the LSTM averaged P 0.717, R 0.715, F1 0.70 (Table 2) | OK. Validation qualifier kept; test F1 0.70 added to II-B and Table I |
| 13 | Rahimi et al. 2021 (rahimi2021) | ✔ 10.3390/e23101264 | Ensemble: 92.56% accuracy one-phase; two-phase 95.7% (binary), 93.4% (multi-class) | Abstract: 95.7% and 93.4%. Table 10: "accuracy per class as a weight" ensemble 92.56% (one-phase, 17 classes). The dataset is a 659-statement PROMISE variant with FR subclasses | OK. Add "17-class PROMISE variant" |
| 14 | Hey et al. 2020, NoRBERT (hey2020norbert) | ✔ 10.1109/RE48521.2020.00028 | F1 up to 94% (F/NFR); 87% on frequent NFR classes; +15 pp on unseen projects | IEEE abstract: 94% and 87% confirmed. The 15 pp is "in an unseen project setup **on a relabeled PROMISE NFR dataset**". The corrected version (row N3) gives **ten** pp | **FIX**: say "relabelled PROMISE" and report 10 pp from the corrected version |
| 15 | Kici et al. 2021 (kici2021) | ✔ 10.21428/594757db.a4880a62 | DistilBERT outperformed LSTM and BiLSTM on several requirements datasets | Abstract and PDF: DistilBERT compared with LSTM and BiLSTM (plus GloVe/ELMo) on DOORS Next Generation and PROMISE-NFR; DistilBERT best | OK |
| 16 | Luo et al. 2022, PRCBERT (luo2022prcbert) | ✔ 10.1145/3551349.3560417 | Zero-shot F1 53.27% (NFR-Review), 72.96% (NFR-SO) with self-learning | Abstract and Table 9: Trans_PRCBERT (fine-tuned on PROMISE, then transferred) with self-learning, **weighted** F1 0.5327 / 0.7296 | OK. Specify weighted F1, after transfer from PROMISE |
| 17 | Tikayat Ray et al. 2023 (tikayatray2023) | ✔ 10.3390/aerospace10030279 | aeroBERT classified 310 aerospace requirements, average F1 0.83 | Paper: corpus of 310 requirements, 279 train / 31 test; "average F1 score of 0.83 across all three requirement types in the unseen test data" | OK. Add that the test set is 31 items |
| 18 | Yucalar 2023 (yucalar2023) | ✔ 10.3390/app132011127 | BERTurk on new Turkish requirements, F-score about 95% | Abstract: 4,600 Turkish requirements; BERTurk best, "95% F-score" | REMOVE (Phase 13; see below) |
| 19 | Alsanoosy 2026 (alsanoosy2026) | ✔ 10.1007/s13369-026-11242-w | 4,908 requirements; BERT+LSTM binary F1 86.93% | Springer page: 4,908 (2,595 FR / 2,313 NFR); binary F1 86.93% (BERT+LSTM); DeBERTa 86.85%; multi-class weighted F1 89.45% | OK |
| 20 | Eltahier et al. 2025 (eltahier2025) | ✔ 10.3390/info16110981 | F1 0.99 (PROMISE), 0.97 (FR_NFR) | MDPI: average F1 0.99 on "PROMISE dataset (version 3)" and 0.97 on FR_NFR. Binary task, stratified 10-fold CV, weighted F1, hyperparameters chosen by ablation on the same data | OK. Add the protocol detail (weighted F1; tuned on the evaluation data) |
| 21 | Alhoshan et al. 2023 (alhoshan2023) | ✔ 10.1016/j.infsof.2023.107202 | Zero-shot best F1 0.66 (FR), 0.65 (NFR) | Table 2, best Sbert+FR_E: FR F1 0.66, NFR F1 0.65 (weighted F1 0.66). The abstract also gives 0.66 for the FR/NFR task. **Phase 3 check (arXiv 2302.04723v2 full text, Table 12 and text):** supervised comparison F1 = 0.93 for K&M (SVM, all word features, FR) and 0.93 for NoRBERT (large, NFR), compiled from the original papers | OK; the paper now says these supervised figures were taken from the original studies |
| 22 | Tunstall et al. 2022, SetFit (tunstall2022setfit) | ✔ arXiv 2209.11055 | With 8 labelled examples per class, competitive with fully fine-tuned RoBERTa-Large on a sentiment benchmark | PDF Sec. 1: "with only 8 labeled examples in the Customer Reviews (CR) sentiment dataset, SetFit is competitive with fine-tuning on the full training set". Sec. 4: the baseline is RoBERTa-Large; N is samples per class | OK. Name the CR dataset |
| 23 | Hou et al. 2024 (hou2024llm4se) | ✔ 10.1145/3695988 | Review documenting the shift to LLMs in SE | Abstract: systematic literature review of 395 papers (2017–2024) on LLMs for SE | OK |
| 24 | Scrum Guide 2020 (scrumguide2020) | URL ✔ (no DOI) | Product Backlog is the single source of work; the Product Owner is accountable for it, including ordering | Guide text: "It is the single source of work undertaken by the Scrum Team"; "The Product Owner is also accountable for effective Product Backlog management, which includes … ordering Product Backlog items" | OK |
| 25 | Sedano et al. 2019 (sedano2019) | ✔ 10.1109/ICSE.2019.00036 | Grounded theory, 8 projects, 56 interviews at Pivotal; the backlog is a model of work to be done and a boundary object | ACM/IEEE abstract: the same (plus a survey of 27 designers) | OK |
| 26 | Lucassen et al. 2016a, QUS (lucassen2016qus) | ✔ 10.1007/s00766-016-0250-x | QUS framework with 13 criteria; AQUSA tool | Abstract: 13 quality criteria; AQUSA; evaluation on 1,023 stories from 18 companies | OK |
| 27 | Lucassen et al. 2016b (lucassen2016use) | ✔ 10.1007/978-3-319-30282-9_14 | Surveyed 182 practitioners and interviewed 21; Connextra template dominant | Abstract: 182 responses and 21 interviews. Sec. 3.3: 59% use Connextra (+10% without "so that") | OK |
| 28 | van Can & Dalpiaz 2025 (vancan2025) | ✔ 10.1016/j.infsof.2024.107644 | 1,636 backlog items from 14 projects; inconsistent labelling; multiple requirements per item; encoder-only models best | Highlights and abstract: the same. Encoder-only (BERT, RoBERTa) beat Llama 3, Mistral 7B and GPT-4 | OK |
| 29 | Hujainah et al. 2018 (hujainah2018) | ✔ 10.1109/ACCESS.2018.2881755 | Reviewed prioritisation techniques, stakeholders and challenges | IEEE Access abstract: systematic review (Kitchenham); 108 techniques; 84 criteria; limitations | OK |
| 30 | Choetkiertikul et al. 2019 (choetkiertikul2019) | ✔ 10.1109/TSE.2018.2792473 | Story-point estimation with LSTM + recurrent highway net; 23,313 issues from 16 projects | Abstract (arXiv 1609.00489 version): the same | REMOVE (Phase 13; see below) |
| 31 | Johnson & Khoshgoftaar 2019 (johnson2019) | ✔ 10.1186/s40537-019-0192-5 | Inverse-frequency class weighting is a standard algorithm-level remedy; macro score is the honest report | Survey: algorithm-level methods are "commonly implemented with a weight or cost schema"; "accuracy may mislead" | OK. Reword: "accuracy can mislead under imbalance [J], so we report macro-F1" (the macro-F1 choice is ours) |
| 32 | Zhao et al. 2022 (zhao2022nlp4re) | ✔ 10.1145/3444689 (Crossref: published online 17 Apr 2021; print issue 54(3), 30 Apr 2022; paper cites 2022, the issue year) | Mapped NLP4RE and documented the research-practice gap | Abstract: 404 studies; 7% evaluated in industry; only 17 of 130 tools available | OK |
| 33 | Binkhonain & Zhao 2019 (binkhonain2019) | ✔ 10.1016/j.eswax.2019.100001 | Catalogued ML methods for identifying NFRs | Systematic review of 24 ML approaches; 16 algorithms; SVM most used | OK |
| 34 | Mejía-Domínguez et al. 2026 (mejia2026loona) | ✔ 10.3390/math14193637 | LOONA, an LLM assistant for Spanish user stories, "κ of 0.76 in an evaluation on 100 stories" | κ = 0.76 is **Fleiss agreement among 3 experts** labelling 100 stories, not a tool score. LOONA is a fine-tuned Spanish BERT whose confidence threshold gates generative rewriting. 5-fold: accuracy 0.91, F1 0.91, MCC 0.82. 70% judged improved (n = 30) | **FIX**: rewrite the sentence |
| 35 | Hey et al. 2020, Zenodo note (hey2020supp) | ✔ 10.5281/zenodo.8347866 | Fold-indexing bug; corrected results about 5 pp lower; unseen-project advantage holds | Note: the same | Claim OK, but **REMOVE**: superseded by the corrected KIT version (row N3), which itself discloses the bug, frees a slot and gives the corrected numbers |

## Replacements (verified)

| # | New reference | DOI resolves? | Use in paper | What the source says | Status |
|---|---|---|---|---|---|
| N1 | Dias Canedo & Cordeiro Mendes 2020, *Entropy* 22(9):1057 (diascanedo2020) | ✔ 10.3390/e22091057 | Classical baselines on PROMISE_exp | Abstract: BoW vs TF-IDF vs CHI2 with LR, SVM, MNB and kNN on PROMISE_exp. TF-IDF + LR best: F-measure **0.91 binary (tying with SVM)**, 0.74 NFR classes, 0.78 overall | NEW (peer-reviewed, 2020) |
| N2 | Petrillo et al. 2025, *Future Internet* 17(1):15 (petrillo2025) | ✔ 10.3390/fi17010015 | Evidence that SetFit has been applied to requirements (SecReq, security vs non-security), for the softened Step 2 claim | Uses SecReq (Knauss et al.; 623 requirements from 3 industrial specifications); fine-tuning plus SetFit few-shot; best accuracy 0.94 (BERT, augmented data) | NEW (peer-reviewed, 2025) |
| N3 | Hey et al. 2022, corrected NoRBERT, KIT report (hey2022corrected) | ✔ 10.5445/IR/1000150464 (DataCite: resourceType Report, BibTeX techreport, KIT, 2022; official title "NoRBERT: Transfer Learning for Requirements Classification") | Corrected unseen-project figure; bug disclosure | KIT record: "Corrected Version due to a bug in a part of the evaluation." Abstract: F1 up to 94%, 87% average on frequent classes, "improvement of ten percentage points" on relabelled PROMISE | NEW (technical report, not peer-reviewed) |

## Effect on the list
- The list stays at 35 references: 3 removed and 3 added.
- Peer-reviewed sources from 2018–2026 rise from 23 to **25 of 35**.
- The remaining 10 are:
  - 4 preprints or reports (RoBERTa, DistilBERT, SetFit, KIT NoRBERT);
  - the dataset record (PROMISE, Zenodo);
  - the Scrum Guide;
  - 4 peer-reviewed sources from before 2018 (Cleland-Huang 2007, Kurtanović 2017, Lucassen 2016a/b).

## Step 2: "to our knowledge" claims

| Claim (Phase 1) | Search done | Finding | New wording |
|---|---|---|---|
| "To our knowledge [SetFit] has not yet been evaluated on PROMISE" | Web search on SetFit with requirements, PROMISE, NFR, few-shot and user stories (3 queries) | Petrillo et al. 2025 applied SetFit to **SecReq**, not PROMISE. No SetFit study on PROMISE NFR was found. Few-shot **LLM prompting** on PROMISE does exist (e.g., arXiv 2509.13196, 2025; not cited) | "SetFit has been applied to security-requirements classification on SecReq [N2]; we did not find a study that applies it to PROMISE NFR, although our search was not systematic." |
| "NoRBERT was the first systematic use of BERT for requirements classification" | Checked the Hey et al. abstracts (IEEE and KIT); no priority claim is made there | A priority claim we cannot support | "NoRBERT was an early and widely cited application of BERT fine-tuning to requirements classification" |
| "almost every result comes from the PROMISE NFR corpus" | Compared against our own Table I | Overstated. Table I also lists a 4,908-item corpus, Turkish, aerospace, NFR-SO and backlog datasets | "most results on FR/NFR classification come from the PROMISE NFR corpus or its extensions" |
| "few studies say what a team should *do* with a predicted label" | No exhaustive count is possible | Opinion; must be scoped | "few of the studies we reviewed say …" |
| "None of these studies feeds requirement-type labels into prioritisation or refinement" | Re-read the four cited studies (QUS, Choetkiertikul, LOONA, Hujainah) | True of those four studies only | "None of the studies cited in this subsection …" |

This search covered phrases such as "to our knowledge", "first", "novel", "has not", "not yet", "none of these" and "gap" across the full paper text in `work/content.py`.

## Formatting changes made for numbered IEEE style (Step 5)

These changes affect presentation only; no reference was added or removed.

- **Rendering:** biblatex-ieee drops the year of `@online` entries. The three arXiv preprints (Liu 2019, Sanh 2019, Tunstall 2022) and the Scrum Guide are therefore entered as `@misc`, which keeps the year and the arXiv identifier or URL.
- **PROMISE dataset:** its Zenodo title is literally "nfr". A descriptive `titleaddon` ("PROMISE NFR data set") was added, and the title itself is unchanged.
- **Name prefix:** `useprefix=true` is set so that "van Can" keeps its prefix in citations.
- **Word reference list:** it reproduces the biblatex-ieee output string for string. All 35 entries were compared automatically with the PDF text (`work/refcompare.py`).

## Phase 3 corrections (24 Oct 2026)

- **Zhao et al. (ACM CSUR 54(3)):** Crossref gives online publication on 17 Apr 2021 (its "issued" date) and the print issue on 30 Apr 2022. The paper cites 2022, the year of the volume/issue it gives, and this audit now agrees.
- **KIT report [13]:** the entry now uses the official DataCite title without "(corrected version)" and type "Tech. Rep.", with the note "corrected version". PDF and Word both print "… Karlsruhe Institute of Technology (KIT), Tech. Rep., 2022, corrected version. DOI: 10.5445/IR/1000150464."
- **DOI prefix:** the PDF now prints "DOI:" in plain capitals, as the Word file does, instead of biblatex's small-caps acronym. URL inter-character stretch in the PDF bibliography was set to zero, which removes spacing such as "10 . 1109".
- **Alhoshan et al. 2023:** 0.93 (K&M, FR) and 0.93 (NoRBERT, NFR) confirmed in Table 12 of the full text. They are the original studies' figures as compiled by Alhoshan et al.
- **Rahman et al. 2019:** "roughly 370" NFR sentences confirmed. The II-B claim "the highest scores come from the smallest evaluation sets" was softened to "some of the highest scores" because Eltahier et al. also report 0.97 on FR_NFR. The FR_NFR set size was not checked, so the paper does not call it larger.
- **Lucassen et al. 2016b:** the intro no longer says "most" backlog items are user stories. It says user stories are "an increasingly popular" way to write them (abstract wording) and keeps the Connextra-template finding (Sec. 3.3).
- **"Screened around 60 candidate records":** no search log exists in the workspace, so the number was removed. The paper now says only that candidate records were screened.

## Phase 5: IEEE Reference Guide conformance (24 Oct 2026)

Presentation only. No reference was added, removed or reordered, and no author, title, year, volume, page range or DOI changed. Source used: the IEEE Reference Guide (Google Doc text export, saved in `work/src/g.txt`), including its list of standard word abbreviations.

- **"doi:" in lowercase** in all 34 entries that have a DOI, in both PDF and Word. This replaces the Phase 3 "DOI:" note above.
- **Journal names abbreviated** using the guide's word list: Requirements Eng. [6], [31]; Inf. Softw. Technol. [5], [27]; Appl. Sci. [25]; Arabian J. Sci. Eng. [26]; ACM Trans. Softw. Eng. Methodol. [30]; IEEE Trans. Softw. Eng. [32]; J. Big Data [35]; ACM Comput. Surv. [17]; Expert Syst. Appl.: X [16]. These stay spelled out because the guide spells out one-word titles: *Entropy*, *Information*, *Aerospace*, *Mathematics*. *IEEE Access* and *Future Internet* contain no listed word.
- **Proceedings names abbreviated:** [2], [3], [4], [7], [9], [11], [12], [15], [21], [22], [23]. "Proc." is prefixed where the guide's conference format calls for it, and the conference year is kept in the title (as in the guide's example "Proc. 1996 Robot. Automat. Conf."). "XXXIII" in [15] is written as "33rd". Words not on the IEEE list (Requirements, Workshop, Chapter, Linguistics, Human, Automated) are spelled out, as the guide directs.
- **Publisher repeats removed** where the proceedings title already names the publisher: "IEEE" in [2], [4], [7], [12]; "ACM" in [9], [23]; "Association for Computational Linguistics" in [11]. Publishers are kept where the title does not name them: Springer [3], [21]; ACM [15] (the Brazilian Symposium); Canadian Artificial Intelligence Association [22].
- **[11] Devlin et al.:** the volume is now printed as "vol. 1". The ACL Anthology subtitle "(Long and Short Papers)" was dropped as part of the abbreviated title.
- **[14] PROMISE NFR dataset** now follows the guide's dataset format (Author, Date, "Title," Source, doi). It reads: J. Cleland-Huang, S. Mazrouee, L. Huang, and D. Port, Mar. 17, 2007, "nfr" (PROMISE NFR data set), Zenodo. doi: 10.5281/zenodo.268542. The day comes from the Zenodo record 268542 publication_date (2007-03-17). In LaTeX this uses a custom biblatex `dataset` driver.
- **Verification:** `work/refcompare.py` confirms the Word list matches the PDF list entry by entry. The 2 flagged entries are the known pdftotext column-merge artefact for [3]/[4], and their text is identical. Every before/after string is in `work/ref_diff_phase5.txt`.

## Phase 5b: BibTeX with IEEEtran.bst (24 Oct 2026)

The bibliography is now produced by BibTeX with the stock `IEEEtran.bst` (v1.14) instead of biblatex-ieee. No reference, author, title, year, volume, issue, page range or DOI changed, and the numbering [1]–[35] is the same. These presentation changes follow from IEEEtran.bst:

- **", doi:"** now follows the year (IEEE guide form) instead of ". doi:". IEEEtran.bst has no doi field, so the DOI is stored in `note`.
- **"Art. no."** now precedes article numbers ([5], [8], [10], [16], [18], [24], [25], [27], [29], [33], [35]).
- **arXiv preprints [19], [20], [28] and the Scrum Guide [1]:** titles are now in quotation marks instead of italics. The arXiv identifier now follows the year ("2019, arXiv:1907.11692, doi: …").
- **[3], [21] (LNCS):** "ser. Lecture Notes in Computer Science. Springer, …" (IEEEtran puts a period and a wide space before the publisher). [21] now reads "in Chinese Comput. Linguistics" (lowercase "in"; biblatex had printed "In" after the question mark).
- **[15], [22]:** the publisher follows the booktitle after a period (IEEEtran convention): "Proc. 33rd Brazilian Symp. Softw. Eng. ACM, 2019"; "Proc. Can. Conf. Artif. Intell. Canadian Artificial Intelligence Association, 2021".
- **[14] dataset:** IEEEtran.bst has no dataset type, so the entry is `@misc` and the date moves after the source: J. Cleland-Huang, S. Mazrouee, L. Huang, and D. Port, "nfr," PROMISE NFR data set, Zenodo, Mar. 17, 2007, doi: 10.5281/zenodo.268542. This departs from the guide's dataset order (Author, Date, "Title," Source), which the Phase 5 biblatex driver had followed.
- **Author lists:** "et al." after the first author when there are more than six authors (IEEE guide rule; set with an IEEEtran BST control entry), as before. "et al." is now italic, as IEEEtran.bst prints it. Repeated author lists ([12], [13]) are printed in full, not as a dash.
- **Word list:** generated from the `.bbl`, so it matches the PDF; verified entry by entry.


## Phase 13: references for the GPU-results rewrite (30 Oct 2026)

The paper still cites 35 references. Because the order of first citation changed, reference **numbers** differ from the earlier sections of this audit; the keys stay the same.

**Removed** (the sentences that cited them are no longer in the paper):
- **sun2019finetune** (Sun et al. 2019): its only use was a sentence saying its advice informed our settings. Our settings are now stated directly from the notebooks.
- **yucalar2023** (Yucalar 2023): its row in Table I and the BERTurk clause were removed to make room. The source itself was valid.
- **choetkiertikul2019** (Choetkiertikul et al. 2019): story-point estimation was a side remark in the Agile Backlog Support section.

**Added** (all verified in Phase 13):
- **guo2017calibration**: C. Guo, G. Pleiss, Y. Sun, K. Q. Weinberger, "On calibration of modern neural networks," Proc. 34th ICML, PMLR 70, pp. 1321–1330, 2017. Checked on proceedings.mlr.press/v70/guo17a.html (HTTP 200) and arXiv 1706.04599. Claim in paper: fine-tuned neural networks are often over-confident, and temperature scaling (logits divided by a single T fitted by NLL on held-out data) corrects this. The abstract states that modern neural networks are poorly calibrated and that temperature scaling, a single-parameter variant of Platt scaling, is surprisingly effective. **OK**.
- **qwen2024**: "Qwen2.5 Technical Report," arXiv:2412.15115 (2024). Author list checked with the arXiv API; the first six authors are printed, followed by et al. Use in paper: the source of the Qwen2.5-1.5B-Instruct model used as our zero-shot baseline. **OK**.
- **dalpiaz2019data**: F. Dalpiaz, D. Dell'Anna, F. B. Aydemir, S. Çevikol, "explainable-re/RE-2019-Materials v0," Zenodo, 2019, doi:10.5281/zenodo.3309669. Checked with the Zenodo API: creators, title, date 2019-07-10 and DOI. Use in paper: the source of the four external documents and the relabelled PROMISE used in our external test. **OK**.

**Verification after the rebuild:** `work/check.py` (35 bib entries, 35 printed, all cited in both Word and PDF, first-citation order ascending) and `work/refcompare.py` (35 compared, 0 mismatches) both pass. The comparator now matches on the first 40 characters, because reference [4] begins with "F. Dalpiaz, ", which also occurs inside [3].
