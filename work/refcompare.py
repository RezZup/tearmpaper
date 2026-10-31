import re, subprocess, unicodedata, difflib
from docx import Document
d=Document('/home/user/term_paper.docx'); ps=[p.text for p in d.paragraphs]
dref=[p for p in ps[ps.index('References')+1:] if p.strip()]
raw=subprocess.run(['pdftotext','/home/user/term_paper.pdf','-'],capture_output=True,text=True).stdout
raw=raw[[m.start() for m in re.finditer(r'R\s?EFERENCES',raw)][-1]:]
raw=re.sub(r'\[\d+\]','',raw); raw=unicodedata.normalize('NFC',raw)
flat=re.sub(r'\s+',' ',raw.replace('\f',''))
N=lambda x: re.sub(r'[\s\-\u2009]','',unicodedata.normalize('NFC',x))
starts=[]; pos=0
for t in dref:
    body=t.split('\t',1)[1]; q=flat.find(body[:40],pos); starts.append(q); pos=q+1
starts.append(len(flat)); bad=0
for i,t in enumerate(dref):
    body=t.split('\t',1)[1]; seg=flat[starts[i]:starts[i+1]].strip()
    r=difflib.SequenceMatcher(None,N(body),N(seg)).ratio()
    if r<0.995: bad+=1; print(i+1, round(r,3)); print(' D:',body); print(' P:',seg)
print('references compared',len(dref),'mismatches',bad)
