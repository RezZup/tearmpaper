# -*- coding: utf-8 -*-
"""LaTeX -> native Word equation (OMML) via pandoc, with an on-disk cache.

The cache (omml_cache.json) means later rebuilds do not need pandoc
(pip install pypandoc_binary provides it when the cache is cold).
"""
import hashlib, json, os, re, tempfile, zipfile

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'omml_cache.json')


def _load():
    return json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}


def latex_to_omml(latex):
    """Return the XML string of an <m:oMathPara> element for display math."""
    cache = _load(); key = hashlib.sha1(latex.encode()).hexdigest()
    if key in cache: return cache[key]
    import pypandoc
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'eq.docx')
        pypandoc.convert_text('$$' + latex + '$$', 'docx', format='markdown', outputfile=out)
        xml = zipfile.ZipFile(out).read('word/document.xml').decode('utf-8')
    m = re.search(r'<m:oMathPara\b.*?</m:oMathPara>', xml, re.S)
    if not m: raise RuntimeError('pandoc produced no OMML for: ' + latex)
    cache[key] = m.group(0); json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    return m.group(0)


def omml_inline(latex):
    """Inline equation: the <m:oMath> element inside the display paragraph."""
    x = latex_to_omml(latex)
    return re.search(r'<m:oMath\b.*?</m:oMath>', x, re.S).group(0)
