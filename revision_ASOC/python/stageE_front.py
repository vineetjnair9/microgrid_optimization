"""Stage E: abstract, highlights, keywords, conclusions from results."""
from texedit import Ed
from common import RES
import pandas as pd, numpy as np, re
B = RES / 'benchmark_intcoded'; S = pd.read_csv(B / 'stats_table.csv').set_index('solver'); P = pd.read_csv(B / 'tests.csv').set_index('solver')
K = dict(l.split(' = ') for l in open(B / 'key_numbers.txt').read().splitlines())
N = {'PSO': 'PSO', 'GA': 'GA', 'SA': 'SA', 'SO': 'surrogate optimization', 'MS': 'MultiStart', 'GS': 'GlobalSearch', 'DPS': 'pattern search', 'PSOPS': 'the PSO--pattern-search hybrid'}
T = pd.read_csv(RES / 'rerun' / 'main_tables.csv').set_index('tag'); s3 = T.loc['S3']
EP = pd.read_csv(RES / 'short_runs' / 'eps_front.csv').sort_values('value').reset_index(drop=True); e0 = EP.iloc[0]; e1 = EP[EP.value == 0.01].iloc[0]
ST = pd.read_csv(RES / 'mc' / 'mc_summary_all.csv').set_index('design_id'); MK = dict(l.split(' = ') for l in open(RES / 'mc' / 'key_numbers.txt').read().splitlines())
ch = ST.loc['chosen_S3']; rb = ST.loc[MK['MC_ROBUST_PICK']]
SW = pd.read_csv(RES / 'rerun' / 'sweeps.csv'); it = SW[SW.tag == 'interest'].sort_values('value'); fp = SW[SW.tag == 'diesel_price'].sort_values('value')
F4 = pd.read_csv(RES / 'wind_design' / 'forced_nw.csv').set_index('value').loc[4]
full = [s for s in S.index if S.loc[s, 'success'] >= 0.999]
fin = S[np.isfinite(S.ERT_s)].sort_values('ERT_s')
def lst(L): return L[0] if len(L) == 1 else ', '.join(L[:-1]) + ' and ' + L[-1]
nsig = int((P.p_holm < 0.05).sum())
red = (1 - s3.LCOE_abs / s3.LCOE_base) * 100; ref = (1 - s3.oneminusREF) * 100
pv = s3.ns * 0.255; pvr = rb.ns * 0.255
dcv = (1 - rb.LCOE_cvar95 / ch.LCOE_cvar95) * 100; dmean = (rb.LCOE_mean / ch.LCOE_mean - 1) * 100
full = sorted(full, key=lambda x: (x != 'PSO', x != 'PSOPS'))
bench = (f"{lst([N[s] for s in full])} reach the exhaustively computed integer optimum in all {K['BENCH_NRUNS']} runs; "
         f"{N[fin.index[0]]} does so with the lowest expected running time ({fin.ERT_s.iloc[0]:.1f}~s), and gradient-based multistart methods perform worst")
abstract = rf'''Sizing an islanded hybrid microgrid requires scoring each candidate design with a year-long hourly operating simulation, which makes the objective non-smooth and rules out gradient-based and mixed-integer linear solvers without approximation. We size a solar photovoltaic (PV), wind, lithium-ion battery and diesel microgrid for an off-grid community in Timbila, Kenya, on five objectives: levelized cost of electricity (LCOE), emissions, unmet load, dumped energy and fossil share. We benchmark particle swarm optimization (PSO), a genetic algorithm, simulated annealing, surrogate optimization, two multistart methods, pattern search and a PSO--pattern-search hybrid over {K['BENCH_NRUNS']} independent runs at an equal budget of 2,000 evaluations. {bench}. We then approximate the Pareto front, select designs with knee-point, compromise and TOPSIS rules, trace a cost--reliability front with the generator rating as a decision variable, and re-rank candidate designs over {MK['MC_N']} Monte Carlo scenarios of resource and load. The equal-weight design, {pv:.0f}~kW of PV with a {s3.Eb:.0f}~kWh battery and no wind turbines, supplies {ref:.0f}\% of energy from renewables at {s3.LCOE_abs:.3f}~USD/kWh, {red:.0f}\% below diesel-only supply. Serving all load requires a {e0.PDE:.1f}~kW generator, and accepting 1\% unmet load lowers LCOE to {e1.LCOE_abs:.3f}~USD/kWh. Under uncertainty, a design with a {(pvr/pv-1)*100:.0f}\% larger PV array lowers the 95\% conditional value-at-risk of LCOE by {dcv:.0f}\% for a {dmean:.0f}\% higher expected cost. The interest rate dominates the sensitivity of cost.'''
nw = len(re.findall(r'\S+', re.sub(r'\\[a-zA-Z]+|[{}~$]', ' ', abstract)))
hl = [f"Eight solvers benchmarked over {K['BENCH_NRUNS']} runs at equal budget with statistical tests",
      "Pareto designs selected by knee point, compromise and TOPSIS rules",
      "Monte Carlo re-ranking trades expected cost against cost tail risk",
      f"PV and Li-ion hybrid supplies {ref:.0f}% renewable energy at {red:.0f}% below diesel cost",
      "Reliability target sets the diesel generator size, not the renewable capacity"]
