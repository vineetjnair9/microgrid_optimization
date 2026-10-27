import re, pathlib, subprocess, json
MS = pathlib.Path.home() / 'mnt' / 'Microgrids_paper_v2'; s = (MS / 'AAMain.tex').read_text()
nc = '\n'.join('' if l.strip().startswith('%') else l for l in s.split('\n'))
res = {}
res['placeholders'] = re.findall(r'\{\{[^}]*\}\}|\\ph\{|\\todo|TODO|XXX', nc)
labels = re.findall(r'\\label\{([^}]*)\}', nc); refs = sum([r.split(',') for r in re.findall(r'\\c?ref\{([^}]*)\}', nc)], [])
res['undefined_refs'] = sorted(set(r.strip() for r in refs) - set(labels)); res['dup_labels'] = sorted(set(l for l in labels if labels.count(l) > 1))
banned = ['first-ever', 'for the first time', 'to the best of our knowledge, the first', 'best suited', 'consistently outperform', 'across all trials', 'equally optimal', 'same value of the objective function', 'Overall = ']
res['banned'] = [b for b in banned if b.lower() in nc.lower()]
figs = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}', nc); res['missing_figs'] = [f for f in figs if not (MS / f).exists()]
hl = re.search(r'\\begin\{highlights\}(.*?)\\end\{highlights\}', nc, re.S).group(1)
res['highlight_lengths'] = [len(h.strip()) for h in hl.split(r'\item')[1:]]
LOGP = pathlib.Path.home() / 'build' / 'AAMain.log'; log = LOGP.read_text(errors='ignore') if LOGP.exists() else ''
res['latex_undefined'] = sorted(set(re.findall(r"(?:Reference|Citation) `([^']*)' .*undefined", log)))
res['latex_errors'] = re.findall(r'^! .*', log, re.M)[:10]
for k, v in res.items(): print(k, ':', v)
