"""Stage B (part 1): Sec. 5.2 sizing results, break-even analysis, App. A wind text. Numbers from results CSVs."""
from texedit import Ed
from common import RES
import pandas as pd, json, numpy as np
T = pd.read_csv(RES / 'rerun' / 'main_tables.csv').set_index('tag'); TT = pd.read_csv(RES / 'rerun' / 'tech_tables.csv').set_index('tech')
SS = pd.read_csv(RES / 'short_runs' / 'strategy_stress.csv').set_index('tag')
W = json.load(open(RES / 'wind' / 'wind_validation.json')); WS = pd.read_csv(RES / 'short_runs' / 'wind_sweep.csv').set_index('tag')
s3, s3o, kw, d8 = T.loc['S3'], T.loc['S3_original_fuel_model'], T.loc['LIDE_ii_kW'], T.loc['DG8kW']
E_load = 74085.51; avg_load = E_load / 8760; daily = E_load / 365
def row(r): return f"[{r.ns:.0f}, {r.nw:.0f}, {r.Eb:.2f}] & {r.J:.4f} & {r.LCOE_n:.4f} & {r.Em_n:.4f} & {r.DPSP:.4f} & {r.Dump:.4f} & {r.oneminusREF:.4f} & {r.LCOE_abs:.3f}"
def trow(r): return f"[{r.ns:.0f}, {r.nw:.0f}, {r.Eb:.2f}] & {r.J:.4f} & {r.LCOE_n:.4f} & {r.Em_n:.4f} & {r.DPSP:.4f} & {r.Dump:.4f} & {r.oneminusREF:.4f}"
red_lcoe = (1 - s3.LCOE_abs / s3.LCOE_base) * 100; red_em = (1 - s3.Em_abs / s3.Em_base) * 100; ref = (1 - s3.oneminusREF) * 100
pv_kw = s3.ns * 0.255; wt_kw = s3.nw * 3.5
# strategy stress summary
def best_strat(c, l):
    a = SS.loc[f'S3_C{c:.2f}_L{l}', 'J']; b = SS.loc[f'S4_C{c:.2f}_L{l}', 'J']; return a, b
stress_rows = []; s3wins = 0
for c in [3.20, 5.00, 7.57]:
    for l in [5475, 3000]:
        a, b = best_strat(c, l); s3wins += a <= b
        r3 = SS.loc[f'S3_C{c:.2f}_L{l}']; r4 = SS.loc[f'S4_C{c:.2f}_L{l}']
        stress_rows.append(f"{c:.2f} & {l:,} & {a:.4f} & {b:.4f} & {r3.LCOE_abs:.3f} & {r4.LCOE_abs:.3f} & {r3.Dump:.3f} & {r4.Dump:.3f} \\\\")
stress_sentence = ('Strategy 3 keeps the lower weighted objective in all six combinations' if s3wins == 6 else
                   f'Strategy 3 keeps the lower weighted objective in {s3wins} of the six combinations')