for h in hl: assert len(h) <= 85, (len(h), h)
HL = '\n'.join(r'\item ' + h.replace('%', r'\%') for h in hl)
conc = rf'''\section{{Conclusions}}

We sized an islanded PV, wind, Li-ion and diesel microgrid for an off-grid community in Timbila, Kenya, with a design workflow that combines a statistically validated solver benchmark, a-posteriori Pareto search with explicit selection rules, and Monte Carlo re-ranking of candidate designs. Four findings stand out.

First, the choice of solver matters less than how it is tested. On this non-smooth, simulation-based problem, {lst([N[s] for s in full])} reached the exhaustively computed integer optimum in all {K['BENCH_NRUNS']} runs at a budget of 2,000 evaluations, and {N[fin.index[0]]} did so with the lowest expected running time ({fin.ERT_s.iloc[0]:.1f}~s); the gradient-based multistart methods were the least reliable.

Second, the equal-weight design installs {pv:.0f}~kW of PV, a {s3.Eb:.0f}~kWh Li-ion battery and no wind turbines. It supplies {ref:.0f}\% of the energy from renewables at {s3.LCOE_abs:.3f}~USD/kWh, {red:.0f}\% below a diesel-only system, with emissions {(1 - s3.Em_abs / s3.Em_base) * 100:.0f}\% lower. The generator remains necessary for reliability: with the generator rating as a decision variable, equal weights select no generator and accept {pd.read_csv(RES / 'short_runs' / 'dg_variable.csv').DPSP.min()*100:.0f}\% unmet load, whereas the $\varepsilon$-constraint front shows that a {e0.PDE:.1f}~kW generator serves all load at {e0.LCOE_abs:.3f}~USD/kWh. The reliability target sets the size of the generator, while the PV array and battery hardly change. Wind turbines do not enter the design because the site's wind blows mostly in daylight, together with the PV output; forcing in the four turbines of the original design raises LCOE by {(F4.LCOE_abs/s3.LCOE_abs-1)*100:.1f}\%, and turbines would pay only with a substantially stronger wind resource or cheaper small turbines.

Third, selection rules and uncertainty change which design a planner should build. Knee-point, compromise and TOPSIS rules pick designs that differ in battery size and cost, and the weighted-sum design is not dominated by any point of the Pareto approximation. Over {MK['MC_N']} Monte Carlo scenarios the equal-weight design never loses more than 1\% of load, but a design with a {(pvr/pv-1)*100:.0f}\% larger PV array lowers the 95\% conditional value-at-risk of LCOE by {dcv:.0f}\% at a {dmean:.0f}\% higher expected cost, and cuts mean emissions by {(1 - rb.Em_mean / ch.Em_mean) * 100:.0f}\%.

Fourth, the economics depend strongly on financing. LCOE ranges from {it.LCOE_abs.iloc[0]:.3f} to {it.LCOE_abs.iloc[-1]:.3f}~USD/kWh as the nominal interest rate varies from 0 to 20\%, far more than across the diesel price range ({fp.LCOE_abs.iloc[0]:.3f}--{fp.LCOE_abs.iloc[-1]:.3f}~USD/kWh), which makes concessional finance a strong lever for off-grid renewables in sub-Saharan Africa. Low-resource stress days and alternative demand profiles show that the battery and generator absorb single bad days, while shifting load into daylight hours reduces dumped energy.

These results rest on one year of measured weather, a single wind scaling factor and day-ahead dispatch with perfect foresight; \cref{{sec:limitations}} discusses these limits and \cref{{sec:future}} the extensions that would address them.

'''
e = Ed()
i = e.s.index(r'\begin{abstract}'); j = e.s.index(r'\end{abstract}')
blk = e.s[i:j]; k = blk.index('Optimal sizing and dispatch of islanded hybrid microgrids constitutes') if 'Optimal sizing and dispatch of islanded hybrid microgrids constitutes' in blk else blk.index('Sizing an islanded hybrid microgrid requires')
e.s = e.s[:i] + blk[:k] + abstract + '\n' + e.s[j:]
e.between(r'\begin{highlights}', r'\end{highlights}', '\\begin{highlights}\n' + HL + '\n', keep_end=True)
e.rep('Microgrids, multiobjective optimization, hybrid energy systems, sensitivity analysis, renewables, batteries, energy access',
      r'Microgrids \sep particle swarm optimization \sep metaheuristics \sep Pareto front \sep TOPSIS \sep Monte Carlo \sep energy access')
e.between(r'\section{Conclusions}', r'\subsection{Future work \label{sec:future}}', conc, keep_end=True)
e.save()
print('abstract words', nw); [print(len(h), h) for h in hl]
open(RES / 'highlights_final.txt', 'w').write('\n'.join(hl))
