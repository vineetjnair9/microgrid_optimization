import re, json, pathlib
txt = (pathlib.Path.home() / 'mnt' / 'MG paper' / 'ASOC_revision_runbook' / 'reviews_verbatim.txt').read_text()
r1 = txt.split('Reviewer 1 - Initial submission, 29/07/2026')[1].split('Reviewer 2\n')[0]
r2 = txt.split('Reviewer 2 - Initial submission, 31/07/2026')[1]
def clean(s): return re.sub(r'\s+', ' ', s.replace('multiobjective optimal', 'multiobjective optimal')).strip()
r1 = clean(r1)
marks = ['The main concern is the level', 'The algorithm comparison also requires', 'The treatment of multiobjective optimization',
         'Another limitation concerns the robustness', 'Similarly, the use of perfect foresight', 'Overall, the study is technically']
idx = [r1.index(m) for m in marks]
R1 = {'intro': r1[:idx[0]].strip()}
for k in range(5): R1[f'R1.{k+1}'] = r1[idx[k]:idx[k+1]].strip()
R1['closing'] = r1[idx[5]:].strip()
r2 = clean(r2)
pos = [r2.index(f'{k}.') if k > 1 else r2.index('1.Two stage') for k in range(1, 12)]
pos = []
start = 0
for k in range(1, 12):
    m = re.search(rf'(?<![\d.]){k}\.(?=[A-Z])', r2[start:]); pos.append(start + m.start()); start = pos[-1] + 2
R2 = {'intro': r2[:pos[0]].strip()}
for k in range(11):
    seg = r2[pos[k]:(pos[k+1] if k < 10 else len(r2))].strip()
    R2[f'R2.{k+1}'] = re.sub(rf'^{k+1}\.', '', seg).strip()
out = {**{k: v for k, v in R1.items()}, **{('R2_' + k if k == 'intro' else k): v for k, v in R2.items()}}
json.dump(out, open(pathlib.Path(__file__).parent.parent / 'results' / 'reviews_split.json', 'w'), indent=1)
for k, v in out.items(): print(k, '|', v[:90], '...', v[-50:])
