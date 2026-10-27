"""Stage B (part 1): Sec. 5.2 sizing results, break-even analysis, App. A wind text. Numbers from results CSVs."""
from texedit import Ed
from common import RES
import pandas as pd, json, numpy as np
T = pd.read_csv(RES / 'rerun' / 'main_tables.csv').set_index('tag'); TT = pd.read_csv(RES / 'rerun' / 'tech_tables.csv').set_index('tech')
SS = pd.read_csv(RES / 'short_runs' / 'strategy_stress.csv').set_index('tag')
W = json.load(open(RES / 'wind' / 'wind_validation.json')); WS = pd.read_csv(RES / 'short_runs' / 'wind_sweep.csv').set_index('tag')
s3, s3o, kw, d8 = T.loc['S3'], T.loc['S3_original_fuel_model'], T.loc['LIDE_ii_kW'], T.loc['DG8kW']
_cf = pd.read_csv(RES / 'wind_design' / 'unit_cf.csv').set_index('wind_scale'); CF_WT, CF_PV = _cf.loc[1.0, 'CF_WT'], _cf.loc[1.0, 'CF_PV']
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
cells4 = [(c, l) for c in [3.20, 5.00, 7.57] for l in [5475, 3000] if SS.loc[f'S4_C{c:.2f}_L{l}','LCOE_abs'] < SS.loc[f'S3_C{c:.2f}_L{l}','LCOE_abs']]
def gap_txt(g, n):
    pre = 'by at most ' if n > 1 else 'by '
    return ('by less than 0.001~USD/kWh' if g < 0.0005 else pre + f'{g:.3f}~USD/kWh')
if cells4: stress_sentence += ', although Strategy 4 reaches a slightly lower absolute LCOE in ' + ' and '.join(f'the {c:.2f}~USD/gal, {l:,}-cycle case' for c, l in cells4) + ' (' + gap_txt(max(SS.loc[f'S3_C{c:.2f}_L{l}','LCOE_abs'] - SS.loc[f'S4_C{c:.2f}_L{l}','LCOE_abs'] for c, l in cells4), len(cells4)) + ')'
L3 = SS[SS.index.str.endswith('L3000')]; L5 = SS[SS.index.str.endswith('L5475')]
stress_sentence += (f'. With the default 5,475-cycle life the battery completes {L5.BS_cycles.min():.0f}--{L5.BS_cycles.max():.0f} equivalent full cycles a year. '
    + f'With a 3,000-cycle life the optimum enlarges the battery to about {L3.Eb.median():.0f}~kWh, so that it completes about {L3.BS_cycles.median():.0f} cycles a year and lasts the 25-year project without replacement, and LCOE rises to {L3.LCOE_abs.min():.3f}--{L3.LCOE_abs.max():.3f}~USD/kWh')
wsh = s3.E_WT_kWh / (s3.E_WT_kWh + s3.E_PV_kWh) * 100
wind_text = ((f"The optimum installs no wind turbines. With the scaled station data, a 3.5~kW turbine at the 14.5~m hub height has a capacity factor of {CF_WT*100:.0f}\\%, close to the {CF_PV*100:.0f}\\% of a PV module, but wind costs 1,500~USD/kW installed against 1,210~USD/kW for PV, so PV supplies the renewable energy more cheaply. " if s3.nw == 0 else f"Wind supplies {wsh:.0f}\\% of the renewable energy. ")
    + "\\cref{sec:wind_role} examines why, and at what wind resource and turbine cost wind would enter the mix.")
w25 = WS.loc['wind_0.75']; w10 = WS.loc['wind_1.00']; w125 = WS.loc['wind_1.25']
wind_app = ("the optimal design installs no wind turbines whether the wind input is scaled by 0.75 (which matches the reanalysis hub-height mean), 1.00 or 1.25, so the uncertainty in the wind data does not change the result." if (w25.nw == 0 and w10.nw == 0 and w125.nw == 0) else
    f"scaling the wind input by 0.75, which matches the reanalysis hub-height mean, changes the optimal design from [{w10.ns:.0f}, {w10.nw:.0f}, {w10.Eb:.0f}] to [{w25.ns:.0f}, {w25.nw:.0f}, {w25.Eb:.0f}] and LCOE from {w10.LCOE_abs:.3f} to {w25.LCOE_abs:.3f}~USD/kWh; scaling it by 1.25 gives [{w125.ns:.0f}, {w125.nw:.0f}, {w125.Eb:.0f}] at {w125.LCOE_abs:.3f}~USD/kWh.")
