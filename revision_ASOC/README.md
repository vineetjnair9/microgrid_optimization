# Revision for Applied Soft Computing (ASOC-D-26-10040)

Code, inputs and results behind the revised manuscript "Multiobjective optimization-based design and
dispatch of islanded, hybrid microgrids for remote, off-grid communities in sub-Saharan Africa".
The original MATLAB models are in the repository root; everything added or corrected for the revision is here.

| Folder | Contents |
| --- | --- |
| `matlab/` | Corrected sizing objective (`obj_sizing.m`), day-ahead dispatch (`dispatch_obj.m`, `run_dispatch.m`), benchmark, Monte Carlo scenario evaluation, and `job_daemon.m`, which runs job scripts dropped into `jobs/` |
| `jobs/done/` | Every MATLAB job that produced a result file, time-stamped (the `L` series is the final, corrected run) |
| `results/` | Result files used in the paper (`stale_*` folders are superseded runs kept for the record) |
| `python/` | Statistics, Pareto selection, Monte Carlo analysis, figures, and the scripts that build the manuscript text and response letter |
| `data/` | NASA POWER data for the site, the Natural Earth map subset, manuscript snapshots |
| `figures/` | All figures of the paper (PDF for print, PNG for preview) |

## Reproducing the results

1. MATLAB R2026a with the Optimization and Global Optimization Toolboxes: in `matlab/`, run `job_daemon` and copy a
   job script from `jobs/done/` (without its time stamp) into `jobs/`. The daemon writes results to `results/` and a
   log to `logs/`. Random seeds are set inside each job.
2. Python 3.10 or later with numpy, pandas, scipy and matplotlib:
   - `python3 benchmark_stats.py`, `pareto_select.py`, `mc_analysis.py`, `wind_validation.py`: statistics and tables
   - `python3 figures_final.py`: every figure of the paper, in one style, at printed size
   - `python3 dispatch_metrics.py`: checks that the Python cost model of a daily schedule reproduces `dispatch_obj.m`

## Rebuilding the manuscript (author workflow)

`python/apply_text_pipeline.sh` rebuilds `AAMain.tex` from the pre-revision snapshot by applying the scripted
stages B to H in order, so every number in the text comes from a result file. `build_response.py` builds the
response letter, `qa_checks.py` runs the consistency checks and `make_diff.sh` produces the marked-up version.
