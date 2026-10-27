"""Stage D: Sec. 5.2.4 role of wind turbines (forced n_w, entry thresholds, complementarity)."""
from texedit import Ed
from common import RES
import pandas as pd, numpy as np
W = RES / 'wind_design'
F = pd.read_csv(W / 'forced_nw.csv').set_index('value'); TH = pd.read_csv(W / 'threshold_sweeps.csv'); TL = pd.read_csv(W / 'threshold_lcoe_only.csv')
CF = pd.read_csv(W / 'unit_cf.csv').set_index('wind_scale')
S = pd.read_csv(W / 'series_nw4.csv'); S['h'] = np.tile(np.arange(24), 365); md = [31,28,31,30,31,30,31,31,30,31,30,31]; S['m'] = np.repeat(np.repeat(np.arange(12), md), 24)
f0, f4 = F.loc[0], F.loc[4]
r_h = np.corrcoef(S.P_PV, S.P_WT)[0, 1]; M = S.groupby('m')[['P_PV', 'P_WT']].sum(); r_m = np.corrcoef(M.P_PV, M.P_WT)[0, 1]
sh_surplus = S.P_WT[S.P_PV > S.load].sum() / S.P_WT.sum()
sh_eve = S.P_WT[S.h >= 15].sum() / S.P_WT.sum()
aso = M.P_WT.iloc[7:11].mean() / M.P_WT.drop(M.index[7:11]).mean()
def first(df, tag, cond):
    d = df[df.tag == tag].sort_values('value', ascending=(tag.startswith('wind')))
    d = d[cond(d)]; return d.iloc[0] if len(d) else None
