"""T2.5: Monte Carlo statistics and robust selection over the 16 kW Pareto front."""
from common import *
M = RES / 'mc'; R = pd.read_csv(M / 'mc_results.csv'); D = pd.read_csv(M / 'designs.csv')
nom = R[R.scenario == 0].set_index('design_id'); S = R[R.scenario > 0]
def cvar(x, a=0.95):
    q = np.quantile(x, a); return x[x >= q].mean()
g = S.groupby('design_id')
st = pd.DataFrame({'LCOE_mean': g.LCOE_abs.mean(), 'LCOE_p5': g.LCOE_abs.quantile(0.05), 'LCOE_p95': g.LCOE_abs.quantile(0.95), 'LCOE_cvar95': g.LCOE_abs.apply(lambda x: cvar(x.to_numpy())),
    'Em_mean': g.Em_abs.mean(), 'Em_p5': g.Em_abs.quantile(0.05), 'Em_p95': g.Em_abs.quantile(0.95),
    'DPSP_mean': g.DPSP.mean(), 'DPSP_p95': g.DPSP.quantile(0.95), 'P_DPSP_gt_1pct': g.DPSP.apply(lambda x: (x > 0.01).mean()), 'P_DPSP_gt_0': g.DPSP.apply(lambda x: (x > 0).mean()),
    'REF_mean': 1 - g.oneminusREF.mean(), 'REF_p5': 1 - g.oneminusREF.quantile(0.95), 'Dump_mean': g.Dump.mean(), 'J_mean': g.J.mean()})
st['LCOE_nom'] = nom.LCOE_abs; st['Em_nom'] = nom.Em_abs; st['DPSP_nom'] = nom.DPSP; st['J_nom'] = nom.J
st = st.join(D.set_index('design_id'))
st.to_csv(M / 'mc_summary_all.csv')
# robust TOPSIS over the 16 kW candidates (chosen + front)
C = st[st.PDE == 16].copy()
crit = ['LCOE_mean', 'LCOE_cvar95', 'Em_mean', 'P_DPSP_gt_0']  # P(DPSP>1%) is zero for every 16 kW candidate, so the probability of any unmet load is used
F = C[crit].to_numpy(float); F = F + 1e-12
Rn = F / np.sqrt((F ** 2).sum(0)); V = Rn / len(crit); b, w = V.min(0), V.max(0)
C['closeness_robust'] = np.sqrt(((V - w) ** 2).sum(1)) / (np.sqrt(((V - b) ** 2).sum(1)) + np.sqrt(((V - w) ** 2).sum(1)))
Fn = C[['LCOE_nom', 'Em_nom']].to_numpy(float)
robust = C.closeness_robust.idxmax()
C.sort_values('closeness_robust', ascending=False).to_csv(M / 'robust_ranking.csv')
reps = pd.read_csv(RES / 'pareto' / 'representatives_continuous.csv'); reps = reps[reps.front == '16kW']
pick = {'Weighted-sum PSO (chosen)': 'chosen_S3', 'Robust TOPSIS': robust}
for lab, nm in [('Knee', 'knee'), ('TOPSIS (equal, nominal)', 'TOPSIS_equal'), ('Min LCOE', 'min_LCOE_n')]:
    rr = reps[reps.label == nm]
    if len(rr): pick[lab] = f'front_{int(rr.orig_row.iloc[0]):03d}'
pick['8 kW DE design'] = 'DG8kW'
tab = st.loc[list(pick.values())].copy(); tab.insert(0, 'label', list(pick.keys()))
tab.to_csv(M / 'mc_table.csv')
with open(M / 'mc_table.tex', 'w') as f:
    f.write('\\begin{tabular}{lccccccc}\n\\toprule\nDesign & $[n_s, n_w, E_b]$ & LCOE nominal & LCOE 5--95\\% & CVaR$_{95}$ LCOE & Emissions 5--95\\% & $P$(DPSP$>$1\\%) & REF mean\\\\\n & & [USD/kWh] & [USD/kWh] & [USD/kWh] & [kg/y] & & \\\\\n\\midrule\n')
    for _, r in tab.iterrows():
        f.write(f"{r.label} & [{r.ns:.0f}, {r.nw:.0f}, {r.Eb:.0f}] & {r.LCOE_nom:.3f} & {r.LCOE_p5:.3f}--{r.LCOE_p95:.3f} & {r.LCOE_cvar95:.3f} & {r.Em_p5:,.0f}--{r.Em_p95:,.0f} & {r.P_DPSP_gt_1pct:.2f} & {r.REF_mean:.3f}\\\\\n")
    f.write('\\bottomrule\n\\end{tabular}\n')
