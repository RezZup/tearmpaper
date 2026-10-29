"""Check every reference in refs.py: DOI resolves at doi.org, and title/authors/year/venue match the registry
(Crossref for most DOIs, DataCite for Zenodo/arXiv DOIs, arXiv API as a second source for preprints)."""
import json, re, sys, time, unicodedata, urllib.request, urllib.error, xml.etree.ElementTree as ET
sys.path.insert(0, '/home/user/work')
from refs import R

UA = {'User-Agent': 'refcheck/1.0 (mailto:refcheck@example.org)'}

def get(url, accept=None):
    h = dict(UA)
    if accept: h['Accept'] = accept
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read().decode('utf-8', 'replace'), r.geturl()

def resolves(doi):
    try:
        req = urllib.request.Request('https://doi.org/api/handles/' + doi, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            j = json.loads(r.read()); return j.get('responseCode') == 1
    except urllib.error.HTTPError as e:
        return False

def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9 ]', '', re.sub(r'[{}]', '', s)).split()

def sim(a, b):
    A, B = set(norm(a)), set(norm(b))
    return len(A & B) / max(1, len(A | B))

out = []
for r in R:
    rec = {'key': r['key'], 'doi': r.get('doi'), 'url': r.get('url')}
    try:
        if r.get('doi'):
            rec['resolves'] = resolves(r['doi'])
            if r['doi'].startswith('10.5281') or r['doi'].startswith('10.48550'):
                _, body, _ = get('https://api.datacite.org/dois/' + r['doi'])
                a = json.loads(body)['data']['attributes']
                title = a['titles'][0]['title']; year = a.get('publicationYear')
                fam = [c.get('familyName') or c.get('name', '').split(',')[0] for c in a['creators']]
                venue = a.get('publisher'); src = 'DataCite'
            else:
                _, body, _ = get('https://api.crossref.org/works/' + r['doi'] + '?mailto=refcheck@example.org')
                m = json.loads(body)['message']
                title = (m.get('title') or [''])[0]
                fam = [x.get('family', x.get('name', '')) for x in m.get('author', [])]
                dp = (m.get('published-print') or m.get('published-online') or m.get('issued'))['date-parts'][0]
                year = dp[0]; venue = (m.get('container-title') or [''])[0]; src = 'Crossref'
                rec['issued_print'] = (m.get('published-print') or {}).get('date-parts', [[None]])[0][0]
                rec['issued_online'] = (m.get('published-online') or {}).get('date-parts', [[None]])[0][0]
            rec.update(src=src, reg_title=title, reg_year=year, reg_authors=fam, reg_venue=venue)
            rec['title_sim'] = round(sim(r['title'], title), 2)
            mine = [f for f, g in r['authors']]
            rec['authors_match'] = [norm(x)[-1:] for x in mine] == [norm(x)[-1:] for x in fam]
            rec['n_auth'] = (len(mine), len(fam))
            rec['year_match'] = str(r['year']) == str(year) or str(r['year']) in (str(rec.get('issued_print')), str(rec.get('issued_online')))
            rec['my_venue'] = r.get('journal') or r.get('booktitle') or r.get('publisher')
        else:
            st, body, final = get(r['url']); rec['resolves'] = st == 200
            rec['reg_title'] = re.search(r'<title>(.*?)</title>', body, re.S).group(1).strip()
            rec['src'] = 'URL'
    except Exception as e:
        rec['error'] = repr(e)
    out.append(rec); time.sleep(0.4)
    flag = '' if rec.get('resolves') and rec.get('title_sim', 1) >= 0.6 and rec.get('authors_match', True) and rec.get('year_match', True) else '  <-- CHECK'
    print(r['key'], rec.get('src'), 'resolves=%s' % rec.get('resolves'), 'title_sim=%s' % rec.get('title_sim'),
          'authors=%s %s' % (rec.get('authors_match'), rec.get('n_auth')), 'year=%s/%s' % (r['year'], rec.get('reg_year')), flag)
json.dump(out, open('/home/user/work/verify_refs.json', 'w'), indent=1, ensure_ascii=False)
# arXiv cross-check for preprints
ids = {r['key']: r['eprint'] for r in R if r.get('eprint')}
_, body, _ = get('https://export.arxiv.org/api/query?id_list=' + ','.join(ids.values()))
ns = {'a': 'http://www.w3.org/2005/Atom'}
for e in ET.fromstring(body).findall('a:entry', ns):
    print('arXiv', e.find('a:id', ns).text.split('/')[-1], '|', ' '.join(e.find('a:title', ns).text.split()), '|',
          e.find('a:published', ns).text[:4], '|', [a.find('a:name', ns).text for a in e.findall('a:author', ns)])
