# BERT-Based Requirement Classification for Agile Backlog Management

[![Paper PDF](https://img.shields.io/badge/Paper-PDF-red.svg)](term_paper.pdf)
[![Paper DOCX](https://img.shields.io/badge/Paper-Word%20DOCX-blue.svg)](term_paper.docx)
[![LaTeX Source](https://img.shields.io/badge/LaTeX-IEEEtran-brightgreen.svg)](term_paper.tex)
[![Reproducibility](https://img.shields.io/badge/Reproducibility-Verified-success.svg)](repro/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](repro/requirements.txt)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Author:** Gaurav Rajbhar  
**Supervision:** Lovely Professional University, Phagwara, Punjab, India  
**Correspondence:** `gauravrajbhar2115@gmail.com`

---

## 📌 Abstract

Product backlogs mix feature requests, quality constraints, defects, and technical chores, yet few agile teams label them consistently. Consequently, non-functional requirements (NFRs) tend to surface late during implementation, incurring substantial rework costs. This research investigates whether BERT-family neural encoders can classify agile backlog items reliably enough to support backlog refinement.

We synthesise 35 empirical sources and propose a two-level refinement framework equipped with a temperature-scaled confidence gate that routes uncertain requirements to human Product Owners. On the benchmark **PROMISE NFR** dataset (625 requirements across 15 software projects), we conducted full fine-tuning of **DistilBERT**, **BERT-base**, and **RoBERTa-base**, comparing them against strong TF-IDF Support Vector Machine (SVM) baselines under two protocols across three seeds (42, 43, 44):
1. **Standard Random 10-Fold Cross-Validation**
2. **Realistic Project-Held-Out (GroupKFold) Cross-Validation**

In addition, models trained on PROMISE were evaluated against **327 industrial requirements** from four independent systems (Dalpiaz et al., RE'19), alongside a zero-shot LLM baseline (**Qwen2.5-1.5B-Instruct**).

### Key Empirical Findings
- **Random Splits Flatter Classifiers:** On random 10-fold splits, all neural models and the TF-IDF SVM tie on functional vs. non-functional classification (Macro-F1 0.909–0.917).
- **The Cross-Project Performance Cliff:** When entire projects are held out, performance drops across the board, but transformers demonstrate superior cross-project generalisation (Macro-F1 0.736–0.806) compared to the linear SVM (0.590). Project-level cluster bootstrap intervals confirm this advantage is statistically significant in 8 of 9 runs.
- **External Generalisation:** On 327 unseen industrial requirements, transformers maintain a lead of +0.070 to +0.081 Macro-F1 over the SVM.
- **Confidence Gate Brittleness:** A raw confidence gate ($\tau = 0.95$) calibrated on PROMISE items fails on new projects (achieving precision between 0.82 and 1.00 instead of the target 0.95). Post-hoc temperature scaling is essential, confirming that automated classifiers should act as **refinement assistants** rather than autonomous decision-makers.

---

## 📊 Experimental Results

### 1. PROMISE NFR Evaluation (Macro-F1, Mean ± SD over Seeds 42, 43, 44)

| Model | Task A (FR vs NFR)<br>Random 10-Fold | Task A (FR vs NFR)<br>Project-Held-Out | Task B (4 NFR Sub-classes)<br>Random 10-Fold | Task B (4 NFR Sub-classes)<br>Project-Held-Out |
|---|:---:|:---:|:---:|:---:|
| **TF-IDF + Linear SVM** | 0.912 ± 0.003 | 0.590 ± 0.013 | 0.821 ± 0.015 | 0.718 ± 0.001 |
| **DistilBERT** | 0.909 ± 0.002 | 0.736 ± 0.024 | 0.892 ± 0.016 | **0.825 ± 0.022** |
| **BERT-base** | 0.915 ± 0.004 | 0.765 ± 0.010 | 0.858 ± 0.004 | 0.774 ± 0.002 |
| **RoBERTa-base** | **0.917 ± 0.011** | **0.806 ± 0.028** | **0.913 ± 0.024** | 0.810 ± 0.018 |

### 2. External Industrial Requirements (Dalpiaz et al., 327 Items)

| Model | Macro-F1 (Trained on PROMISE) | Precision | Recall | Target Precision Met? |
|---|:---:|:---:|:---:|:---:|
| **TF-IDF + SVM** | 0.582 | 0.596 | 0.579 | No |
| **DistilBERT** | 0.652 | 0.680 | 0.648 | Partial (5/8 seeds) |
| **BERT-base** | 0.657 | 0.685 | 0.652 | Partial |
| **RoBERTa-base** | **0.663** | **0.691** | **0.658** | Partial |
| **Qwen2.5-1.5B (Zero-Shot)** | 0.618 | 0.641 | 0.612 | Baseline |

---

## 🗂 Repository Structure

```text
.
├── term_paper.tex                   # Primary IEEEtran LaTeX manuscript source
├── term_paper.pdf                   # Compiled publication-ready PDF (11 pages, IEEE style)
├── term_paper.docx                  # Formatted Word document with OMML math equations
├── references.bib                   # 35 verified BibTeX references (IEEEtran style)
├── figures/                         # High-resolution publication figures (PDF and PNG)
│   ├── fig1_architecture.{pdf,png}  # System architecture: 2-tier classifier & confidence gate
│   ├── fig2_finetune.{pdf,png}      # Transformer fine-tuning pipeline & calibration diagram
│   ├── fig3_workflow.{pdf,png}      # Agile backlog refinement workflow with Product Owner
│   └── fig4_results.{pdf,png}       # Multi-panel performance, calibration & gate charts
│
├── repro/                           # Self-contained reproducibility package
│   ├── analyze.py                   # Recomputes all numbers, tables, CIs, and Fig. 4 (~5 min)
│   ├── requirements.txt             # Python dependencies for analyze.py
│   ├── README.md                    # Detailed reproducibility and execution manual
│   ├── data/                        # PROMISE NFR dataset (nfr.tar and promise_nfr.csv)
│   ├── results/                     # All 72 raw prediction npz files and CSV summaries
│   │   ├── bert_paper_results/      # PROMISE in-domain experiments (Seeds 42, 43, 44)
│   │   └── paper_v2_results/        # External industrial experiments and Qwen2.5 zero-shot
│   ├── notebooks/                   # Google Colab training notebooks
│   │   ├── rezz_bert_experiments.ipynb # PROMISE GPU fine-tuning notebook
│   │   └── paper_v2_experiments.ipynb   # External validation notebook
│   └── outputs/                     # Verification outputs (results.json, folds.json, fig4)
│
├── bert_paper_results/              # In-domain experiment predictions and metric tables
├── paper_v2_result/                 # External dataset predictions and calibration evaluations
├── us result/                       # User story annotation trial (242 stories, Cohen's kappa analysis)
│
├── RUN_ON_COLAB.md                  # Step-by-step instructions for running experiments on Google Colab
├── paper_v3_all_experiments.ipynb   # All-in-one Colab notebook (A100 GPU: Large models, LoRA, UStAI)
├── calibrated_gate_from_your_runs.csv # Temperature-scaled confidence gate threshold data
├── github_repo_review.md            # Technical audit and verification of all saved predictions
├── publish_readiness_plan.md        # Roadmap for conference/journal submission
├── checklist.md                     # IEEE compliance, word counts, formatting, and audit checks
├── viva_prep.md                     # Comprehensive Viva Voce defense preparation (16 Q&A)
├── reference_audit.md               # Fact-checking and DOI verification of all 35 references
│
└── work/                            # Pipeline generation scripts and source assets
    ├── build.py                     # LaTeX-to-DOCX and paper rendering engine
    ├── content.py                   # Structured text components and abstract
    ├── refs.py                      # Reference database mappings
    ├── bibtools.py                  # IEEE citation tools and validator
    └── omml.py                      # OMML XML equation converter for MS Word
```

---

## 🚀 Quickstart & Reproduction

### 1. Recompute All Results (CPU Only, ~5 Minutes)
You do not need a GPU to verify the paper's findings. All raw out-of-fold predictions and external model outputs are included:

```bash
cd repro
python3 -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
python3 analyze.py
```
`analyze.py` recalculates:
- Macro-F1, Precision, and Recall for all 4 models across both tasks and protocols.
- Expected Calibration Error (ECE) before and after temperature scaling.
- Project-level cluster bootstrap 95% confidence intervals.
- The three-panel visualization saved to `outputs/fig4_results.pdf` and `outputs/fig4_results.png`.

### 2. Retrain Models on Google Colab (GPU Runtime)
To train the neural models from scratch on a GPU:
1. Refer to [RUN_ON_COLAB.md](RUN_ON_COLAB.md).
2. Open [`paper_v3_all_experiments.ipynb`](paper_v3_all_experiments.ipynb) or [`repro/notebooks/rezz_bert_experiments.ipynb`](repro/notebooks/rezz_bert_experiments.ipynb) in [Google Colab](https://colab.research.google.com).
3. Select an **A100** or **T4 GPU** runtime (`Runtime -> Change runtime type -> GPU`).
4. Execute all cells; results are saved and can be exported directly.

### 3. Compile LaTeX Document
To compile the IEEE paper locally:
```bash
pdflatex term_paper.tex
bibtex term_paper
pdflatex term_paper.tex
pdflatex term_paper.tex
```

---

## 📖 Supporting Documentation

- 📋 [**Checklist & Audit (`checklist.md`)**](checklist.md): 0 errors, 0 warnings, strict IEEEtran adherence.
- 🔍 [**Reference Audit (`reference_audit.md`)**](reference_audit.md): Complete audit verifying DOIs, URLs, and cited claims for all 35 references.
- 🎓 [**Viva Voce Guide (`viva_prep.md`)**](viva_prep.md): Detailed examiner questions, architectural defenses, and plain-language explanations.
- 📈 [**Publish Readiness Plan (`publish_readiness_plan.md`)**](publish_readiness_plan.md): Concrete steps for publishing this study in IEEE/ACM venues.

---

## 📜 Citation

If you use this code, data splits, or experimental findings in your research, please cite:

```bibtex
@misc{rajbhar2026bert,
  author       = {Gaurav Rajbhar},
  title        = {BERT-Based Requirement Classification for Agile Backlog Management},
  howpublished = {School of Computer Science and Engineering, Lovely Professional University},
  year         = {2026},
  url          = {https://github.com/RezZup/tearmpaper}
}
```

---

## 📄 License
This repository is released under the [MIT License](LICENSE). Academic datasets (PROMISE NFR, Dalpiaz et al.) remain subject to their original distribution terms.
