import re, csv
rows=[]
for line in open('data/nfr/nfr.arff', encoding='latin-1'):
    line=line.strip()
    if re.match(r"^\d+,", line):
        m = re.match(r"^(\d+),'(.*)',([A-Z]+)$", line)
        if not m: print("BAD", line[:100]); continue
        rows.append((int(m.group(1)), m.group(2).replace("\\'","'"), m.group(3)))
with open('data/promise_nfr.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['project','text','label']); w.writerows(rows)
from collections import Counter
print(len(rows)); print(Counter(r[2] for r in rows)); print(len(set(r[0] for r in rows)),'projects')
print(rows[0]); print(rows[300])
