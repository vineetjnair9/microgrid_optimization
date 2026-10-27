"""Compute response-letter values and sentences from results -> results/letter_values.txt."""
from common import RES
import pandas as pd, numpy as np
V = {'BENCH_NRUNS': 30, 'MC_N': 500, 'MIN_IRR_PCT': 31, 'MIN_WIND_PCT': 43}
T = pd.read_csv(RES / 'rerun' / 'main_tables.csv').set_index('tag'); s3 = T.loc['S3']
DV = pd.read_csv(RES / 'short_runs' / 'dg_variable.csv'); V['DPSP_OPT_PCT'] = f"{DV.DPSP.min()*100:.1f}"
EP = pd.read_csv(RES / 'short_runs' / 'eps_front.csv').sort_values('value').reset_index(drop=True); e0, e1, e5 = EP.iloc[0], EP[EP.value == 0.01].iloc[0], EP.iloc[-1]
V['EPS_RESULT_SENTENCE'] = (f"Serving all load requires a {e0.PDE:.1f}~kW generator, below the 15.0~kW peak because the battery covers part of it, at {e0.LCOE_abs:.3f}~USD/kWh; "
    f"accepting 1\\% unmet load reduces the generator to {e1.PDE:.1f}~kW and LCOE to {e1.LCOE_abs:.3f}~USD/kWh, and at 5\\% the generator disappears ({e5.LCOE_abs:.3f}~USD/kWh). The PV array and battery hardly change along the front, so the reliability target sets the size of the backup generator.")
SW = pd.read_csv(RES / 'rerun' / 'sweeps.csv'); fp = SW[SW.tag == 'diesel_price'].sort_values('value')
V['LCOE_ABS_DIESEL_LOW'] = f"{fp.LCOE_abs.iloc[0]:.3f}"; V['LCOE_ABS_DIESEL_HIGH'] = f"{fp.LCOE_abs.iloc[-1]:.3f}"
MK = dict(l.split(' = ') for l in open(RES / 'mc' / 'key_numbers.txt').read().splitlines()); ST = pd.read_csv(RES / 'mc' / 'mc_summary_all.csv').set_index('design_id')
ch, rb = ST.loc['chosen_S3'], ST.loc[MK['MC_ROBUST_PICK']]
V['MC_CHOSEN_LCOE_P5'] = MK['MC_CHOSEN_LCOE_P5']; V['MC_CHOSEN_LCOE_P95'] = MK['MC_CHOSEN_LCOE_P95']
V['MC_CHOSEN_P_DPSP'] = f"zero in all scenarios (some load is lost in {ch.P_DPSP_gt_0*100:.1f}\\% of them, when load noise lifts an hourly peak above the 16~kW rating while the battery is empty)"
V['MC_ROBUST_SENTENCE'] = (f"Re-ranking the Pareto candidates with TOPSIS on mean LCOE, CVaR$_{{95}}$ of LCOE, mean emissions and the probability of any unmet load selects [{rb.ns:.0f}, {rb.nw:.0f}, {rb.Eb:.0f}] rather than the equal-weight design: "
    f"its {(rb.ns/ch.ns-1)*100:.0f}\\% larger PV array raises mean LCOE by {(rb.LCOE_mean/ch.LCOE_mean-1)*100:.0f}\\% but lowers CVaR$_{{95}}$ by {(1-rb.LCOE_cvar95/ch.LCOE_cvar95)*100:.0f}\\% and mean emissions by {(1-rb.Em_mean/ch.Em_mean)*100:.0f}\\%.")
PK = dict(l.split(' = ') for l in open(RES / 'pareto' / 'key_numbers.txt').read().splitlines()); V['N_FRONT_16'] = PK['N_FRONT_16']
V['WS_CHECK_SENTENCE'] = (f"none of the {PK['N_FRONT_16']} non-dominated points of the 16~kW Pareto approximation dominates the equal-weight PSO design, and its equal-weight score ({PK['WS_SCORE']}) is lower than that of every front point (best {PK['FRONT_BEST_WS']}); "
    "the Pareto approximation is therefore sparse near this design, and we add the weighted-sum design to the candidate set of Section~5.4.")
def gap_txt(g, n):
    pre = 'by at most ' if n > 1 else 'by '
    return ('by less than 0.001~USD/kWh' if g < 0.0005 else pre + f'{g:.3f}~USD/kWh')
SS = pd.read_csv(RES / 'short_runs' / 'strategy_stress.csv').set_index('tag')
wins = sum(SS.loc[f'S3_C{c:.2f}_L{l}', 'J'] <= SS.loc[f'S4_C{c:.2f}_L{l}', 'J'] for c in [3.20, 5.00, 7.57] for l in [5475, 3000])
cells = [(c, l) for c in [3.20, 5.00, 7.57] for l in [5475, 3000] if SS.loc[f'S4_C{c:.2f}_L{l}', 'LCOE_abs'] < SS.loc[f'S3_C{c:.2f}_L{l}', 'LCOE_abs']]
V['R22_OPENING'] = ("We respectfully disagree that Strategy~3 reflects an inefficient charging pathway, and we have added the explanation that the original text lacked (Section~5.2)." if wins == 6 else
    "We agree that the preference for Strategy~3 depends on fuel and battery-life assumptions, and we have added both an explanation and a stress test (Section~5.2).")
