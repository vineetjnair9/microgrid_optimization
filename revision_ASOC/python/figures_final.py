"""All figures of the revised manuscript in one consistent style (stage H, 30 Oct 2026).

Reads only result files written by the earlier stages (results/...), so it can be re-run at any time:
    python3 figures_final.py            # every figure
    python3 figures_final.py mc dgfront # selected figures
Figures are drawn at printed width (figstyle.FULL) and copied to the manuscript folder.
Supersedes the plotting parts of figures_results.py, benchmark_stats.py, pareto_select.py,
mc_analysis.py and wind_validation.py (their statistics and tables are unchanged).
"""
import sys, json
import numpy as np, pandas as pd
import scipy.io as sio
from matplotlib.patches import FancyBboxPatch, Patch
from matplotlib.lines import Line2D
import matplotlib.ticker as mticker
from figstyle import *

RR = RES / 'rerun'
PV_KW, WT_KW = 0.255, 3.5
MONTHS = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
MDAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MSTART = np.cumsum([0] + MDAYS[:-1])  # day-of-year index (0-based) of the 1st of each month


def month_axis(ax, label=True, fs=None):
    ax.set_xticks(MSTART + 15); ax.set_xticklabels(MONTHS, fontsize=fs); ax.set_xlim(0, 365)
    ax.tick_params(axis='x', length=0)
    if label: ax.set_xlabel('Month (2018)')


# ---------------------------------------------------------------- workflow (Fig. 2)
def workflow():
    fig, ax = plt.subplots(figsize=(FULL, 1.2)); ax.axis('off'); ax.set_xlim(0, 100); ax.set_ylim(0, 17)
    boxes = [('Data', 'TAHMO weather\nand REopt load;\nhourly, 2018'),
             ('Stage 1:\nsizing', '8,760-h rule-\nbased simulation;\nPSO, weighted sum'),
             ('Pareto\nsearch', 'paretosearch;\n$\\varepsilon$-constraint\nfront, DE rating\nfree'),
             ('Design\nselection', 'extremes, knee,\n$L_2$ compromise,\nTOPSIS'),
             ('Monte Carlo\nre-ranking', '500 scenarios;\nmean, CVaR$_{95}$,\nP(unmet load)'),
             ('Stage 2:\ndispatch', 'PSO + SQP on a\nrepresentative and\na low-resource day')]
    n = len(boxes); gap = 1.6; w = (100 - gap * (n - 1)) / n
    for i, (t, b) in enumerate(boxes):
        x = i * (w + gap); hl = i in (3, 4)
        ax.add_patch(FancyBboxPatch((x + 0.2, 0.3), w - 0.4, 16.4, boxstyle='round,pad=0,rounding_size=1.2',
                                    fc='#eaf2fc' if hl else 'white', ec=BLUE if hl else MUTED, lw=0.8))
        ax.text(x + w / 2, 13.2, t, ha='center', va='center', fontsize=7.2, weight='bold', color=INK, linespacing=1.05)
        ax.text(x + w / 2, 5.4, b, ha='center', va='center', fontsize=6.6, color=INK, linespacing=1.2)
        if i < n - 1:
            ax.annotate('', xy=(x + w + gap + 0.15, 8.5), xytext=(x + w - 0.15, 8.5),
                        arrowprops=dict(arrowstyle='-|>', color=INK2, lw=0.8, mutation_scale=6, shrinkA=0, shrinkB=0))
    save(fig, 'rev_workflow')


# ---------------------------------------------------------------- benchmark (Fig. 3)
SOLVERS = ['PSOPS', 'PSO', 'DPS', 'SO', 'GA', 'SA', 'GS', 'MS']
SNAME = {'PSO': 'PSO', 'GA': 'GA', 'SA': 'SA', 'SO': 'SO', 'MS': 'MS', 'GS': 'GS', 'DPS': 'DPS', 'PSOPS': 'PSO+PS'}
SCOL = dict(zip(SOLVERS, [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]))


def benchmark():
    B = RES / 'benchmark_intcoded'; df = pd.read_csv(B / 'summary.csv')
    fstar = min(float(np.ravel(sio.loadmat(RES / 'benchmark' / 'exhaustive_int.mat')['fstar'])[0]), df.J_int.min())
    st = pd.read_csv(B / 'stats_table.csv'); order = list(st.solver)  # ordered by median
    gap = lambda J: (np.asarray(J) / fstar - 1) * 100
    fig, ax = plt.subplots(1, 2, figsize=(FULL, 2.45), gridspec_kw=dict(width_ratios=[1, 1.15], wspace=0.32))
    a = ax[0]; rng = np.random.default_rng(0)
    for i, s in enumerate(order):
        g = gap(df.loc[df.solver == s, 'J_int'])
        q1, med, q3 = np.percentile(g, [25, 50, 75])
        a.add_patch(plt.Rectangle((i - 0.3, max(q1, 1e-4)), 0.6, max(q3, 1e-4) - max(q1, 1e-4), fc='none', ec=INK2, lw=0.6, zorder=2))
        a.plot([i - 0.3, i + 0.3], [med, med], color=INK, lw=1.1, zorder=3)
        a.scatter(i + rng.uniform(-0.22, 0.22, len(g)), np.maximum(g, 0), s=7, color=SCOL[s], alpha=0.85, lw=0, zorder=4)
    a.set_yscale('symlog', linthresh=0.01, linscale=0.6)
    a.axhline(0.5, color=INK2, lw=0.7, ls='--', zorder=1); a.text(-0.45, 0.6, 'success threshold (0.5%)', ha='left', va='bottom', fontsize=6.5, color=INK2)
    a.set_ylim(-0.002, 100); a.set_yticks([0, 0.01, 0.1, 1, 10, 100]); a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:g}'))
    a.set_xticks(range(len(order))); a.set_xticklabels([SNAME[s] for s in order], rotation=35, ha='right', rotation_mode='anchor'); a.set_xlim(-0.6, len(order) - 0.4)
    a.set_ylabel('Gap of final design to $f^*$ [%]'); a.grid(axis='x', visible=False); panel(a, 'a')
    a = ax[1]; grid = np.arange(1, 2001)
    for s in order:
        curves = []
        for seed in df.loc[df.solver == s, 'seed']:
            tr = np.loadtxt(B / 'traces' / f'{s}_seed{int(seed):02d}.csv', delimiter=',', ndmin=2)
            y = np.full(grid.shape, np.nan); idx = np.searchsorted(tr[:, 0], grid, side='right') - 1
            ok = idx >= 0; y[ok] = np.minimum.accumulate(tr[:, 1])[idx[ok]]; curves.append(y)
        Cg = gap(np.array(curves)); med = np.nanmedian(Cg, 0); lo, hi = np.nanpercentile(Cg, [25, 75], 0)
        lw, ls = (1.6, '-') if s == 'PSOPS' else ((1.0, (0, (3, 1.5))) if s == 'PSO' else (1.1, '-'))
        a.plot(grid, med, color=SCOL[s], lw=lw, ls=ls, label=SNAME[s], zorder=3 if s != 'PSOPS' else 2)
        a.fill_between(grid, lo, hi, color=SCOL[s], alpha=0.10, lw=0)
    a.set_yscale('symlog', linthresh=0.01, linscale=0.6); a.set_ylim(-0.002, 300)
    a.set_yticks([0, 0.01, 0.1, 1, 10, 100]); a.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:g}'))
    a.axhline(0.5, color=INK2, lw=0.7, ls='--'); a.set_xlim(0, 2000)
    a.set_xlabel('Objective evaluations'); a.set_ylabel('Best-so-far gap to $f^*$ [%]')
    panel(a, 'b')
    h_, l_ = a.get_legend_handles_labels(); fig.legend(h_, l_, loc='upper center', ncol=8, bbox_to_anchor=(0.5, 1.07), fontsize=7, handlelength=1.8)
    save(fig, 'rev_benchmark')


