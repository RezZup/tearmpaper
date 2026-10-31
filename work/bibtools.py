# -*- coding: utf-8 -*-
"""Generate references.bib and APA-7 citation/reference strings from refs.R."""
import re
from refs import R

TEX_ACC = {'ć': "{\\'c}", 'á': "{\\'a}", 'é': "{\\'e}", 'í': "{\\'i}", 'ú': "{\\'u}", 'ã': '{\\~a}', 'ş': '{\\c{s}}', 'Ç': '{\\c{C}}',
           'ç': '{\\c{c}}', 'ê': '{\\^e}', 'ó': "{\\'o}", 'Í': "{\\'I}"}

def tex(s):
    return ''.join(TEX_ACC.get(ch, ch) for ch in s).replace('&', '\\&')

def bib_entry(r):
    t = r['type']
    def nm(f, g):   # brace multi-word surnames, but leave lowercase prefixes (van, von, de) visible to biber
        if ' ' in f and not f.split()[0].islower(): return f"{{{tex(f)}}}, {tex(g)}"
        return f"{tex(f)}, {tex(g)}"
    names = ' and '.join(nm(f, g) for f, g in r['authors'])
    f = {'author': names, 'title': tex(r['title']), 'date': r.get('date', str(r['year']))}
    if r.get('doi'): f['doi'] = r['doi']
    if r.get('url'): f['url'] = r['url']
    if t == 'article':
        etype = 'article'; f['journaltitle'] = tex(r['journal'])
        for k in ('volume', 'number', 'pages', 'eid'):
            if r.get(k): f[k] = r[k]
    elif t == 'inproceedings':
        etype = 'inproceedings'; f['booktitle'] = tex(r['booktitle'])
        for k in ('volume', 'pages', 'publisher', 'series'):
            if r.get(k): f[k] = tex(r[k])
    elif t == 'arxiv':
        etype = 'misc'; f['eprint'] = r['eprint']; f['eprinttype'] = 'arxiv'   # @misc keeps the year in biblatex-ieee
    elif t == 'dataset':
        etype = 'dataset'; f['publisher'] = r['publisher']; f['title'] = '{' + tex(r['title']) + '}'
        if r.get('titleaddon'): f['titleaddon'] = tex(r['titleaddon'])
    elif t == 'software':
        etype = 'software'; f['publisher'] = r['publisher']
    elif t == 'online':
        etype = 'misc'   # biblatex-ieee drops the year of @online entries
    elif t == 'report':
        etype = 'report'; f['institution'] = tex(r['institution']); f['type'] = r.get('reptype', 'Tech. Rep.') + ('\\isdot' if r.get('reptype', 'Tech. Rep.').endswith('.') else '')   # abbreviation dot: keeps the comma before the date
        if r.get('note'): f['note'] = tex(r['note'])
    order = ['author', 'date', 'title', 'titleaddon', 'journaltitle', 'booktitle', 'series', 'volume', 'number', 'pages', 'eid', 'publisher', 'institution', 'type', 'note', 'eprint', 'eprinttype', 'doi', 'url']
    body = ',\n'.join(f"  {k:<12} = {{{f[k]}}}" for k in order if k in f)
    return f"@{etype}{{{r['key']},\n{body}\n}}\n"

BSTCTL = """@IEEEtranBSTCTL{IEEEexample:BSTcontrol,
  CTLuse_forced_etal       = "yes",
  CTLmax_names_forced_etal = "6",
  CTLnames_show_etal       = "1",
  CTLdash_repeated_names   = "no"
}
"""

MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

def doi_tex(d):
    return f"doi: \\href{{https://doi.org/{d}}}{{\\nolinkurl{{{d}}}}}"