tj = {'LI+DE': s3.J, 'LI+MT': TT.loc['LI_MT','J'], 'LA+DE': TT.loc['LA_DE','J'], 'LA+MT': TT.loc['LA_MT','J']}
order_t = sorted(tj, key=tj.get)
tech_text = (f"LI+DE gives the lowest weighted objective ({s3.J:.4f}), followed by " + ', '.join(f"{k} ({tj[k]:.4f})" for k in order_t[1:]) + ". "
    + f"Lead-acid needs a much larger nominal capacity ({TT.loc['LA_DE','Eb']:.0f}~kWh with DE) because only 40\\% of it is usable and its round-trip efficiency is 75\\%, which raises its cost despite the lower price per kWh.")
S4r = T.loc['S4']; best_lcoe = min(['S1','S2','S3','S4'], key=lambda k: T.loc[k,'LCOE_abs'])
strat_text = (f"Strategy 3 gives the lowest weighted objective ({s3.J:.4f})" + (f" and the lowest absolute LCOE ({s3.LCOE_abs:.3f}~USD/kWh)" if best_lcoe == 'S3' else f"; Strategy {best_lcoe[1]} has the lowest absolute LCOE ({T.loc[best_lcoe,'LCOE_abs']:.3f}~USD/kWh)") + ", and we use Strategy 3 in all subsequent results. "
    + f"Storing the generator's minimum-load surplus (Strategies 1 and 3) lowers dumped energy and fuel use relative to dumping it (Strategies 2 and 4). "
    + f"Cycle-based replacement (Strategies 3 and 4) costs less than a fixed 15-year schedule because the battery completes only about {s3.BS_cycles:.0f} equivalent full cycles a year, so its 5,475-cycle life " + ("outlasts the 25-year project." if 5475/s3.BS_cycles >= 25 else f"lasts about {5475/s3.BS_cycles:.0f} years."))
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

\cref{{tab:strat}} lists the best design found for each strategy (best of ten integer-coded PSO runs). {strat_text}

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
The MG designer also has to choose the battery and backup generator technologies. Four combinations were sized (\cref{{tab:tech_select}}). {tech_text} LCOE and emissions are normalized with respect to a single-DG system of the same technology; the baseline values are listed in \cref{{tab:baseline}}.

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

Microturbines running on natural gas have lower specific emissions than diesel engines and, alone, a lower LCOE (\cref{{tab:baseline}}). Yet the MG with a DE backup has lower emissions and costs than the one with an MT backup, because the backup runs for only about {s3.DE_hours:.0f}~h per year: the MT's higher capital cost is not recovered by its fuel savings over so few operating hours. Lead-acid is costlier in both configurations: with DE backup its LCOE exceeds that of the diesel-only system.

\subsubsection{{Optimal capacities for baseline LI+DE system}}

We sized the LI+DE system with two sets of decision variables: (i) unit counts $[n_s, n_w, E_{{b,\;init}}]$ with integer $n_s$ and $n_w$, and (ii) total rated powers $[P_{{PV,\;r,\;total}}, P_{{WT,\;r,\;total}}, E_{{b,\;init}}]$ treated as continuous. Design (i) corresponds to [{pv_kw:.2f}~kW, {wt_kw:.1f}~kW, {s3.Eb:.1f}~kWh] in rated terms and design (ii) to [{kw.ns:.2f}~kW, {kw.nw:.2f}~kW, {kw.Eb:.1f}~kWh]. The two approaches give practically the same design and objective ({kw.J:.5f} vs {s3.J:.5f}); the continuous approach (ii) is marginally lower because it is not restricted to whole PV modules and turbines, while a designer limited to specific products should use approach (i).

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