# ---------------------------------------------------------------- dispatch-style panel helpers
def power_panel(ax, h, load, pv, de, pb, dump, wt=None, lost=None, step=True, de_bars=True, legend=False, ylim=None):
    """Hourly flows: PV area, DE bars, battery line (+ discharge), dump hatched below zero, load line."""
    hh = np.asarray(h, float); x = np.r_[hh - 1, hh[-1]]                 # hour-ending values -> steps
    st = lambda v: np.r_[np.asarray(v, float), np.asarray(v, float)[-1]]
    ax.fill_between(x, 0, st(pv), step='post', color=C['PV'], alpha=0.35, lw=0)
    ax.step(x, st(pv), where='post', color=C['PV'], lw=0.9, label='PV')
    if wt is not None and np.nanmax(wt) > 0.01:
        ax.step(x, st(wt), where='post', color=C['WT'], lw=1.0, label='WT')
    if de_bars:
        ax.bar(hh - 0.5, de, width=0.82, color=C['DE'], lw=0, label='DE', zorder=3)
    ax.fill_between(x, 0, -st(dump), step='post', facecolor='none', edgecolor=C['dump'], hatch='////', lw=0, label='Dump')
    ax.step(x, st(pb), where='post', color=C['BS'], lw=1.1, label='Battery (+ discharge)', zorder=4)
    ax.step(x, st(load), where='post', color=C['load'], lw=1.3, label='Load', zorder=5)
    if lost is not None and np.nansum(lost) > 1e-3:
        ax.bar(hh - 0.5, lost, bottom=np.asarray(load) - np.asarray(lost), width=0.82, color=C['lost'], lw=0, label='Unserved', zorder=6)
    ax.axhline(0, color=INK2, lw=0.5)
    if ylim: ax.set_ylim(*ylim)


def soc_panel(ax, h, soc, color=None):
    hh = np.asarray(h, float); x = np.r_[hh - 1, hh[-1]]
    s = np.asarray(soc, float); s = np.r_[s, s[-1]] if len(s) == len(hh) else s
    ax.axhspan(0, 0.1, color='#efeeea', lw=0); ax.axhspan(0.9, 1, color='#efeeea', lw=0)
    ax.plot(x, s * 100 if s.max() <= 1.01 else s, color=color or C['BS'], lw=1.1)
    ax.set_ylim(0, 100); ax.set_yticks([10, 50, 90]); ax.set_ylabel('SOC [%]')


def legend_handles(keys):
    H = {'Load': Line2D([], [], color=C['load'], lw=1.3), 'PV': Patch(fc=C['PV'], alpha=0.5, ec=C['PV'], lw=0.8),
         'WT': Line2D([], [], color=C['WT'], lw=1.0), 'DE': Patch(fc=C['DE'], lw=0),
         'Battery (+ discharge)': Line2D([], [], color=C['BS'], lw=1.1),
         'Dump': Patch(fc='none', ec=C['dump'], hatch='////', lw=0), 'Unserved': Patch(fc=C['lost'], lw=0)}
    return [H[k] for k in keys], keys


# ---------------------------------------------------------------- sizing-stage operation (Fig. 4)
def sizing_operation():
    d = pd.read_csv(RR / 'series_S3_16kW.csv'); n = len(d)
    day = np.repeat(np.arange(365), 24); hod = np.tile(np.arange(24), 365)
    fig = plt.figure(figsize=(FULL, 5.1))
    outer = fig.add_gridspec(2, 1, height_ratios=[2.75, 2.6], hspace=0.28)
    gt = outer[0].subgridspec(2, 2, height_ratios=[2.0, 0.75], hspace=0.1, wspace=0.12)
    gb = outer[1].subgridspec(2, 1, hspace=0.62)
    weeks = [(0, 'Sunny week, 1–7 January'), (165, 'Low-resource week, 15–21 June')]
    ylim = (-45, 55)
    for j, (d0, title) in enumerate(weeks):
        sl = slice(d0 * 24, (d0 + 7) * 24); s = d.iloc[sl]; h = np.arange(1, 7 * 24 + 1)
        a = fig.add_subplot(gt[0, j]); b = fig.add_subplot(gt[1, j], sharex=a)
        power_panel(a, h, s.load, s.P_PV, s.P_DE, s.P_b, s.P_dump, wt=s.P_WT, lost=s.P_lost, ylim=ylim)
        soc_panel(b, h, s.soc.to_numpy())
        for x_ in (a, b):
            x_.set_xlim(0, 168); x_.set_xticks(range(0, 169, 24))
        b.set_xticklabels([''] * 8); b.set_xticks(range(12, 169, 24), minor=True)
        b.set_xticklabels([str(k) for k in range(d0 - MSTART[0 if d0 < 31 else 5] + 1, d0 - MSTART[0 if d0 < 31 else 5] + 8)], minor=True)
        b.tick_params(axis='x', which='minor', length=0); b.set_xlabel(['Day of January', 'Day of June'][j])
        a.tick_params(axis='x', which='both', labelbottom=False)
        panel(a, 'ab'[j], title)
        if j == 0: a.set_ylabel('Power [kW]')
        else: a.set_yticklabels([]); b.set_ylabel(''); b.set_yticklabels([])
    hdl, lab = legend_handles(['Load', 'PV', 'DE', 'Battery (+ discharge)', 'Dump'])
    fig.legend(hdl, lab, loc='upper center', ncol=5, bbox_to_anchor=(0.5, 0.965), fontsize=7)
    for r, (col, cmap, lab_, letter, vmax) in enumerate([('soc', SEQ_VIOLET, 'Battery SOC [%]', 'c', 100), ('P_DE', SEQ_RED, 'DE output [kW]', 'd', None)]):
        a = fig.add_subplot(gb[r, 0])
        M = d[col].to_numpy().reshape(365, 24).T * (100 if col == 'soc' else 1)
        if col == 'P_DE': M = np.ma.masked_less_equal(M, 0); cmap = cmap.copy(); cmap.set_bad('white')
        im = a.imshow(M, aspect='auto', origin='lower', cmap=cmap, vmin=0, vmax=vmax or M.max(), extent=(0, 365, 0, 24), interpolation='nearest')
        a.set_yticks([0, 6, 12, 18, 24]); a.set_ylabel('Hour'); a.grid(False)
        month_axis(a, label=(r == 1))
        for m in MSTART[1:]: a.axvline(m, color='white', lw=0.4)
        cb = fig.colorbar(im, ax=a, pad=0.012, fraction=0.03, aspect=8); cb.set_label(lab_, fontsize=7); cb.outline.set_linewidth(0.4); cb.ax.tick_params(labelsize=6.5, width=0.4, length=2)
        panel(a, letter, ['Battery state of charge over the year', 'DE output over the year'][r])
    save(fig, 'rev_sizing_operation')