def bibtex_entry(r):
    """Classic BibTeX entry for IEEEtran.bst (v1.14), which has no doi/eid/dataset support:
    DOI -> note; article number -> 'Art. no.' appended to number (or volume); dataset -> @misc."""
    t = r['type']
    def nm(f, g):
        if ' ' in f and not f.split()[0].islower(): return f"{{{tex(f)}}}, {tex(g)}"
        return f"{tex(f)}, {tex(g)}"
    f = {'author': ' and '.join(nm(a, g) for a, g in r['authors']), 'title': tex(r['title']), 'year': str(r['year'])}
    notes = []
    if t == 'article':
        etype = 'article'; f['journal'] = tex(r['journal'])
        for k in ('volume', 'number', 'pages'):
            if r.get(k): f[k] = r[k]
        if r.get('eid'):
            slot = 'number' if 'number' in f else 'volume'
            f[slot] = f[slot] + ', Art.~no.~' + r['eid']
    elif t == 'inproceedings':
        etype = 'inproceedings'; f['booktitle'] = tex(r['booktitle'])
        for k in ('series', 'volume', 'pages', 'publisher'):
            if r.get(k): f[k] = tex(r[k])
    elif t == 'arxiv':
        etype = 'misc'; notes.append('arXiv:' + r['eprint'])
    elif t == 'dataset':
        etype = 'misc'; f['title'] = '{' + tex(r['title']) + '}'
        f['howpublished'] = ', '.join(x for x in (tex(r.get('titleaddon', '')), r['publisher']) if x)
        y, m, d = (r.get('date', '').split('-') + [None, None, None])[:3]
        if m: f['month'] = MONTHS[int(m) - 1] + (f' # "~{int(d)},"' if d else '')
    elif t == 'online':
        etype = 'misc'; f['url'] = r['url']
    elif t == 'report':
        etype = 'techreport'; f['institution'] = tex(r['institution'])
        if r.get('note'): notes.append(tex(r['note']))
    if r.get('doi'): notes.append(doi_tex(r['doi']))
    if notes: f['note'] = ', '.join(notes)
    if r.get('url') and t != 'online': f['url'] = r['url']
    order = ['author', 'title', 'journal', 'booktitle', 'howpublished', 'series', 'volume', 'number', 'pages',
             'publisher', 'institution', 'month', 'year', 'note', 'url']
    def val(k):
        v = f[k]
        return v if (k == 'month') else '{' + v + '}'
    body = ',\n'.join(f"  {k:<12} = {val(k)}" for k in order if k in f)
    e = f"@{etype}{{{r['key']},\n{body}\n}}\n"
    assert e.isascii(), (r['key'], [c for c in e if not c.isascii()])
    return e

def write_bib(path):
    with open(path, 'w', encoding='ascii') as fh:
        fh.write('% references.bib -- 35 sources for \\bibliographystyle{IEEEtran} (BibTeX). Journal and proceedings\n'
                 '% names are abbreviated per the IEEE Reference Guide. IEEEtran.bst has no doi/eid fields, so DOIs are\n'
                 '% given in "note" and article numbers as "Art. no." in number/volume. DOIs checked against\n'
                 '% Crossref/DataCite/arXiv; see reference_audit.md.\n'
                 '% The control entry below is activated by \\bstctlcite{IEEEexample:BSTcontrol} in term_paper.tex:\n'
                 '% "et al." after the first author when there are more than six authors; no dash for repeated authors.\n\n')
        fh.write(BSTCTL + '\n')
        for r in R:
            fh.write(bibtex_entry(r) + '\n')

def write_biblatex_bib(path):   # Phase 5a biblatex version, kept for reference
    with open(path, 'w', encoding='utf-8') as fh:
        for r in R:
            fh.write(bib_entry(r) + '\n')

def initials(given):
    parts = re.split(r'\s+', given.strip())
    out = []
    for p in parts:
        if p.endswith('.') and len(p) <= 3:          # "M." or "Md."
            out.append(p[0] + '.')
        elif '-' in p:
            out.append('-'.join(q[0] + '.' for q in p.split('-') if q))
        else:
            out.append(p[0] + '.')
    return ' '.join(out)

def apa_authors(auth):
    names = [f"{f}, {initials(g)}" for f, g in auth]
    if len(names) == 1: return names[0]
    if len(names) <= 20: return ', '.join(names[:-1]) + ', & ' + names[-1]
    return ', '.join(names[:19]) + ', . . . ' + names[-1]

def strip_braces(s):
    return s.replace('{', '').replace('}', '').replace("``", '\u201c').replace("''", '\u201d')

def pages(p): return p.replace('--', '\u2013')

