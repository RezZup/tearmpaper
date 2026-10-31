# Review of github.com/RezZup/tearmpaper (commit 2462936)

I checked everything against the saved raw outputs. Nothing in the repository was changed. Nothing in the paper was changed.

## 1. GPU fine-tuning results (rezz_bert_experiments.ipynb → bert_paper_results/): VERIFIED, usable

- **Notebook design is sound:**
  - full fine-tuning of DistilBERT, BERT-base and RoBERTa-base;
  - 3 seeds; class-weighted loss;
  - temperature scaling cross-fitted on the other folds, so no leakage;
  - a bootstrap that resamples whole projects.
- **Macro-F1 recomputed from all 48 saved prediction files:** every value matches per_seed_results.csv exactly. argmax(logits) equals the saved predictions.
- **Folds are the same as in my repro/ run, in all 12 task/protocol/seed settings.** The comparisons are therefore paired. No project is split across folds in the project-held-out runs.
- **ECE before and after temperature scaling:** all 24 values recompute exactly.
- **Bootstrap:** 4 rows spot-checked. The differences and 95% CIs reproduce exactly.
- **bestresult/ is a byte-identical copy of bert_paper_results/.** The name does not mean anything was cherry-picked. Delete one copy, or say it is a duplicate.
- **Your SVM vs my SVM:** they differ by at most 0.009 macro-F1 per run on the same folds. That is most likely small differences in parsing the dataset text.

**Verified results.** Macro-F1, mean ± SD over 3 seeds; accuracy in brackets.

| Model | A project | A random | B project | B random |
|---|---|---|---|---|
| BERT | .765 ± .010 [.791] | .915 ± .004 [.918] | .774 ± .002 [.778] | .858 ± .004 [.858] |
| DistilBERT | .736 ± .024 [.766] | .909 ± .002 [.913] | .825 ± .022 [.829] | .892 ± .016 [.893] |
| RoBERTa | .806 ± .028 [.821] | .917 ± .011 [.921] | .810 ± .018 [.819] | .913 ± .024 [.914] |
| SVM | .590 ± .013 [.673] | .912 ± .003 [.915] | .718 ± .001 [.723] | .821 ± .015 [.822] |

**What these results change in the current paper:**
- The paper says the CPU partial fine-tuning result is a **lower bound** for full fine-tuning. **Task A project-held-out contradicts this:**
  - full-FT DistilBERT averages .736; the frozen CPU version averaged .751;
  - for seed 42 the full-FT run is .711 vs .748.
  - The claim must be removed or rewritten.
- **Task A random split:** no transformer differs from the SVM. All 9 project-bootstrap CIs include 0, which matches the paper's existing conclusion.
- **Task A project split:** transformers beat the SVM by +.11 to +.25. 8 of 9 CIs exclude 0; DistilBERT seed 42 does not.
- **Task B:**
  - RoBERTa beats the SVM in 6 of 6 runs; DistilBERT in 5 of 6.
  - **BERT in 0 of 6.** BERT-base is also badly calibrated on Task B (ECE .27–.30).
- **The confidence gate does not carry over.**
  - The paper's τ = 0.95 gate gave 22% coverage on Task B.
  - With full fine-tuning and class weighting, Task B softmax confidences almost never reach 0.95: coverage is 0–7% with raw scores.
  - Gate results would need to be recomputed on the calibrated scores.

## 2. User-story evaluation (rezz_user_story_eval.ipynb → "us result/"): NOT reportable as it stands

1. **No `disagreements_resolved.csv` in the repo.** Notebook cell 9 then uses Annotator 1's labels as gold and prints "TEMPORARY gold. Do not report that." user_story_results.csv and user_story_bootstrap.csv were therefore almost certainly computed against A1's labels only.
2. **Inter-annotator agreement is at chance level.**

   | A1 \ A2 | F | FQ | NFR | Total |
   |---|---|---|---|---|
   | F | 92 | 14 | 39 | 145 |
   | FQ | 15 | 4 | 3 | 22 |
   | NFR | 47 | 11 | 17 | 75 |
   | Total | 154 | 29 | 59 | 242 |

   - Raw agreement is 46.7%. The agreement expected by chance from the label proportions is 46.8%.
   - **Cohen's κ = −0.002.** κ is −0.005 if FQ is merged with NFR, and −0.033 on items both annotators called F or NFR.
   - Clearly functional stories got NFR or FQ labels, for example:
     - "create, update and delete any records" (A2: NFR);
     - "create deposit forms specific to the collection" (A1: NFR);
     - "identify the number of whales heard in a single audio file" (A2: FQ).
   - The annotation notes columns are empty for both annotators.