# ---------------------------------------------------------------- wind role (Fig. 5)
def wind_role():
    W = RES / 'wind_design'; F = pd.read_csv(W / 'forced_nw.csv').sort_values('value')
    S = pd.read_csv(W / 'series_nw4.csv'); S['h'] = np.tile(np.arange(24), 365)
    fig, ax = plt.subplots(1, 3, figsize=(FULL, 1.95), gridspec_kw=dict(wspace=0.42))
    a = ax[0]; a.plot(F.nw, F.LCOE_abs, color=BLUE, marker='o', ms=3.5); a.set_ylabel('LCOE [USD/kWh]')
    a.set_xlabel('Number of turbines (fixed)'); panel(a, 'a')
    a = ax[1]; a.plot(F.nw, F.Dump, color=AQUA, marker='^', ms=3.5); a.set_ylabel('Dump fraction'); a.set_ylim(0, None)
    a.set_xlabel('Number of turbines (fixed)'); panel(a, 'b')
    a = ax[2]; dm = S.groupby('h')[['load', 'P_PV', 'P_WT']].mean(); hh = np.arange(24) + 0.5
    for col, lab, c_, ls in [('load', 'Load', C['load'], '-'), ('P_PV', 'PV', C['PV'], '-'), ('P_WT', 'WT', C['WT'], '--')]:
        a.plot(hh, dm[col] / dm[col].mean(), color=c_, ls=ls, label=lab, lw=1.3 if col == 'load' else 1.2)
    a.set_xlim(0, 24); a.set_xticks(range(0, 25, 6)); a.set_xlabel('Hour of day'); a.set_ylabel('Mean output / daily mean'); a.set_ylim(0, None)
    a.legend(loc='upper left', fontsize=6.8); panel(a, 'c')
    save(fig, 'rev_wind_role')


# ---------------------------------------------------------------- Pareto figures (Figs. 6-8)
def nondominated(F):
    keep = np.ones(len(F), bool)
    for i in range(len(F)):
        if keep[i]:
            dom = np.all(F <= F[i], 1) & np.any(F < F[i], 1)
            if dom.any(): keep[i] = False
    return keep


def pareto_inputs():
    A = np.loadtxt(RR / 'pareto_16kW_5obj.csv', delimiter=',')
    pv, wt, eb, lc = A[:, 0] * PV_KW, A[:, 1] * WT_KW, A[:, 2], A[:, 3]
    fig, ax = plt.subplots(1, 2, figsize=(FULL, 2.3), gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.38))
    a = ax[0]; nw0 = A[:, 1] == 0
    sc = a.scatter(pv[nw0], eb[nw0], c=lc[nw0], cmap=SEQ_BLUE, vmin=lc.min(), vmax=lc.max(), s=11, lw=0, zorder=3)
    a.scatter(pv[~nw0], eb[~nw0], c=lc[~nw0], cmap=SEQ_BLUE, vmin=lc.min(), vmax=lc.max(), s=20, marker='D', edgecolors=INK, linewidths=0.5, zorder=4)
    cb = fig.colorbar(sc, ax=a, pad=0.02, aspect=18); cb.set_label('LCOE (norm.)', fontsize=7); cb.outline.set_linewidth(0.4); cb.ax.tick_params(labelsize=6.5)
    a.set_xlabel('PV capacity [kW]'); a.set_ylabel('Battery capacity [kWh]')
    a.legend([Line2D([], [], ls='', marker='o', ms=3.5, color=SEQ_BLUE(0.6)), Line2D([], [], ls='', marker='D', ms=3.5, mfc=SEQ_BLUE(0.6), mec=INK, mew=0.5)],
             ['no wind turbine', 'with wind turbines'], loc='lower right', fontsize=6.8, handletextpad=0.2)
    panel(a, 'a')
    a = ax[1]; x, y = A[:, 7], A[:, 4]
    c = np.polyfit(x, y, 1); r2 = np.corrcoef(x, y)[0, 1] ** 2
    a.scatter(x, y, s=9, color=BLUE, lw=0, zorder=3); xs = np.linspace(0, x.max() * 1.03, 20); a.plot(xs, np.polyval(c, xs), color=INK2, lw=0.8, ls='--', zorder=2)
    a.text(0.05, 0.93, f'$R^2$ = {r2:.3f}', transform=a.transAxes, fontsize=7, va='top')
    a.set_xlabel(r'$1-$REF'); a.set_ylabel('Emissions (norm.)'); a.set_xlim(0, None); a.set_ylim(0, None); panel(a, 'b')
    save(fig, 'rev_pareto_inputs')


def pareto_objectives():
    F = np.loadtxt(RR / 'pareto_7kW_4obj.csv', delimiter=','); f = F[:, 3:7].copy(); f[:, 2] *= 100
    nm = ['LCOE (norm.)', 'Emissions (norm.)', 'DPSP [%]', 'Dump fraction']
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (3, 2)]
    fig, ax = plt.subplots(2, 3, figsize=(FULL, 3.35), gridspec_kw=dict(hspace=0.55, wspace=0.38))
    rk = lambda v: pd.Series(v).rank().to_numpy()
    for k, (a, (i, j)) in enumerate(zip(ax.ravel(), pairs)):
        a.scatter(f[:, i], f[:, j], s=7, color=BLUE, lw=0, alpha=0.9)
        rho = np.corrcoef(rk(f[:, i]), rk(f[:, j]))[0, 1]
        px, py, ha = {0: (0.04, 0.95, 'left'), 1: (0.04, 0.95, 'left'), 2: (0.97, 0.55, 'right'), 3: (0.04, 0.95, 'left')}.get(k, (0.97, 0.95, 'right'))
        a.text(px, py, rf'$\rho$ = {rho:.2f}'.replace('-', '\u2212'), transform=a.transAxes, ha=ha, va='top', fontsize=7,
               bbox=dict(fc='white', ec='none', pad=1.0, alpha=0.9))
        a.set_xlabel(nm[i]); a.set_ylabel(nm[j]); panel(a, 'abcdef'[k])
    save(fig, 'rev_pareto_objectives')


