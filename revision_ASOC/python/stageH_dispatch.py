"""Stage H, part 2 (30 Oct 2026): day-ahead dispatch on the low-resource day 17 June 2018 (MATLAB job L111,
results/dispatch_lowres/) added to Secs. 7 and 8.3, with the rule-based schedule of the same day scored by the
dispatch cost model (dispatch_metrics.py). Also merges the stress-test input figure into fig:dispatch_robust_RES.
Runs after stageH_polish.py in apply_text_pipeline.sh. Key numbers -> results/dispatch_lowres/key_numbers.txt."""
import pandas as pd, numpy as np
from texedit import Ed
from figstyle import RES
from dispatch_metrics import day_metrics

D1 = RES / 'dispatch'; D2 = RES / 'dispatch_lowres'
T = pd.read_csv(RES / 'rerun' / 'main_tables.csv').set_index('tag')
x16 = T.loc['S3', ['ns', 'nw', 'Eb']].to_numpy(float); x8 = T.loc['DG8kW', ['ns', 'nw', 'Eb']].to_numpy(float)
CFG = {'i_16kW': (x16, 16, '(i) 16~kW DE'), 'ii_8kW_16kWsizing': (x16, 8, '(ii) 8~kW DE, design sized for 16~kW'),
       'iii_8kW_8kWsizing': (x8, 8, '(iii) 8~kW DE, design sized for 8~kW')}
R1 = pd.read_csv(D1 / 'dispatch_cases.csv').set_index('case'); R2 = pd.read_csv(D2 / 'dispatch_cases_d168.csv').set_index('case')

# rule-based schedules of 17 June scored with the dispatch cost model
RB = {}
for c, (x, P, _) in CFG.items():
    r = pd.read_csv(D2 / f'rule_{c}.csv')
    m = day_metrics(r.load, r.P_PV + r.P_WT * 0.9, r.P_DE, r.P_b, r.P_dump, x, P)
    m['DPSP'] = r.P_lost.sum() / r.load.sum(); m['J'] = 0.25 * (m['COE_n'] + m['Em_n'] + m['Dump'] + 1 - m['REF'])
    RB[c] = m
for c in CFG:  # optimized schedules: fuel etc. from the same model (checks against MATLAB)
    d = pd.read_csv(D2 / f'dispatch_d168_{c}.csv'); m = day_metrics(d.load, d.P_RES, d.P_DE, d.P_b, d.P_dump, *CFG[c][:2])
    assert abs(m['COE'] - R2.loc[c, 'COE']) < 1e-6 and abs(m['Em_kg'] - R2.loc[c, 'Em_kg']) < 1e-6, c


def row(lab, J, COE, COE_n, Em, DPSP, Dump, REF, DE):
    return f"{lab} & {J:.4f} & {COE:.3f} & {COE_n:.4f} & {Em:.1f} & {DPSP * 100:.2f} & {Dump:.3f} & {REF * 100:.1f} & {int(round(DE))} \\\\\n"


def rr(R, c, lab):
    r = R.loc[c]; return row(lab, r.J, r.COE, r.COE_n, r.Em_kg, r.DPSP, r.Dump, r.REF, r.DE_hours)


HEAD = r"""\begin{tabular}{l c c c c c c c c}
\toprule
\textbf{Case} & \textbf{$J$} & \textbf{COE} & \textbf{COE} & \textbf{Em.} & \textbf{DPSP} & \textbf{Dump} & \textbf{REF} & \textbf{DE} \\
 & & [USD/kWh] & (norm.) & [kg] & [\%] & & [\%] & [h] \\
"""
grp = lambda t: f"\\midrule\n\\multicolumn{{9}}{{l}}{{\\textit{{{t}}}}} \\\\\n"
tab1 = HEAD + grp('1 January (representative day), optimized dispatch') + ''.join(rr(R1, c, CFG[c][2]) for c in CFG) \
    + grp('17 June (low-resource day), optimized dispatch') + ''.join(rr(R2, c, CFG[c][2]) for c in CFG) \
    + grp('17 June, rule-based operation of the sizing stage') + ''.join(row(CFG[c][2], RB[c]['J'], RB[c]['COE'], RB[c]['COE_n'], RB[c]['Em_kg'], RB[c]['DPSP'], RB[c]['Dump'], RB[c]['REF'], RB[c]['DE_hours']) for c in CFG) \
    + "\\bottomrule\n\\end{tabular}\n"
