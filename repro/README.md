# Reproducibility package

This package accompanies "BERT-Based Requirement Classification for Agile Backlog Management". It holds one script, `reproduce.py`, which produces every number in Section IV-A, Table III and Fig. 4 of the paper.

## What is included

| Path | Contents |
|---|---|
| `reproduce.py` | The whole pipeline: data download and parsing, splits, TF-IDF baselines, DistilBERT fine-tuning, metrics, McNemar tests, confidence-gate table and Fig. 4 |
| `requirements.txt` | The exact package versions used |
| `data/nfr.tar`, `data/promise_nfr.csv` | The PROMISE NFR archive from Zenodo (doi:10.5281/zenodo.268542, MD5-checked) and the parsed CSV (625 rows) |
| `outputs/folds.json` | Test-fold assignment for each task, protocol and seed |
| `outputs/predictions/{A,B}_{random,grouped}_seed{42,43,44}.csv` | Out-of-fold predictions of every model (see the column list below) |
| `outputs/results.json` | All metrics: `runs` (per run), `summary` (mean/SD over seeds), `mcnemar`, `gate` |
| `outputs/fig4_results.{png,pdf}` | Fig. 4 of the paper |
| `tools/import_phase1_random.py` | Imports the original random-fold DistilBERT predictions (see "One shortcut" below) |
| `logs/bert_runs.log` | Training log of the DistilBERT runs reported in the paper |

## Setup

Tested with Python 3.13.16 on Linux, CPU only (2 cores, about 2 GB RAM).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu   # CPU build
pip install -r requirements.txt
```

The first DistilBERT run downloads `distilbert-base-uncased` from the Hugging Face Hub (about 270 MB), so internet access is needed once. Data download also needs internet, unless `data/nfr.tar` is already present.

## Exact run steps

```bash
python3 reproduce.py data        # download nfr.tar from Zenodo, verify MD5, parse ARFF -> data/promise_nfr.csv
python3 reproduce.py folds       # random 10-fold and project-held-out 5-fold splits, seeds 42-44 -> outputs/folds.json
python3 reproduce.py baselines   # TF-IDF + MNB / LogReg / LinearSVM, both tasks, both protocols, 3 seeds (about 1 min)

# DistilBERT: run ONE job at a time on a small machine (each job is resumable per fold)
python3 reproduce.py bert --task A --protocol random  --seed 42     # about 40 min
python3 reproduce.py bert --task B --protocol random  --seed 42     # about 15 min
for s in 42 43 44; do
  python3 reproduce.py bert --task A --protocol grouped --seed $s   # about 17-19 min each
  python3 reproduce.py bert --task B --protocol grouped --seed $s   # about 7 min each
done

