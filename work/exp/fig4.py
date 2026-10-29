"""Figure 4: our experiment -- per-class F1 (Task B) and macro-F1 (Tasks A, B) from exp/results_all.json."""
import json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
plt.rcParams.update({'font.family': 'STIXGeneral', 'mathtext.fontset': 'stix', 'font.size': 7.5,
                     'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6})
R = json.load(open('/home/user/work/exp/results_all.json'))
models = [('TF-IDF + MNB', 'MNB'), ('TF-IDF + LogReg', 'LogReg'), ('TF-IDF + LinearSVM', 'Linear SVM'), ('DistilBERT', 'DistilBERT')]
colors = ['#C9D6E8', '#8FA9CC', '#3A5A80', '#C8833A']
hatches = ['', '', '', '//']
fig, (a1, a2) = plt.subplots(2, 1, figsize=(3.4, 3.5), gridspec_kw={'height_ratios': [1.25, 1]})
cls = ['US', 'SE', 'O', 'PE']; names = {'US': 'Usability', 'SE': 'Security', 'O': 'Operability', 'PE': 'Performance'}
x = np.arange(len(cls)); w = 0.2
for i, (k, lab) in enumerate(models):
    v = [R[f'B|{k}']['per_class'][c]['F1'] for c in cls]
    a1.bar(x + (i - 1.5) * w, v, w, label=lab, color=colors[i], edgecolor='#333333', linewidth=0.4, hatch=hatches[i])
a1.set_xticks(x); a1.set_xticklabels([f'{names[c]}\n({c}, n={R["B|DistilBERT"]["per_class"][c]["n"]})' for c in cls])
a1.set_ylabel('F1 (Task B)'); a1.set_ylim(0.5, 1.0); a1.grid(axis='y', lw=0.3, alpha=0.6); a1.set_axisbelow(True)
a1.legend(ncol=4, fontsize=6.5, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.2), handlelength=1.2, columnspacing=0.8)
tasks = [('A', 'Task A: FR vs. NFR\n(n = 625)'), ('B', 'Task B: US / SE / O / PE\n(n = 249)')]
x2 = np.arange(2)
for i, (k, lab) in enumerate(models):
    v = [R[f'{t}|{k}']['macro_F1'] for t, _ in tasks]
    bars = a2.bar(x2 + (i - 1.5) * w, v, w, color=colors[i], edgecolor='#333333', linewidth=0.4, hatch=hatches[i])
    for b, val in zip(bars, v):
        a2.text(b.get_x() + b.get_width() / 2, val + 0.006, f'{val:.3f}'.lstrip('0'), ha='center', va='bottom', fontsize=5.6, rotation=90)
a2.set_xticks(x2); a2.set_xticklabels([l for _, l in tasks]); a2.set_ylabel('Macro-F1'); a2.set_ylim(0.6, 1.0)
a2.grid(axis='y', lw=0.3, alpha=0.6); a2.set_axisbelow(True)
for a in (a1, a2):
    a.spines['top'].set_visible(False); a.spines['right'].set_visible(False)
fig.tight_layout(h_pad=0.8)
for ext in ('png', 'pdf'):
    fig.savefig(f'/home/user/figures/fig4_results.{ext}', dpi=300)
    fig.savefig(f'/home/user/work/figs/fig4_results.{ext}', dpi=300)
print('saved')
