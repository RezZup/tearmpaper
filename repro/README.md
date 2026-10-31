# Reproducibility package

This package accompanies "BERT-Based Requirement Classification for Agile Backlog Management" (G. Rajbhar). It contains the training notebooks, the saved predictions of every model and one analysis script, `analyze.py`. The script recomputes every number in Section IV-A, Table III and Fig. 4 from those predictions.

## What is included

| Path | Contents |
|---|---|
| `notebooks/rezz_bert_experiments.ipynb` | PROMISE NFR experiments: TF-IDF+SVM, DistilBERT, BERT and RoBERTa on Tasks A and B, with random 10-fold and project-held-out 5-fold splits and seeds 42–44 |
| `notebooks/paper_v2_experiments.ipynb` | External test on the Dalpiaz et al. industrial requirements (models trained on all of PROMISE, original or relabelled), plus the Qwen2.5-1.5B-Instruct zero-shot baseline |
| `results/bert_paper_results/` | 48 prediction files `{A,B}_{random,project}_{svm,distilbert,bert,roberta}_{42,43,44}.npz` (keys `y`, `pred`, `logits`, `fold`, `project`; for the SVM, `logits` holds its decision scores) and the CSV tables the notebook wrote |
| `results/paper_v2_results/` | 24 files `ext_{orig,reclass}_{svm,distilbert,bert,roberta}_{42,43,44}.npz`, `llm_zeroshot.npz`, CSV tables, `environment.json`, `data_card.json` |
| `data/nfr.tar`, `data/promise_nfr.csv` | The PROMISE NFR archive from Zenodo (doi:10.5281/zenodo.268542) and the parsed CSV (625 rows; columns `project`, `text`, `label`; the row order matches the Task A arrays) |
| `analyze.py` | Recomputes all metrics, bootstrap intervals, calibration and gate results, and Fig. 4 |
| `outputs/results.json` | Every number used in the paper |
| `outputs/fig4_results.{pdf,png}` | Fig. 4 |
| `requirements.txt` | Package versions for running `analyze.py` |

## Re-running the analysis (no GPU needed)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 analyze.py          # about 5 minutes on 2 CPU cores
```

`analyze.py` checks its macro-F1, bootstrap, calibration and external results against the CSV tables written by the notebooks, and it stops if any of them differ.

## Re-training the models (GPU needed)

Both notebooks were written for Google Colab with a GPU runtime. Open each notebook in Colab, choose a GPU runtime and run all cells.

- `paper_v2_experiments.ipynb` recorded its environment in `results/paper_v2_results/environment.json`: Python 3.13.16, torch 2.11.0+cu130, transformers 5.20.2, NVIDIA A100-SXM4-40GB.
- `rezz_bert_experiments.ipynb` did not record its GPU type or package versions.
- The models are downloaded from the Hugging Face Hub, so internet access is needed: `distilbert-base-uncased`, `bert-base-uncased`, `roberta-base` and `Qwen/Qwen2.5-1.5B-Instruct`.

GPU training is not bit-for-bit deterministic. A rerun may therefore give slightly different predictions. That is why the paper's numbers are computed from the saved prediction files.

## Protocols and settings (as in Section IV-A)

- **Task A:** functional (F) vs. non-functional (all other labels); 625 items.
- **Task B:** US / SE / O / PE; 249 items.
- **Random protocol:** stratified 10-fold cross-validation.
- **Project-held-out protocol:** `StratifiedGroupKFold(5)` with the PROMISE project id as the group.
- **Seeds:** 42, 43 and 44, for every model and protocol.
- **SVM:** TF-IDF over word 1–2-grams, sublinear tf, English stop words, fitted inside each training fold; LinearSVC with C = 1 and balanced class weights.
- **Transformers:** full fine-tuning, with all weights trainable.
  - Learning rate 5e-5 for DistilBERT; 3e-5 for BERT-base and RoBERTa-base.
  - AdamW, weight decay 0.01, 10% linear warm-up then linear decay, gradient clipping 1.0.
  - 5 epochs, batch size 16, maximum 64 tokens, class-weighted cross-entropy.
  - No hyper-parameter search.
- **External test:** data from Dalpiaz et al., Zenodo doi:10.5281/zenodo.3309669 (folder `Manually tagged datasets`).
  - 327 items from Dronology, Leeds, ReqView and WASP that have a functional and/or quality aspect.
  - The main metric is the quality-aspect macro-F1 on the 246 items with only one aspect.
  - Models were trained on all 625 PROMISE items (original labels) or on the 612 relabelled PROMISE items that carry an aspect.
- **Statistics (`analyze.py`):**
  - The paired project cluster bootstrap for PROMISE uses 1,000 resamples of the 15 projects. The external test uses a paired within-document bootstrap with 2,000 resamples.
  - ECE uses 15 equal-width bins.
  - Temperature scaling and the gate threshold τ are cross-fitted over folds. τ is the smallest grid value (0.50–0.995, step 0.005) that gives precision ≥ 0.95 on at least 20 items.
  - The external temperature and τ come from the Task A project-held-out predictions of the same model and seed.
- **Zero-shot LLM:** Qwen2.5-1.5B-Instruct with one prompt per task. The prediction is the option letter with the highest next-token probability, from one run over all items.

## Not included

The paper mentions a pilot annotation of 242 user stories by two annotators. Their agreement was at chance level (Cohen's κ = −0.002), so the labels were not used for any result and are not part of this package.
