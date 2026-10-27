"""Stage D: Sec. 5.1 solver benchmark from results/benchmark_intcoded (+ relax-and-round variant in results/benchmark)."""
from texedit import Ed
from common import RES
import pandas as pd, numpy as np, shutil, pathlib
MS = pathlib.Path.home() / 'mnt' / 'Microgrids_paper_v2'
B = RES / 'benchmark_intcoded'; S = pd.read_csv(B / 'stats_table.csv').set_index('solver'); P = pd.read_csv(B / 'tests.csv').set_index('solver')
K = dict(l.split(' = ') for l in open(B / 'key_numbers.txt').read().splitlines())
D = pd.read_csv(B / 'summary.csv'); RI = dict(l.split(' = ') for l in open(RES / 'run_info.txt').read().splitlines())
N = {'PSO': 'PSO', 'GA': 'GA', 'SA': 'SA', 'SO': 'SO', 'MS': 'MS', 'GS': 'GS', 'DPS': 'DPS', 'PSOPS': 'PSO+PS'}
fstar = float(K['BENCH_FSTAR']); nruns = int(K['BENCH_NRUNS']); ref = [k for k, v in N.items() if v == K['BENCH_BEST_SOLVER']][0]
full = [N[s] for s in S.index if S.loc[s, 'success'] >= 0.999]
part = [f"{N[s]} ({S.loc[s,'success']*100:.0f}\\%)" for s in S.index if 0 < S.loc[s, 'success'] < 0.999]
none = [N[s] for s in S.index if S.loc[s, 'success'] == 0]
fin = S[np.isfinite(S.ERT_s)].sort_values('ERT_s')
ms_eval = (D.wall_search_s / D.evals_search.clip(lower=1)).median() * 1000
sig = [N[s] for s in P.index if P.loc[s, 'p_holm'] < 0.05]; nsig = [N[s] for s in P.index if P.loc[s, 'p_holm'] >= 0.05]
def lst(L): return L[0] if len(L) == 1 else ', '.join(L[:-1]) + ' and ' + L[-1] if L else 'none'
rr_txt = ''
RR = RES / 'benchmark' / 'summary.csv'
if RR.exists():
    R = pd.read_csv(RR); fs = 1.005 * fstar
    pso_rr = R[R.solver == 'PSO']; pso_ic = D[D.solver == 'PSO']
    ga_rr = R[R.solver == 'GA']; ga_ic = D[D.solver == 'GA']
    rr_txt = (f" We also ran PSO and GA on the continuous relaxation, rounding only the final point (relax-and-round with the same polish, {pso_rr.seed.nunique()} seeds each). "
        f"On this problem the choice matters little: PSO reaches the target in {(pso_rr.J_int <= fs).mean()*100:.0f}\\% of runs either way, and GA in {(ga_rr.J_int <= fs).mean()*100:.0f}\\% with relax-and-round against {(ga_ic.J_int <= fs).mean()*100:.0f}\\% with integer coding, because the optimum has no wind turbines and is flat in $n_s$.")
ref_med_evals = S.loc[ref, 'med_evals']
m_, e_ = f"{float(K['BENCH_KW_P']):.1e}".split('e'); ptex = f"{m_} \\times 10^{{{int(e_)}}}"
neg = [s_ for s_ in P.index if P.loc[s_, 'p_holm'] < 0.05 and S.loc[s_, 'success'] >= 0.999]
big = [s_ for s_ in P.index if P.loc[s_, 'p_holm'] < 0.05 and s_ not in neg]
medgap = max(abs(S.loc[s_, 'median'] / fstar - 1) * 100 for s_ in neg + [ref]) if neg else 0
sig_txt = (f"Holm-corrected Mann--Whitney tests against {N[ref]}, the solver with the lowest median, " + (f"find no significant difference for {lst(nsig)} and " if nsig else "") + f"detect differences for {lst(sig)} (\\cref{{tab:bench_tests}}), but these differ greatly in size. "
    + (f"For {lst([N[x] for x in neg])} the median final objective lies within {max(medgap, 0.001):.3f}\\% of $f^*$, as for {N[ref]}, so the difference is far below any practical tolerance; " if neg else "")
    + (f"for {lst([N[x] for x in big])} the differences are large, with {N[ref]} ending lower in " + ('every pairwise comparison' if min(P.loc[x, 'P_ref_better'] for x in big) > 0.995 else f"at least {min(P.loc[x, 'P_ref_better'] for x in big)*100:.0f}\\% of pairwise comparisons") + "." if big else ""))