3. **Consequence.** With κ ≈ 0, neither annotator's labels can serve as ground truth. Adjudicating the 129 disagreements would not fix this either: it would mostly produce one person's labels again. Model scores against these labels (macro-F1 .40–.49) say nothing about the models. Fixing it would need:
   - written labelling guidelines with examples;
   - a pilot round;
   - re-annotation;
   - κ reported (as a guide, above about 0.6).
4. **Smaller issues:**
   - The sample is 242 stories (11 × 22 projects), not 250.
   - The stories appear to come from the public user-story dataset by Dalpiaz (Mendeley Data). It must be cited, and its licence checked, if used.
   - The user-story predictions were not saved, so the results cannot be re-scored against better labels without re-running the notebook.

## 3. Repository housekeeping (public repo)

- The repository is public. It contains work/ (build scripts, logs) and checklist.md, which document how the paper was produced. Anyone with the link can read them. Make the repo private if that is not intended.
- work/src/alhoshan.pdf is a full copy of a published paper. Check its licence before redistributing it, or remove it.
- The paper files in the repo are the Phase 7 version, not the latest Phase 8 build. references.bib is identical.

---

# v2 results (commit 44cf7ba, paper_v2_result/): VERIFIED

**Run details:** A100-SXM4-40GB; quick_test = false; seeds 42–44; 5 epochs, batch 16, max_len 64.

**Checks, all passed:**
- **Labels and order:** in all 24 external npz files, the gold labels, dataset names and item order match the rebuilt Dalpiaz data exactly.
- **Predictions:** argmax(logits) equals the saved prediction in every run.
- **SVM:** I re-ran it here. Its predictions are identical in all 6 runs (orig and reclass, each × 3 seeds).
- **Tables recomputed from the npz files:**
  - table_external.csv (means and SDs) and table_external_per_dataset.csv: difference 0.000;
  - table_external_bootstrap.csv: all 14 rows identical;
  - calibration table: max difference 0.0005 (numerical optimiser);
  - table_llm_zeroshot.csv: identical.
- **No collapsed runs:** the share of items predicted Quality is 0.42–0.64 in every run.

**Main numbers.** Macro-F1 on items that are only F or only Q (n = 246), mean ± SD over 3 seeds:

| Training labels | SVM | DistilBERT | BERT | RoBERTa |
|---|---|---|---|---|
| PROMISE original F/NFR | .638 | .708 ± .076 | .711 ± .072 | .719 ± .094 |
| Dalpiaz relabelled ("has quality") | .632 | .712 ± .015 | .700 ± .005 | .781 ± .033 |

- **Transformers vs SVM** (bootstrap within dataset, seed-averaged): +.07 to +.08 with original labels; +.07 to +.15 with relabelled data. All 6 CIs exclude 0.
- **Relabelled minus original:** only RoBERTa improves, by +.062 [.030, .093]. For the SVM, DistilBERT and BERT the CI includes 0.
- **Quality flag** (gold = has any quality aspect, all 327 items):
  - F1 is .67–.71 for every model;
  - transformers flag about 60% of mixed F+Q items and wrongly flag about 33% of purely functional ones; the SVM wrongly flags 45%.
- **Per dataset:** results vary widely.
  - Dronology has only 2 only-Q items and WASP only 6, so their per-dataset macro-F1 is unreliable. Report it with counts.
- **Calibration transfer** (T and τ chosen on PROMISE project-held-out OOF):
  - external ECE .22–.24 before temperature scaling, .11–.13 after, so the models are still miscalibrated;
  - the gate meets 0.95 precision in only 5 of 8 seeds where a τ existed (no τ for DistilBERT seed 43);
  - coverage is 12–44%, i.e. about 30–110 of 246 items;
  - precision is .82–1.00; seed 44 fails for all three models.
- **Qwen2.5-1.5B-Instruct, zero-shot:**
  - Task A macro-F1 .408: it predicts NFR for only 7.5% of items;
  - Task B .716, the same as the project-held-out SVM (.718);
  - external quality-flag recall .04.
  - Caveats: a small model, one prompt, and PROMISE may be in its pre-training data.