def pareto_reps():
    A = np.loadtxt(RR / 'pareto_16kW_5obj.csv', delimiter=','); F16 = A[:, 3:8]
    nd = nondominated(F16); F16 = F16[nd]
    B = np.loadtxt(RR / 'pareto_7kW_4obj.csv', delimiter=','); F7 = B[:, 3:7]; F7 = F7[nondominated(F7)]
    R = pd.read_csv(RES / 'pareto' / 'representatives_continuous.csv')
    T = pd.read_csv(RR / 'main_tables.csv'); s3 = T[T.tag == 'S3'].iloc[0]
    mk = {'knee': ('D', ORANGE, 'Knee point'), 'compromise_L2': ('s', AQUA, 'Compromise ($L_2$)'),
          'TOPSIS_equal': ('^', VIOLET, 'TOPSIS, equal'), 'TOPSIS_cost': ('v', YELLOW, 'TOPSIS, cost'),
          'TOPSIS_sustain': ('P', GREEN, 'TOPSIS, sustainability'), 'TOPSIS_reliability': ('X', MAGENTA, 'TOPSIS, reliability')}
    fig, ax = plt.subplots(1, 2, figsize=(FULL, 2.75), gridspec_kw=dict(wspace=0.5))
    # (a) 16 kW
    a = ax[0]; sc = a.scatter(F16[:, 0], F16[:, 1], c=F16[:, 3], cmap=SEQ_BLUE, s=9, lw=0, vmin=0, zorder=2)
    cb = fig.colorbar(sc, ax=a, pad=0.02, aspect=18); cb.set_label('Dump fraction', fontsize=7); cb.outline.set_linewidth(0.4); cb.ax.tick_params(labelsize=6.5)
    r16 = R[R.front == '16kW'].set_index('label')
    for lab, (m, c_, txt) in mk.items():
        if lab in r16.index:
            r = r16.loc[lab]; a.scatter(r.LCOE_n, r.Em_n, marker=m, s=34, color=c_, edgecolors=INK, linewidths=0.5, zorder=5, label=txt)
    a.scatter(s3.LCOE_n, s3.Em_n, marker='*', s=70, color=RED, edgecolors=INK, linewidths=0.5, zorder=6, label='Weighted-sum PSO')
    a.set_xlabel('LCOE (norm.)'); a.set_ylabel('Emissions (norm.)'); panel(a, 'a', '16 kW DE, five objectives')
    ins = a.inset_axes([0.14, 0.5, 0.4, 0.46]); x0, x1, y0, y1 = 0.355, 0.465, -0.003, 0.062
    ins.scatter(F16[:, 0], F16[:, 1], c=F16[:, 3], cmap=SEQ_BLUE, s=9, lw=0, vmin=0, zorder=2)
    for lab, (m, c_, txt) in mk.items():
        if lab in r16.index:
            r = r16.loc[lab]; ins.scatter(r.LCOE_n, r.Em_n, marker=m, s=34, color=c_, edgecolors=INK, linewidths=0.5, zorder=5)
    ins.scatter(s3.LCOE_n, s3.Em_n, marker='*', s=70, color=RED, edgecolors=INK, linewidths=0.5, zorder=6)
    ins.set_xlim(x0, x1); ins.set_ylim(y0, y1); ins.tick_params(labelsize=6, length=1.5); ins.set_facecolor('white')
    for s_ in ins.spines.values(): s_.set_visible(True); s_.set_linewidth(0.5); s_.set_color(INK2)
    a.indicate_inset_zoom(ins, edgecolor=INK2, lw=0.5, alpha=0.8)
    # (b) 7 kW
    a = ax[1]; sc = a.scatter(F7[:, 0], F7[:, 2] * 100, c=F7[:, 1], cmap=SEQ_BLUE, s=9, lw=0, vmin=0, zorder=2)
    cb = fig.colorbar(sc, ax=a, pad=0.02, aspect=18); cb.set_label('Emissions (norm.)', fontsize=7); cb.outline.set_linewidth(0.4); cb.ax.tick_params(labelsize=6.5)
    r7 = R[R.front == '7kW'].set_index('label')
    for lab, (m, c_, txt) in mk.items():
        if lab in r7.index:
            r = r7.loc[lab]; a.scatter(r.LCOE_n, r.DPSP * 100, marker=m, s=34, color=c_, edgecolors=INK, linewidths=0.5, zorder=5)
    a.set_xlabel('LCOE (norm.)'); a.set_ylabel('DPSP [%]'); panel(a, 'b', '7 kW DE, four objectives')
    hd = [Line2D([], [], ls='', marker=m, ms=5.5 if m != 'P' else 6, mfc=c_, mec=INK, mew=0.5) for _, (m, c_, _t) in mk.items()] + \
         [Line2D([], [], ls='', marker='*', ms=8, mfc=RED, mec=INK, mew=0.5)]
    lb = [t for _, (_m, _c, t) in mk.items()] + ['Weighted-sum PSO (16 kW only)']
    fig.legend(hd, lb, loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.13), fontsize=7)
    save(fig, 'rev_pareto_representatives')


# ---------------------------------------------------------------- cost-reliability front (Fig. 10)
def dg_front():
    E = pd.read_csv(RES / 'short_runs' / 'eps_front.csv').sort_values('value'); x = E.value * 100
    fig, ax = plt.subplots(1, 3, figsize=(FULL, 1.9), gridspec_kw=dict(wspace=0.42))
    for a, (y, c_, m, yl) in zip(ax, [(E.LCOE_abs, BLUE, 'o', 'LCOE [USD/kWh]'), (E.PDE, C['DE'], 's', 'DE rating [kW]'), (E.Em_abs / 1000, ORANGE, '^', 'Emissions [t/y]')]):
        a.plot(x, y, color=c_, marker=m, ms=3.5); a.set_ylabel(yl); a.set_xlabel(r'DPSP limit $\varepsilon$ [%]'); a.set_xlim(-0.15, 5.15)
    ax[1].set_ylim(0, None); ax[2].set_ylim(0, None)
    for a, l in zip(ax, 'abc'): panel(a, l)
    save(fig, 'rev_dg_front')


# ---------------------------------------------------------------- sensitivity grid (Figs. 11-15 merged)
SENS = [('DG_rating', 'DG rating [kW]', 1), ('diesel_price', 'Diesel price [USD/gal]', 1), ('interest', 'Interest rate [%]', 100),
        ('inflation', 'Inflation rate [%]', 100), ('LI_price', 'Li-ion price [USD/kWh]', 1)]


