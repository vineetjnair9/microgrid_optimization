"""Stage D: Sections 7 (dispatch) and 8 (Monte Carlo, stress tests, demand profiles) from the corrected runs."""
from texedit import Ed
from common import RES
import pandas as pd, numpy as np
D = pd.read_csv(RES / 'dispatch' / 'dispatch_cases.csv').set_index('case')
M = pd.read_csv(RES / 'mc' / 'mc_table.csv').set_index('design_id'); ST = pd.read_csv(RES / 'mc' / 'mc_summary_all.csv').set_index('design_id')
K = dict(l.split(' = ') for l in open(RES / 'mc' / 'key_numbers.txt').read().splitlines())
SP = dict(l.split(' = ') for l in open(RES / 'mc' / 'scenario_spread.txt').read().splitlines())
T = pd.read_csv(RES / 'rerun' / 'main_tables.csv').set_index('tag'); s3 = T.loc['S3']; d8 = T.loc['DG8kW']
ch = ST.loc['chosen_S3']; rb = ST.loc[K['MC_ROBUST_PICK']]; e8 = ST.loc['DG8kW']
mn = M[M.label == 'Min LCOE'].iloc[0] if (M.label == 'Min LCOE').any() else None
def drow(lab, c):
    r = D.loc[c]; return f"{lab} & {r.J:.4f} & {r.COE:.3f} & {r.COE_n:.4f} & {r.Em_kg:.1f} & {r.DPSP*100:.2f} & {r.Dump:.3f} & {r.REF*100:.1f} & {r.DE_hours:.0f} \\\\"
def dtable(rows, label, cap):
    body = '\n'.join(drow(a, b) for a, b in rows)
    return rf'''\begin{{table}}[htbp]
\centering
\small
\begin{{tabular}}{{l c c c c c c c c}}
\toprule
\textbf{{Case}} & \textbf{{$J$}} & \textbf{{COE}} & \textbf{{COE}} & \textbf{{Em.}} & \textbf{{DPSP}} & \textbf{{Dump}} & \textbf{{REF}} & \textbf{{DE}} \\
 & & [USD/kWh] & (norm.) & [kg] & [\%] & & [\%] & [h] \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\caption{{\label{{{label}}} {cap}}}
\end{{table}}
'''
i, ii, iii = D.loc['i_16kW'], D.loc['ii_8kW_16kWsizing'], D.loc['iii_8kW_8kWsizing']; ls, lw, lb = D.loc['low_solar'], D.loc['low_wind'], D.loc['low_solar_wind']
pk, sh, sc = D.loc['load_peaky'], D.loc['load_shift'], D.loc['load_shift_curtail']
same_wind = abs(lw.J - iii.J) < 1e-9
TAB0 = dtable([('(i) 16~kW DE', 'i_16kW'), ('(ii) 8~kW DE, design sized for 16~kW', 'ii_8kW_16kWsizing'), ('(iii) 8~kW DE, design sized for 8~kW', 'iii_8kW_8kWsizing')], 'tab:DG_size', 'Day-ahead dispatch on 1 January 2018 for three DE and design configurations. $J$ is the equally weighted sum of normalized COE, emissions, dump fraction and $(1-REF)$; DPSP is constrained to at most 1\%.')
TAB1 = dtable([('Low solar irradiance (10\\%)', 'low_solar'), ('Low wind speed (10\\%)', 'low_wind'), ('Low solar and wind', 'low_solar_wind')], 'tab:dispatch_robust_RES', 'Day-ahead dispatch under low renewable resource (8~kW DE design).')
TAB2 = dtable([('Baseline profile', 'iii_8kW_8kWsizing'), ('Peakier profile', 'load_peaky'), ('Load shifting', 'load_shift'), ('Load shifting and 10\\% curtailment', 'load_shift_curtail')], 'tab:dispatch_robust_load', 'Day-ahead dispatch under alternative demand profiles (8~kW DE design).')
LW_TXT = 'Low wind has no effect, because the design installs no wind turbines.' if same_wind else ''
STRESS_TXT = (f"\\cref{{tab:dispatch_robust_RES}} shows that on a day with 10\\% of normal irradiance the DE runs for {ls.DE_hours:.0f}~h, the renewable fraction falls to {ls.REF*100:.0f}\\% and the daily COE rises to {ls.COE:.3f}~USD/kWh, while DPSP stays within the 1\\% limit." if ls.DE_hours > 0 else
    f"\\cref{{tab:dispatch_robust_RES}} shows that on a day with 10\\% of normal irradiance the {d8.Eb:.0f}~kWh battery, which enters the day at 90\\% SOC, carries the load without the DE: it ends the day near its lower SOC limit, DPSP reaches the 1\\% limit and the daily COE is {ls.COE:.3f}~USD/kWh. A second consecutive dark day would require the DE, which the single-day horizon does not capture.")
