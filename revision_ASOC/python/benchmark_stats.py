"""T2.2: statistics, tests and figures for the multi-seed benchmark."""
from common import *
from scipy import stats
import scipy.io as sio
import sys
B = RES / (sys.argv[1] if len(sys.argv) > 1 else 'benchmark_intcoded'); df = pd.read_csv(B / 'summary.csv')
SUF = '' if B.name == 'benchmark_intcoded' else '_' + B.name
NAMES = {'PSO': 'PSO', 'GA': 'GA', 'SA': 'SA', 'SO': 'SO', 'MS': 'MS', 'GS': 'GS', 'DPS': 'DPS', 'PSOPS': 'PSO+PS'}
ex = sio.loadmat(RES / 'benchmark' / 'exhaustive_int.mat'); fstar_ex = float(ex['fstar']); xstar = ex['xstar'].ravel()
fstar = min(fstar_ex, df.J_int.min()); tol = 1.005 * fstar
rows = []
for s, g in df.groupby('solver'):
    succ = g.J_int <= tol
    ett = []
    for _, r in g.iterrows():
        tr = np.loadtxt(B / 'traces' / f'{s}_seed{int(r.seed):02d}.csv', delimiter=',', ndmin=2)
        hit = np.where(tr[:, 1] <= tol)[0] if tr.size else []
        ett.append(tr[hit[0], 0] if len(hit) else np.nan)
    ert = g.evals.sum() / max(succ.sum(), 1e-9) if succ.any() else np.inf
    mode = g.groupby(['ns', 'nw']).size().sort_values(ascending=False)
    rows.append(dict(solver=s, N=len(g), best=g.J_int.min(), median=g.J_int.median(), mean=g.J_int.mean(), sd=g.J_int.std(ddof=1),
        worst=g.J_int.max(), success=succ.mean(), med_evals_to_target=np.nanmedian(ett) if np.isfinite(ett).any() else np.nan,
        ERT_evals=ert, ERT_s=ert * (g.wall_s / g.evals).mean() if np.isfinite(ert) else np.inf,
        med_wall_s=g.wall_s.median(), med_evals=g.evals.median(), modal_design=f'[{mode.index[0][0]}, {mode.index[0][1]}]', modal_freq=mode.iloc[0] / len(g),
        share_nw4=(g.nw == 4).mean()))
S = pd.DataFrame(rows).sort_values(['median', 'mean']).reset_index(drop=True)
S.to_csv(B / 'stats_table.csv', index=False)
groups = {s: df.loc[df.solver == s, 'J_int'].to_numpy() for s in S.solver}
H, pkw = stats.kruskal(*groups.values())
ref = S.solver.iloc[0]; pairs = []
for s in S.solver[1:]:
    a, b = groups[ref], groups[s]
    U, p = stats.mannwhitneyu(a, b, alternative='two-sided')
    a12 = (stats.rankdata(np.r_[a, b])[:len(a)].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(b))
    pairs.append([s, U, p, 1 - a12])
P = pd.DataFrame(pairs, columns=['solver', 'U', 'p_raw', 'P_ref_better'])
o = np.argsort(P.p_raw.to_numpy()); m = len(P); adj = np.empty(m); run = 0
for k, i in enumerate(o): run = max(run, min(1, (m - k) * P.p_raw.iloc[i])); adj[i] = run
P['p_holm'] = adj; P.to_csv(B / 'tests.csv', index=False)
# LaTeX tables
def f4(x): return f'{x:.4f}'
with open(B / 'stats_table.tex', 'w') as f:
    g = lambda v: f'{(v / fstar - 1) * 100:.3f}'
    f.write('\\begin{tabular}{lrrrrrrrr}\n\\toprule\n & \\multicolumn{5}{c}{Gap to $f^*$ [\\%]} & & \\multicolumn{2}{c}{ERT} \\\\\n\\cmidrule(lr){2-6}\\cmidrule(lr){8-9}\nSolver & Best & Median & Mean & SD & Worst & Success & [evals] & [s]\\\\\n\\midrule\n')
    for _, r in S.iterrows():
        ert = '--' if not np.isfinite(r.ERT_evals) else f'{r.ERT_evals:,.0f}'; erts = '--' if not np.isfinite(r.ERT_s) else f'{r.ERT_s:.2f}'
        f.write(f"{NAMES[r.solver]} & {g(r.best)} & {g(r['median'])} & {g(r['mean'])} & {r.sd / fstar * 100:.3f} & {g(r.worst)} & {r.success*100:.0f}\\% & {ert} & {erts}\\\\\n")
    f.write('\\bottomrule\n\\end{tabular}\n')