python3 reproduce.py evaluate    # metrics, mean/SD, McNemar, gate -> outputs/results.json (prints a summary)
python3 reproduce.py figures     # Fig. 4 -> outputs/fig4_results.{png,pdf}
```

`python3 reproduce.py all` runs every stage in this order (about 2.5 h on a 2-core CPU). If a DistilBERT job is interrupted, rerunning the same command continues from the last finished fold. The progress is kept in `outputs/predictions/.bert_state_*.json`; delete those files to start from scratch.

## Protocols and settings (as in Section IV-A)

- **Task A:** functional (F) vs. non-functional (all other labels); 625 items.
- **Task B:** US / SE / O / PE; 249 items.
- **Random protocol:** `StratifiedKFold(10, shuffle=True, random_state=seed)`.
- **Project-held-out protocol:** `StratifiedGroupKFold(5, shuffle=True, random_state=seed)` with the PROMISE project id as the group, so no project appears in both training and test data.
- **Seeds:** 42, 43, 44 for everything, except random-fold DistilBERT (seed 42 only, because of CPU time).
- **TF-IDF:** word 1–2-grams, sublinear tf, English stop words; fitted inside each training fold.
- **Baselines:**
  - MultinomialNB: α = 0.1.
  - LinearSVC: C = 1, class_weight balanced.
  - LogisticRegression: C = 10, class_weight balanced, max_iter 2000.
- **DistilBERT** (`distilbert-base-uncased`):
  - 5 epochs; AdamW with learning rate 5e-5 and weight decay 0.01; batch size 8; maximum 64 tokens.
  - 10% linear warm-up then linear decay; gradient clipping 1.0.
  - Inverse-frequency class-weighted cross-entropy (Eq. 1).
  - Embeddings and the first 2 of 6 transformer blocks frozen.
  - Per-fold seed = seed + fold index.
- **Metrics:** computed on the pooled out-of-fold predictions of each run. Mean and SD are over seeds (SD with ddof = 1). McNemar is the exact two-sided binomial test on discordant items, within one seed.

## Prediction CSV columns

`idx` (row in `promise_nfr.csv`), `project` (PROMISE project id 1–15), `fold` (test fold), `gold`, `text`, `MNB`, `LogReg`, `LinearSVM`, `DistilBERT` (predicted labels), `DistilBERT_pmax` (maximum softmax probability), `DistilBERT_secs_per_fold` (mean training time per fold).

## One shortcut, stated openly

The random-fold DistilBERT predictions for seed 42 (`A_random_seed42.csv`, `B_random_seed42.csv`) come from the original run behind the first version of the paper, not from a fresh run of this script.

- **Why:** to save about 55 min of CPU time.
- **How we checked them:**
  - That run used the same folds, configuration and per-fold seeds.
  - We re-ran fold 0 of both tasks with `reproduce.py` and obtained identical predictions (Task A 63/63, Task B 25/25 items).
  - We then imported the other nine folds with `tools/import_phase1_random.py`.
- **Known gap:** the original run did not store probabilities, so `DistilBERT_pmax` is empty in these two files. The confidence-gate figures therefore come from the project-held-out runs.
- **To recompute everything:** run the two `--protocol random` commands above. The state files record only fold 0 as done, so folds 1–9 are retrained and the CSVs are overwritten.

Bit-for-bit identical DistilBERT results are expected only with the same library versions and CPU threading (`--threads 2`). Other hardware may give small differences.

## Check against the paper

Running `evaluate` should print these summary values; they are the numbers in Table III of the paper. Macro-F1 is mean ± SD over seeds 42–44 (accuracy in brackets).

| Model | A random | A project-held-out | B random | B project-held-out |
|---|---|---|---|---|
| TF-IDF+NB | 0.906 ± 0.003 [0.909] | 0.638 ± 0.036 [0.698] | 0.791 ± 0.016 [0.790] | 0.696 ± 0.009 [0.703] |
| TF-IDF+LogReg | 0.911 ± 0.003 [0.914] | 0.589 ± 0.017 [0.672] | 0.819 ± 0.008 [0.819] | 0.718 ± 0.011 [0.723] |
| TF-IDF+SVM | 0.912 ± 0.003 [0.915] | 0.593 ± 0.012 [0.674] | 0.824 ± 0.012 [0.825] | 0.718 ± 0.009 [0.723] |
| DistilBERT | 0.901 (seed 42 only) [0.906] | 0.751 ± 0.003 [0.776] | 0.919 (seed 42 only) [0.920] | 0.813 ± 0.014 [0.819] |

Seed-42 random-fold values quoted in the text of Section IV-A:

- Task A: TF-IDF+NB 0.907, TF-IDF+LogReg 0.914, TF-IDF+SVM 0.916, DistilBERT 0.901
- Task B: TF-IDF+NB 0.783, TF-IDF+LogReg 0.824, TF-IDF+SVM 0.832, DistilBERT 0.919
- McNemar, DistilBERT vs. SVM, random seed 42: Task A 24/32, p = 0.35; Task B 30/8, p = 0.00047.
- McNemar, DistilBERT vs. each baseline, project-held-out, seeds 42–44: DistilBERT better in all 18 comparisons (largest p: Task A 0.003 vs. NB; Task B 0.017 vs. LogReg). With a Bonferroni correction for three baselines, Task B seed 43 vs. LogReg (corrected p = 0.051) no longer passes. The test assumes independent items, which items from one project are not.
- Training-set size: random 10-fold trains on 90% of the items (562–563 in Task A); project-held-out 5-fold trains on about 80% on average (409–600 in Task A).

These values match the first version of the paper exactly for the seed-42 random-fold runs. The three-seed and project-held-out numbers are new in this version.