EXM = pd.read_csv(RES / 'benchmark' / 'exhaustive_int_bestJ.csv', header=None).to_numpy(); ii, jj = np.where(EXM <= 1.005 * fstar)
EX_ns, EX_nw = ii, jj   # rows: n_s = 0..400, cols: n_w = 0..40
nw_txt = 'no wind turbines' if EX_nw.max() == 0 else f'{EX_nw.min()}--{EX_nw.max()} wind turbines'
pso_ok = S.loc['PSO', 'success'] >= 0.999; pso_rank = list(fin.index).index('PSO') + 1 if 'PSO' in fin.index else None
pso_txt = (f"Based on these results we use integer-coded PSO for all subsequent sizing results (best of ten seeds with the integer polish): it reaches the target in every run" + (" with the lowest expected running time." if pso_rank == 1 else f", with the {['','','second','third','fourth'][pso_rank] if pso_rank and pso_rank < 5 else ''} lowest expected running time ({S.loc['PSO','ERT_s']:.1f}~s).")) if pso_ok else \
    f"PSO reaches the target in {S.loc['PSO','success']*100:.0f}\\% of runs; we use it for the subsequent sizing results with the best of ten seeds and the integer polish, which recovers $f^*$ in our runs."
new = rf'''\subsection{{Comparison of solution algorithms for MG planning and design optimization}}

The sizing objective is non-smooth: the hourly simulation switches the DE on and off, counts battery cycles and schedules replacements, so the objective has steps and kinks even when $n_s$ and $n_w$ are relaxed to continuous values, and gradient-based solvers can stall on flat or stepped regions. We therefore compare global solvers from MATLAB's Global Optimization Toolbox on the base LI+DE problem (16~kW DE, equal weights $w_i = 0.2$). The comparison follows standard practice for benchmarking stochastic optimizers \cite{{hansen2021coco, derrac2011tutorial}}: every solver receives the same budget of 2,000 objective evaluations, counted by a wrapper around the objective, and runs {nruns} times with independent random seeds (\cref{{tab:protocol}}). All solvers use MATLAB's default settings, reflecting how a practitioner would apply them. The integer variables are handled by integer coding: $n_s$ and $n_w$ are rounded inside the objective, so every evaluated point is a feasible design. After the search, a local polish evaluates the four integer neighbours of the best point and re-optimizes $E_{{b,\;init}}$ for each with Brent's method; these evaluations (at most 80) count toward the budget. The bounds are $[0, 0, 0]$ and $[400, 40, 400]$.

\begin{{table}}[htbp]
\centering
\scriptsize
\begin{{tabular}}{{p{{2.6cm}} p{{2.3cm}} p{{7.4cm}}}}
\toprule
\textbf{{Solver}} & \textbf{{MATLAB function}} & \textbf{{Settings (defaults unless stated)}} \\
\midrule
Particle swarm (PSO) & \texttt{{particleswarm}} & swarm size 30; stops at the budget or on its default stall criterion \\
Genetic algorithm (GA) & \texttt{{ga}} & population 50; stops at the budget or on default criteria \\
Simulated annealing (SA) & \texttt{{simulannealbnd}} & random start point; \texttt{{MaxFunctionEvaluations}} = budget \\
Surrogate optimization (SO) & \texttt{{surrogateopt}} & \texttt{{MaxFunctionEvaluations}} = budget \\
MultiStart (MS) & \texttt{{MultiStart}} + \texttt{{fmincon}} & active-set local solver; up to 1,000 random start points; stopped at the budget \\
GlobalSearch (GS) & \texttt{{GlobalSearch}} + \texttt{{fmincon}} & active-set local solver; 400 trial points, 100 stage-one points \\
Pattern search (DPS) & \texttt{{patternsearch}} & complete poll; restarted from random points until the budget is spent \\
PSO + pattern search & \texttt{{particleswarm}}, \texttt{{patternsearch}} & PSO for 80\% of the budget, then pattern search from the best point \\
\midrule
All & & budget 2,000 evaluations including the integer polish; {nruns} seeds (1--{nruns}); integer-coded $n_s, n_w$; serial evaluation; {RI['matlab'].split('(')[1].split(')')[0]} on an {RI['cpu']} ({RI['mem_GB']}~GB) \\
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:protocol}} Benchmark protocol.}}
\end{{table}}

We score each run by the objective of its final integer design and compare it with the best integer design $f^* = {fstar:.5f}$, found by exhaustive enumeration of all $401 \times 41$ combinations of $n_s$ and $n_w$ with $E_{{b,\;init}}$ optimized for each (grid search followed by Brent's method). A run succeeds if it ends within 0.5\% of $f^*$. The expected running time (ERT) is the total number of evaluations over all runs divided by the number of successful runs \cite{{hansen2021coco}}; it rewards solvers that succeed often and cheaply, and is infinite for a solver that never succeeds. We test for differences between solvers with the Kruskal--Wallis test and then compare each solver with the best-ranked one using two-sided Mann--Whitney tests with Holm correction and the Vargha--Delaney effect size $\hat{{A}}_{{12}}$ \cite{{derrac2011tutorial, vargha2000a12}}. These measures replace the product of runtime and objective value used in the submitted version, which mixed units and rewarded speed regardless of solution quality.

\begin{{table}}[htbp]
\centering
\scriptsize
\setlength{{\tabcolsep}}{{4pt}}
\input{{rev_bench_stats.tex}}
\caption{{\label{{tab:bench_stats}} Final objective of the integer design over {nruns} runs per solver (budget 2,000 evaluations), success rate (within 0.5\% of $f^* = {fstar:.5f}$) and expected running time to that target, in evaluations and seconds. Solvers are ordered by median.}}
\end{{table}}

\begin{{table}}[htbp]
\centering
\scriptsize
\input{{rev_bench_tests.tex}}
\caption{{\label{{tab:bench_tests}} Pairwise two-sided Mann--Whitney tests of each solver against {N[ref]}, with Holm-corrected $p$-values and the probability $\hat{{P}}$ that a run of {N[ref]} ends with a lower objective (Vargha--Delaney $1-\hat{{A}}_{{12}}$, ties counted as one half).}}
\end{{table}}

\begin{{figure}}[htbp]
  \centering
  \begin{{subfigure}}[b]{{0.49\linewidth}}
    \includegraphics[width=\linewidth]{{rev_benchmark_box.pdf}}
    \caption{{\label{{fig:bench_box}}}}
  \end{{subfigure}}
  \begin{{subfigure}}[b]{{0.49\linewidth}}
    \includegraphics[width=\linewidth]{{rev_benchmark_convergence.pdf}}
    \caption{{\label{{fig:bench_conv}}}}
  \end{{subfigure}}
  \caption{{\label{{fig:solver_comp}} (a) Final objective of each run (dashed line: $f^*$ + 0.5\%); (b) median best-so-far gap to $f^*$ against evaluations, with interquartile bands; PSO and PSO+PS share their first 80\% of evaluations and their curves coincide.}}
\end{{figure}}

\cref{{tab:bench_stats}} and \cref{{fig:solver_comp}} summarize the results. The Kruskal--Wallis test rejects equal performance across solvers ($H = {K['BENCH_KW_H']}$, $p = {ptex}$). {lst(full)} reach the target in every run; {('' if not part else lst(part) + ' succeed in some runs; ')}{('' if not none else lst(none) + ' never reach it.')} {sig_txt} Among the solvers that reach the target, the expected running time is lowest for {N[fin.index[0]]} ({fin.ERT_evals.iloc[0]:,.0f} evaluations, {fin.ERT_s.iloc[0]:.1f}~s), followed by {N[fin.index[1]]} ({fin.ERT_evals.iloc[1]:,.0f}, {fin.ERT_s.iloc[1]:.1f}~s); surrogate optimization is reliable but spends most of its time fitting the surrogate, so its ERT in seconds is the highest ({S.loc['SO','ERT_s']:.1f}~s). PSO stops on its own stall criterion after a median of {S.loc['PSO','med_evals']:,.0f} evaluations, well within the budget. The gradient-based multistart methods perform worst, as expected on a stepped objective: their local solver stops on flat regions. The integer optimum is not unique in practice: {int((pd.read_csv(RES / 'benchmark' / 'exhaustive_int_bestJ.csv', header=None).to_numpy() <= 1.005*fstar).sum())} integer designs lie within 0.5\% of $f^*$, with {nw_txt} and {EX_ns.min()}--{EX_ns.max()} PV modules, so solvers that succeed may end at slightly different designs with practically the same objective.{rr_txt}

One evaluation of the 8,760-hour simulation takes about {ms_eval:.1f}~ms on the hardware of \cref{{tab:protocol}}, so a full PSO run takes a few seconds. The rule-based dispatch inside the simulation is what keeps evaluations this cheap; an inner optimization of hourly dispatch would multiply the cost of every evaluation. {pso_txt}

'''
e = Ed()
if 'All these results were obtained using a Dell XPS 15 9560' in e.s:
    i0 = e.s.index('All these results were obtained using a Dell XPS 15 9560'); j0 = e.s.index('\n', i0)
    e.s = e.s[:i0] + f"All results in this revision were obtained with MATLAB {RI['matlab'].split('(')[1].split(')')[0]} on an {RI['cpu']} with {RI['mem_GB']}~GB of memory, without parallel evaluation." + e.s[j0:]
e.between(r'\subsection{Comparison of solution algorithms for MG planning and design optimization}', r'\subsection{Sizing results}', new, keep_end=True)
e.save()
shutil.copy(B / 'stats_table.tex', MS / 'rev_bench_stats.tex'); shutil.copy(B / 'tests.tex', MS / 'rev_bench_tests.tex')