LP = [('Baseline profile', 'iii_8kW_8kWsizing', 'iii_8kW_8kWsizing'), ('Peakier profile', 'load_peaky', 'load_peaky'),
      ('Load shifting', 'load_shift', 'load_shift'), ('Load shifting and 10\\% curtailment', 'load_shift_curtail', 'load_shift_curtail')]
tab2 = HEAD + grp('1 January') + ''.join(rr(R1, a, l) for l, a, _ in LP) + grp('17 June') + ''.join(rr(R2, b, l) for l, _, b in LP) + "\\bottomrule\n\\end{tabular}\n"

# ---------------------------------------------------------------- key numbers for the text
o, rb = R2, RB
pct = lambda a, b: (a / b - 1) * 100
K = dict(
    soc0_lo=R2.loc[list(CFG), 'soc0'].min() * 100, soc0_hi=R2.loc[list(CFG), 'soc0'].max() * 100,
    i_rule_COE=rb['i_16kW']['COE'], i_opt_COE=o.loc['i_16kW', 'COE'], i_cost_gap=-pct(o.loc['i_16kW', 'COE'], rb['i_16kW']['COE']),
    i_rule_fuel=rb['i_16kW']['fuel_L'], i_opt_fuel=o.loc['i_16kW', 'fuel_L'], i_fuel_cut=-pct(o.loc['i_16kW', 'fuel_L'], rb['i_16kW']['fuel_L']),
    i_rule_DEh=rb['i_16kW']['DE_hours'], i_opt_DEh=o.loc['i_16kW', 'DE_hours'],
    rule8_DPSP_lo=min(rb['ii_8kW_16kWsizing']['DPSP'], rb['iii_8kW_8kWsizing']['DPSP']) * 100,
    rule8_DPSP_hi=max(rb['ii_8kW_16kWsizing']['DPSP'], rb['iii_8kW_8kWsizing']['DPSP']) * 100,
    opt8_COE=o.loc['iii_8kW_8kWsizing', 'COE'], rule8_COE=rb['iii_8kW_8kWsizing']['COE'],
    c8_up_lo=min(pct(o.loc[c, 'COE'], rb[c]['COE']) for c in ['ii_8kW_16kWsizing', 'iii_8kW_8kWsizing']),
    c8_up_hi=max(pct(o.loc[c, 'COE'], rb[c]['COE']) for c in ['ii_8kW_16kWsizing', 'iii_8kW_8kWsizing']),
    c8_vs_16=-pct(o.loc['iii_8kW_8kWsizing', 'COE'], o.loc['i_16kW', 'COE']),
    em_lo=o.loc[list(CFG), 'Em_kg'].min(), em_hi=o.loc[list(CFG), 'Em_kg'].max(),
    sh_COE=o.loc['load_shift', 'COE'], sh_COE_d=pct(o.loc['load_shift', 'COE'], o.loc['iii_8kW_8kWsizing', 'COE']),
    sh_em_d=pct(o.loc['load_shift', 'Em_kg'], o.loc['iii_8kW_8kWsizing', 'Em_kg']),
    pk_COE_d=pct(o.loc['load_peaky', 'COE'], o.loc['iii_8kW_8kWsizing', 'COE']), pk_fuel_d=pct(o.loc['load_peaky', 'fuel_L'], o.loc['iii_8kW_8kWsizing', 'fuel_L']),
    pk_fuel=o.loc['load_peaky', 'fuel_L'], base_fuel=o.loc['iii_8kW_8kWsizing', 'fuel_L'],
    cu_em=o.loc['load_shift_curtail', 'Em_kg'], base_em=o.loc['iii_8kW_8kWsizing', 'Em_kg'],
    cu_em_d=pct(o.loc['load_shift_curtail', 'Em_kg'], o.loc['iii_8kW_8kWsizing', 'Em_kg']), cu_fuel_d=pct(o.loc['load_shift_curtail', 'fuel_L'], o.loc['iii_8kW_8kWsizing', 'fuel_L']))
