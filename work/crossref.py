import json, sys, time, urllib.request, urllib.parse
dois = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
out = {}
try:
    out = json.load(open('meta.json'))
except Exception:
    pass
for d in dois:
    if d in out:
        continue
    url = "https://api.crossref.org/works/" + urllib.parse.quote(d) + "?mailto=research@example.org"
    try:
        r = json.load(urllib.request.urlopen(url, timeout=20))['message']
        out[d] = r
        a = "; ".join(f"{x.get('family','')}, {x.get('given','')}" for x in r.get('author', [])[:8])
        yr = (r.get('published-print') or r.get('published-online') or r.get('issued'))['date-parts'][0]
        print("OK", d, "|", yr, "|", r.get('title', [''])[0][:90], "|", (r.get('container-title') or [''])[0][:60], "|", r.get('volume', ''), r.get('issue', ''), r.get('page', ''), r.get('article-number', ''), "|", a[:140], flush=True)
    except Exception as e:
        print("FAIL", d, e, flush=True)
    time.sleep(0.3)
    json.dump(out, open('meta.json', 'w'))
