"""Stage B (part 2): Sec. 6 sensitivity analysis rewritten from the corrected sweeps."""
from texedit import Ed
from common import RES
import pandas as pd, numpy as np
S = pd.read_csv(RES / 'rerun' / 'sweeps.csv'); WS = pd.read_csv(RES / 'short_runs' / 'wind_sweep.csv')
g = lambda t: S[S.tag == t].sort_values('value').reset_index(drop=True)
dg, fp, it, inf, bp = g('DG_rating'), g('diesel_price'), g('interest'), g('inflation'), g('LI_price')
# DG rating facts
zero = dg[dg.DPSP <= 1e-9].value; full_rel = min(v for v in zero if all(dg[dg.value >= v].DPSP <= 1e-9))
r8 = dg[dg.value == 8].iloc[0]; r0 = dg[dg.value == 0].iloc[0]; r16 = dg[dg.value == 16].iloc[0]; r20 = dg[dg.value == 20].iloc[0]
le1 = dg[dg.DPSP <= 0.01].value.min()
fp0, fp1 = fp.iloc[0], fp.iloc[-1]; it0, it1 = it.iloc[0], it.iloc[-1]; inf0, inf1 = inf.iloc[0], inf.iloc[-1]; bp0, bp1 = bp.iloc[0], bp.iloc[-1]
def rng(d, c, f='{:.3f}'): return f.format(d[c].min()) + '--' + f.format(d[c].max())
wsr = WS.sort_values('value').reset_index(drop=True)
wrows = '\n'.join(f"{r.value:.2f} & [{r.ns:.0f}, {r.nw:.0f}, {r.Eb:.1f}] & {r.ns*0.255:.2f} & {r.nw*3.5:.1f} & {r.J:.4f} & {r.LCOE_abs:.3f} & {r.Em_abs:,.0f} & {(1-r.oneminusREF)*100:.1f} & {r.E_WT_kWh/(r.E_WT_kWh+r.E_PV_kWh)*100:.0f} \\\\" for r in wsr.itertuples())
wl, wm, wh = wsr.iloc[0], wsr.iloc[1], wsr.iloc[2]
jmin = dg.loc[dg.J.idxmin()]
dg_text = (f"Without any DG, {r0.DPSP*100:.1f}\\% of the load is lost, yet the equal-weight objective ($J$ = {r0.J:.4f}) is " + ("the lowest of all ratings" if jmin.value == 0 else f"only {r0.J - jmin.J:.4f} above its minimum at {jmin.value:.0f}~kW") + ": with equal weights, a 10\\% loss of load adds only 0.02 to $J$, so the scalarized objective undervalues reliability for an off-grid community.")
NAMES_ = {'diesel_price': 'the highest fuel prices', 'interest': 'the lowest interest rates', 'inflation': 'the highest inflation rates', 'LI_price': 'the lowest battery prices', 'DG_rating': 'some DG ratings'}
SW_ = S[S.tag.isin(list(NAMES_))]; atb = SW_[(SW_.ns >= 399) | (SW_.nw >= 40) | (SW_.Eb >= 399)]
bound_text = ("The upper bound on battery capacity (400~kWh) binds only at " + (lambda L: ', '.join(L[:-1]) + ' and ' + L[-1] if len(L) > 1 else L[0])([NAMES_[t] for t in atb.tag.unique()]) + "; there the optimum would install more storage. ") if len(atb) else ""
def _d(r): return f"[{r.ns:.0f}, {r.nw:.0f}, {r.Eb:.0f}]"
wsweep_text = ("The design installs no wind turbines at 0.75 and 1.00 times the default wind, so the uncertain wind level does not affect the base result. " if (wl.nw == 0 and wm.nw == 0) else f"With 25\\% less wind the optimal design changes from {_d(wm)} to {_d(wl)} and LCOE from {wm.LCOE_abs:.3f} to {wl.LCOE_abs:.3f}~USD/kWh. ") \
    + (f"With 25\\% more wind the optimum adds {wh.nw:.0f} turbines ({_d(wh)}) and LCOE falls to {wh.LCOE_abs:.3f}~USD/kWh, so wind becomes competitive only if the resource is above our default estimate." if wh.nw > 0 else f"Even with 25\\% more wind the optimum installs no turbines ({_d(wh)}).") \
    + " The hybrid system with renewables, Li-ion storage and DE backup beats diesel-only supply across this range."