With either approach the hybrid microgrid improves substantially on the diesel-only baseline: LCOE falls by {red_lcoe:.0f}\% (from {s3.LCOE_base:.3f} to {s3.LCOE_abs:.3f}~USD/kWh), emissions by {red_em:.0f}\%, and renewables supply {ref:.1f}\% of generation. The battery completes about {min(s3.BS_cycles, kw.BS_cycles):.0f}--{max(s3.BS_cycles, kw.BS_cycles):.0f} equivalent full cycles a year, so its 5,475-cycle life {'outlasts the 25-year project' if 5475/max(s3.BS_cycles, kw.BS_cycles) >= 25 else 'requires one replacement over the project'}. The DE runs about {min(kw.DE_hours, s3.DE_hours):.0f}--{max(kw.DE_hours, s3.DE_hours):.0f}~h a year, {'well within its 15,000-h life over 25 years' if 25*max(kw.DE_hours, s3.DE_hours) < 15000 else 'so its 15,000-h life implies one replacement over the project'}.

The renewable capacity of design (i) is {pv_kw + wt_kw:.1f}~kW, {(pv_kw + wt_kw) / avg_load:.1f} times the average load of {avg_load:.2f}~kW and {(pv_kw + wt_kw) / 15.02:.1f} times the annual peak of 15.0~kW, and the battery holds {s3.Eb / daily:.2f} days of average consumption ({daily:.0f}~kWh/day). This overbuild is the price of supplying {ref:.0f}\% of the energy from a single variable source: {s3.Dump*100:.0f}\% of the generated energy is still dumped. \cref{{fig:sizing_operation}} shows the resulting rule-based operation over a day, a week and a month. {wind_text}

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_sizing_operation.pdf}}
  \caption{{\label{{fig:sizing_operation}} Rule-based operation of the selected LI+DE design (16~kW DE) over 1 January 2018, the first week and the first 30 days: power flows (left) and battery state of charge (right). Battery power is positive when discharging.}}
\end{{figure}}

Global averages of installed costs were used for both PV and WT; small turbines usually cost more per kW than these averages, which would further favor PV.

'''
e = Ed()
e.between(r'\subsection{Sizing results}', r'\subsection{Variation of Pareto-optimal combinations of input variables\label{sec:pareto_opt}}', new52, keep_end=True)
# --- break-even
TAC = s3.TAC; CRF = 0.0582; grid_cost = 0.125 * E_load; bed = (TAC - grid_cost) / (157470 * CRF)
bed_txt = ("This is more than the MG's annualized cost, so the break-even distance is zero: the MG is cheaper than grid supply at any distance." if bed <= 0 else
    f"The MG's annualized cost is {TAC - grid_cost:,.0f}~USD/y higher, but each kilometer of line extension costs {157470*CRF:,.0f}~USD/y when annualized, so the break-even distance is only {bed:.2f}~km: farther from the grid than this, the MG is the cheaper option.")
newbed = rf'''\subsection{{Break-even distance analysis}}

The break-even distance (BED) is the distance from the existing grid beyond which the stand-alone MG becomes cheaper than extending the grid \cite{{kaabeche2011a}}:
\begin{{align*}}
    BED \; [km] & = \frac{{TAC - LCOE_{{grid}} \cdot \Sigma_{{t=1}}^{{t=8760}}\; P_{{load}}(t)\cdot \Delta t}}{{C_{{ext}} \cdot CRF}}
\end{{align*}}
where $LCOE_{{grid}}$ is the levelized cost of grid electricity and $C_{{ext}}$ the cost of line extension. For the selected design, $TAC = {TAC:,.0f}$~USD/y and $CRF = {CRF}$. With $LCOE_{{grid}} = 0.125$~USD/kWh \cite{{LCOEgrid}} and $C_{{ext}} = 157,470$~USD/km \cite{{Cext}} for Kenya, buying the community's {E_load:,.0f}~kWh from the grid would cost {grid_cost:,.0f}~USD/y before any extension cost. {bed_txt} Timbila lies about 111~km from Voi, the nearest large town, and 305~km from Nairobi.

