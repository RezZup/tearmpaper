# Submission checklist (revised version): "BERT-Based Requirement Classification for Agile Backlog Management"

Updated 24 Oct 2026 after the audit and the Phase 3 corrections (see the last section). The counts below come from `work/check.py` (saved in `work/check.json`) and `work/refcompare.py`, not from hand counting.

## Files

| File | Status |
|---|---|
| `term_paper.pdf` | Compiled from `term_paper.tex` (pdflatex → bibtex → pdflatex ×2): 0 errors, 0 warnings, 0 overfull boxes. Phase 5b: 10 pages. |
| `term_paper.tex` + `references.bib` | IEEEtran `[conference]`, 10 pt, Times (`mathptmx`). `\bibliographystyle{IEEEtran}` + BibTeX (no biblatex) since Phase 5b; `cite` package for [3], [5] and [3]–[5]. Written natively in LaTeX. Overleaf upload: `term_paper_overleaf.zip` (tex, bib, 4 figure PDFs). |
| `term_paper.docx` | Two-column IEEE-style layout with 4 embedded images and 4 real Word tables. Both equations are **real Word equation objects** (OMML), editable in Word. Numbered citations and reference list match the PDF. |
| `figures/` | Fig. 1–4 as PNG (300 dpi) and PDF. Fig. 4 is new: random vs. project-held-out results. |
| `reference_audit.md` | Step 1 reference table (35 rows plus replacements) and Step 2 claims table. |
| `repro/` | Reproducibility package: `reproduce.py`, `requirements.txt`, `README.md`, prediction CSVs, `results.json`, training log. |
| `viva_prep.md` | Plain-language method explanation and 16 examiner questions with answers. |

## Counts

| Item | Required | Actual |
|---|---|---|
| Pages (PDF) | 6–10 | **10**, references included (no page limit applies any more). |
| Pages (DOCX) | 6–10 | **10** when rendered by LibreOffice. Word may differ by about ±1 page. |
| Abstract | 150–200 words | **200 words** |
| Figures | 3–4 | **4**, all numbered, captioned and referenced in the text |
| Tables | 3–4 (original brief) | **5**, all numbered, captioned and referenced. Table IV (McNemar tests) was added at your request in Phase 4; challenges is now Table V. |
| Equations | – | 2, both referenced in the text ((1) and (2)) |
| References | 30–35 | **35** (3 replaced; see `reference_audit.md`) |
| Peer-reviewed, 2018–2026 | as many as possible | **25 of 35** (was 23) |

## Citation and reference checks (all automated and passing)

- **LaTeX:**
  - The 35 cited keys equal the 35 .bib keys, with none missing either way.
  - Numbering follows the order of first citation.
- **DOCX:**
  - Numbers 1–35 are each cited at least once, and first citations appear in ascending order.
  - The reference list is numbered [1]–[35] in the same order as the BibTeX `.bbl`, and its text is generated from that `.bbl`.
- **DOCX vs. LaTeX:**
  - The multiset of citation numbers in the docx body equals the multiset produced by the .tex citations.
  - All 35 reference strings in the docx match the PDF text (fuzzy comparison; the only 2 flags are a known text-extraction split between [3] and [4]).
- **Clean text:** no leftover markup or "??" and no banned phrases (checked in both the PDF and DOCX text).

## Our experiment vs. the literature (kept separate)

- **Our experiment:** PROMISE NFR from Zenodo, 625 requirements and 15 projects. Two protocols:
  - random stratified 10-fold;
  - project-held-out 5-fold (StratifiedGroupKFold by project).
