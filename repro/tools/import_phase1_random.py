"""Import the original (Phase 1) random-fold DistilBERT predictions, seed 42, into the
reproducibility package.

Why: a full 10-fold DistilBERT run takes about 40 min (Task A) + 15 min (Task B) on a
2-core CPU. The original run used the same folds, configuration and per-fold seeds as
`reproduce.py bert`. We re-ran fold 0 of both tasks with `reproduce.py` and checked that
the predictions are identical to the original run (see check output below). We then
imported the remaining folds instead of recomputing them.

Run `python3 reproduce.py bert --task A --protocol random --seed 42` (and B) to
recompute all ten folds from scratch instead.

The original run did not store the max softmax probability, so DistilBERT_pmax is empty
for these two files; the confidence-gate analysis uses the project-held-out runs.

Usage: python3 tools/import_phase1_random.py <dir with bert_preds_A.json, bert_preds_B.json>
"""
import json, os, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PRED = os.path.join(HERE, '..', 'outputs', 'predictions')
FOLDS = os.path.join(HERE, '..', 'outputs', 'folds.json')


def main(src):
    folds = json.load(open(FOLDS))
    for task in 'AB':
        old = json.load(open(os.path.join(src, f'bert_preds_{task}.json')))
        state_p = os.path.join(PRED, f'.bert_state_{task}_random_42.json')
        # 1) identity check on every fold that reproduce.py has re-run
        if os.path.exists(state_p):
            new = json.load(open(state_p))
            for k in new['done']:
                te = folds[f'{task}|random|42'][k][1]
                same = sum(new['pred'][i] == old['pred'][i] for i in te)
                print(f'Task {task} fold {k}: {same}/{len(te)} predictions identical to the original run')
                if same != len(te):
                    sys.exit('Mismatch: not importing.')
        else:
            sys.exit(f'No re-run fold found for task {task}; run reproduce.py bert --task {task} --protocol random --seed 42 --folds 0 first.')
        # 2) write the DistilBERT columns
        p = os.path.join(PRED, f'{task}_random_seed42.csv')
        df = pd.read_csv(p, keep_default_na=False)
        assert len(df) == len(old['pred']) and all(old['pred'])
        df['DistilBERT'] = old['pred']
        df['DistilBERT_pmax'] = ''
        df['DistilBERT_secs_per_fold'] = sum(old['secs']) / len(old['secs'])
        df.to_csv(p, index=False)
        print(f'Task {task}: wrote DistilBERT predictions to {os.path.relpath(p, HERE)} '
              f'(mean {df.DistilBERT_secs_per_fold.iloc[0]:.1f} s per fold in the original run)')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', 'work', 'exp'))