ws_eq = first(TH, 'wind_scale', lambda d: d.nw > 0); ws_lc = first(TL, 'wind_scale_lcoe_only', lambda d: d.nw > 0)
c_lc = first(TL, 'C_WT_lcoe_only', lambda d: d.nw > 0)
c_eq_any = (TH[TH.tag == 'C_WT'].nw > 0).any(); cmin = TH[TH.tag == 'C_WT'].value.min()
lc600 = TL[(TL.tag == 'C_WT_lcoe_only') & (TL.value == 600)].iloc[0]; lc0 = TL[(TL.tag == 'C_WT_lcoe_only') & (TL.value == 1500)].iloc[0]
hub = 4.681
_de = (f4.Em_abs/f0.Em_abs-1)*100
em_txt = ('annual emissions are essentially unchanged' if abs(_de) < 1 else f'annual emissions by {_de:.0f}\\%')
rows = '\n'.join(f"{int(v)} & [{r.ns:.0f}, {r.nw:.0f}, {r.Eb:.0f}] & {r.J:.4f} & {r.LCOE_abs:.3f} & {r.Em_abs:,.0f} & {r.Dump:.3f} & {(1-r.oneminusREF)*100:.1f} & {r.DE_hours:.0f} \\\\" for v, r in F.iterrows() if v in (0, 1, 2, 4, 8, 16))
new = rf'''\subsubsection{{Role of wind turbines\label{{sec:wind_role}}}}
The submitted version of this paper found a PV--wind mix with four turbines. That result came from the turbine power-curve error corrected in this revision (\cref{{app:mg_models}}); with the corrected curve the optimum installs no turbines. To understand why, and when wind would pay, we ran three additional analyses.

\textit{{Cost of including wind.}} We fixed the number of turbines and re-optimized the PV array and battery (best of five PSO runs with a local polish of $E_{{b,\;init}}$; \cref{{tab:wind_forced}}, \cref{{fig:wind_role}}a--b). With the four turbines of the original design, LCOE rises by {(f4.LCOE_abs/f0.LCOE_abs-1)*100:.0f}\% (from {f0.LCOE_abs:.3f} to {f4.LCOE_abs:.3f}~USD/kWh), the weighted objective by {(f4.J/f0.J-1)*100:.0f}\% and {em_txt}, while the battery shrinks by {(1-f4.Eb/f0.Eb)*100:.0f}\% and the PV array by {f0.ns-f4.ns:.0f} modules. The penalty grows steadily with the number of turbines.

\textit{{Why wind adds little here.}} At this site the wind blows mostly in daylight hours, at the same time as the PV output (\cref{{fig:wind_role}}c): hourly PV and wind output are positively correlated ($r = {r_h:.2f}$), and {sh_surplus*100:.0f}\% of the wind energy arrives in hours when PV alone already exceeds the load, so much of it is dumped. Wind does continue into the late afternoon and evening ({sh_eve*100:.0f}\% of wind energy falls after 15:00 local time), which is why it lets the battery shrink. Seasonally, wind is about {aso:.1f} times stronger from August to November than in the rest of the year, but PV output does not drop in those months, so the two resources do not complement each other across seasons either (monthly $r = {r_m:.2f}$). Under the corrected power curve a 3.5~kW turbine has a capacity factor of {CF.loc[1.0,'CF_WT']*100:.0f}\%, close to the {CF.loc[1.0,'CF_PV']*100:.0f}\% of a PV module, at a higher installed cost per kW.

\textit{{When wind would enter.}} We swept the wind resource and the installed turbine cost (best of three to five PSO runs per point). Under the equal-weight objective, turbines enter only when the wind input is scaled by {ws_eq.value:.1f} (a hub-height mean of about {hub*ws_eq.value:.1f}~m/s and a turbine capacity factor of {CF.loc[round(ws_eq.value,2),'CF_WT']*100:.0f}\%), and {('they do not enter at any turbine cost down to ' + f'{cmin:.0f}~USD/kW') if not c_eq_any else 'they enter at lower turbine costs'}, because the extra midday energy raises the dump fraction, which the objective penalizes. Under a cost-only objective ($w_1 = 1$), wind is closer to the margin: turbines enter at an installed cost of {c_lc.value:,.0f}~USD/kW or below ({(1-c_lc.value/1500)*100:.0f}\% below our assumption), or when the wind input is {(ws_lc.value-1)*100:.0f}\% stronger (hub-height mean {hub*ws_lc.value:.1f}~m/s). At 600~USD/kW the cost-optimal design has {lc600.nw:.0f} turbines, a {(1-lc600.Eb/lc0.Eb)*100:.0f}\% smaller battery and a {(1-lc600.LCOE_abs/lc0.LCOE_abs)*100:.0f}\% lower LCOE than the PV-only design. Wind therefore earns a place in the mix at sites with a stronger or more nocturnal wind resource, or where small turbines cost substantially less than assumed here; at Timbila, with the current data and costs, PV with storage is the better choice.

\begin{{table}}[htbp]
\centering
\small
\begin{{tabular}}{{c l c c c c c c}}
\toprule
\textbf{{$n_w$ (fixed)}} & \textbf{{$[n_s, n_w, E_b]$}} & \textbf{{$J$}} & \textbf{{LCOE [USD/kWh]}} & \textbf{{Em. [kg/y]}} & \textbf{{Dump}} & \textbf{{REF [\%]}} & \textbf{{DE [h/y]}} \\
\midrule
{rows}
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:wind_forced}} Best design with a fixed number of wind turbines (16~kW DE, equal weights); PV array and battery re-optimized for each $n_w$.}}
\end{{table}}

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_wind_role.pdf}}
  \caption{{\label{{fig:wind_role}} Role of wind turbines: (a) LCOE and (b) dump fraction, emissions and battery capacity (relative to their maxima) when the number of turbines is fixed and the PV array and battery are re-optimized; (c) mean daily profiles of load, PV output (divided by 10) and wind output for the design with four turbines.}}
\end{{figure}}

'''
e = Ed()
anchor = r'\subsection{Pareto approximation\label{sec:pareto_opt}}'
assert e.s.count(anchor) == 1
if r'\label{sec:wind_role}' in e.s:
    i = e.s.index(r'\subsubsection{Role of wind turbines'); e.s = e.s[:i] + e.s[e.s.index(anchor):]
e.s = e.s.replace(anchor, new + anchor); e.log.append('wind role')
e.save()