with open(B / 'tests.tex', 'w') as f:
    f.write('\\begin{tabular}{lrrrr}\n\\toprule\n' + f'Solver vs {NAMES[ref]} & $U$ & $p$ & $p_{{\\mathrm{{Holm}}}}$ & $\\hat{{P}}$({NAMES[ref]} better)\\\\\n\\midrule\n')
    for _, r in P.iterrows():
        f.write(f"{NAMES[r.solver]} & {r.U:.0f} & {r.p_raw:.2e} & {r.p_holm:.2e} & {r.P_ref_better:.2f}\\\\\n")
    f.write('\\bottomrule\n\\end{tabular}\n')
kn = {'BENCH_FSTAR': f'{fstar:.6f}', 'BENCH_FSTAR_EXHAUSTIVE': f4(fstar_ex), 'BENCH_XSTAR': f'[{int(xstar[0])}, {int(xstar[1])}, {xstar[2]:.1f}]',
      'BENCH_KW_H': f'{H:.1f}', 'BENCH_KW_P': f'{pkw:.1e}', 'BENCH_BEST_SOLVER': NAMES[ref], 'BENCH_NRUNS': int(df.groupby("solver").size().iloc[0])}
for _, r in S.iterrows():
    k = r.solver
    kn.update({f'BENCH_{k}_MEDIAN': f4(r['median']), f'BENCH_{k}_SUCCESS': f'{r.success*100:.0f}%', f'BENCH_{k}_ERT_S': f'{r.ERT_s:.2f}', f'BENCH_{k}_ERT_EVALS': f'{r.ERT_evals:.0f}'})
keynum(B / 'key_numbers.txt', kn if not SUF else {k + SUF.upper(): v for k, v in kn.items()})
print(S.round(4).to_string()); print(P.round(4).to_string()); print('KW', H, pkw, 'fstar', fstar, 'exhaustive', fstar_ex, xstar)
# Figure: box + strip
order = list(S.solver); col = {s: PAL[i] for i, s in enumerate(['PSO', 'GA', 'SA', 'SO', 'MS', 'GS', 'DPS', 'PSOPS'])}
fig, ax = plt.subplots(figsize=(3.5, 2.6))
data = [groups[s] for s in order]
bp = ax.boxplot(data, widths=0.55, showfliers=False, patch_artist=True, medianprops=dict(color=INK, lw=1.2))
for b_, s in zip(bp['boxes'], order): b_.set(facecolor='white', edgecolor=col[s], lw=1.2)
rng = np.random.default_rng(0)
for i, s in enumerate(order):
    ax.scatter(i + 1 + rng.uniform(-0.15, 0.15, len(groups[s])), groups[s], s=6, color=col[s], alpha=0.8, edgecolors='none', zorder=3)
ax.axhline(tol, ls='--', lw=0.8, color=INK2); ax.text(0.55, tol * 1.02, 'f* + 0.5%', va='bottom', ha='left', fontsize=6, color=INK2)
ax.set_xticks(range(1, len(order) + 1)); ax.set_xticklabels([NAMES[s] for s in order], rotation=30)
ax.set_ylabel('Final objective J (integer design)'); fig.tight_layout(); save(fig, 'rev_benchmark_box' + SUF)
# Figure: convergence (median and IQR of best-so-far J - f*)
fig, ax = plt.subplots(figsize=(3.5, 2.6)); grid = np.arange(1, 2001)
for s in ['PSO', 'GA', 'SA', 'SO', 'MS', 'GS', 'DPS', 'PSOPS']:
    if s not in groups: continue
    curves = []
    for seed in df.loc[df.solver == s, 'seed']:
        tr = np.loadtxt(B / 'traces' / f'{s}_seed{int(seed):02d}.csv', delimiter=',', ndmin=2)
        y = np.full(grid.shape, np.nan); idx = np.searchsorted(tr[:, 0], grid, side='right') - 1
        ok = idx >= 0; y[ok] = np.minimum.accumulate(tr[:, 1])[idx[ok]]; curves.append(y)
    C = np.array(curves) - fstar + 1e-4
    med = np.nanmedian(C, 0); lo, hi = np.nanpercentile(C, 25, 0), np.nanpercentile(C, 75, 0)
    ax.plot(grid, med, color=col[s], lw=1.2, label=NAMES[s]); ax.fill_between(grid, lo, hi, color=col[s], alpha=0.12, lw=0)
ax.set_yscale('log'); ax.set_xlabel('Objective evaluations'); ax.set_ylabel(r'Best-so-far $J - f^* + 10^{-4}$')
ax.legend(frameon=False, ncol=2, fontsize=6); fig.tight_layout(); save(fig, 'rev_benchmark_convergence' + SUF)