lc4 = [c for c in [3.20, 5.00, 7.57] if SS.loc[f'S4_C{c:.2f}_L5475','LCOE_abs'] < SS.loc[f'S3_C{c:.2f}_L5475','LCOE_abs']]
if lc4: stress_sentence += f', although at diesel prices of {lc4[0]:.2f}~USD/gal and above Strategy 4 reaches a slightly lower absolute LCOE because its larger battery displaces more fuel'
stress_sentence += '. The cycle life does not bind in either strategy: the battery completes only about 45--65 cycles a year, so even 3,000 cycles last longer than the 25-year project'
new52 = rf'''\subsection{{Sizing results}}

\subsubsection{{\label{{sec:strat}} Strategy selection}}

Before optimizing the capacities of the PV, WT and BS components, two strategy decisions had to be made, relating to (1) the replacement of the BS and (2) whether surplus DG output may charge the BS.
\begin{{itemize}}
    \item The operator can replace the battery at fixed intervals set by its warranty or expected life (here every 15 years for LI), or when it has completed its rated number of charge--discharge cycles (5,475 for LI and 1,400 for LA). The second approach follows actual use and is the more realistic of the two.
    \item The DG has a minimum stable output. When the residual deficit is below this level, the DG still runs at its minimum and produces a surplus. This surplus can either be rectified and stored in the BS or sent to the dump load.
\end{{itemize}}

\begin{{table}}[htbp] 
\centering
\begin{{tabular}}{{p{{0.75cm}} p{{10cm}}}}
\toprule
\multicolumn{{1}}{{c}}{{\textbf{{Strategy}}}} & \multicolumn{{1}}{{c}}{{\textbf{{Description}}}}    \\
\midrule
1 & DE minimum-load surplus can charge LI; LI replaced every 15 y \\[1ex]
2 & DE surplus is dumped; LI replaced every 15 y \\[1ex]
3 & DE minimum-load surplus can charge LI; LI replaced every 5475 cycles \\[1ex]
4 & DE surplus is dumped; LI replaced every 5475 cycles \\
\bottomrule
\end{{tabular}}
\caption{{Strategy selection for the LI+DE microgrid.}}
\label{{tab:strat_select}} 
\end{{table}}

\cref{{tab:strat}} lists the best design found for each strategy (best of ten integer-coded PSO runs). Strategy 3 gives the lowest weighted objective ({s3.J:.4f}) and the lowest absolute LCOE ({s3.LCOE_abs:.3f}~USD/kWh), and we use it in all subsequent results. Strategy 4 reaches lower emissions and a higher renewable fraction, but only with a {T.loc['S4'].Eb:.0f}~kWh battery and more dumped energy. Cycle-based replacement lowers costs because the battery cycles only about {s3.BS_cycles:.0f} times a year, so it is replaced far less often than a fixed 15-year schedule assumes.

The DE never runs in order to charge the battery. Under the load-following rule it starts only when renewable output and battery discharge cannot cover the load. When the residual deficit is smaller than the engine's minimum stable output ($0.3P_{{DG,\;r}}$), the engine still runs at that minimum, and the difference is surplus energy. Strategies 2 and 4 send this surplus to the dump load; Strategies 1 and 3 rectify it ($\eta_{{rec}} = 0.9$) and store it (round-trip efficiency 0.9). Both options burn the same fuel in that hour, so storage recovers energy that would otherwise be wasted. Battery wear from the extra throughput is costed through cycle-based replacement and capacity fade. To test whether the preference for Strategy 3 depends on cheap fuel or a long battery life, \cref{{tab:strategy_stress}} repeats the comparison of Strategies 3 and 4 at diesel prices up to 7.57~USD/gal (2.0~USD/L) and with the cycle life cut to 3,000. {stress_sentence}.

\begin{{table}}[htbp]
\centering
\small
\begin{{tabular}}{{l l c c c c c c c}}
\toprule
\textbf{{Strategy}} & \textbf{{Soln. $[n_s, n_w, E_{{b,init}}]$}} & \textbf{{$J$}} & \textbf{{LCOE}} & \textbf{{Em.}} & \textbf{{DPSP}} & \textbf{{Dump}} & \textbf{{1-REF}} & \textbf{{LCOE [USD/kWh]}} \\
\midrule
1 & {row(T.loc['S1'])} \\
2 & {row(T.loc['S2'])} \\
3 & {row(T.loc['S3'])} \\
4 & {row(T.loc['S4'])} \\
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:strat}} Best design for each strategy (16~kW DE, equal weights). LCOE and emissions are normalized by the diesel-only baseline (\cref{{tab:baseline}}).}}
\end{{table}}

\begin{{table}}[htbp]
\centering
\small
\begin{{tabular}}{{c c c c c c c c}}
\toprule
\textbf{{Diesel price}} & \textbf{{LI cycle life}} & \multicolumn{{2}}{{c}}{{\textbf{{$J$}}}} & \multicolumn{{2}}{{c}}{{\textbf{{LCOE [USD/kWh]}}}} & \multicolumn{{2}}{{c}}{{\textbf{{Dump fraction}}}} \\
\textbf{{[USD/gal]}} & \textbf{{[cycles]}} & S3 & S4 & S3 & S4 & S3 & S4 \\
\midrule
{chr(10).join(stress_rows)}
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:strategy_stress}} Strategy 3 (DE surplus stored) vs Strategy 4 (DE surplus dumped) under higher diesel prices and shorter battery cycle life; best of five PSO runs per cell.}}
\end{{table}}

\subsubsection{{Technology selection\label{{sec:tech_select}}}}
The MG designer also has to choose the battery and backup generator technologies. Four combinations were sized (\cref{{tab:tech_select}}). LI+DE gives the lowest weighted objective. LA+DE reaches a lower normalized LCOE but dumps more than twice as much energy, because its small, cycle-limited battery absorbs little of the renewable surplus. Both MT combinations have markedly higher emissions and fossil shares. LCOE and emissions are normalized with respect to a single-DG system of the same technology; the baseline values are listed in \cref{{tab:baseline}}.

\begin{{table}}[htbp]
\centering
\small
\begin{{tabular}}{{l l c c c c c c}}
\toprule
\textbf{{System}} & \textbf{{Soln. $[n_s, n_w, E_{{b,init}}]$}} & \textbf{{$J$}} & \textbf{{LCOE}} & \textbf{{Em.}} & \textbf{{DPSP}} & \textbf{{Dump}} & \textbf{{1-REF}} \\
\midrule
LI+DE & {trow(s3)} \\
LI+MT & {trow(TT.loc['LI_MT'])} \\
LA+DE & {trow(TT.loc['LA_DE'])} \\
LA+MT & {trow(TT.loc['LA_MT'])} \\
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:tech_select}} Best design for each technology combination (best of five to ten integer-coded PSO runs).}}
\end{{table}}

\begin{{table}}[htbp]
\centering
\begin{{tabular}}{{@{{}}lcc@{{}}}}
\toprule
\textbf{{Parameter}} & DE system & MT system \\ 
\midrule
LCOE [$\$/kWh$] & 0.4968 & 0.3321 \\
Emissions [$kg$ of pollutants/y] & 50,189 & 48,562 \\
Emissions [$kg$ of pollutants/$kWh$] & 0.6774 & 0.6555 \\
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:baseline}} Baseline LCOE and emissions for the MG running on a single fossil-fuel 16 kW DG.}}
\end{{table}}

Microturbines running on natural gas have lower specific emissions than diesel engines and, alone, a lower LCOE (\cref{{tab:baseline}}). Yet the MG with a DE backup has lower emissions and costs than the one with an MT backup, because the backup runs for only about {s3.DE_hours:.0f}~h per year: the MT's higher capital cost is not recovered by its fuel savings over so few operating hours. The same reasoning explains why LI is preferred over LA despite LA's lower capital cost.

\subsubsection{{Optimal capacities for baseline LI+DE system}}

We sized the LI+DE system with two sets of decision variables: (i) unit counts $[n_s, n_w, E_{{b,\;init}}]$ with integer $n_s$ and $n_w$, and (ii) total rated powers $[P_{{PV,\;r,\;total}}, P_{{WT,\;r,\;total}}, E_{{b,\;init}}]$ treated as continuous. Design (i) corresponds to [{pv_kw:.2f}~kW, {wt_kw:.1f}~kW, {s3.Eb:.1f}~kWh] in rated terms and design (ii) to [{kw.ns:.2f}~kW, {kw.nw:.2f}~kW, {kw.Eb:.1f}~kWh]. The continuous approach (ii) reaches a slightly lower weighted objective ({kw.J:.4f} vs {s3.J:.4f}) because it is not restricted to whole PV modules and turbines; a designer limited to specific products should use approach (i).

\begin{{table}}[htbp]
\centering
\begin{{tabular}}{{p{{5cm}} p{{4.3cm}} p{{4.3cm}}}}
\toprule
\multicolumn{{1}}{{l}}{{\textbf{{Parameter}}}} & \multicolumn{{1}}{{l}}{{(i) unit counts}} & \multicolumn{{1}}{{l}}{{(ii) rated powers}} \\
\midrule
$LCOE_{{normalized}}$ & {s3.LCOE_n:.4f} & {kw.LCOE_n:.4f} \\
LCOE [$\$/kWh$] & {s3.LCOE_abs:.4f} & {kw.LCOE_abs:.4f} \\
$Emissions_{{normalized}}$ & {s3.Em_n:.4f} & {kw.Em_n:.4f} \\
Annual emissions [$kg/y$] & {s3.Em_abs:,.0f} & {kw.Em_abs:,.0f} \\
DPSP & {s3.DPSP:.0f} & {kw.DPSP:.0f} \\
Dump & {s3.Dump:.4f} & {kw.Dump:.4f} \\
1-REF & {s3.oneminusREF:.4f} & {kw.oneminusREF:.4f} \\
No. of online DE hours [$h/y$] & {s3.DE_hours:.0f} & {kw.DE_hours:.0f} \\
No. of LI BS cycles [$/y$] & {s3.BS_cycles:.0f} & {kw.BS_cycles:.0f} \\
Optimal solution & $[n_s, n_w, E_{{b,\; init}}]$ = [{s3.ns:.0f}, {s3.nw:.0f}, {s3.Eb:.2f}] & $[P_{{PV}}, P_{{WT}}, E_{{b}}]$ = [{kw.ns:.2f}, {kw.nw:.2f}, {kw.Eb:.2f}] \\
Weighted objective $J$ & {s3.J:.4f} & {kw.J:.4f} \\
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:LIDE}} Sizing results for the baseline LI+DE system using two sets of decision variables.}}
\end{{table}}

With either approach the hybrid microgrid improves substantially on the diesel-only baseline: LCOE falls by {red_lcoe:.0f}\% (from {s3.LCOE_base:.3f} to {s3.LCOE_abs:.3f}~USD/kWh), emissions by {red_em:.0f}\%, and renewables supply {ref:.1f}\% of generation. The battery cycles only about {s3.BS_cycles:.0f}--{kw.BS_cycles:.0f} times a year, so at 5,475 cycles it would not need replacement within the 25-year project life. The DE runs about {kw.DE_hours:.0f}--{s3.DE_hours:.0f}~h a year, so its 15,000-h life implies roughly one replacement over the project.

The renewable capacity of design (i) is {pv_kw + wt_kw:.1f}~kW, {(pv_kw + wt_kw) / avg_load * 100 - 100:.0f}\% above the average load of {avg_load:.2f}~kW and {(pv_kw + wt_kw) / 15.02 * 100 - 100:.0f}\% above the annual peak of 15.0~kW. The battery stores {s3.Eb / daily * 100:.0f}\% of the average daily consumption of {daily:.0f}~kWh. \cref{{fig:sizing_operation}} shows the resulting rule-based operation over a day, a week and a month. Wind dominates the renewable supply ({s3.E_WT_kWh / (s3.E_WT_kWh + s3.E_PV_kWh) * 100:.0f}\% of renewable energy), because the assumed installed cost per kW is lower for wind than for PV and the scaled station data imply a hub-height mean wind speed of 4.7~m/s. \cref{{app:climate}} and \cref{{sec:sizing_sensitivity}} examine how sensitive this result is to the wind data.

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_sizing_operation.pdf}}
  \caption{{\label{{fig:sizing_operation}} Rule-based operation of the selected LI+DE design (16~kW DE) over 1 January 2018, the first week and the first 30 days: power flows (left) and battery state of charge (right). Battery power is positive when discharging.}}
\end{{figure}}

Global averages of installed costs were used for both PV and WT. Small-scale PV costs have fallen faster than small-scale wind costs over the past decade, so component-specific prices would likely shift the optimum toward PV.

'''
e = Ed()
e.between(r'\subsection{Sizing results}', r'\subsection{Variation of Pareto-optimal combinations of input variables\label{sec:pareto_opt}}', new52, keep_end=True)
# --- break-even
TAC = s3.TAC; CRF = 0.0582; grid_cost = 0.125 * E_load; bed = (TAC - grid_cost) / (157470 * CRF)
newbed = rf'''\subsection{{Break-even distance analysis}}

The break-even distance (BED) is the distance from the existing grid beyond which the stand-alone MG becomes cheaper than extending the grid \cite{{kaabeche2011a}}:
\begin{{align*}}
    BED \; [km] & = \frac{{TAC - LCOE_{{grid}} \cdot \Sigma_{{t=1}}^{{t=8760}}\; P_{{load}}(t)\cdot \Delta t}}{{C_{{ext}} \cdot CRF}}
\end{{align*}}
where $LCOE_{{grid}}$ is the levelized cost of grid electricity and $C_{{ext}}$ the cost of line extension. For the selected design, $TAC = {TAC:,.0f}$~USD/y and $CRF = {CRF}$. With $LCOE_{{grid}} = 0.125$~USD/kWh \cite{{LCOEgrid}} and $C_{{ext}} = 157,470$~USD/km \cite{{Cext}} for Kenya, buying the community's {E_load:,.0f}~kWh from the grid would cost {grid_cost:,.0f}~USD/y before any extension cost, more than the MG's annualized cost. The break-even distance is therefore zero (the formula returns {bed:.2f}~km): the MG is cheaper than grid supply at any distance. Timbila lies about 111~km from Voi, the nearest large town, and 305~km from Nairobi.

The MG's LCOE of {s3.LCOE_abs:.3f}~USD/kWh is at the low end of the 0.12--0.20~USD/kWh residential grid tariff in Kenya \cite{{LCOEgrid}}, and the tariff excludes connection fees of 136--400~USD per household that are prohibitive for rural customers \cite{{quak_CBA, golumbeanu2013}} as well as frequent outages in many peri-urban areas \cite{{iea_africa2019}}. Households without electricity pay far more for kerosene lighting (1.00--2.50~USD/kWh equivalent) \cite{{tracy2012}} or small diesel generators (0.80--1.50~USD/kWh) \cite{{quak_CBA}}. This comparison rests on the model's cost assumptions (IRENA 2018 installed costs and a real discount rate of {(0.09-0.057)/1.057*100:.1f}\%); \cref{{sec:sizing_sensitivity}} shows how LCOE responds to them.

'''
e.between(r'\subsection{Break-even distance analysis}', r'\section{Sensitivity analysis of sizing optimization\label{sec:sizing_sensitivity}}', newbed, keep_end=True)
# --- App. A wind paragraph
w25 = WS.loc['wind_0.75']; w10 = WS.loc['wind_1.00']
newwind = rf'''The TAHMO wind speeds at the Timbila station average only {W['mean_tahmo_raw']:.2f}~m/s, far below typical values for the area. The original analysis therefore scaled the series by a factor of about 3.70 (= 3.19/0.86) so that its annual mean matched forecast-website values for Timbila. For the revision we checked the series against an independent source, NASA POWER hourly data for 2018 at the same coordinates \cite{{nasapower}}, whose wind speeds come from the MERRA-2 reanalysis \cite{{gelaro2017merra2}}. After a {W['lag_h']:.0f}-hour time alignment (chosen by maximizing the correlation of irradiance, $r = {W['r_irr_hourly']:.2f}$), the two wind series agree in timing ($r = {W['r_wind_hourly']:.2f}$ hourly, {W['r_wind_daily']:.2f} for daily and {W['r_wind_monthly']:.2f} for monthly means; \cref{{fig:wind_val}}) but not in level: the reanalysis 2~m wind averages {W['mean_ws2']:.2f}~m/s, {W['s_P']:.2f} times the TAHMO mean, and monthly ratios range from {W['ratio_min']:.2f} to {W['ratio_max']:.2f} (\cref{{tab:wind_val}}). At the 14.5~m hub height, the scaled TAHMO data with the model's 1~m reference height give a mean of {W['hub_model']:.2f}~m/s, while the reanalysis 10~m wind extrapolated with its own 10--50~m shear gives {W['hub_power_shear']:.2f}~m/s, {(1 - W['hub_ratio_power_to_model']) * 100:.0f}\% lower. A 2~m reference height would lower the model's hub-height mean by 9\% ({W['hub_model_href2']:.2f}~m/s). Reanalysis data represent a grid cell of about 50~km in complex terrain near Mount Kilimanjaro rather than the site itself, so neither source is definitive; on-site measurement at hub height would be needed before construction. We keep the original scaling for comparability and report the sensitivity of the design to the wind level in \cref{{sec:sizing_sensitivity}}: scaling the wind input by 0.75, which matches the reanalysis hub-height mean, changes the optimal design from [{w10.ns:.0f}, {w10.nw:.0f}, {w10.Eb:.0f}] to [{w25.ns:.0f}, {w25.nw:.0f}, {w25.Eb:.0f}] and raises LCOE from {w10.LCOE_abs:.3f} to {w25.LCOE_abs:.3f}~USD/kWh. The TAHMO irradiance agrees closely with the CERES irradiance in NASA POWER in timing ($r = {W['r_irr_hourly']:.2f}$) and is {(1 - W['irr_daily_tahmo'] / W['irr_daily_power']) * 100:.0f}\% lower on average ({W['irr_daily_tahmo']:.2f} vs {W['irr_daily_power']:.2f}~kWh/m$^2$/day), so the PV results are, if anything, conservative.

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_wind_validation.pdf}}
  \caption{{\label{{fig:wind_val}} TAHMO station wind (raw and scaled by 3.70) compared with NASA POWER (MERRA-2) wind at 2~m and 10~m for Timbila, 2018: (a) monthly means, (b) mean diurnal profiles after time alignment.}}
\end{{figure}}

\begin{{table}}[htbp]
\centering
\scriptsize
\setlength{{\tabcolsep}}{{3pt}}
\input{{rev_wind_monthly.tex}}
\caption{{\label{{tab:wind_val}} Monthly mean wind speed of the raw TAHMO series and NASA POWER at 2~m, and their ratio (2018).}}
\end{{table}}

'''
e.between(r'It was also found that the wind speeds measured by the TAHMO stations were consistently lower than actual', r'so that the new scaled annual average is close to 3.19 m/s.', newwind.rstrip() + ' ')
e.save()
import shutil, pathlib; shutil.copy(RES / 'wind' / 'monthly_ratios.tex', pathlib.Path.home() / 'mnt' / 'Microgrids_paper_v2' / 'rev_wind_monthly.tex')
print('stage B sizing applied')
