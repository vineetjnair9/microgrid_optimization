"""Stage D: Pareto analysis, selection rules and cost-reliability front (Secs. 5.3-5.5)."""
from texedit import Ed
from common import RES
import pandas as pd, numpy as np, shutil, pathlib
MS = pathlib.Path.home() / 'mnt' / 'Microgrids_paper_v2'
IS = dict(l.split(' = ') for l in open(RES / 'pareto' / 'inputs_stats.txt').read().splitlines())
PK = dict(l.split(' = ') for l in open(RES / 'pareto' / 'key_numbers.txt').read().splitlines())
r2 = float(open(RES / 'pareto' / 'ref_em_r2.txt').read().split(' = ')[1])
F7 = pd.DataFrame(np.loadtxt(RES / 'rerun' / 'pareto_7kW_4obj.csv', delimiter=',')[:, 3:7], columns=['LCOE', 'Em', 'DPSP', 'Dump'])
rho = F7.corr('spearman')
RX = pd.read_csv(RES / 'pareto' / 'representatives_exact.csv')
T = pd.read_csv(RES / 'rerun' / 'main_tables.csv').set_index('tag'); s3 = T.loc['S3']
DV = pd.read_csv(RES / 'short_runs' / 'dg_variable.csv'); EP = pd.read_csv(RES / 'short_runs' / 'eps_front.csv').sort_values('value').reset_index(drop=True)
dv = DV.loc[DV.J.idxmin()]; ndv = int((DV.value.round(2) == round(dv.value, 2)).sum())
e0, e1, e5 = EP.iloc[0], EP[EP.value == 0.01].iloc[0], EP.iloc[-1]
LAB = {'min_LCOE_n': 'Min LCOE', 'min_Em_n': 'Min emissions', 'min_Dump': 'Min dump', 'min_oneminusREF': 'Max REF', 'knee': 'Knee', 'compromise_L2': 'Compromise ($L_2$)',
       'TOPSIS_equal': 'TOPSIS, equal', 'TOPSIS_cost': 'TOPSIS, cost', 'TOPSIS_sustain': 'TOPSIS, sustainability', 'min_DPSP': 'Min DPSP', 'TOPSIS_reliability': 'TOPSIS, reliability'}
rows = []
for _, r in RX.iterrows():
    fr, lab = r.tag.split('_', 1)
    if lab == 'min_oneminusREF' or (fr == '7kW' and lab == 'min_DPSP'): continue  # identical to min emissions
    rows.append(f"{fr.replace('kW', '~kW')} & {LAB[lab]} & [{r.ns:.0f}, {r.nw:.0f}, {r.Eb:.0f}] & {r.LCOE_abs:.3f} & {r.Em_abs:,.0f} & {r.DPSP*100:.2f} & {r.Dump:.3f} & {(1-r.oneminusREF)*100:.1f} & {r.J:.4f} \\\\")
