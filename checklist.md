# Submission checklist: "BERT-Based Requirement Classification for Agile Backlog Management"

Updated 30 Oct 2026 (Phase 13: rewrite with the author's own GPU results). The counts come from `work/check.py`, `work/refcompare.py` and `work/numaudit.py`, not from hand counting.

## Files

| File | Status |
|---|---|
| `term_paper.pdf` | Compiled from `term_paper.tex` (pdflatex → bibtex → pdflatex ×2): 0 errors, 0 warnings, 0 overfull boxes, 0 undefined references. **11 pages.** |
| `term_paper.tex` + `references.bib` | IEEEtran `[conference]`, 10 pt, Times (`mathptmx`), `\bibliographystyle{IEEEtran}` + BibTeX, written natively in LaTeX. |
| `term_paper_overleaf.zip` | `term_paper.tex`, `references.bib`, `figures/fig1–4.pdf`. Upload it to Overleaf and compile with pdfLaTeX. |
| `term_paper.docx` | Two-column IEEE-style layout with 4 images, 4 real Word tables and 2 Word equation objects. The citations and reference list match the PDF. LibreOffice renders it as **10 pages**; it has not been tested in MS Word itself. |
| `figures/` | Fig. 1 and Fig. 3 are unchanged. Fig. 2 has been redrawn for full fine-tuning. Fig. 4 is new: three panels with the GPU results. |
| `reference_audit.md` | The per-reference checks, with a Phase 13 section for the 3 removed and 3 added references. |
| `repro/` | The reproducibility package: both Colab notebooks, all 72 GPU prediction files plus the LLM file, `analyze.py`, `outputs/results.json`, Fig. 4, and a new `README.md` and `requirements.txt`. |
| `Gaurav_Rajbhar_term_paper_ALL.zip` | One bundle with the PDF, DOCX, TEX, BIB and the Overleaf zip. |

## Counts

| Item | Required | Actual |
|---|---|---|
| Pages | no limit (author's instruction) | PDF **11**, DOCX **10** (LibreOffice; Word may differ by about ±1) |
| Abstract | 150–200 words | **191** |
| Figures | 3–4 | **4**, all numbered, captioned "Fig. N." and referenced |
| Tables | 3–4 | **4**: I literature, II data, III results, IV challenges. The old McNemar table has been removed. |
| Equations | – | 2, both referenced |
| References | 30–35 | **35** |
| Peer-reviewed, 2018–2026 | as many as possible | **22 of 35** |

## Checks (automated, all passing)

- **check.py:**
  - Every one of the 35 bib keys is cited in both the .tex and the docx.
  - First citations appear in ascending order.
  - The docx reference list is numbered [1]–[35] in .bbl order.
  - The citation multiset is the same in the docx and the .tex.
  - No leftover markup or banned phrases.
- **refcompare.py:** all 35 Word references match the PDF text, with 0 mismatches. The old [3]/[4] false alarm is fixed.
- **numaudit.py (new):** 294 numbers checked in the abstract, IV-A, Table III, IV-B, V-A, the threats section and the conclusion, with **0 unmatched**.
  - Each number must be derived from `repro/outputs/results.json` or the prediction files, or be a listed design constant or dataset fact.
- **make_fill.py:** builds every result sentence from `results.json`. Its asserts check each qualitative claim against the data, for example "intervals exclude zero in 8 of 9 runs", "all three transformers predicted functional in every random-fold run", and the per-document item counts.
- **analyze.py:** recomputes the metrics from the npz predictions and checks them against the CSV tables your notebooks wrote.

## Our experiments vs. the literature (kept separate)

Our results (macro-F1 mean ± SD over seeds 42–44, from your GPU runs):

| Model | A random | A project | B random | B project | Ext. original | Ext. relabelled |
|---|---|---|---|---|---|---|
| TF-IDF+SVM | 0.912 ± 0.003 | 0.590 ± 0.013 | 0.821 ± 0.015 | 0.718 ± 0.001 | 0.638 ± 0.000 | 0.632 ± 0.000 |
| DistilBERT | 0.909 ± 0.002 | 0.736 ± 0.024 | 0.892 ± 0.016 | **0.825 ± 0.022** | 0.708 ± 0.076 | 0.712 ± 0.015 |
| BERT-base | 0.915 ± 0.004 | 0.765 ± 0.010 | 0.858 ± 0.004 | 0.774 ± 0.002 | 0.711 ± 0.072 | 0.700 ± 0.005 |
| RoBERTa-base | **0.917 ± 0.011** | **0.806 ± 0.028** | **0.913 ± 0.024** | 0.810 ± 0.018 | **0.719 ± 0.094** | **0.781 ± 0.033** |
| Qwen2.5-1.5B, zero-shot | – | 0.408 | – | 0.716 | 0.530 | – |

Table I and Section IV-B contain only numbers reported by the cited authors. Table III contains only ours.

## Caveats (stated in the paper)

1. **No hyper-parameter search; three seeds.** The external results vary strongly with the seed: seed 44 gave 0.61–0.63 for all three transformers.
2. **The PROMISE notebook did not record its GPU type**, so the paper says only "Google Colab GPU runtimes". The external runs recorded an NVIDIA A100.
3. **Project-held-out folds** train on less data (about 80% vs. 90%) and are uneven, so the random→project drop is not leakage alone.
4. **Calibration does not transfer.** A threshold set on PROMISE met its 0.95 precision target on the external data in only 5 of 8 runs.
5. **User stories:** the pilot of 242 stories by two annotators reached κ = −0.002. It is reported as a limitation only, with no story-level results. The title is kept as you asked, and the paper says plainly that all test data are specification sentences.
6. **The zero-shot LLM** is one small model with one prompt, and PROMISE may be part of its pre-training data.
7. **No similarity or AI-detection report** has been produced or is claimed.

## Rebuilding

```bash
cd repro && python3 analyze.py                     # optional, ~5 min: results.json + Fig. 4 from the npz files
cd ../work && python3 make_fill.py && python3 build.py tex
cd .. && pdflatex term_paper && bibtex term_paper && pdflatex term_paper && pdflatex term_paper
cd work && python3 build.py docx && python3 check.py && python3 refcompare.py && python3 numaudit.py
```

## Phase 13 change log (30 Oct 2026)

| # | Change | Where |
|---|---|---|
| 1 | All CPU results were replaced by your GPU results: full fine-tuning of DistilBERT, BERT-base and RoBERTa-base plus TF-IDF+SVM, 3 seeds, both protocols, both tasks. The Naive Bayes and logistic-regression baselines were dropped because your runs did not include them. | Abstract, IV-A, Table III, Fig. 4, IV-B, V-A, VI |
| 2 | New external test: 327 Dalpiaz et al. industrial requirements, with models trained on original or relabelled PROMISE, and a within-document bootstrap. | IV-A (data, protocol, results), Table III, Fig. 4c |
| 3 | New calibration analysis: ECE, cross-fitted temperature scaling and threshold, and transfer to the external data. Temperature scaling is now part of the framework. | III-D, IV-A |
| 4 | New zero-shot Qwen2.5-1.5B-Instruct baseline. | IV-A, Table III, threats |
| 5 | The McNemar tests and their table were replaced by a paired project cluster bootstrap. The McNemar table (old Table IV) has been removed, so the challenges table is now Table IV. | IV-A, V-D |
| 6 | The text about "CPU", "frozen layers", "2 GB RAM", the "lower bound", one seed for random DistilBERT, and the imported run was all removed, because none of it applies to the GPU runs. Fig. 2 was redrawn for full fine-tuning. | III-C, IV-A, IV-B, V-D, Fig. 2 |
| 7 | Encoder paragraph: three encoders; WordPiece vs. byte-level BPE; median length 21–22 tokens; 6–9 items truncated at 64 tokens. | III-C, IV-A |
| 8 | References: removed Sun 2019, Yucalar 2023 and Choetkiertikul 2019 (and the sentences and Table I row that used them); added Guo 2017 (calibration), the Qwen2.5 report and the Dalpiaz 2019 Zenodo data. Still 35 in total. | II, Table I, III-D, IV-A |
| 9 | Error examples re-checked on the GPU predictions. "Case history" (legal): all three transformers predicted functional in every random-fold run. ADA (usability): RoBERTa predicted security in all six Task B runs. | IV-A |
| 10 | Threats rewritten: GPU nondeterminism, seed 44, few purely quality items in Dronology and WASP, the LLM caveats, and the story pilot (κ = −0.002). | V-D |
| 11 | Future work: a story corpus with guidelines and agreement, project and time splits, larger LLMs or SetFit under one protocol, and a recalibrated field study. | VI |
| 12 | Keywords: "DistilBERT" and "user stories" were replaced by "RoBERTa", "cross-project evaluation" and "calibration". | Keywords |
| 13 | The repro package was restructured around your notebooks and npz files. `analyze.py` replaces `reproduce.py`, and the README and requirements were rewritten. | `repro/` |

Earlier phases (1–8b: reference audit, IEEE conformance, BibTeX conversion, author block, Word spacing and your wording edits) are unchanged where the text still exists. The Phase 8b wordings about the CPU environment no longer apply, because that text has been removed.