- **Seeds:** 42–44 for everything, except random-fold DistilBERT (seed 42 only).
- **Results** (macro-F1 mean ± SD):

  | Model | A random | A project | B random | B project |
  |---|---|---|---|---|
  | TF-IDF+NB | 0.906 ± 0.003 | 0.638 ± 0.036 | 0.791 ± 0.016 | 0.696 ± 0.009 |
  | TF-IDF+LogReg | 0.911 ± 0.003 | 0.589 ± 0.017 | 0.819 ± 0.008 | 0.718 ± 0.011 |
  | TF-IDF+SVM | 0.912 ± 0.003 | 0.593 ± 0.012 | 0.824 ± 0.012 | 0.718 ± 0.009 |
  | DistilBERT | 0.901 (1 seed) | 0.751 ± 0.003 | 0.919 (1 seed) | 0.813 ± 0.014 |

- **Literature numbers:** Table I and Section IV-B contain only numbers reported by the cited authors. Table III contains only ours.

## Caveats (please read)

1. **Page limit lifted** (Phase 4). PDF and DOCX are both 10 pages.
2. **Peer-reviewed and 2018–2026: 25 of 35.** The other 10 are:
   - foundational work: Cleland-Huang 2007, Kurtanović 2017, Lucassen 2016a/b;
   - arXiv preprints without a peer-reviewed version: RoBERTa, DistilBERT, SetFit;
   - the PROMISE dataset (Zenodo);
   - the NoRBERT corrected version (KIT repository report);
   - the Scrum Guide 2020.
3. **Literature review:** it is structured but not systematic, and the paper says so.
4. **Experimental limits** (stated in Sec. IV-A and V-D):
   - DistilBERT is partly frozen and untuned;
   - random-fold DistilBERT has one seed;
   - three seeds give only a rough SD;
   - project-held-out folds are uneven (25–216 items in Task A) and train on less data (about 80% vs. 90%), so the random→project drop is not leakage alone;
   - McNemar assumes independent items; items from one project are not, so p-values are likely optimistic. One of 18 project-held-out comparisons fails a Bonferroni correction;
   - PROMISE contains "shall" statements, not user stories. The agile examples are written by us, not data.
5. **Author block:** Gaurav Rajbhar, School of Computer Science and Engineering, Lovely Professional University, Phagwara, Punjab, India, gauravrajbhar2115@gmail.com (set in `AUTHOR` in `work/content.py`). Acknowledgment thanks Shairy Kalra (supervisor) — `ACK` in `work/content.py`.
6. **Imported runs:** the seed-42 random-fold DistilBERT predictions were imported from the original run after fold 0 was verified as identical. The other DistilBERT runs are fresh (see `repro/README.md`).
7. **No similarity or AI-detection report** has been produced or is claimed.

## Rebuilding

```bash
cd work && python3 make_fill.py && python3 build.py tex          # numbers from repro/outputs/results.json
cd .. && pdflatex term_paper && bibtex term_paper && pdflatex term_paper && pdflatex term_paper
cd work && python3 build.py docx && python3 check.py && python3 refcompare.py   # docx numbering comes from the .bbl
```

Word equations are cached in `work/omml_cache.json`. Only a changed equation needs `pip install pypandoc_binary`.

## Phase 3 corrections (applied consistently to .tex, .pdf and .docx)