V['STRESS_RESULT_SENTENCE'] = (f"Strategy~3 keeps the lower weighted objective in {'all six' if wins == 6 else f'{wins} of the six'} combinations." +
    (" Strategy~4 reaches a slightly lower absolute LCOE only in " + " and ".join(f"the {c:.2f}~USD/gal, {l:,}-cycle case" for c, l in cells) + ", " + gap_txt(max(SS.loc[f'S3_C{c:.2f}_L{l}','LCOE_abs'] - SS.loc[f'S4_C{c:.2f}_L{l}','LCOE_abs'] for c, l in cells), len(cells)) + "." if cells else ""))
WS = pd.read_csv(RES / 'short_runs' / 'wind_sweep.csv').set_index('tag')
FW = pd.read_csv(RES / 'wind_design' / 'forced_nw.csv').set_index('value'); TL = pd.read_csv(RES / 'wind_design' / 'threshold_lcoe_only.csv')
cth = TL[(TL.tag == 'C_WT_lcoe_only') & (TL.nw > 0)].value.max(); wth = TL[(TL.tag == 'wind_scale_lcoe_only') & (TL.nw > 0)].value.min()
V['WIND_SWEEP_SENTENCE'] = (f"After the correction of the turbine power curve (see Additional changes), the optimal design installs no wind turbines at any of the three wind levels, so the wind correction factor no longer affects the selected design. Because wind was central to the submitted version, a new Section~5.2.4 explains this result: at Timbila the wind blows mostly in daylight, together with the PV output, so much of its energy would be dumped; forcing in the four turbines of the original design raises LCOE by about {(FW.loc[4,'LCOE_abs']/FW.loc[0,'LCOE_abs']-1)*100:.0f}\\%; and turbines would enter the cost-optimal mix only at an installed cost of about {cth:,.0f}~USD/kW or below, or with a wind resource about {(wth-1)*100:.0f}\\% stronger." if (WS.nw == 0).all() else
    f"The optimal number of turbines changes from {WS.loc['wind_0.75','nw']:.0f} to {WS.loc['wind_1.25','nw']:.0f} and LCOE from {WS.loc['wind_0.75','LCOE_abs']:.3f} to {WS.loc['wind_1.25','LCOE_abs']:.3f}~USD/kWh.")
B = RES / 'benchmark_intcoded'
if (B / 'stats_table.csv').exists():
    S = pd.read_csv(B / 'stats_table.csv').set_index('solver'); BK = dict(l.split(' = ') for l in open(B / 'key_numbers.txt').read().splitlines())
    NM = {'PSO': 'PSO', 'GA': 'GA', 'SA': 'SA', 'SO': 'surrogate optimization', 'MS': 'MultiStart', 'GS': 'GlobalSearch', 'DPS': 'pattern search', 'PSOPS': 'the PSO--pattern-search hybrid'}
    full = [NM[s] for s in S.index if S.loc[s, 'success'] >= 0.999]; fin = S[np.isfinite(S.ERT_s)].sort_values('ERT_s')
    lst = lambda L: L[0] if len(L) == 1 else ', '.join(L[:-1]) + ' and ' + L[-1]
    P = pd.read_csv(B / 'tests.csv').set_index('solver'); fstar = float(BK['BENCH_FSTAR']); ref = S.index[0]
    nsig = [NM[s] for s in P.index if P.loc[s, 'p_holm'] >= 0.05]; neg = [s for s in P.index if P.loc[s, 'p_holm'] < 0.05 and S.loc[s, 'success'] >= 0.999]
    gap = max([abs(S.loc[s, 'median'] / fstar - 1) * 100 for s in neg] + [0])
    sig_letter = (f" Pairwise tests against {NM[ref]}, the solver with the lowest median, find no significant difference for {lst(nsig) if nsig else 'no solver'}" + (f"; the differences for {lst([NM[s] for s in neg])} are significant but amount to at most {max(gap, 0.001):.3f}\\% of $f^*$ in the median, far below any practical tolerance." if neg else "."))
    msgs_txt = (f"{S.loc['MS','success']*100:.0f}\\% of runs each" if round(S.loc['MS','success'],3) == round(S.loc['GS','success'],3) else f"{S.loc['MS','success']*100:.0f}\\% and {S.loc['GS','success']*100:.0f}\\% of runs")
    V['BENCH_KW_H'] = BK['BENCH_KW_H']; m_, e_ = f"{float(BK['BENCH_KW_P']):.1e}".split('e'); V['BENCH_KW_P'] = f'{m_}\\times 10^{{{int(e_)}}}'
    V['BENCH_RESULT_SENTENCE'] = (f"{lst(full)[0].upper() + lst(full)[1:]} reach the target in all runs, and {NM[fin.index[0]]} has the lowest expected running time ({fin.ERT_evals.iloc[0]:,.0f} evaluations, {fin.ERT_s.iloc[0]:.1f}~s); "
        f"GA succeeds in {S.loc['GA','success']*100:.0f}\\% of runs, and the gradient-based MultiStart and GlobalSearch in {msgs_txt}." + sig_letter)
with open(RES / 'letter_values.txt', 'w') as f:
    for k, v in V.items(): f.write(f'{k} = {v}\n')
print('\n'.join(f'{k} = {v}' for k, v in V.items()))