def sensitivity():
    S = pd.read_csv(RR / 'sweeps.csv')
    fig, ax = plt.subplots(5, 5, figsize=(FULL, 7.3), gridspec_kw=dict(hspace=0.78, wspace=0.5))
    cols = ['LCOE [USD/kWh]', 'Emissions [t/y]', 'PV [kW]', 'Battery [kWh]', 'DE operation [h/y]']
    letters = 'abcdefghijklmnopqrstuvwxy'; k = 0
    for r, (tag, xl, fac) in enumerate(SENS):
        d = S[S.tag == tag].sort_values('value'); x = d.value * fac
        a = ax[r, 0]; a.plot(x, d.LCOE_abs, color=BLUE, label='Hybrid MG'); a.plot(x, d.LCOE_base, color=C['base'], ls='--', lw=1.0, label='Diesel-only')
        a.set_ylim(0, None)
        ax[r, 1].plot(x, d.Em_abs / 1000, color=ORANGE); ax[r, 1].set_ylim(0, None)
        ax[r, 2].plot(x, d.ns * PV_KW, color=C['PV']); ax[r, 2].set_ylim(0, 90)
        ax[r, 3].plot(x, d.Eb, color=C['BS']); ax[r, 3].set_ylim(0, 420)
        ok = ~((tag == 'DG_rating') & (d.value <= 0)).to_numpy()  # no generator installed at 0 kW
        ax[r, 4].plot(x[ok], d.DE_hours[ok], color=C['DE']); ax[r, 4].set_ylim(0, None)
        for j in range(5):
            a = ax[r, j]; a.set_xlim(ax[r, 0].get_xlim()); a.set_xlabel(xl, fontsize=7); a.tick_params(labelsize=7); panel(a, letters[k]); k += 1
            if r == 0: a.text(0.5, 1.3, cols[j], transform=a.transAxes, ha='center', fontsize=7.6, weight='bold')
    if (S[S.tag.isin([t for t, _, _ in SENS])].nw > 0).any(): print('WARNING: some sweep designs have wind turbines; not shown')
    fig.subplots_adjust(top=0.9); h_, l_ = ax[0, 0].get_legend_handles_labels(); fig.legend(h_, l_, loc='upper center', ncol=2, bbox_to_anchor=(0.5, 0.985), fontsize=7)
    save(fig, 'rev_sensitivity')


def weights():
    S = pd.read_csv(RR / 'sweeps.csv'); W = S[S.tag.str.startswith('w')]
    wl = ['$w_1$ (LCOE)', '$w_2$ (emissions)', '$w_3$ (DPSP)', '$w_4$ (dump)', r'$w_5$ ($1-$REF)']
    fig, ax = plt.subplots(3, 5, figsize=(FULL, 4.6), sharey='row', gridspec_kw=dict(hspace=0.5, wspace=0.12))
    for k in range(5):
        d = W[W.tag == f'w{k+1}'].sort_values('value')
        for c in ['LCOE_n', 'Em_n', 'Dump', 'DPSP', 'oneminusREF']:
            if c == 'DPSP' and d.DPSP.max() <= 0: continue
            col, m, ls = OBJ[c]; ax[0, k].plot(d.value, d[c], color=col, marker=m, ms=2.6, ls=ls, lw=1.0, label=OBJLAB[c])
        ax[1, k].plot(d.value, d.ns * PV_KW, color=C['PV'], marker='o', ms=2.6, lw=1.0, label='PV')
        ax[1, k].plot(d.value, d.nw * WT_KW, color=C['WT'], marker='^', ms=2.6, lw=1.0, ls='--', label='WT')
        ax[2, k].plot(d.value, d.Eb, color=C['BS'], marker='o', ms=2.6, lw=1.0)
        ax[2, k].set_xlabel(wl[k])
        for r in range(3): ax[r, k].set_xticks([0, 0.5, 1]); ax[r, k].set_xlim(-0.03, 1.03)
        for r in range(2): ax[r, k].set_xticklabels([])
        panel(ax[0, k], 'abcde'[k]); panel(ax[1, k], 'fghij'[k]); panel(ax[2, k], 'klmno'[k])
    ax[0, 0].set_ylabel('Normalized value'); ax[1, 0].set_ylabel('Rated power [kW]'); ax[2, 0].set_ylabel('Battery [kWh]')
    ax[2, 0].set_ylim(0, 420); ax[1, 0].set_ylim(0, None)
    h0, l0 = ax[0, 3].get_legend_handles_labels(); h1, l1 = ax[1, 0].get_legend_handles_labels()
    fig.legend(h0 + h1, l0 + l1, loc='upper center', ncol=7, bbox_to_anchor=(0.5, 0.965), fontsize=6.8)
    save(fig, 'rev_vary_weights')


# ---------------------------------------------------------------- Monte Carlo (Fig. 17)
def mc():
    M = RES / 'mc'; R = pd.read_csv(M / 'mc_results.csv'); S = R[R.scenario > 0]; tab = pd.read_csv(M / 'mc_table.csv')
    ids = list(tab.design_id); labs = [f'{l}\n[{n:.0f}, {w:.0f}, {e:.0f}]' for l, n, w, e in zip(tab.label.str.replace(' (chosen)', '', regex=False), tab.ns, tab.nw, tab.Eb)]
    labs = [l.replace('Weighted-sum PSO', 'Equal-weight (PSO)').replace('TOPSIS (equal, nominal)', 'TOPSIS, equal (nominal)') for l in labs]
    metrics = [('LCOE_abs', 'LCOE [USD/kWh]', 1, 0), ('Em_abs', 'Emissions [t/y]', 1e-3, 0), ('DPSP', 'DPSP [%]', 100, 0), ('oneminusREF', 'REF [%]', -100, 100)]
    fig, ax = plt.subplots(1, 4, figsize=(FULL, 2.55), sharey=True, gridspec_kw=dict(wspace=0.12))
    yy = np.arange(len(ids))[::-1]
    hl = {ids[0]: INK, ids[1]: BLUE}
    for a, (col, xl, fac, off) in zip(ax, metrics):
        for y, i in zip(yy, ids):
            v = S[S.design_id == i][col].to_numpy() * fac + off
            p5, q1, med, q3, p95 = np.percentile(v, [5, 25, 50, 75, 95]); c_ = hl.get(i, INK2)
            a.plot([p5, p95], [y, y], color=c_, lw=0.8)
            a.add_patch(plt.Rectangle((q1, y - 0.26), max(q3 - q1, 1e-9), 0.52, fc='#eaf2fc' if i == ids[1] else ('#ecebe7' if i == ids[0] else 'white'), ec=c_, lw=0.8, zorder=3))
            a.plot([med, med], [y - 0.26, y + 0.26], color=c_, lw=1.4, zorder=4)
            nom = R[(R.scenario == 0) & (R.design_id == i)][col].iloc[0] * fac + off
            a.scatter([nom], [y], marker='o', s=14, color=RED, edgecolors='white', linewidths=0.5, zorder=5)
        a.set_xlabel(xl); a.grid(axis='y', visible=False); a.set_ylim(-0.6, len(ids) - 0.4)
    ax[0].set_yticks(yy); ax[0].set_yticklabels(labs, fontsize=7, linespacing=1.0); ax[0].tick_params(axis='y', length=0)
    for a, l in zip(ax, 'abcd'): panel(a, l)
    fig.legend([Line2D([], [], color=INK2, lw=0.8), Patch(fc='white', ec=INK2, lw=0.8), Line2D([], [], color=INK2, lw=1.4), Line2D([], [], ls='', marker='o', ms=4, mfc=RED, mec='white', mew=0.5)],
               ['5th–95th percentile', 'Interquartile range', 'Median', '2018 data (nominal)'], loc='lower center', ncol=4, bbox_to_anchor=(0.55, -0.13), fontsize=7)
    save(fig, 'rev_mc_distributions')


