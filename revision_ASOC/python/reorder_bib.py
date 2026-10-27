"""Reorder the inline thebibliography so numbering follows order of first citation; report uncited items."""
import re, pathlib
TEX = pathlib.Path.home() / 'mnt' / 'Microgrids_paper_v2' / 'AAMain.tex'
s = TEX.read_text()
body, bib = s.split(r'\begin{thebibliography}', 1)
head_bib, rest = bib.split('\n', 1)
items_txt, tail = rest.split(r'\end{thebibliography}', 1)
pre = items_txt[:items_txt.index(r'\bibitem')]
chunks = re.split(r'(?=\\bibitem\{)', items_txt[items_txt.index(r'\bibitem'):])
items = {re.match(r'\\bibitem\{([^}]*)\}', c).group(1): c.rstrip() + '\n\n' for c in chunks if c.strip()}
nocomment = '\n'.join(re.split(r'(?<!\\)%', l)[0] for l in body.split('\n'))
order = []
for m in re.finditer(r'\\cite[pt]?\*?(?:\[[^\]]*\])?\{([^}]*)\}', nocomment):
    for k in m.group(1).split(','):
        k = k.strip()
        if k and k not in order: order.append(k)
missing = [k for k in order if k not in items]; uncited = [k for k in items if k not in order]
new_items = ''.join(items[k] for k in order if k in items)  # uncited items are dropped
TEX.write_text(body + r'\begin{thebibliography}' + head_bib + '\n' + pre + new_items + r'\end{thebibliography}' + tail)
print('cited', len(order), 'items', len(items), 'missing bibitems:', missing, 'uncited (dropped):', uncited)