| # | Correction | Where | Status |
|---|---|---|---|
| 1 | Seed-42 vs. three-seed means made explicit | IV-A random paragraph (seed-42 values plus means 0.824/0.819/0.791), abstract, IV-B ("seed-42 … (three-seed mean 0.912)"), conclusion | Done |
| 2 | "mostly on random splits" → "often without project-level splits" | Abstract | Done |
| 3 | "picture reversed" → "changed from a statistical tie to a clear DistilBERT lead" | Conclusion | Done |
| 4 | Lead holds vs. NB, LR and SVM in every seed; Bonferroni caveat; functional recall 0.56 | Abstract (p ≤ 0.017; 56%), IV-A, conclusion | Done |
| 5 | Drop not attributed to leakage alone (80% vs. 90% training data; projects 11–15 have no F items) | IV-A, IV-B, V-A, V-D | Done |
| 6 | McNemar independence caveat | V-D, conclusion validity | Done |
| 7 | Alhoshan 0.93/0.93 verified (Table 12); Rahman ~370 verified, test F1 0.70 added; "smallest evaluation sets" softened | II-B, II-D, Table I | Done |
| 8 | "Cheap linear model …" marked as an untested hypothesis | V-A | Done |
| 9 | "35 verified sources" → "35 sources" | Abstract, .bib header comment | Done |
| 10 | "replication" → "comparative experiment" | Abstract, contribution 3, IV-A heading, conclusion | Done |
| 11 | "around 60" removed (no search log) | III-A | Done |
| 12 | Lucassen sentence | Introduction | Done |
| 13 | Zhao year: 2022 (issue year); Crossref dates recorded | reference_audit.md (paper already 2022) | Done |
| 14 | KIT entry → Tech. Rep.; "DOI:" consistent; URL spacing fixed | Reference list | Done |
| 15 | viva_prep Q15 corrected | viva_prep.md | Done (your message was cut off here) |

Number audit: `work/numaudit.py` checks every number in the abstract, IV-A, Table III, V-A and VI against values derived from `repro/outputs/results.json` and the prediction CSVs; none are unmatched. No result was changed.

## Phase 4 changes

| # | Request | Result |
|---|---|---|
| 1 | Citations both ways | DOCX and PDF: [1]–[35] each cited, no citation outside the list; .tex: 35 keys cited = 35 .bib keys, 35 printed |
| 2 | Same numbers across abstract, Tables III–IV, IV-A, IV-B, V-A, V-D, VI, viva_prep.md | `work/numaudit2.py`: every number derived from `results.json`/CSVs or a listed constant; key-quantity matrix shows no conflicting values. DOCX vs PDF decimals identical (only Fig. 4 axis ticks and wrapped DOIs differ in extraction) |
| 3 | Abstract wording | "56% of the functional requirements in unseen projects"; "before multiple-comparison correction" added. Kept at 200 words by trimming 5 words elsewhere |
| 4 | viva_prep.md new question | Q6 "Why are your p-values questionable?"; old Q6–Q15 renumbered Q7–Q16; Q5 now points to Q6 |
| 5 | McNemar table | New Table IV (task, seed, baseline, p, Bonferroni p; 18 rows); IV-A text shortened and cites Table IV; challenges table renumbered V automatically in .tex/.pdf/.docx |

## Phase 5 changes (IEEEtran conformance)

| # | Request | Result |
|---|---|---|
| 1 | "Fig." in figure captions | **Wrongly reported as already conforming.** Word and in-text references said "Fig.", but the PDF printed "Figure 1."–"Figure 4." because babel reset `\figurename`. Fixed in Phase 5b |
| 2 | Abbreviate journal/proceedings names | 11 journal entries and 11 proceedings entries abbreviated per the IEEE Reference Guide word list (see reference_audit.md, Phase 5) |
| 3 | Lowercase "doi:" | All 34 DOI entries, PDF and Word |
| 4 | Drop repeated publishers | Removed in [2], [4], [7], [9], [11], [12], [23]. Kept where the title does not name the publisher: [3], [15], [21], [22] |
| 5 | Tidy [14] | IEEE dataset format: date Mar. 17, 2007; quoted title "nfr"; (PROMISE NFR data set); Zenodo; doi |
| 6 | Consistency | .bib/.tex/PDF rebuilt (0 LaTeX errors); Word rebuilt; check.py all pass; refcompare 35 compared, only the 2 known extraction artefacts; numaudit/numaudit2 0 unmatched. PDF 10 pages, Word (LibreOffice) 10 pages. Body text unchanged |

## Phase 5b changes (Fig. captions; BibTeX conversion)