# ---------------------------------------------------------------- wind validation (Fig. A.22)
def wind_validation():
    w = sio.loadmat(ROOT / 'wind_speed.mat')['wind_speed'].ravel(); raw = w / 3.70
    lines = (REV / 'data' / 'nasa_power_timbila_2018.csv').read_text().split('\n'); k = [i for i, l in enumerate(lines) if l.startswith('YEAR')][0]
    P = pd.read_csv(REV / 'data' / 'nasa_power_timbila_2018.csv', skiprows=k)
    lag = int(json.load(open(RES / 'wind' / 'wind_validation.json'))['lag_h']); r = np.roll(raw, lag)
    df = pd.DataFrame({'mo': P.MO, 'hr': P.HR, 'raw': r, 'scaled': r * 3.70, 'ws2': P.WS2M, 'ws10': P.WS10M})
    m = df.groupby('mo').mean(numeric_only=True); dh = df.groupby('hr').mean(numeric_only=True)
    fig, ax = plt.subplots(1, 2, figsize=(FULL, 2.2), gridspec_kw=dict(wspace=0.3))
    a = ax[0]; mo = np.arange(1, 13)
    a.plot(mo, m.scaled, color=BLUE, marker='o', ms=3.2, label=r'TAHMO $\times$3.70 (model input)')
    a.plot(mo, m.raw, color=BLUE, marker='o', ms=3.2, mfc='white', ls=':', label='TAHMO raw')
    a.plot(mo, m.ws10, color=AQUA, marker='^', ms=3.2, label='POWER 10 m')
    a.plot(mo, m.ws2, color=ORANGE, marker='s', ms=3.2, label='POWER 2 m')
    a.set_xticks(mo); a.set_xticklabels(MONTHS); a.set_xlabel('Month (2018)'); a.set_ylabel('Mean wind speed [m/s]'); a.set_ylim(0, None)
    panel(a, 'a', 'Monthly means')
    a = ax[1]; h = np.arange(24)
    a.plot(h, dh.scaled, color=BLUE); a.plot(h, dh.raw, color=BLUE, ls=':'); a.plot(h, dh.ws10, color=AQUA); a.plot(h, dh.ws2, color=ORANGE)
    a.set_xlabel('Hour of day (local time)'); a.set_ylabel('Mean wind speed [m/s]'); a.set_ylim(0, None); a.set_xlim(0, 23); a.set_xticks(range(0, 24, 6))
    panel(a, 'b', 'Mean diurnal profiles')
    h_, l_ = ax[0].get_legend_handles_labels(); fig.legend(h_, l_, loc='upper center', ncol=4, bbox_to_anchor=(0.5, 1.06), fontsize=7)
    save(fig, 'rev_wind_validation')


# ---------------------------------------------------------------- climate inputs (Figs. A.23-A.24 merged)
def climate():
    sh = 2  # station series shifted by +2 h to local time, as in the model (load_data.m)
    irr = np.roll(sio.loadmat(ROOT / 'irradiance.mat')['irradiance'].ravel(), sh)
    ws = np.roll(sio.loadmat(ROOT / 'wind_speed.mat')['wind_speed'].ravel(), sh)
    tp = np.roll(sio.loadmat(ROOT / 'temp.mat')['temp'].ravel(), sh)
    fig, ax = plt.subplots(2, 3, figsize=(FULL, 3.8), gridspec_kw=dict(height_ratios=[1, 1], hspace=0.55, wspace=0.4))
    spec = [(irr, 'Irradiance [kW/m$^2$]', C['PV']), (ws, 'Wind speed [m/s]', C['WT']), (tp, 'Temperature [°C]', INK2)]
    days = {'1 Jan': 0, '17 Jun': 167}
    for j, (v, yl, c_) in enumerate(spec):
        a = ax[0, j]; D = v.reshape(365, 24)
        lo, hi = np.percentile(D, [10, 90], axis=0); hh = np.arange(24) + 0.5
        a.fill_between(hh, lo, hi, color=c_, alpha=0.18, lw=0, label='10th–90th pct., all days')
        a.plot(hh, D.mean(0), color=c_, lw=1.2, label='Mean of all days')
        a.plot(hh, D[0], color=INK, lw=0.9, ls='--', label='1 January (representative day)')
        a.plot(hh, D[167], color=INK, lw=0.9, ls=':', label='17 June (low-resource day)')
        a.set_xlim(0, 24); a.set_xticks(range(0, 25, 6)); a.set_xlabel('Hour of day (local time)'); a.set_ylabel(yl)
        if j < 2: a.set_ylim(0, None)
        panel(a, 'abc'[j])
        a = ax[1, j]; dmean = D.mean(1)
        a.plot(np.arange(365) + 0.5, dmean, color=c_, lw=0.8)
        a.plot(np.arange(365) + 0.5, pd.Series(dmean).rolling(15, center=True, min_periods=1).mean(), color=INK, lw=1.0)
        month_axis(a, fs=6.4); a.set_ylabel('Daily mean ' + yl[0].lower() + yl[1:].split(' [')[0] + ' [' + yl.split('[')[1])
        if j < 2: a.set_ylim(0, None)
        panel(a, 'def'[j])
    h_, l_ = ax[0, 0].get_legend_handles_labels()
    fig.legend(h_ + [Line2D([], [], color=INK, lw=1.0)], l_ + ['15-day running mean (bottom row)'], loc='upper center', ncol=3, bbox_to_anchor=(0.5, 1.07), fontsize=6.8)
    save(fig, 'rev_climate')