_dl, _dh = round(min(i.Dump, ii.Dump, iii.Dump)*100), round(max(i.Dump, ii.Dump, iii.Dump)*100)
dump_rng = f'{_dl}' if _dl == _dh else f'{_dl}--{_dh}'
sec7 = rf'''\section{{\label{{sec:dispatch_opt}} Optimal economic and environmental dispatch results}}

The sizing stage (Stage~1) scores each design under the rule-based, priority-ordered controller of \cref{{sec:disp_strat}}, which is fast and non-anticipative but does not minimize cost or emissions over time. Stage~2 asks how much optimized day-ahead scheduling changes the operation of a given design. For a fixed design it chooses the hourly DE output $P_{{DE}}(t)$ and battery power $P_{{BS}}(t)$ over the next 24~h to minimize the equally weighted sum of four normalized terms, daily COE, emissions, dumped energy and $(1-REF)$ (Eq.~\ref{{eq:dispatch}}). DPSP enters as a constraint ($DPSP \leq 1\%$) together with the SOC limits (10--90\%), the DE output limits and the battery power rating; lost load carries no cost in this objective, so the optimizer may use the permitted 1\% where that lowers the other terms. The daily cost includes battery wear at 0.068~USD per kWh discharged (the replacement cost of 300~USD/kWh divided by the lifetime throughput of 5,475 cycles over 80\% of capacity), so the optimizer does not cycle the battery without need. The weighted sum is again an a-priori scalarization (\cref{{sec:opt_prob}}). The dispatch assumes perfect foresight of load and weather over the day, which makes its results optimistic (\cref{{sec:limitations}}). We solve it in two steps: particle swarm optimization on a penalty form of the problem (five seeds, swarm size 100, 600 iterations) followed by \texttt{{fmincon}} with the SQP algorithm, started from each PSO result, from a flat schedule and from a load-following schedule that respects the SOC limits, enforcing the constraints exactly; the best feasible solution is kept. Each case takes about 5~s.

\cref{{tab:DG_size}} compares three configurations on the representative day (1 January 2018): (i) the equal-weight design with a 16~kW DE, (ii) the same design with an 8~kW DE, and (iii) the design re-sized for an 8~kW DE ([{d8.ns:.0f}, {d8.nw:.0f}, {d8.Eb:.0f}]). The representative day is sunny (irradiation 136\% of the annual daily mean), so the {s3.ns*0.255:.0f}~kW PV array and {s3.Eb:.0f}~kWh battery cover the whole load without the DE in all three cases: emissions are zero, the daily COE (operating and annualized fixed costs over the day's load) is {min(i.COE, ii.COE, iii.COE):.3f}--{max(i.COE, ii.COE, iii.COE):.3f}~USD/kWh including battery wear, and {dump_rng}\% of the generated energy is dumped because the battery reaches its upper SOC limit by midday. The smaller DE lowers the fixed cost of the backup, so cases (ii) and (iii) have a lower COE than case (i){'' if iii.J <= ii.J else '; the small difference between (ii) and (iii), whose designs are almost identical, reflects the tolerance of the dispatch solver'}. \cref{{fig:dispatch_P_base}} shows the schedules.

{TAB0}
\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_dispatch_base.pdf}}
  \caption{{\label{{fig:dispatch_P_base}} Optimized day-ahead schedules on 1 January 2018 for the three configurations of \cref{{tab:DG_size}}: power flows (top; battery power positive when discharging) and battery SOC (bottom).}}
\end{{figure}}

'''
sec8 = rf'''\section{{Robustness to resource and demand uncertainty}}

\subsection{{Monte Carlo analysis of resource and load uncertainty\label{{sec:mc}}}}
The sizing results rest on one year of weather and one load profile. To quantify how annual performance varies, we simulate each candidate design over {K['MC_N']} synthetic years. Each scenario is built in three steps. (1) Day-block bootstrap: for each calendar day we draw a donor day from the same month of 2018 and copy its 24-hour irradiance, temperature and wind series, which preserves diurnal shapes, cross-correlation between the variables and seasonality. (2) Inter-annual variability: the whole year's irradiance is scaled by $a_I \sim \mathcal{{N}}(1, 0.05^2)$ and wind speed by $a_W \sim \mathcal{{N}}(1, 0.10^2)$. (3) Load noise: hourly load is multiplied by $(1 + \epsilon_t)$, where $\epsilon_t$ follows an Ornstein--Uhlenbeck process with mean reversion $\theta = 0.3$~h$^{{-1}}$ and volatility $\sigma = 0.1$, discretized hourly. The inter-annual spreads are assumptions of the order reported for East African sites; the resulting scenario set has coefficients of variation of {float(SP['irr_cv'])*100:.1f}\% in annual irradiation, {float(SP['wind_cv'])*100:.1f}\% in mean wind speed and {float(SP['load_cv'])*100:.1f}\% in annual load. All designs are evaluated on the same scenarios (common random numbers, seed 2026), with the diesel-only baseline fixed at its nominal value so that normalized objectives remain comparable across scenarios.

We evaluated the equal-weight design, the 8~kW DE design and all {int(K.get('MC_N_FRONT', 0)) or len(ST) - 2} points of the 16~kW Pareto approximation (\cref{{sec:pareto_select}}). \cref{{tab:mc}} and \cref{{fig:mc}} summarize six of them. For the equal-weight design, annual LCOE ranges from {K['MC_CHOSEN_LCOE_P5']} to {K['MC_CHOSEN_LCOE_P95']}~USD/kWh (5th--95th percentile) with CVaR$_{{95}}$ = {K['MC_CHOSEN_LCOE_CVAR']}~USD/kWh, and the renewable fraction stays above {float(K['MC_CHOSEN_REF_P5'])*100:.1f}\% in 95\% of scenarios. With the 16~kW DE, unmet load exceeds 1\% in none of the scenarios and is non-zero in {float(K['MC_CHOSEN_P_DPSP_GT_0'])*100:.1f}\% of them, when load noise lifts an hourly peak above the DE rating while the battery is empty. With the 8~kW DE, some load is lost in every scenario, but DPSP stays below {e8.DPSP_p95*100:.1f}\% at the 95th percentile and never exceeds 1\%, at a lower LCOE ({K['MC_8KW_LCOE_P5']}--{K['MC_8KW_LCOE_P95']}~USD/kWh).

We then re-ranked the 16~kW candidates with TOPSIS (equal weights) on four risk-aware criteria: mean LCOE, CVaR$_{{95}}$ of LCOE, mean emissions and the probability of any unmet load. (The probability of exceeding 1\% unmet load is zero for every 16~kW candidate and therefore cannot discriminate between them.) The robust choice is [{rb.ns:.0f}, {rb.nw:.0f}, {rb.Eb:.0f}], which differs from the equal-weight design: its mean LCOE is {(rb.LCOE_mean/ch.LCOE_mean-1)*100:.0f}\% higher ({rb.LCOE_mean:.3f} vs {ch.LCOE_mean:.3f}~USD/kWh), but its CVaR$_{{95}}$ is {(1-rb.LCOE_cvar95/ch.LCOE_cvar95)*100:.0f}\% lower ({rb.LCOE_cvar95:.3f} vs {ch.LCOE_cvar95:.3f}~USD/kWh), its mean emissions are {(1-rb.Em_mean/ch.Em_mean)*100:.0f}\% lower and its probability of any unmet load falls from {ch.P_DPSP_gt_0*100:.1f}\% to {rb.P_DPSP_gt_0*100:.1f}\%. A {(rb.ns/ch.ns-1)*100:.0f}\% larger PV array ({rb.ns*0.255:.0f} vs {ch.ns*0.255:.0f}~kW) buys insurance against poor resource years: in those years the equal-weight design burns more diesel, which raises its cost tail. The equal-weight design ranks {K['MC_ROBUST_RANK_OF_CHOSEN']} of {len(ST) - 1} under this robust criterion. The knee point of the nominal front has the highest cost and emissions of the six, because it buys a near-zero dump fraction with a smaller PV array that leaves more of the load to the DE. A designer who weighs cost tail risk and emissions above expected cost should therefore choose the robust design; one who prioritizes expected cost can keep the equal-weight design, whose LCOE distribution is narrow.

\begin{{table}}[htbp]
\centering
\scriptsize
\setlength{{\tabcolsep}}{{3pt}}
\input{{rev_mc_table.tex}}
\caption{{\label{{tab:mc}} Monte Carlo performance of selected designs over {K['MC_N']} annual scenarios of irradiance, wind and load. LCOE nominal: value for the 2018 data; CVaR$_{{95}}$: mean LCOE over the worst 5\% of scenarios.}}
\end{{table}}

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_mc_distributions.pdf}}
  \caption{{\label{{fig:mc}} Distributions of annual LCOE, emissions, DPSP and REF over {K['MC_N']} Monte Carlo scenarios for the designs of \cref{{tab:mc}} (boxes: interquartile range; whiskers: 1.5 times the interquartile range; outliers not shown; numbers identify the designs listed below the panels).}}
\end{{figure}}

\subsection{{Deterministic stress tests\label{{sec:stress}}}}
The Monte Carlo analysis describes typical variability; it does not test extreme single days. We therefore keep two deterministic stress tests on the dispatch problem, using the 8~kW DE design. The low-resource days scale the irradiance and wind speed of the representative day to 10\% of their values (\cref{{fig:dispatch_profiles}}a--b). They are deliberately extreme: the lowest-irradiation day of 2018 still delivers 31\% of the annual mean daily irradiation, and the calmest day has 43\% of the mean daily wind speed, so the 10\% cases bound a worst single day rather than represent a likely one. {STRESS_TXT} {LW_TXT}

{TAB1}
\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_dispatch_profiles.pdf}}
  \caption{{\label{{fig:dispatch_profiles}} Inputs of the stress tests on the representative day: (a) baseline and low (10\%) irradiance, (b) baseline and low (10\%) wind speed at the measurement height, (c) baseline and alternative load profiles.}}
\end{{figure}}

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_dispatch_res.pdf}}
  \caption{{\label{{fig:dispatch_robust_RES}} Optimized schedules under low renewable resource (8~kW DE design).}}
\end{{figure}}

\subsection{{Demand profiles}}
We also repeated the dispatch with three alternative load profiles (\cref{{fig:dispatch_profiles}}c): a peakier profile in which hourly loads vary by up to $\pm 30\%$ around the baseline, a flatter profile in which load is shifted toward the hours of solar output, and the shifted profile with 10\% daily curtailment. With this PV-dominated design, demand shape matters mainly through dumped energy: shifting load into daylight hours lowers the dump fraction from {iii.Dump:.3f} to {sh.Dump:.3f} and the weighted objective from {iii.J:.4f} to {sh.J:.4f} (\cref{{tab:dispatch_robust_load}}). The DE stays off in all three cases on this sunny day. Demand-side measures that move load into hours of renewable surplus therefore have value even when the generation mix is fixed (\cref{{sec:dr}}).

{TAB2}
\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_dispatch_load.pdf}}
  \caption{{\label{{fig:dispatch_load}} Optimized schedules under alternative demand profiles (8~kW DE design).}}
\end{{figure}}

'''
e = Ed()
e.between(r'\section{\label{sec:dispatch_opt} Optimal economic and environmental dispatch results}', r'\section{Discussion and limitations\label{sec:discussion}}', sec7 + sec8, keep_end=True)
e.save()
import shutil, pathlib; shutil.copy(RES / 'mc' / 'mc_table.tex', pathlib.Path.home() / 'mnt' / 'Microgrids_paper_v2' / 'rev_mc_table.tex')
