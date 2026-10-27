import re, pathlib, sys
TEX = pathlib.Path.home() / 'mnt' / 'Microgrids_paper_v2' / 'AAMain.tex'
class Ed:
    def __init__(self): self.s = TEX.read_text(); self.log = []
    def rep(self, old, new, count=1):
        n = self.s.count(old)
        if n != count: raise SystemExit(f'anchor found {n}x (expected {count}): {old[:90]!r}')
        self.s = self.s.replace(old, new); self.log.append(old[:60])
    def between(self, start, end, new, keep_end=False):
        i = self.s.find(start); j = self.s.find(end, i)
        if i < 0 or j < 0 or self.s.count(start) != 1: raise SystemExit(f'between anchors not found/unique: {start[:60]!r} .. {end[:60]!r}')
        j2 = j if keep_end else j + len(end)
        self.s = self.s[:i] + new + self.s[j2:]; self.log.append('between:' + start[:50])
    def resub(self, pat, new, count=1):
        s2, n = re.subn(pat, new, self.s, count=count)
        if n != count: raise SystemExit(f'regex matched {n}: {pat[:80]}')
        self.s = s2; self.log.append('re:' + pat[:50])
    def save(self):
        TEX.write_text(self.s); print('\n'.join(self.log)); print('saved', TEX)