ch = st.loc['chosen_S3']; rb = st.loc[robust]; d8 = st.loc['DG8kW']
keynum(M / 'key_numbers.txt', {'MC_N': int(S.scenario.nunique()), 'MC_CHOSEN_LCOE_P5': f'{ch.LCOE_p5:.3f}', 'MC_CHOSEN_LCOE_P95': f'{ch.LCOE_p95:.3f}',
    'MC_CHOSEN_LCOE_CVAR': f'{ch.LCOE_cvar95:.3f}', 'MC_CHOSEN_P_DPSP_GT_1PCT': f'{ch.P_DPSP_gt_1pct:.3f}', 'MC_CHOSEN_P_DPSP_GT_0': f'{ch.P_DPSP_gt_0:.3f}',
    'MC_CHOSEN_EM_P5': f'{ch.Em_p5:.0f}', 'MC_CHOSEN_EM_P95': f'{ch.Em_p95:.0f}', 'MC_CHOSEN_REF_P5': f'{ch.REF_p5:.3f}',
    'MC_ROBUST_PICK': robust, 'MC_ROBUST_X': f'[{rb.ns:.0f}, {rb.nw:.0f}, {rb.Eb:.1f}]', 'MC_ROBUST_LCOE_MEAN': f'{rb.LCOE_mean:.3f}', 'MC_ROBUST_LCOE_CVAR': f'{rb.LCOE_cvar95:.3f}',
    'MC_ROBUST_P_DPSP': f'{rb.P_DPSP_gt_1pct:.3f}', 'MC_ROBUST_IS_CHOSEN': robust == 'chosen_S3', 'MC_ROBUST_RANK_OF_CHOSEN': int((C.closeness_robust > C.loc['chosen_S3', 'closeness_robust']).sum() + 1),
    'MC_8KW_P_DPSP_GT_1PCT': f'{d8.P_DPSP_gt_1pct:.3f}', 'MC_8KW_LCOE_P5': f'{d8.LCOE_p5:.3f}', 'MC_8KW_LCOE_P95': f'{d8.LCOE_p95:.3f}', 'MC_8KW_DPSP_P95': f'{d8.DPSP_p95:.4f}'})
print(tab.round(4).T.to_string()); print('robust pick', robust)
sc = pd.read_csv(M / 'scenario_summary.csv'); s1 = sc[sc.scenario > 0]
keynum(M / 'scenario_spread.txt', {'irr_cv': round(s1.irr_kWh_m2.std() / s1.irr_kWh_m2.mean(), 4), 'wind_cv': round(s1.wind_mean.std() / s1.wind_mean.mean(), 4), 'load_cv': round(s1.load_kWh.std() / s1.load_kWh.mean(), 4)})
ids = list(pick.values()); labs = list(pick.keys()); cols = [PAL[7], PAL[0], PAL[1], PAL[6], PAL[3], PAL[2]]
fig, ax = plt.subplots(1, 4, figsize=(7.0, 2.4))
for a, (col, yl, fac) in zip(ax, [('LCOE_abs', 'LCOE [USD/kWh]', 1), ('Em_abs', 'Emissions [t/y]', 1e-3), ('DPSP', 'DPSP [%]', 100), ('oneminusREF', 'REF [%]', -100)]):
    data = [(S[S.design_id == i][col].to_numpy() * fac + (100 if fac == -100 else 0)) for i in ids]
    bp = a.boxplot(data, widths=0.6, showfliers=False, patch_artist=True, medianprops=dict(color=INK, lw=1))
    for b_, c in zip(bp['boxes'], cols): b_.set(facecolor='white', edgecolor=c, lw=1.2)
    a.set_xticks(range(1, len(ids) + 1)); a.set_xticklabels([str(k + 1) for k in range(len(ids))]); a.set_ylabel(yl)
ax[0].set_xlabel('Design'); fig.tight_layout()
fig.text(0.5, -0.05, '   '.join(f'{k+1}: {l}' for k, l in enumerate(labs)), ha='center', fontsize=6, color=INK2)
save(fig, 'rev_mc_distributions')
