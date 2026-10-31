# How to run `paper_v3_all_experiments.ipynb` on Colab (A100)

This is the **only** file you need to run. It contains every experiment for the paper. You do not need to run the older notebooks (`rezz_bert_experiments`, `paper_v2_experiments`) again; their results are reused automatically.

## Steps
1. Go to https://colab.research.google.com → **File → Upload notebook** → pick `paper_v3_all_experiments.ipynb`.
2. **Runtime → Change runtime type** → **A100 GPU**. Turn on **High-RAM** if it is offered. Click Save.
3. **Runtime → Run all**.
4. When asked, allow Google Drive access. Results are saved in `MyDrive/paper_v3_results` after every run.
5. Leave the tab open. Expected time is **3–5 hours** on an A100 40 GB.
   - If Colab disconnects or the session ends, reconnect, set the A100 again and press **Run all**. Finished runs are skipped, so it continues where it stopped.
6. At the end the browser downloads **`paper_v3_results.zip`**. Push the folder or the zip to GitHub (e.g. `paper_v3_results/`) and tell me.

## Earlier results (found automatically)
- The notebook looks for `MyDrive/bert_paper_results` and `MyDrive/paper_v2_results` in your Drive.
- If they are not there, it downloads them from your GitHub repo `RezZup/tearmpaper`. That only works while the repo is **public**. If you make the repo private before running, put the two folders in Drive first.

## What it runs (in this order)

| Part | Models | Approx. time (A100 40 GB) |
|---|---|---|
| 1 | SVM, DistilBERT, BERT, RoBERTa trained on all PROMISE (original and relabelled labels), tested on the external requirements and the UStAI user stories | ~15 min |
| 2 | Qwen2.5 1.5B, 7B, 14B Instruct (32B only on 80 GB GPUs), zero-shot and 8-shot, no training | ~45 min |
| 3 | RoBERTa-large, DeBERTa-v3-large: PROMISE random and project-held-out, external, user stories | ~1.5–2.5 h |
| 4 | Qwen2.5-7B + LoRA: PROMISE project-held-out, external, user stories | ~1 h |
| 5 | All tables, bootstrap confidence intervals, calibration and a reproducibility check vs your v2 run | ~5 min |

## Things to know
- **Don't change any setting** in the configuration cell, and **don't edit or delete** files in the results folder. If you change something, tell me exactly what.
- **If a cell fails:** copy the error message plus the last 10 printed lines and send them to me. Don't fix it by changing the code.
- **"Out of memory" in Part 2 or 4:** Runtime → Restart session, then Run all again (finished runs are skipped). If it happens again, send me the message.
- **Compute units:** an A100 uses Colab compute units quickly. If you run low, the important parts (1 and 2) finish first, so partial results are still useful. Send whatever is in the folder.
- **User stories:** the notebook uses the public UStAI dataset (1,260 annotated user stories, Yamani et al., PROMISE 2025). Your own 242-story annotation is not used: its inter-annotator agreement was at chance level (κ ≈ 0), so it cannot serve as ground truth.
- **About the numbers:** I will recompute every number from the saved predictions before anything goes into the paper, and every result will be reported as it comes out, including the ones that do not favour BERT.