def fig(tag, cap): return rf'''
\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_vary_{tag}.pdf}}
  \caption{{\label{{fig:vary_{tag}}} {cap} (a) normalized objectives and weighted objective $J$; (b) absolute LCOE of the hybrid MG and of the diesel-only baseline; (c) rated PV and WT capacity; (d) battery capacity. Each point is the best of three integer-coded PSO runs.}}
\end{{figure}}
'''
new = rf'''\section{{Sensitivity analysis of sizing optimization\label{{sec:sizing_sensitivity}}}}

We assess the sensitivity of the design by varying one parameter at a time and re-optimizing the sizing problem at each value; all other parameters keep the defaults in \cref{{tab:default}}. Each point is the best of three integer-coded PSO runs. {bound_text}Because LCOE is normalized by a diesel-only baseline that itself depends on fuel price and financial parameters (\cref{{app:costs}}), every figure reports absolute LCOE next to the normalized objectives.

\begin{{table}}[htbp]
\centering
\begin{{tabular}}{{@{{}}lc@{{}}}}
\toprule
\textbf{{Parameter}}                 & \textbf{{Default value}}                        \\ \midrule
DG power rating [$kW$]         & 16                                            \\
Diesel fuel price [USD/US gal] & 3.20                                          \\
Nominal interest rate (\%)         & 9                                             \\
Inflation rate (\%)                & 5.70                                           \\
Price of BS ($\$/kWh$)               & 300  \\
{{[}}$w_1$ $w_2$ $w_3$ $w_4$ $w_5${{]}}  &  [0.2 0.2 0.2 0.2 0.2] \\ 
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:default}} Default parameter values used for sensitivity analysis.}}
\end{{table}}

\subsection{{Varying DG power rating}}
With the default 16~kW DG, DPSP is zero for every design because the DG exceeds the annual peak load. We varied the DG rating from 0 to 20~kW, keeping the normalization baseline at 16~kW (\cref{{fig:vary_DG_rating}}). DPSP is zero for ratings of {full_rel:.0f}~kW and above, and stays below 1\% down to {le1:.0f}~kW; an 8~kW DG gives DPSP = {r8.DPSP:.4f}. LCOE is {r8.LCOE_abs:.3f}~USD/kWh with an 8~kW DG, {r16.LCOE_abs:.3f} with 16~kW and {r20.LCOE_abs:.3f} with 20~kW; larger generators add capital and fixed O\&M costs. {dg_text} \cref{{sec:pareto_rel}} therefore treats reliability as an explicit constraint.
{fig('DG_rating', 'Effect of the DG power rating.')}
\subsection{{Varying fuel price}}
The diesel price was varied from 0.2 to 12~USD/gal, the range of current global prices \cite{{diesel_price}} (\cref{{fig:vary_diesel_price}}). The absolute LCOE of the hybrid MG rises from {fp0.LCOE_abs:.3f} to {fp1.LCOE_abs:.3f}~USD/kWh, while the normalized LCOE falls, because the diesel-only baseline rises much faster (from {fp0.LCOE_base:.3f} to {fp1.LCOE_base:.3f}~USD/kWh). Across the price range the battery changes from {fp0.Eb:.0f} to {fp1.Eb:.0f}~kWh, the PV array from {fp0.ns*0.255:.0f} to {fp1.ns*0.255:.0f}~kW and DE operation from {fp0.DE_hours:.0f} to {fp1.DE_hours:.0f}~h per year. At the 2.0~USD/L (7.57~USD/gal) level typical of remote sites the hybrid system's advantage over diesel-only supply grows further.
{fig('diesel_price', 'Effect of the diesel price.')}
\subsection{{\label{{sec:varyInterest}} Varying nominal interest or discount rate}}
The nominal interest rate sets the opportunity cost of capital and hence the trade-off between capital-intensive renewables and storage and fuel-intensive backup generation. We varied it from 0 to 20\%, the current spread of central bank rates \cite{{interest_rates}} (\cref{{fig:vary_interest}}). With inflation fixed at 5.7\%, the real discount rate $r = (i - f)/(1 + f)$ ranges from $-5.4\%$ to $13.5\%$. Higher rates penalize upfront investment: from 0 to 20\% the battery changes from {it0.Eb:.0f} to {it1.Eb:.0f}~kWh, the PV array from {it0.ns*0.255:.0f} to {it1.ns*0.255:.0f}~kW, DE operation from {it0.DE_hours:.0f} to {it1.DE_hours:.0f}~h per year, and LCOE from {it0.LCOE_abs:.3f} to {it1.LCOE_abs:.3f}~USD/kWh. Interest rates in many SSA countries sit in the upper half of this range, which makes concessional finance an important lever for off-grid renewables.
{fig('interest', 'Effect of the nominal interest rate.')}
\subsection{{Varying inflation rate}}
Inflation was varied from 0 to 15\%, the range currently observed worldwide \cite{{inflation_rate}} (\cref{{fig:vary_inflation}}). At a fixed nominal interest rate of 9\%, higher inflation lowers the real discount rate, so the effect mirrors that of the interest rate: as inflation rises from 0 to 15\%, LCOE changes from {inf0.LCOE_abs:.3f} to {inf1.LCOE_abs:.3f}~USD/kWh and the battery from {inf0.Eb:.0f} to {inf1.Eb:.0f}~kWh.
{fig('inflation', 'Effect of the inflation rate.')}
\subsection{{Varying price of battery energy storage (BS)}}
Li-ion prices have fallen steeply and are projected to keep falling \cite{{bnef}}, so we varied the battery price from 50 to 300~USD/kWh (\cref{{fig:vary_LI_price}}). At 50~USD/kWh the optimal battery is {bp0.Eb:.0f}~kWh, against {bp1.Eb:.0f}~kWh at 300~USD/kWh; DE operation is {bp0.DE_hours:.0f} vs {bp1.DE_hours:.0f}~h per year and LCOE {bp0.LCOE_abs:.3f} vs {bp1.LCOE_abs:.3f}~USD/kWh.
{fig('LI_price', 'Effect of the Li-ion battery price.')}
\subsection{{Varying the wind-speed correction factor\label{{sec:windsens}}}}
The wind input rests on station data scaled by a factor of 3.70 (\cref{{app:climate}}). A comparison with NASA POWER reanalysis suggests that the resulting hub-height wind may be about 25\% too high, so we re-optimized the design with the wind input scaled by 0.75, 1.00 and 1.25 (\cref{{tab:wind_sweep}}). {wsweep_text}

\begin{{table}}[htbp]
\centering
\scriptsize
\setlength{{\tabcolsep}}{{4pt}}
\begin{{tabular}}{{c l c c c c c c c}}
\toprule
\textbf{{Factor}} & \textbf{{$[n_s, n_w, E_b]$}} & \textbf{{PV [kW]}} & \textbf{{WT [kW]}} & \textbf{{$J$}} & \textbf{{LCOE [USD/kWh]}} & \textbf{{Em. [kg/y]}} & \textbf{{REF [\%]}} & \textbf{{WT share [\%]}} \\
\midrule
{wrows}
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:wind_sweep}} Optimal design when the wind input is scaled by 0.75, 1.00 and 1.25, i.e.\ with wind correction factors of 2.78, 3.70 and 4.63. WT share: wind share of renewable energy.}}
\end{{table}}

'''
e = Ed()
e.between(r'\section{Sensitivity analysis of sizing optimization\label{sec:sizing_sensitivity}}', r'\section{\label{sec:dispatch_opt} Optimal economic and environmental dispatch results}', new, keep_end=True)
e.save()