| # | Request | Result |
|---|---|---|
| 1 | "Fig. N." captions in PDF, Word and .tex | Cause: `\usepackage[english]{babel}` reset IEEEtran's `\figurename` "Fig." to "Figure" (and `\tablename` "TABLE" to "Table"). babel removed (US English hyphenation is the LaTeX default, so line breaking is unchanged). PDF now prints "Fig. 1."–"Fig. 4." and "TABLE I"–"TABLE V". Word was already "Fig. N." / "TABLE N". The .tex uses `\caption` with no hard-coded prefix |
| 2 | Report the original class and bibliography system | Class was already `\documentclass[conference,10pt,letterpaper]{IEEEtran}`; bibliography was biblatex (`style=ieee`, backend biber) |
| 3 | Convert to IEEEtran.bst + BibTeX | Removed biblatex, its 15 formatting lines, babel and csquotes. Added `cite`, `\bstctlcite{IEEEexample:BSTcontrol}`, `\bibliographystyle{IEEEtran}`, `\bibliography{references}`. 34 `\textcite`/`\Textcite` replaced by written-out names + `\cite` (same wording as before). references.bib rewritten in classic BibTeX (ASCII, `journal`, `year`, `@techreport`, `@misc`; DOI in `note`; article numbers as "Art. no.") |
| 4 | Keep 35 references and every number | 35 `\bibitem`s, same order as the biber build, so [1]–[35] are unchanged. PDF body text diff vs. the biblatex build: only the 4 "Figure"→"Fig." and 5 "Table"→"TABLE" caption labels. numaudit/numaudit2: 0 unmatched |
| 5 | Compiles with pdflatex + bibtex; Overleaf zip | 0 errors, 0 warnings, 0 undefined references, 0 overfull boxes, 0 BibTeX warnings. `term_paper_overleaf.zip` was unpacked into an empty folder and compiled there; its PDF text is identical to term_paper.pdf |
| 6 | Word reference list matches PDF | The Word list is now generated from the BibTeX `.bbl`. All 35 entries appear verbatim in the PDF text; check.py all pass. PDF 10 pages, Word (LibreOffice) 10 pages |

## Phase 6: author and acknowledgment

| Change | Where |
|---|---|
| Placeholders replaced by: Gaurav Rajbhar / School of Computer Science and Engineering / Lovely Professional University / Phagwara, Punjab, India / gauravrajbhar2115@gmail.com | Title block in .tex, PDF, Word; Word document properties (author) |
| New unnumbered "Acknowledgment" section before References: "The author thanks Shairy Kalra, Lovely Professional University, for supervising this work." | .tex (`\section*{Acknowledgment}`), PDF p. 9, Word |
| Checks | 0 LaTeX errors, 0 overfull, 0 undefined, 0 BibTeX warnings; check.py all pass; Word references verbatim in PDF (35/35); numaudit/numaudit2 0 unmatched; Overleaf zip rebuilt and recompiled cleanly (identical PDF text). PDF 10 pages, Word 10 pages |

## Phase 6b: Word spacing fix

| Problem | Fix |
|---|---|
| python-docx put each of the 9 section breaks (needed to switch to one column for full-width figures/tables and back) in its own empty paragraph. These inherited the template default (11 pt Calibri, 1.15 line spacing, 10 pt after), giving large gaps around every wide figure/table in MS Word | 7 breaks moved into the preceding paragraph and the empty paragraphs deleted. The 2 after wide tables sit in the existing small spacer paragraph |
| Template defaults (10 pt after, 1.15 line spacing, Calibri 11 pt) applied to any paragraph without its own formatting, including new paragraphs typed in Word | Document defaults and Normal style set to Times New Roman 10 pt, single spacing, 0 pt before/after. Every paragraph now has explicit spacing |
| File opened in "Compatibility Mode" (Word 2010 layout) | Compatibility mode 15 (Word 2013 and later) |
| Checks | check.py all pass (text, citations, 35 references, 5 tables, 4 images, 2 equations unchanged); LibreOffice render 10 pages, no gaps. Not tested in MS Word itself (not available in the sandbox) |