rows.insert(0, f"16~kW & Weighted-sum PSO & [{s3.ns:.0f}, {s3.nw:.0f}, {s3.Eb:.0f}] & {s3.LCOE_abs:.3f} & {s3.Em_abs:,.0f} & {s3.DPSP*100:.2f} & {s3.Dump:.3f} & {(1-s3.oneminusREF)*100:.1f} & {s3.J:.4f} \\\\")
R16 = RX[RX.tag.str.startswith('16kW')].set_index('tag')
kn, cp, te, tc, tsu, ml = [R16.loc[f'16kW_{k}'] for k in ['knee', 'compromise_L2', 'TOPSIS_equal', 'TOPSIS_cost', 'TOPSIS_sustain', 'min_LCOE_n']]
TAB = '\n'.join(rows)
e0_txt = ('about the same as' if abs(1 - e0.LCOE_abs / s3.LCOE_abs) < 0.01 else f'{(1 - e0.LCOE_abs / s3.LCOE_abs) * 100:.0f}\\% below')
bat_txt = (f'the largest battery allowed ({te.Eb:.0f}~kWh)' if abs(te.Eb - tsu.Eb) < 1 and te.Eb >= 399 else f'larger batteries ({te.Eb:.0f} and {tsu.Eb:.0f}~kWh)')
new = rf'''\subsection{{Pareto approximation\label{{sec:pareto_opt}}}}

The weighted-sum problem in Eq.~(\ref{{eq:sizing}}) has a single minimum value, but the five-objective problem behind it has no single optimum: along the Pareto front, any improvement in one objective worsens at least one other. The Pareto set contains the designs that no other design matches or beats in every objective while beating them in at least one. We approximate this set with the pattern-search multiobjective solver \texttt{{paretosearch}} in MATLAB's Global Optimization Toolbox (200 points, integer-coded unit counts, 16~kW DE). The points are mutually non-dominated: they represent different trade-offs, not equally good designs, and choosing among them requires stated preferences or a selection rule (\cref{{sec:pareto_select}}).

\cref{{fig:pareto_inputs}} shows the designs on the front. PV capacity ranges from {float(IS['PV_min']):.0f} to {float(IS['PV_max']):.0f}~kW and battery capacity from {float(IS['EB_min']):.0f} to {float(IS['EB_max']):.0f}~kWh; {IS['N_EB400']} of the {IS['N']} points sit at the 400~kWh upper bound, at the low-emission end of the front. {IS['N_WT0']} points install no wind turbine, and the rest at most {float(IS['WT_max']):.0f}~kW, mainly in low-dump designs with small PV arrays. Normalized emissions and $(1-REF)$ are almost perfectly correlated along the front ($R^2 = {r2:.3f}$, \cref{{fig:correl}}), because the DE is the only source of both; one of the two objectives is therefore redundant for this system. With a 16~kW DE, DPSP is zero everywhere on the front.

To expose the reliability dimension we also computed a four-objective front (LCOE, emissions, DPSP and dump) with a 7~kW DE and rated-power decision variables (\cref{{fig:pareto_obj}}). Along this front, dumped energy trades off almost one-for-one against emissions and DPSP (Spearman $\rho = {rho.loc['Dump','Em']:.2f}$ and ${rho.loc['Dump','DPSP']:.2f}$): avoiding dumped energy requires smaller renewable arrays, which leaves more load to the small DE and, when the DE is at its rating, unserved. Emissions and DPSP rise together ($\rho = {rho.loc['Em','DPSP']:.2f}$), so for this system the cleanest designs are also the most reliable. LCOE is only weakly related to the other objectives along the front ($|\rho| \leq {max(abs(rho.loc['LCOE','Em']), abs(rho.loc['LCOE','DPSP']), abs(rho.loc['LCOE','Dump'])):.2f}$): the cost-optimal region is flat, and moderate changes in emissions or dump cost little.

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_pareto_inputs.pdf}}
  \caption{{\label{{fig:pareto_inputs}} Designs on the 16~kW Pareto approximation (\texttt{{paretosearch}}, five objectives): (a) battery vs PV capacity and (b) WT vs PV capacity, colored by normalized LCOE.}}
\end{{figure}}

\begin{{figure}}[htbp]
\centering
    \includegraphics[width=0.42\linewidth]{{rev_ref_emissions.pdf}}
  \caption{{\label{{fig:correl}} Normalized emissions vs $(1-REF)$ along the 16~kW Pareto approximation.}}
\end{{figure}}

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_pareto_objectives.pdf}}
  \caption{{\label{{fig:pareto_obj}} Pairwise relationships between the objectives on the four-objective Pareto approximation with a 7~kW DE (\texttt{{paretosearch}}, 200 points).}}
\end{{figure}}

\subsection{{Selecting designs from the Pareto set\label{{sec:pareto_select}}}}
A Pareto set is useful to a designer only with a rule for choosing from it. We extract four kinds of representative design from each front. All objectives are first min--max normalized over the front, and objectives that are constant on the front (DPSP with the 16~kW DE) are dropped.
\begin{{itemize}}
\item \textit{{Extreme solutions}}: the best design for each single objective.
\item \textit{{Knee point}}: the design with the largest distance below the hyperplane through the extreme solutions, where a small gain in one objective costs a large loss in another \cite{{deb2011knee}}.
\item \textit{{Compromise solution}}: the design closest to the ideal point in the $L_2$ norm.
\item \textit{{TOPSIS}} \cite{{hwang1981topsis}}: the design with the highest relative closeness to the ideal and distance from the anti-ideal solution, under three weightings: equal; cost priority (four times the weight on LCOE); and sustainability priority (2.5 times the weight on emissions and $(1-REF)$) for the 16~kW front, or reliability priority (three times the weight on DPSP) for the 7~kW front.
\end{{itemize}}
Each representative is rounded to whole PV modules and turbines and re-evaluated exactly (\cref{{tab:pareto_reps}}, \cref{{fig:pareto_reps}}).

On the 16~kW front the compromise solution and the cost-priority TOPSIS choice coincide at [{cp.ns:.0f}, {cp.nw:.0f}, {cp.Eb:.0f}] (LCOE {cp.LCOE_abs:.3f}~USD/kWh). Equal-weight and sustainability-priority TOPSIS choose {bat_txt}, which cut emissions to {te.Em_abs:,.0f} and {tsu.Em_abs:,.0f}~kg/y at an LCOE of {te.LCOE_abs:.3f} and {tsu.LCOE_abs:.3f}~USD/kWh. The knee point, [{kn.ns:.0f}, {kn.nw:.0f}, {kn.Eb:.0f}], sits where dumped energy falls to almost zero; reaching it costs {kn.LCOE_abs:.3f}~USD/kWh and {kn.Em_abs:,.0f}~kg/y of emissions, so a designer who does not value dump reduction highly would not choose it. As a consistency check, none of the {PK['N_FRONT_16']} non-dominated front points dominates the equal-weight PSO design, and its equal-weight score ({PK['WS_SCORE']}) is lower than that of every front point (best {PK['FRONT_BEST_WS']}). The \texttt{{paretosearch}} approximation therefore does not sample the front densely near this design, and we add the weighted-sum design to the candidate set. \cref{{sec:mc}} re-ranks all candidates by their performance under uncertainty.

\begin{{table}}[htbp]
\centering
\scriptsize
\setlength{{\tabcolsep}}{{3pt}}
\begin{{tabular}}{{l l l c c c c c c}}
\toprule
\textbf{{DE}} & \textbf{{Selection rule}} & \textbf{{$[n_s, n_w, E_b]$}} & \textbf{{LCOE}} & \textbf{{Em.}} & \textbf{{DPSP}} & \textbf{{Dump}} & \textbf{{REF}} & \textbf{{$J$}} \\
 & & & [USD/kWh] & [kg/y] & [\%] & & [\%] & \\
\midrule
{TAB}
\bottomrule
\end{{tabular}}
\caption{{\label{{tab:pareto_reps}} Representative designs selected from the 16~kW (five objectives) and 7~kW (four objectives) Pareto approximations, after rounding to whole units and exact re-evaluation. $J$: equal-weight objective. Max REF coincides with min emissions and is not listed.}}
\end{{table}}

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_pareto_representatives.pdf}}
  \caption{{\label{{fig:pareto_reps}} Pareto approximations and representative designs: (a) 16~kW DE, normalized LCOE vs emissions colored by dump fraction, with the weighted-sum PSO design; (b) 7~kW DE, normalized LCOE vs DPSP colored by emissions.}}
\end{{figure}}

\subsection{{Cost--reliability trade-off with the DE rating as a decision variable\label{{sec:pareto_rel}}}}
With a DE rated above the peak load, DPSP is zero for every design and the reliability objective never trades off against the others. We expose this trade-off in two ways. First, we add the DE rating (0--20~kW) to the decision variables, with its capital, replacement, maintenance and fuel costs scaling with rating. Under equal weights, {'all' if ndv == len(DV) else f'{ndv} of the'} {len(DV)} PSO runs converge to a design without a generator ({dv.value:.0f}~kW): the design [{dv.ns:.0f}, {dv.nw:.0f}, {dv.Eb:.0f}] leaves {dv.DPSP*100:.1f}\% of the load unserved at an LCOE of {dv.LCOE_abs:.3f}~USD/kWh. The equal-weight objective thus accepts a loss of load that no off-grid community would, which confirms that reliability must enter as a requirement rather than as one of several equally weighted terms (see also \cref{{sec:sizing_sensitivity}}).

Second, we solve an $\varepsilon$-constraint problem: minimize the mean of the other four normalized objectives subject to DPSP $\leq \varepsilon$, with the DE rating free, for $\varepsilon$ from 0 to 5\% (best of five PSO runs each). \cref{{fig:dg_front}} shows the resulting cost--reliability front. Supplying all load requires a {e0.PDE:.1f}~kW DE, below the 15.0~kW hourly peak because the battery covers part of the peak, at an LCOE of {e0.LCOE_abs:.3f}~USD/kWh, {e0_txt} the equal-weight design with the default 16~kW DE ({s3.LCOE_abs:.3f}~USD/kWh). Allowing 1\% unmet load reduces the DE to {e1.PDE:.1f}~kW and LCOE to {e1.LCOE_abs:.3f}~USD/kWh; at 5\% the generator disappears and LCOE falls to {e5.LCOE_abs:.3f}~USD/kWh. The PV array and battery hardly change along the front ({EP.ns.min()*0.255:.0f}--{EP.ns.max()*0.255:.0f}~kW and {EP.Eb.min():.0f}--{EP.Eb.max():.0f}~kWh): the reliability target sets the size of the backup generator, not of the renewable system.

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_dg_front.pdf}}
  \caption{{\label{{fig:dg_front}} Cost--reliability front from the $\varepsilon$-constraint problem with the DE rating as a decision variable: (a) LCOE, (b) DE rating, (c) annual emissions, PV capacity and battery capacity (in units of 10~kWh) vs the DPSP limit $\varepsilon$.}}
\end{{figure}}

'''
e = Ed()
e.between(r'\subsection{Variation of Pareto-optimal combinations of input variables\label{sec:pareto_opt}}', r'\subsection{Break-even distance analysis}', new, keep_end=True)
e.save()