with open(D2 / 'key_numbers.txt', 'w') as f:
    for k, v in K.items(): f.write(f'D168_{k.upper()} = {v:.4f}\n')
    f.write(f"D168_I_COST_GAP_TXT = {K['i_cost_gap']:.1f}\nD168_I_FUEL_CUT_TXT = {K['i_fuel_cut']:.0f}\nD168_RULE8_DPSP_TXT = {K['rule8_DPSP_lo']:.1f}\n")
print({k: round(float(v), 4) for k, v in K.items()})
assert K['i_cost_gap'] < 1 and K['rule8_DPSP_lo'] > 4 and 6 < K['c8_up_lo'] and K['c8_up_hi'] < 9, 'narrative below assumes these results'

E = Ed()


def table_before(caption_start, new):
    """Replace the tabular that precedes the caption starting with `caption_start`, through the end of that caption line."""
    i = E.s.find(caption_start); assert i > 0 and E.s.count(caption_start) == 1, caption_start[:60]
    j = E.s.rfind(r'\begin{tabular}', 0, i); k = E.s.find('\n', i)
    E.s = E.s[:j] + new + E.s[k:]; E.log.append('table:' + caption_start[:40])

# ---------------------------------------------------------------- Sec. 7
E.rep(r"The smaller DE lowers the fixed cost of the backup, so cases (ii) and (iii) have a lower COE than case (i); the small difference between (ii) and (iii), whose designs are almost identical, reflects the tolerance of the dispatch solver. \cref{fig:dispatch_P_base} shows the schedules.",
      r"The smaller DE lowers the fixed cost of the backup, so cases (ii) and (iii) have a lower COE than case (i); the small difference between (ii) and (iii), whose designs are almost identical, reflects the tolerance of the dispatch solver." + "\n\n" +
      r"Because the DE stays off on the representative day, we repeat the comparison on 17 June 2018, the day on which the equal-weight design burns the most diesel under rule-based operation (19~h and 122~kWh of DE output). It is the calmest day of the year and the fourth-least sunny (irradiation 35\% of the annual daily mean), and each configuration starts it with the battery almost empty, at the SOC that its own rule-based simulation reaches at midnight (" + f"{K['soc0_lo']:.0f}--{K['soc0_hi']:.0f}" + r"\%). To compare the two controllers directly, \cref{tab:DG_size} also scores the rule-based schedule of that day with the dispatch cost model. With the 16~kW DE, optimized dispatch changes little: it runs the DE for " + f"{K['i_opt_DEh']:.0f} instead of {K['i_rule_DEh']:.0f}~h, burns {K['i_fuel_cut']:.0f}\\% less fuel ({K['i_opt_fuel']:.1f} vs {K['i_rule_fuel']:.1f}~L) and lowers the daily COE from {K['i_rule_COE']:.3f} to {K['i_opt_COE']:.3f}~USD/kWh" + r", partly by using the 1\% unmet-load allowance that the rule-based controller does not use. For the selected design, rule-based operation thus costs almost the same as optimized scheduling on the day with the most diesel use. With an 8~kW DE the difference lies in reliability rather than cost. The rule-based controller runs the battery empty before the evening, when the load exceeds the DE rating, and leaves " + f"{K['rule8_DPSP_lo']:.1f}\\%" + r" of the day's load unserved; the optimized schedule runs the DE early in the day to charge the battery and keeps unmet load within the 1\% limit, at a " + f"{K['c8_up_lo']:.0f}--{K['c8_up_hi']:.0f}\\% higher daily COE ({K['opt8_COE']:.3f} vs {K['rule8_COE']:.3f}~USD/kWh)" + r" because it serves more load. On this day the 8~kW configurations cost " + f"{K['c8_vs_16']:.0f}\\% less per kWh than the 16~kW one, with the same emissions ({K['em_lo']:.0f}--{K['em_hi']:.0f}~kg)" + r", because the smaller engine burns less no-load fuel. \cref{fig:dispatch_P_base} shows the schedules.")
