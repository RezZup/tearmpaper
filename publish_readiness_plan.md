# What the term paper needs before you submit it for publication

**Short answer.** The writing and formatting are already in good shape. What's missing is (1) evidence that the results hold beyond PROMISE, (2) a calibrated confidence gate, (3) removing the user-story numbers, and (4) the paperwork that journals and conferences require (AI-use disclosure, data and code availability, authorship). Steps A–C fix the research content. Your part is one Colab run of about 30–45 minutes; I can do the rest.

Being honest about the bar: a PROMISE-only FR/NFR classifier on its own is not a new contribution. Many published papers already report 0.9+ on PROMISE. What can make this paper publishable is the **evaluation angle**:
- how much performance is lost on unseen projects and on other researchers' datasets;
- whether a confidence gate stays trustworthy when the data changes.

The steps below build that story. No one can promise acceptance.

---

## A. Research content (must do)

### A1. Replace the CPU experiment with your GPU full fine-tuning runs (no new runs needed)
Your `bert_paper_results` are verified (see `github_repo_review.md`). I will:
- rewrite Section IV (methods and Tables III/IV) around full fine-tuning of DistilBERT, BERT and RoBERTa, 3 seeds, T4 GPU;
- delete the "lower bound for full fine-tuning" claim, which your Task A project result contradicts (.736 vs .751), along with the frozen-layer and hardware caveats;
- report the project-cluster bootstrap CIs, and claim differences only where the CI excludes 0.

### A2. External validation: run `paper_v2_experiments.ipynb` (YOU run this)
This is the main new result, and it needs no annotation.
- **Training data:** all 625 PROMISE requirements.
- **Test data:** four public industrial datasets labelled by Dalpiaz et al. (RE'19): Dronology, ReqView, Leeds library and WASP. That is 327 usable requirements, none overlapping PROMISE.
- **Labelling-scheme test:** the models are also trained on Dalpiaz's relabelled PROMISE. This checks whether the label definition explains the external errors.
- **Confidence-gate transfer:** the threshold is chosen on PROMISE and applied unchanged to the external sets.
- **Zero-shot LLM baseline:** Qwen2.5-1.5B-Instruct, no training. Reviewers in 2026 will ask "why not an LLM?"

I tested the notebook end to end on CPU with tiny stand-in models (the real models need the GPU). Data downloads, training, saving, tables, bootstrap, calibration and zipping all work.

### A3. Fix the confidence-gate section (already done from your saved predictions: `calibrated_gate_from_your_runs.csv`)
- **Old paper result:** "τ = 0.95 → Task A 89% coverage" came from uncalibrated CPU scores and no longer applies.
- **New result, temperature-scaled with cross-fitting.** τ is chosen on the other folds to reach 0.95 precision, then applied to the held-out fold.

| Setting | Coverage | Precision |
|---|---|---|
| Task A, random split | 88% | ~0.95 (target met, all models) |
| Task A, unseen projects | 0.4–23% | 0.82–1.00 (**target not reliably met**) |
| Task B, unseen projects | 30–65% | 0.91–0.95 |

- **What this means:** a threshold tuned on familiar projects does not keep its promise on new projects. That is a useful, honest finding, and A2 tests it on fully external data.

### A4. Remove the user-story results (or redo the annotation properly)
- Cohen's κ = −0.002 between your two annotators, which is chance level. The reported scores used one annotator as gold. They **cannot** be published.
- **Recommended:** leave user stories out and list them as future work (the Dalpiaz external sets in A2 replace them as the "outside PROMISE" test).
- **If you want them in later**, you would need:
  - a written guideline with examples;
  - a 30-story pilot with discussion;
  - fresh independent labels from two people with RE background;
  - κ ≥ ~0.6, with the annotators' backgrounds reported.

### A5. Match the claims to the evidence
- **Title:** the experiments use requirement sentences, not real backlogs. Either keep "Agile Backlog" only as motivation, or retitle. For example: *"Fine-Tuned Transformers for Functional/Non-Functional Requirement Classification: Project-Held-Out, External and Calibration Analysis"*.
- **Contribution list:** 3 concrete bullets that each map to a table or figure.
- **Threats to Validity subsection:**
  - small, old datasets;
  - fixed hyper-parameters taken from the literature, not tuned;
  - only 4 external sets;
  - possible pre-training contamination of PROMISE in the LLM;
  - single annotator team in the external labels.

## B. Writing and paperwork (must do)

| Item | Why | Who |
|---|---|---|
| **AI-use disclosure in the Acknowledgment** | IEEE requires disclosure of AI-generated content (text, figures, code) in the acknowledgments: the system used, the sections, and the level of use. Most other publishers have similar rules. Leaving it out can lead to retraction. | I'll draft a truthful text; you confirm it |
| **Data and code availability statement** | Reviewers check that the work can be reproduced. Clean the repo, archive a release on Zenodo, cite the DOI. | You (I'll write the README) |
| **Authorship** | Ask Shairy Kalra whether she should be co-author or only acknowledged. Many venues and universities expect the supervisor as co-author. | You |
| **Length** | Most IEEE conferences allow 6–8 pages. The paper is 10 now, and the new results add more. The literature review must be cut by about 40%. | I'll cut; you approve |
| **Recent related work** | Add verified 2024–2026 work on LLM / small-language-model NFR classification (e.g. NICE, ICSE 2025 [dataset on Zenodo 14590935]) and cite the Dalpiaz RE'19 dataset DOI (10.5281/zenodo.3309669). | I'll verify and add |
| **Your own voice** | You must be able to defend every number and choice to reviewers and your examiner. Read every section and rewrite where needed. | You |

## C. Repository cleanup (before you share the link in the paper)
- **Keep:** the two experiment notebooks, `bert_paper_results/`, `paper_v2_results/`, a README, a LICENSE and `requirements.txt`.
- **Remove:**
  - `bestresult/` (duplicate);
  - `work/` build logs;
  - `work/src/alhoshan.pdf` (a publisher PDF);
  - the docx/aux/log build files;
  - `us result/`, until re-annotated.
- **Check:** `checklist.md` and `viva_prep.md` are internal files. Decide whether to keep them public.
- **Data licences:** PROMISE NFR (Zenodo 268542); Dalpiaz RE'19 materials (GPL-3.0). Cite both. Don't re-upload the data files; the notebook downloads them.

## D. Choosing a venue
- **Pick the venue before the final rewrite.** It fixes the page limit, the template and the reviewing standard.
- **Reasonable targets:**
  - Scopus/IEEE-indexed conferences with real peer review (check the exact indexing on the publisher site, not on the CFP);
  - requirements-engineering workshops (e.g. NLP4RE, AIRE), which have strict reviews but give expert feedback.
- **Avoid:** journals that guarantee acceptance, publish within days or ask for fees before review. Verify any journal's indexing directly in Scopus or Web of Science.

---

## Order of work
1. **You:** run `paper_v2_experiments.ipynb` on a Colab T4 (Runtime → Run all). Send me `paper_v2_results.zip`, or push it to GitHub.
   - If `bert_paper_results` is not in your Drive at `MyDrive/bert_paper_results`, upload `bert_paper_results.zip` to the Colab file panel first. It is needed for the gate-transfer test.
2. **Me:** verify every number from the saved predictions, then rewrite the paper (A1–A5, B), keeping Word, LaTeX and PDF in sync.
3. **You:** decide the venue and authorship, rewrite in your own voice, then clean the repo and get a Zenodo DOI.
4. **Me:** final consistency check against the venue template and page limit.
