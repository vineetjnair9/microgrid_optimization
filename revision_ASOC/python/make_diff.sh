#!/bin/bash
# Marked-up manuscript (stage H): latexdiff of the submitted version against the revision.
# Settings as in STATUS_LOG (stage G): UNDERLINE, new graphics only, default math markup, tables and (stage H) figures treated as
# pictures (latexdiff cannot mark up inside them and still compile), and the new bibliography unmarked
# (the reordered bibliography breaks the diff).
# Usage: bash make_diff.sh [MS_DIR]   (needs latexdiff >= 1.3 and pdflatex)
set -e
MS="${1:-$HOME/mnt/Microgrids_paper_v2}"
cd "$MS"
latexdiff --type=UNDERLINE --graphics-markup=new-only \
  --config="PICTUREENV=(?:picture|DIFnomarkup|tabular|longtable|figure)[\w\d*@]*" \
  AAMain_ASOC_submitted.tex AAMain.tex > AAMain_diff_ASOC.tex
python3 - <<'EOF'
import re
d = open('AAMain_diff_ASOC.tex').read(); n = open('AAMain.tex').read()
nb = n[n.index(r'\begin{thebibliography}'):n.index(r'\end{thebibliography}') + len(r'\end{thebibliography}')]
i = d.index(r'\begin{thebibliography}'); j = d.index(r'\end{thebibliography}') + len(r'\end{thebibliography}')
open('AAMain_diff_ASOC.tex', 'w').write(d[:i] + nb + d[j:])
print('bibliography replaced by the unmarked new one')
EOF
for k in 1 2; do pdflatex -interaction=nonstopmode AAMain_diff_ASOC.tex > /dev/null 2>&1 || true; done
grep -nE "^!" AAMain_diff_ASOC.log | head -5 || true
pdfinfo AAMain_diff_ASOC.pdf | grep Pages