The MG's LCOE of {s3.LCOE_abs:.3f}~USD/kWh is {'below' if s3.LCOE_abs < 0.12 else ('within' if s3.LCOE_abs <= 0.20 else 'above')} the 0.12--0.20~USD/kWh residential grid tariff in Kenya \cite{{LCOEgrid}}, and the tariff excludes connection fees of 136--400~USD per household that are prohibitive for rural customers \cite{{quak_CBA, golumbeanu2013}} as well as frequent outages in many peri-urban areas \cite{{iea_africa2019}}. Households without electricity pay far more for kerosene lighting (1.00--2.50~USD/kWh equivalent) \cite{{tracy2012}} or small diesel generators (0.80--1.50~USD/kWh) \cite{{quak_CBA}}. This comparison rests on the model's cost assumptions (IRENA 2018 installed costs and a real discount rate of {(0.09-0.057)/1.057*100:.1f}\%); \cref{{sec:sizing_sensitivity}} shows how LCOE responds to them.

'''
e.between(r'\subsection{Break-even distance analysis}', r'\section{Sensitivity analysis of sizing optimization\label{sec:sizing_sensitivity}}', newbed, keep_end=True)
# --- App. A wind paragraph
w25 = WS.loc['wind_0.75']; w10 = WS.loc['wind_1.00']
newwind = rf'''The TAHMO wind speeds at the Timbila station average only {W['mean_tahmo_raw']:.2f}~m/s, far below typical values for the area. The original analysis therefore scaled the series by a factor of about 3.70 (= 3.19/0.86) so that its annual mean matched forecast-website values for Timbila. For the revision we checked the series against an independent source, NASA POWER hourly data for 2018 at the same coordinates \cite{{nasapower}}, whose wind speeds come from the MERRA-2 reanalysis \cite{{gelaro2017merra2}}. The station time stamps lead local time: the irradiance series match best after a {W['lag_h']:.0f}-hour shift ($r = {W['r_irr_hourly']:.2f}$), and the load profile is in local time, so in this revision we shift all station series (irradiance, temperature and wind) by {W['lag_h']:.0f}~h; the submitted version used the unshifted series. After this alignment the two wind series agree in timing ($r = {W['r_wind_hourly']:.2f}$ hourly, {W['r_wind_daily']:.2f} for daily and {W['r_wind_monthly']:.2f} for monthly means; \cref{{fig:wind_val}}) but not in level: the reanalysis 2~m wind averages {W['mean_ws2']:.2f}~m/s, {W['s_P']:.2f} times the TAHMO mean, and monthly ratios range from {W['ratio_min']:.2f} to {W['ratio_max']:.2f} (\cref{{tab:wind_val}}). At the 14.5~m hub height, the scaled TAHMO data with the model's 1~m reference height give a mean of {W['hub_model']:.2f}~m/s, while the reanalysis 10~m wind extrapolated with its own 10--50~m shear gives {W['hub_power_shear']:.2f}~m/s, {(1 - W['hub_ratio_power_to_model']) * 100:.0f}\% lower. A 2~m reference height would lower the model's hub-height mean by 9\% ({W['hub_model_href2']:.2f}~m/s). Reanalysis data represent a grid cell of about 50~km in complex terrain near Mount Kilimanjaro rather than the site itself, so neither source is definitive; on-site measurement at hub height would be needed before construction. We keep the original scaling for comparability and report the sensitivity of the design to the wind level in \cref{{sec:sizing_sensitivity}}: {wind_app} The TAHMO irradiance agrees closely with the CERES irradiance in NASA POWER in timing ($r = {W['r_irr_hourly']:.2f}$) and is {(1 - W['irr_daily_tahmo'] / W['irr_daily_power']) * 100:.0f}\% lower on average ({W['irr_daily_tahmo']:.2f} vs {W['irr_daily_power']:.2f}~kWh/m$^2$/day), so the PV results are, if anything, conservative.

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