table_before(r"""\caption{\label{tab:DG_size} Day-ahead dispatch on 1 January 2018""",
          tab1 + r"""\caption{\label{tab:DG_size} Day-ahead dispatch of three DE and design configurations on the representative day (1 January 2018) and on the low-resource day (17 June 2018), and the rule-based schedule of 17 June scored with the same cost model. $J$ is the equally weighted sum of normalized COE, emissions, dump fraction and $(1-REF)$; DPSP is constrained to at most 1\% in the optimized dispatch but not in the rule-based schedule, so $J$ does not penalize the unmet load of the rule-based (ii) and (iii).}""")
E.rep(r"\caption{\label{fig:dispatch_P_base} Optimized day-ahead schedules on 1 January 2018 for the three configurations of \cref{tab:DG_size}: power flows (top; battery power positive when discharging) and battery SOC (bottom).}",
      r"\caption{\label{fig:dispatch_P_base} Optimized day-ahead schedules: (a) 1 January, configuration (i), with which configurations (ii) and (iii) practically coincide; (b--d) 17 June, configurations (i)--(iii) of \cref{tab:DG_size}, with the DE output of the rule-based schedule (dashed) for comparison. Power flows on top (battery power positive when discharging; dumped power below zero; unserved load stacked on the load line) and battery SOC below.}")
# ---------------------------------------------------------------- Sec. 8.2: merged stress-test figure
E.rep(r"The low-resource days scale the irradiance and wind speed of the representative day to 10\% of their values (\cref{fig:dispatch_profiles}a--b). They are deliberately extreme: the lowest-irradiation day of 2018 still delivers 31\% of the annual mean daily irradiation, and the calmest day has 43\% of the mean daily wind speed,",
      r"The low-resource days scale the irradiance and wind speed of the representative day to 10\% of their values (\cref{fig:dispatch_robust_RES}a--b). They are deliberately extreme: the lowest-irradiation day of 2018 still delivers 31\% of the annual mean daily irradiation, and the calmest day, 17 June (\cref{sec:dispatch_opt}), has 43\% of the mean daily wind speed,")
E.between(r"""\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{rev_dispatch_profiles.pdf}""", r"""\label{fig:dispatch_profiles} Inputs of the stress tests on the representative day: (a) baseline and low (10\%) irradiance, (b) baseline and low (10\%) wind speed at the measurement height, (c) baseline and alternative load profiles.}
\end{figure}

""", "")
E.rep(r"\caption{\label{fig:dispatch_robust_RES} Optimized schedules under low renewable resource (8~kW DE design).}",
      r"\caption{\label{fig:dispatch_robust_RES} Stress test with low renewable resource (8~kW DE design): (a) irradiance and (b) wind speed (measurement height) on the representative day and scaled to 10\%; (c) optimized schedule and SOC with 10\% irradiance. With 10\% wind speed alone the schedule is that of the representative day, and with both resources at 10\% it is that of (c), because the design has no wind turbines.}")