# ---------------------------------------------------------------- load (Fig. A.25)
def load():
    L = sio.loadmat(ROOT / 'Load.mat')['Load']; Ld = sio.loadmat(ROOT / 'Load_day.mat')['Load_day'].ravel()
    fig, ax = plt.subplots(1, 2, figsize=(FULL, 2.0), gridspec_kw=dict(width_ratios=[1, 1.5], wspace=0.3))
    a = ax[0]; hh = np.arange(24) + 0.5
    lo, hi = L.min(0), L.max(0)
    a.fill_between(np.r_[0, hh + 0.5], np.r_[lo[0], lo], np.r_[hi[0], hi], step='pre', color=MUTED, alpha=0.22, lw=0, label='Range over the year')
    a.step(np.r_[0, hh + 0.5], np.r_[Ld[0], Ld], where='pre', color=INK, lw=1.3, label='Representative day')
    a.set_xlim(0, 24); a.set_xticks(range(0, 25, 6)); a.set_ylim(0, None); a.set_xlabel('Hour of day (local time)'); a.set_ylabel('Load [kW]')
    a.legend(loc='upper left', fontsize=6.8); panel(a, 'a')
    a = ax[1]; dsum = L.sum(1)
    a.plot(np.arange(365) + 0.5, dsum, color=INK, lw=0.8); month_axis(a); a.set_ylabel('Daily energy [kWh]')
    a.set_ylim(0, dsum.max() * 1.15); panel(a, 'b')
    save(fig, 'rev_load')


# ---------------------------------------------------------------- site map (Fig. A.21)
def site_map():
    G = json.load(open(REV / 'data' / 'naturalearth_eastafrica.geojson'))
    lat0, lon0 = -3.39, 37.72  # Timbila TAHMO station (Table A.21)
    fig, ax = plt.subplots(1, 2, figsize=(FULL, 2.9), gridspec_kw=dict(width_ratios=[0.8, 1.25], wspace=0.08))

    def draw(a, bbox, lw=0.5, labels=False):
        for f in G['features']:
            p = f['properties']; kind = p.get('_layer')
            geom = f['geometry']; polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
            if kind == 'country':
                fc = '#eaf2fc' if p.get('ADM0_A3') == 'KEN' else '#f4f3ef'
                for poly in polys:
                    ring = np.array(poly[0]); a.fill(ring[:, 0], ring[:, 1], fc=fc, ec=INK2, lw=lw, zorder=1)
            elif kind == 'lake':
                for poly in polys:
                    ring = np.array(poly[0]); a.fill(ring[:, 0], ring[:, 1], fc='#cfe3f7', ec='none', zorder=2)
        a.set_xlim(bbox[0], bbox[1]); a.set_ylim(bbox[2], bbox[3]); a.set_aspect('equal'); a.set_facecolor('#d9e9f8')
        a.set_xticks([]); a.set_yticks([]); a.grid(False)
        for s_ in a.spines.values(): s_.set_visible(True); s_.set_linewidth(0.5); s_.set_color(INK2)

    a = ax[0]; draw(a, (-19, 53, -36, 38), lw=0.25)
    bb = (33.5, 42.0, -7.5, 5.2); a.add_patch(plt.Rectangle((bb[0], bb[2]), bb[1] - bb[0], bb[3] - bb[2], fc='none', ec=RED, lw=0.9, zorder=5))
    panel(a, 'a', 'Africa')
    a = ax[1]; draw(a, bb, lw=0.6)
    for f in G['features']:
        p = f['properties']
        if p.get('_layer') == 'place':
            x, y = f['geometry']['coordinates']
            if bb[0] < x < bb[1] and bb[2] < y < bb[3]:
                a.scatter(x, y, s=8, color=INK, zorder=6)
                dx, ha = (-0.15, 'right') if p['NAME'] in ('Arusha',) else (0.15, 'left')
                a.text(x + dx, y + 0.12, p['NAME'], fontsize=6.8, ha=ha, zorder=6)
    a.scatter(lon0, lat0, marker='*', s=90, color=RED, edgecolors=INK, linewidths=0.5, zorder=7)
    a.text(lon0 + 0.18, lat0 + 0.2, 'Timbila', fontsize=7.5, weight='bold', ha='left', zorder=7)
    for name, (x, y) in {'KENYA': (37.6, 1.0), 'TANZANIA': (35.3, -5.0), 'UGANDA': (33.7, 2.7), 'SOMALIA': (41.4, 2.6), 'ETHIOPIA': (38.2, 4.6)}.items():
        if bb[0] < x < bb[1] and bb[2] < y < bb[3]: a.text(x, y, name, fontsize=6.5, color=INK2, ha='left' if name == 'UGANDA' else 'center', style='italic', zorder=6)
    a.text(41.2, -5.5, 'Indian\nOcean', fontsize=6.5, color='#4d74a6', style='italic', ha='center')
    panel(a, 'b', 'Site and nearby cities')
    a.set_xticks(range(34, 43, 2)); a.set_yticks(range(-6, 6, 2)); a.tick_params(labelsize=6.5, length=2)
    a.set_xticklabels([f'{v}°E' for v in range(34, 43, 2)]); a.set_yticklabels([f'{abs(v)}°{"S" if v < 0 else ("N" if v > 0 else "")}' for v in range(-6, 6, 2)])
    save(fig, 'rev_site_map')


# ---------------------------------------------------------------- day-ahead dispatch (Secs. 7-8)
DD = RES / 'dispatch'; DL = RES / 'dispatch_lowres'


def _dispatch_cell(fig, spec, d, title, letter, ylim, rule=None, ylabel=True, xlabel=True):
    g = spec.subgridspec(2, 1, height_ratios=[2.2, 0.8], hspace=0.08)
    a = fig.add_subplot(g[0]); b = fig.add_subplot(g[1], sharex=a)
    pv = d.P_RES if 'P_PV' not in d else d.P_PV
    power_panel(a, d.hour, d.load, pv, d.P_DE, d.P_b, d.P_dump, lost=d.P_lost, ylim=ylim)
    if rule is not None:
        hh = np.asarray(rule.hour, float); x = np.r_[hh - 1, hh[-1]]
        a.step(x, np.r_[rule.P_DE, rule.P_DE.iloc[-1]], where='post', color=C['DE'], lw=0.8, ls=(0, (2, 1.2)), zorder=6, label='DE, rule-based')
    soc = np.r_[d.soc.to_numpy(), d.soc_end.iloc[-1]] if 'soc_end' in d else d.soc.to_numpy()
    hh = np.asarray(d.hour, float); xs = np.r_[hh - 1, hh[-1]] if len(soc) == len(hh) + 1 else hh - 1
    b.axhspan(0, 10, color='#efeeea', lw=0); b.axhspan(90, 100, color='#efeeea', lw=0)
    b.plot(xs, soc * 100, color=C['BS'], lw=1.1); b.set_ylim(0, 100); b.set_yticks([10, 50, 90])
    for x_ in (a, b): x_.set_xlim(0, 24); x_.set_xticks(range(0, 25, 6))
    a.tick_params(axis='x', labelbottom=False)
    if ylabel: a.set_ylabel('Power [kW]'); b.set_ylabel('SOC [%]')
    else: b.tick_params(axis='y', labelleft=False)
    if xlabel: b.set_xlabel('Hour of day')
    panel(a, letter, title)
    return a, b


def _rule_day(cfg):
    r = pd.read_csv(DL / f'rule_{cfg}.csv'); r['hour'] = np.arange(1, 25); return r