def apa_reference(r, suffix=''):
    """Return list of (text, italic) runs."""
    a = apa_authors(r['authors']); y = f"({r['year']}{suffix}). "
    title = strip_braces(r['title']); runs = [(a + ' ' + y, False)]
    tp = '' if title.endswith('?') else '.'
    doi = f" https://doi.org/{r['doi']}" if r.get('doi') else ''
    t = r['type']
    if t == 'article':
        runs += [(title + tp + ' ', False), (r['journal'] + ', ' + r['volume'], True)]
        tail = ''
        if r.get('number'): tail += f"({r['number']})"
        if r.get('pages'): tail += ', ' + pages(r['pages'])
        elif r.get('eid'): tail += ', Article ' + r['eid']
        runs += [(tail + '.' + doi, False)]
    elif t == 'inproceedings':
        runs += [(title + tp + ' In ', False), (strip_braces(r['booktitle']), True)]
        pp = f" (pp. {pages(r['pages'])})" if r.get('pages') else ''
        runs += [(pp + '. ' + r.get('publisher', '') + '.' + doi, False)]
    elif t == 'arxiv':
        runs += [(title, True), (f" (arXiv:{r['eprint']}). arXiv.{doi}", False)]
    elif t == 'dataset':
        runs += [(title, True), (f" [Data set]. {r['publisher']}.{doi}", False)]
    elif t == 'software':
        runs += [(title, True), (f" [Computer software]. {r['publisher']}.{doi}", False)]
    elif t == 'online':
        runs += [(title, True), (f". {r['url']}", False)]
    return runs

def surname_list(r): return [f for f, g in r['authors']]

def cite_names(r, all_refs):
    """APA 7 in-text name part, disambiguating same-year 'et al.' collisions (APA 8.18)."""
    au = surname_list(r)
    if len(au) == 1: return au[0], au[0]
    if len(au) == 2: return f"{au[0]} & {au[1]}", f"{au[0]} and {au[1]}"
    # 3+ authors: check collision with other refs sharing first author + year but different author list
    n = 1
    for o in all_refs:
        if o is r or o['year'] != r['year']: continue
        ou = surname_list(o)
        if ou[0] == au[0] and ou != au and len(ou) >= 3:
            k = 1
            while k < min(len(au), len(ou)) and au[k] == ou[k]: k += 1
            n = max(n, k + 1)
    if n == 1: return f"{au[0]} et al.", f"{au[0]} et al."
    head = ', '.join(au[:n]); return f"{head}, et al.", f"{head}, et al."

def year_suffixes(all_refs):
    """a/b suffix for identical author lists in the same year, ordered by title (APA 9.47)."""
    suf = {}
    groups = {}
    for r in all_refs:
        groups.setdefault((tuple(surname_list(r)), r['year']), []).append(r)
    for g in groups.values():
        if len(g) > 1:
            def sortkey(x):
                t = strip_braces(x['title']).lower()
                return re.sub(r'^(the|a|an)\s+', '', t)
            for i, r in enumerate(sorted(g, key=sortkey)):
                suf[r['key']] = 'abcdefgh'[i]
    return suf

def sort_key(r):
    """APA alphabetical order: surname (prefix included, as biblatex-apa does), then initials, then year, then title."""
    au = [(f.lower().replace("'", ''), initials(g)) for f, g in r['authors']]
    return (au, r['year'], strip_braces(r['title']).lower())

BYKEY = {r['key']: r for r in R}
SUFFIX = year_suffixes(R)

def intext(keys, narrative=False):
    parts = []
    if not narrative:
        keys = sorted(keys, key=lambda k: sort_key(BYKEY[k]))
    for k in keys:
        r = BYKEY[k]; paren, narr = cite_names(r, R); yr = f"{r['year']}{SUFFIX.get(k, '')}"
        parts.append(f"{narr} ({yr})" if narrative else f"{paren}, {yr}")
    if narrative: return ' and '.join(parts) if len(parts) <= 2 else ', '.join(parts[:-1]) + ', and ' + parts[-1]
    return '(' + '; '.join(parts) + ')'

# ---------- IEEE strings (for Word; mirror biblatex-ieee output) ----------
def ieee_name(f, g):
    return f"{initials(g)} {f}"