# ---------------------------------------------------------------- Sec. 8.3
E.rep(r"We also repeated the dispatch with three alternative load profiles (\cref{fig:dispatch_profiles}c): a peakier profile in which hourly loads vary by up to $\pm 30\%$ around the baseline, a flatter profile in which load is shifted toward the hours of solar output, and the shifted profile with 10\% daily curtailment. With this PV-dominated design, demand shape matters mainly through dumped energy: shifting load into daylight hours lowers the dump fraction from 0.522 to 0.458 and the weighted objective from 0.1686 to 0.1503 (\cref{tab:dispatch_robust_load}). The DE stays off in all three cases on this sunny day. Demand-side measures that move load into hours of renewable surplus therefore have value even when the generation mix is fixed (\cref{sec:dr}).",
      r"We also repeated the dispatch with three alternative load profiles: a peakier profile in which hourly loads vary by up to $\pm 30\%$ around the baseline, a flatter profile in which load is shifted toward the hours of solar output, and the shifted profile with 10\% daily curtailment. On the sunny representative day, demand shape matters mainly through dumped energy: shifting load into daylight hours lowers the dump fraction from 0.522 to 0.458 and the weighted objective from 0.1686 to 0.1503, and the DE stays off in all cases (\cref{tab:dispatch_robust_load}). On 17 June we applied the same hour-by-hour changes to that day's load, keeping its daily energy (90\% with curtailment; \cref{fig:dispatch_load}a). With little solar surplus to absorb, shifting lowers the daily COE by only " + f"{-K['sh_COE_d']:.0f}\\% ({K['sh_COE']:.3f} vs {K['opt8_COE']:.3f}~USD/kWh) and emissions by {-K['sh_em_d']:.0f}\\%, while the peakier profile raises COE by {K['pk_COE_d']:.0f}\\% and fuel use by {K['pk_fuel_d']:.0f}\\% ({K['pk_fuel']:.1f} vs {K['base_fuel']:.1f}~L). Curtailing 10\\% of the load cuts emissions by {-K['cu_em_d']:.0f}\\% ({K['cu_em']:.1f} vs {K['base_em']:.1f}~kg) and fuel use by {-K['cu_fuel_d']:.0f}\\%" + r" (\cref{fig:dispatch_load}b--d). Demand-side measures that move load into hours of renewable surplus therefore pay mainly on sunny days, while on low-resource days only a reduction in demand saves much diesel (\cref{sec:dr}).")
table_before(r"""\caption{\label{tab:dispatch_robust_load} Day-ahead dispatch under alternative demand profiles""",
          tab2 + r"""\caption{\label{tab:dispatch_robust_load} Day-ahead dispatch under alternative demand profiles (8~kW DE design) on the representative day and on the low-resource day.}""")
E.rep(r"\caption{\label{fig:dispatch_load} Optimized schedules under alternative demand profiles (8~kW DE design).}",
      r"\caption{\label{fig:dispatch_load} Day-ahead dispatch of the 8~kW DE design on 17 June under alternative demand profiles: (a) the day's load and the three profiles derived from it; (b--d) optimized schedules, drawn as in \cref{fig:dispatch_P_base}.}")
# ---------------------------------------------------------------- workflow caption, limitations, conclusions
E.rep(r"Stage~2 optimizes day-ahead dispatch of a selected design and tests it on stress days.}",
      r"Stage~2 optimizes day-ahead dispatch of a selected design on a representative and a low-resource day and tests it on stress days.}")
E.rep(r"a design ranked best under rule-based operation may rank differently under optimized dispatch, although its Stage-1 cost bounds its cost under any better operating policy.",
      r"a design ranked best under rule-based operation may rank differently under optimized dispatch, although its Stage-1 cost bounds its cost under any better operating policy; for the selected design, on the day with the most diesel use, optimized dispatch is " + f"{K['i_cost_gap']:.1f}" + r"\% cheaper (\cref{sec:dispatch_opt}).")
E.rep(r"Low-resource stress days and alternative demand profiles show that the battery and generator absorb single bad days, while shifting load into daylight hours reduces dumped energy.",
      r"On the day of 2018 with the most diesel use, optimized day-ahead dispatch lowers the selected design's cost by less than 1\% relative to the rule-based controller used for sizing; with a smaller 8~kW generator it is what keeps unmet load within 1\%. Shifting load into daylight hours reduces dumped energy on sunny days, while on low-resource days only curtailment saves much diesel.")
E.rep(r"a multi-objective economic-environmental dispatch problem is solved for a representative day.", r"a multi-objective economic-environmental dispatch problem is solved for a representative day and for a low-resource day.")
E.save()
