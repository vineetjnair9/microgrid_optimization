"""Build MS_DIR/Response_ASOC-D-26-10040.tex from response_src.tex.
<<VERBATIM:ID>> -> reviewer text from results/reviews_split.json (LaTeX-escaped)
<<KEY>> -> value from any results/**/key_numbers.txt or results/letter_values.txt; else \\ph{KEY}"""
import json, re, subprocess
from common import RES, MS_DIR, REV
src = (REV / 'python' / 'response_src.tex').read_text()
rev = json.loads((RES / 'reviews_split.json').read_text())
def esc(s):
    s = re.sub(r'\s+', ' ', s).strip()
    for a, b in [('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'), ('_', r'\_'), ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'), ('^', r'\^{}')]:
        s = s.replace(a, b)
    s = s.replace('⋅', r'$\cdot$').replace('−', '--').replace('“', '``').replace('”', "''").replace('’', "'").replace('≈', r'$\approx$').replace('‘', '`').replace('×', r'$\times$').replace('–', '--').replace('→', r'$\rightarrow$')
    return s
vals = {}
for f in sorted(RES.rglob('key_numbers.txt')) + [RES / 'letter_values.txt']:
    if 'stale' in str(f) or not f.exists(): continue
    for line in f.read_text().splitlines():
        if ' = ' in line:
            k, v = line.split(' = ', 1); vals[k.strip()] = v.strip()
missing = []
import pathlib
AUX = (pathlib.Path.home() / 'build' / 'AAMain.aux').read_text(errors='ignore')
LBL = {m.group(1): m.group(2).replace('Appendix\\nobreakspace  {}', '').replace('Appendix\\nobreakspace {}', '') for m in re.finditer(r'\\newlabel\{([^}]*)\}\{\{((?:[^{}]|\{\})*)\}', AUX)}
def refname(lab):
    n = LBL.get(lab)
    if n is None: missing.append('REF:' + lab); return r'\ph{' + lab + '}'
    n = re.sub(r'Appendix\\nobreakspace\s*\{\}', '', n).strip()
    if lab.startswith('app:'): return 'Appendix~' + n
    return n
def cref(lab):
    n = refname(lab)
    pre = {'sec': 'Section~', 'fig': 'Fig.~', 'tab': 'Table~', 'eq': 'Eq.~', 'app': '', 'chap': 'Section~'}.get(lab.split(':')[0], '')
    return pre + (f'({n})' if lab.startswith('eq:') else n)
TEXMS = (MS_DIR / 'AAMain.tex').read_text()
def quote(anchor):
    i = TEXMS.find(anchor)
    if i < 0: missing.append('QUOTE:' + anchor[:30]); return r'\ph{QUOTE}'
    t = TEXMS[i:i + 1500].split('\n\n')[0]
    sents = re.split(r'(?<=[.])\s+(?=[A-Z\\(])', t)
    q = ''; 
    for s_ in sents:
        if len(q) > 250: break
        q += (' ' if q else '') + s_
    q = re.sub(r'~?\\cite[pt]?\{[^}]*\}', '', q)
    q = re.sub(r'\\[cC]ref\{([^}]*)\}', lambda m: ' and '.join(cref(x.strip()) for x in m.group(1).split(',')), q)
    q = re.sub(r'\\ref\{([^}]*)\}', lambda m: refname(m.group(1)), q)
    q = re.sub(r'\\label\{[^}]*\}', '', q)
    q = re.sub(r'\s+([:;,.)])', r'\1', q)
    if q.count('{') != q.count('}'): q = re.sub(r'[{}]', '', q)
    return '``' + q.strip() + "''"
def sub(m):
    k = m.group(1)
    if k.startswith('VERBATIM:'): return esc(rev[k.split(':', 1)[1]])
    if k.startswith('REF:'): return refname(k[4:])
    if k.startswith('QUOTE:'): return quote(k[6:])
    if k in vals: return vals[k]
    missing.append(k); return r'\ph{' + k + '}'
out = re.sub(r'<<([^<>]+?)>>', sub, src)
dst = MS_DIR / 'Response_ASOC-D-26-10040.tex'
dst.write_text(out)
print('missing keys:', sorted(set(missing)))
print('remaining \\ph:', len(re.findall(r'\\ph\{', out.split('\\begin{document}')[1])))
r = subprocess.run('cd "%s" && pdflatex -interaction=nonstopmode Response_ASOC-D-26-10040.tex >/dev/null; pdflatex -interaction=nonstopmode Response_ASOC-D-26-10040.tex >/dev/null; grep -n "^!" Response_ASOC-D-26-10040.log | head; grep -c rcomment Response_ASOC-D-26-10040.tex' % MS_DIR, shell=True, capture_output=True, text=True)
print(r.stdout, r.stderr)