def dispatch_base():
    have = (DL / 'dispatch_d168_i_16kW.csv').exists()
    if not have:  # before the L111 run: the three configurations on 1 January only
        fig = plt.figure(figsize=(FULL, 2.4)); G = fig.add_gridspec(1, 3, wspace=0.08)
        for j, (cfg, title) in enumerate([('i_16kW', '(i) 16 kW DE'), ('ii_8kW_16kWsizing', '(ii) 8 kW DE, 16 kW design'), ('iii_8kW_8kWsizing', '(iii) 8 kW DE, 8 kW design')]):
            _dispatch_cell(fig, G[j], pd.read_csv(DD / f'dispatch_{cfg}.csv'), title, 'abc'[j], (-40, 55), ylabel=(j == 0))
        hdl, lab = legend_handles(['Load', 'PV', 'DE', 'Battery (+ discharge)', 'Dump'])
        fig.legend(hdl, lab, loc='upper center', ncol=5, bbox_to_anchor=(0.5, 1.06), fontsize=6.8)
        save(fig, 'rev_dispatch_base'); return
    fig = plt.figure(figsize=(FULL, 4.6)); G = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.16)
    ylim = (-40, 55)
    d = pd.read_csv(DD / 'dispatch_i_16kW.csv')
    _dispatch_cell(fig, G[0, 0], d, '1 January, configuration (i)', 'a', ylim, xlabel=False)
    cases = [('i_16kW', '17 June, (i) 16 kW DE', 'b'), ('ii_8kW_16kWsizing', '17 June, (ii) 8 kW DE, 16 kW design', 'c'), ('iii_8kW_8kWsizing', '17 June, (iii) 8 kW DE, 8 kW design', 'd')]
    pos = [G[0, 1], G[1, 0], G[1, 1]]
    for (cfg, title, l), sp in zip(cases, pos):
        if not have: continue
        d = pd.read_csv(DL / f'dispatch_d168_{cfg}.csv')
        _dispatch_cell(fig, sp, d, title, l, (-15, 20), rule=_rule_day(cfg), ylabel=(l == 'c'), xlabel=(l != 'b'))
    hdl, lab = legend_handles(['Load', 'PV', 'DE', 'Battery (+ discharge)', 'Dump', 'Unserved'])
    hdl.append(Line2D([], [], color=C['DE'], lw=0.8, ls=(0, (2, 1.2)))); lab.append('DE, rule-based')
    fig.legend(hdl, lab, loc='upper center', ncol=7, bbox_to_anchor=(0.5, 0.995), fontsize=6.8, columnspacing=1.0)
    save(fig, 'rev_dispatch_base')


def dispatch_res():
    b = pd.read_csv(DD / 'dispatch_iii_8kW_8kWsizing.csv'); ls = pd.read_csv(DD / 'dispatch_low_solar.csv'); lw = pd.read_csv(DD / 'dispatch_low_wind.csv')
    fig = plt.figure(figsize=(FULL, 2.35)); G = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.45], wspace=0.42)
    hh = b.hour - 0.5
    a = fig.add_subplot(G[0]); a.plot(hh, b.irr, color=C['PV'], label='1 January'); a.plot(hh, ls.irr, color=C['PV'], ls='--', label='10% case')
    a.set_ylabel('Irradiance [kW/m$^2$]'); hourly_axis(a); a.set_ylim(0, None); a.legend(loc='upper left', fontsize=6.8); panel(a, 'a')
    a = fig.add_subplot(G[1]); a.plot(hh, b.wind, color=C['WT'], label='1 January'); a.plot(hh, lw.wind, color=C['WT'], ls='--', label='10% case')
    a.set_ylabel('Wind speed [m/s]'); hourly_axis(a); a.set_ylim(0, None); a.legend(loc='upper left', fontsize=6.8); panel(a, 'b')
    _dispatch_cell(fig, G[2], ls, 'Schedule, 10% irradiance', 'c', (-2, 16))
    hdl, lab = legend_handles(['Load', 'PV', 'DE', 'Battery (+ discharge)'])
    fig.legend(hdl, lab, loc='upper center', ncol=4, bbox_to_anchor=(0.72, 1.08), fontsize=6.8)
    save(fig, 'rev_dispatch_res')


def dispatch_load():
    if not (DL / 'dispatch_d168_load_peaky.csv').exists(): print('dispatch_load: waiting for L111 results'); return
    base = pd.read_csv(DL / 'dispatch_d168_iii_8kW_8kWsizing.csv')
    fig = plt.figure(figsize=(FULL, 4.6)); G = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.08)
    g = G[0, 0].subgridspec(2, 1, height_ratios=[2.2, 0.8], hspace=0.08); a = fig.add_subplot(g[0])
    hh = np.asarray(base.hour, float); x = np.r_[hh - 1, hh[-1]]
    for c_, lab, col, ls_ in [('iii_8kW_8kWsizing', '17 June load', INK, '-'), ('load_peaky', 'Peakier', RED, '-'), ('load_shift', 'Shifted', BLUE, '--'), ('load_shift_curtail', 'Shifted, 10% curtailed', VIOLET, ':')]:
        d = pd.read_csv(DL / f'dispatch_d168_{c_}.csv'); a.step(x, np.r_[d.load, d.load.iloc[-1]], where='post', color=col, ls=ls_, lw=1.1, label=lab)
    a.set_xlim(0, 24); a.set_xticks(range(0, 25, 6)); a.set_ylim(0, 23); a.set_ylabel('Load [kW]'); a.set_xlabel('Hour of day')
    a.legend(loc='upper left', fontsize=6.6, ncol=2); panel(a, 'a', 'Demand profiles, 17 June')
    ylim = (-12, 20)
    for (c_, title, l), sp in zip([('load_peaky', 'Peakier profile', 'b'), ('load_shift', 'Load shifting', 'c'), ('load_shift_curtail', 'Shifting and 10% curtailment', 'd')], [G[0, 1], G[1, 0], G[1, 1]]):
        d = pd.read_csv(DL / f'dispatch_d168_{c_}.csv')
        _dispatch_cell(fig, sp, d, title, l, ylim, ylabel=(l == 'c'), xlabel=(l != 'b'))
    hdl, lab = legend_handles(['Load', 'PV', 'DE', 'Battery (+ discharge)', 'Dump', 'Unserved'])
    fig.legend(hdl, lab, loc='upper center', ncol=6, bbox_to_anchor=(0.5, 0.995), fontsize=6.8)
    save(fig, 'rev_dispatch_load')


ALL = ['workflow', 'benchmark', 'sizing_operation', 'wind_role', 'pareto_inputs', 'pareto_objectives', 'pareto_reps', 'dg_front',
       'sensitivity', 'weights', 'dispatch_base', 'dispatch_res', 'dispatch_load', 'mc', 'wind_validation', 'climate', 'load', 'site_map']
if __name__ == '__main__':
    for f in (sys.argv[1:] or ALL): globals()[f]()
