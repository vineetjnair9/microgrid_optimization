#!/bin/bash
# Rebuild AAMain.tex from the stage-A snapshot + all scripted stages (re-runnable when results change).
set -e
cd "$(dirname "$0")"
MS="$HOME/mnt/Microgrids_paper_v2/AAMain.tex"
cp "$MS" ../data/AAMain_before_pipeline_$(date +%Y%m%d_%H%M%S).tex
cp ../data/AAMain_backup_before_stageB.tex "$MS"
for s in stageB_sizing stageB_sens stageC_text stageC2_wind_eq stageC3_battery stageC4_dispatchrule stageD_weights stageD_secs78 stageD_pareto stageD_wind stageD_misc stageD_bench stageE_front stageF_sources stageF_reread stageF_so2 reorder_bib "$@"; do echo "== $s"; python3 $s.py | tail -1; done
