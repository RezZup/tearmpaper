"""Fetch abstracts for claim checking: Crossref abstract field first, then publisher landing page meta tags / JSON."""
import json, re, sys, html, time, urllib.request
sys.path.insert(0, '/home/user/work')
from refs import R
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36',
      'Accept-Language': 'en'}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode('utf-8', 'replace'), r.geturl()

def clean(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

def page_abstract(url):
    body, final = get(url)
    pats = [r'"abstract":"(.*?)","', r'<meta name="citation_abstract" content="(.*?)"', r'<meta name="dc.description" content="(.*?)"',
            r'<meta name="description" content="(.*?)"', r'<meta property="og:description" content="(.*?)"',
            r'<section[^>]*class="[^"]*[Aa]bstract[^"]*"[^>]*>(.*?)</section>', r'<div[^>]*class="[^"]*abstract[^"]*"[^>]*>(.*?)</div>']
    best = ''
    for p in pats:
        for m in re.finditer(p, body, re.S):
            c = clean(m.group(1).encode().decode('unicode_escape', 'ignore') if p.startswith('"abstract"') else m.group(1))
            if len(c) > len(best): best = c
    return best, final

keys = sys.argv[1:]
for r in R:
    if keys and r['key'] not in keys: continue
    ab, src = '', ''
    try:
        if r.get('doi') and not r['doi'].startswith('10.5281') and not r['doi'].startswith('10.48550'):
            m = json.loads(get('https://api.crossref.org/works/' + r['doi'] + '?mailto=refcheck@example.org')[0])['message']
            if m.get('abstract'): ab, src = clean(m['abstract']), 'crossref'
        if len(ab) < 300:
            url = 'https://doi.org/' + r['doi'] if r.get('doi') else r['url']
            if r.get('eprint'): url = 'https://arxiv.org/abs/' + r['eprint']
            a2, final = page_abstract(url)
            if len(a2) > len(ab): ab, src = a2, final
    except Exception as e:
        src = 'ERROR ' + repr(e)[:120]
    print(f"### {r['key']} [{src}]\n{ab[:2200]}\n", flush=True)
    time.sleep(0.5)