def ieee_authors(auth):
    if len(auth) > 6: return ieee_name(*auth[0]) + ' et al.'
    n = [ieee_name(f, g) for f, g in auth]
    if len(n) == 1: return n[0]
    if len(n) == 2: return n[0] + ' and ' + n[1]
    return ', '.join(n[:-1]) + ', and ' + n[-1]

def _grp(n):   # biblatex-ieee groups numbers of five or more digits with a thin space
    return re.sub(r'\d{5,}', lambda m: f"{int(m.group(0)):,}".replace(',', '\u2009'), n)

def ieee_reference(r):
    """(text, italic) runs that reproduce biblatex-ieee's output for our entry types."""
    a = ieee_authors(r['authors']).replace("'", '\u2019'); title = strip_braces(r['title'])
    doi = f" doi: {r['doi']}." if r.get('doi') else ''
    t = r['type']; yr = str(r['year'])
    q = title[-1] in '?!'
    def quoted(after):   # “Title,” in  /  “Title?” In
        return [(f"{a}, \u201c{title}{'' if q else ','}\u201d {after[0].upper() + after[1:] if q else after}", False)]
    if t == 'article':
        tail = f", vol. {r['volume']}"
        if r.get('number'): tail += f", no. {r['number']}"
        if r.get('pages'): tail += f", pp. {_grp(pages(r['pages']))}"
        elif r.get('eid'): tail += f", {r['eid']}"
        return quoted('') + [(r['journal'], True), (tail + f", {yr}." + doi, False)]
    if t == 'inproceedings':
        tail = ''
        if r.get('volume'): tail += f", vol. {r['volume']}"
        if r.get('series'): tail += f", ser. {r['series']}"
        if r.get('publisher'): tail += f", {r['publisher']}"
        tail += f", {yr}"
        if r.get('pages'): tail += f", pp. {_grp(pages(r['pages']))}"
        return quoted('in ') + [(strip_braces(r['booktitle']), True), (tail + '.' + doi, False)]
    if t == 'arxiv':
        return [(f"{a}, ", False), (title, True), (f", {yr}." + doi + f" arXiv: {r['eprint']}.", False)]
    if t == 'online':
        return [(f"{a}, ", False), (title, True), (f", {yr}. [Online]. Available: {r['url']}.", False)]
    if t == 'dataset':
        # IEEE Reference Guide, datasets: Author, Date, "Title of Dataset," Source, doi
        MON = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']
        dt = r.get('date', yr); y_, m_, d_ = (dt.split('-') + [None, None])[:3]
        ds = f"{MON[int(m_) - 1]} {int(d_)}, {y_}" if d_ else (f"{MON[int(m_) - 1]} {y_}" if m_ else y_)
        add = f" ({r['titleaddon']})" if r.get('titleaddon') else ''
        if add: return [(f"{a}, {ds}, \u201c{title}\u201d{add}, {r['publisher']}." + doi, False)]
        return [(f"{a}, {ds}, \u201c{title},\u201d {r['publisher']}." + doi, False)]
    if t == 'report':
        return quoted('') [:0] + [(f"{a}, \u201c{title},\u201d {r['institution']}, {r.get('reptype', 'Tech. Rep.')}, {yr}" + (f", {r['note']}" if r.get('note') else '') + "." + doi, False)]
    raise ValueError(t)

def ieee_names(k, cap=False):
    """Narrative name part as biblatex-ieee \\textcite prints it (maxcitenames = 2)."""
    au = surname_list(BYKEY[k])
    s = au[0] if len(au) == 1 else (f"{au[0]} and {au[1]}" if len(au) == 2 else f"{au[0]} et al.")
    return s[0].upper() + s[1:] if cap else s

if __name__ == '__main__':
    write_bib('/home/user/work/paper/references.bib')
    for r in sorted(R, key=sort_key):
        print(''.join(t for t, i in apa_reference(r, SUFFIX.get(r['key'], ''))))
    print(intext(['promisenfr2007', 'clelandhuang2007', 'lucassen2016qus', 'lucassen2016use', 'hey2020norbert', 'hey2020supp']))
    print(intext(['kurtanovic2017'], True), intext(['scrumguide2020']))
