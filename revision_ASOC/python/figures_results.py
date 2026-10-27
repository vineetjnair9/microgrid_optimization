"""Figures and tables from the corrected re-runs (sweeps, dispatch, sizing series, Pareto, workflow)."""
from common import *
import sys
from matplotlib.patches import FancyBboxPatch
RR = RES / 'rerun'
LAB = {'J': 'Weighted objective J', 'LCOE_n': 'LCOE (norm.)', 'Em_n': 'Emissions (norm.)', 'DPSP': 'DPSP', 'Dump': 'Dump fraction', 'oneminusREF': '1 - REF'}
OC = {'J': INK, 'LCOE_n': PAL[0], 'Em_n': PAL[1], 'DPSP': PAL[7], 'Dump': PAL[2], 'oneminusREF': PAL[3]}
XL = {'DG_rating': 'DG rated power [kW]', 'diesel_price': 'Diesel price [USD/gal]', 'interest': 'Nominal interest rate [%]',
      'inflation': 'Inflation rate [%]', 'LI_price': 'Battery price [USD/kWh]'}
def sweeps():
    S = pd.read_csv(RR / 'sweeps.csv')
    for tag, xl in XL.items():
        d = S[S.tag == tag].sort_values('value'); x = d.value * (100 if tag in ('interest', 'inflation') else 1)
        fig, ax = plt.subplots(1, 4, figsize=(7.0, 1.9))
        for c in ['J', 'LCOE_n', 'Em_n', 'Dump', 'oneminusREF'] + (['DPSP'] if d.DPSP.max() > 0 else []):
            ax[0].plot(x, d[c], color=OC[c], lw=1.2, label=LAB[c])
        ax[0].set_ylabel('Normalized value'); ax[0].legend(frameon=False, fontsize=5.5)
        ax[1].plot(x, d.LCOE_abs, color=PAL[0], lw=1.2, label='Hybrid MG'); ax[1].plot(x, d.LCOE_base, color=INK2, lw=1.2, ls='--', label='Diesel-only baseline')
        ax[1].set_ylabel('LCOE [USD/kWh]'); ax[1].legend(frameon=False, fontsize=5.5); ax[1].set_ylim(0, None)
        ax[2].plot(x, d.ns * 0.255, color=PAL[3], lw=1.2, label='PV'); ax[2].plot(x, d.nw * 3.5, color=PAL[2], lw=1.2, label='WT')
        ax[2].set_ylabel('Rated capacity [kW]'); ax[2].legend(frameon=False, fontsize=5.5); ax[2].set_ylim(0, None)
        ax[3].plot(x, d.Eb, color=PAL[6], lw=1.2); ax[3].set_ylabel('Battery capacity [kWh]'); ax[3].set_ylim(0, None)
        for a, t in zip(ax, 'abcd'): a.set_xlabel(xl); a.set_title(f'({t})', loc='left')
        fig.tight_layout(); save(fig, f'rev_vary_{tag}')
    W = S[S.tag.str.startswith('w')]
    fig, ax = plt.subplots(2, 5, figsize=(7.0, 3.2), sharey='row')
    wl = ['$w_1$ (LCOE)', '$w_2$ (emissions)', '$w_3$ (DPSP)', '$w_4$ (dump)', '$w_5$ (1-REF)']
    for k in range(5):
        d = W[W.tag == f'w{k+1}'].sort_values('value')
        for c in ['LCOE_n', 'Em_n', 'Dump', 'oneminusREF'] + (['DPSP'] if d.DPSP.max() > 0 else []):
            ax[0, k].plot(d.value, d[c], color=OC[c], lw=1.1, label=LAB[c])
        ax[1, k].plot(d.value, d.ns * 0.255, color=PAL[3], lw=1.1, label='PV [kW]'); ax[1, k].plot(d.value, d.nw * 3.5, color=PAL[2], lw=1.1, label='WT [kW]')
        ax[1, k].plot(d.value, d.Eb / 10, color=PAL[6], lw=1.1, label='Battery [10 kWh]')
        ax[1, k].set_xlabel(wl[k])
    ax[0, 0].set_ylabel('Normalized value'); ax[1, 0].set_ylabel('Capacity')
    ax[0, 0].legend(frameon=False, fontsize=5); ax[1, 0].legend(frameon=False, fontsize=5)
    fig.tight_layout(); save(fig, 'rev_vary_weights')
def dispatch():
    D = RES / 'dispatch'
    groups = {'rev_dispatch_base': [('i_16kW', '16 kW DE, design sized for 16 kW'), ('ii_8kW_16kWsizing', '8 kW DE, design sized for 16 kW'), ('iii_8kW_8kWsizing', '8 kW DE, design sized for 8 kW')],
              'rev_dispatch_res': [('low_solar', 'Low irradiance (10%)'), ('low_wind', 'Low wind speed (10%)'), ('low_solar_wind', 'Low irradiance and wind')],
              'rev_dispatch_load': [('load_peaky', 'Peakier load'), ('load_shift', 'Load shifting'), ('load_shift_curtail', 'Shifting + 10% curtailment')]}
    for name, cases in groups.items():
        fig, ax = plt.subplots(2, 3, figsize=(7.0, 3.3), gridspec_kw={'height_ratios': [2.2, 1]}, sharex=True)
        for j, (c, title) in enumerate(cases):
            d = pd.read_csv(D / f'dispatch_{c}.csv'); h = d.hour
            ax[0, j].plot(h, d.load, color=INK, lw=1.3, label='Load'); ax[0, j].plot(h, d.P_RES, color=PAL[2], lw=1.2, label='RES (DC)')
            ax[0, j].plot(h, d.P_DE, color=PAL[1], lw=1.2, label='DE'); ax[0, j].plot(h, d.P_b, color=PAL[6], lw=1.2, label='Battery (+ discharge)')
            ax[0, j].plot(h, d.P_dump, color=PAL[3], lw=1.0, ls='--', label='Dump')
            ax[0, j].axhline(0, color=INK2, lw=0.5); ax[0, j].set_title(title, loc='left', fontsize=7)
            ax[1, j].plot(h, d.soc, color=PAL[6], lw=1.2); ax[1, j].set_ylim(0, 1); ax[1, j].axhline(0.1, color=INK2, lw=0.5, ls=':'); ax[1, j].axhline(0.9, color=INK2, lw=0.5, ls=':')
            ax[1, j].set_xlabel('Hour'); ax[1, j].set_xticks(range(0, 25, 6))
        ax[0, 0].set_ylabel('Power [kW]'); ax[1, 0].set_ylabel('SOC'); ax[0, 0].legend(frameon=False, fontsize=5.5, loc='upper left')
        fig.tight_layout(); save(fig, name)
def series():
    d = pd.read_csv(RR / 'series_S3_16kW.csv'); 
    fig, ax = plt.subplots(3, 2, figsize=(7.0, 5.0), gridspec_kw={'width_ratios': [2.3, 1]})
    for r, (n, lab) in enumerate([(24, '1 January 2018'), (168, 'First week'), (720, 'First 30 days')]):
        s = d.iloc[:n]; h = np.arange(1, n + 1)
        ax[r, 0].plot(h, s.load, color=INK, lw=1.0, label='Load'); ax[r, 0].plot(h, s.P_PV, color=PAL[3], lw=0.9, label='PV')
        ax[r, 0].plot(h, s.P_WT, color=PAL[2], lw=0.9, label='WT'); ax[r, 0].plot(h, s.P_DE, color=PAL[1], lw=0.9, label='DE')
        ax[r, 0].plot(h, s.P_b, color=PAL[6], lw=0.9, label='Battery (+ discharge)'); ax[r, 0].set_ylabel('Power [kW]'); ax[r, 0].set_title(lab, loc='left', fontsize=7)
        ax[r, 1].plot(h, s.soc, color=PAL[6], lw=0.9); ax[r, 1].set_ylim(0, 1); ax[r, 1].set_ylabel('SOC')
        ax[r, 0].set_xlabel('Hour'); ax[r, 1].set_xlabel('Hour')
    ax[0, 0].legend(frameon=False, fontsize=5.5, ncol=3)
    fig.tight_layout(); save(fig, 'rev_sizing_operation')
def pareto_figs():
    from numpy.polynomial import polynomial as Pn
    A0 = np.loadtxt(RR / 'pareto_16kW_5obj.csv', delimiter=',')
    pv, wt, eb, lc = A0[:, 0] * 0.255, A0[:, 1] * 3.5, A0[:, 2], A0[:, 3]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.4))
    sc = ax[0].scatter(pv, eb, c=lc, cmap='Blues', s=12, edgecolors='none'); fig.colorbar(sc, ax=ax[0], label='LCOE (norm.)', shrink=0.85)
    ax[0].set_xlabel('PV [kW]'); ax[0].set_ylabel('Battery [kWh]'); ax[0].set_title('(a)', loc='left')
    sc = ax[1].scatter(pv, wt, c=lc, cmap='Blues', s=12, edgecolors='none'); fig.colorbar(sc, ax=ax[1], label='LCOE (norm.)', shrink=0.85)
    ax[1].set_xlabel('PV [kW]'); ax[1].set_ylabel('WT [kW]'); ax[1].set_title('(b)', loc='left')
    fig.tight_layout(); save(fig, 'rev_pareto_inputs')
    keynum(RES / 'pareto' / 'inputs_stats.txt', {'N_WT0': int((A0[:, 1] == 0).sum()), 'N': len(A0), 'PV_min': round(pv.min(), 1), 'PV_max': round(pv.max(), 1), 'EB_min': round(eb.min(), 0), 'EB_max': round(eb.max(), 0), 'N_EB400': int((eb >= 399).sum()), 'WT_max': round(wt.max(), 1)})
    F = np.loadtxt(RR / 'pareto_7kW_4obj.csv', delimiter=','); f = F[:, 3:7]; nm = ['LCOE (norm.)', 'Emissions (norm.)', 'DPSP', 'Dump fraction']
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (3, 2)]
    fig, ax = plt.subplots(2, 3, figsize=(7.0, 3.8))
    for a, (i, j) in zip(ax.ravel(), pairs):
        a.scatter(f[:, i], f[:, j], s=8, color=PAL[0], edgecolors='none'); a.set_xlabel(nm[i]); a.set_ylabel(nm[j])
    fig.tight_layout(); save(fig, 'rev_pareto_objectives')
    A = np.loadtxt(RR / 'pareto_16kW_5obj.csv', delimiter=',')
    fig, a = plt.subplots(figsize=(3.0, 2.3)); x, y = A[:, 7], A[:, 4]
    a.scatter(x, y, s=8, color=PAL[0], edgecolors='none'); c = np.polyfit(x, y, 1); r2 = np.corrcoef(x, y)[0, 1] ** 2
    xs = np.linspace(x.min(), x.max(), 20); a.plot(xs, np.polyval(c, xs), color=PAL[1], lw=1); a.text(0.05, 0.92, f'$R^2$ = {r2:.3f}', transform=a.transAxes, fontsize=7, va='top')
    a.set_xlabel('1 - REF'); a.set_ylabel('Emissions (norm.)'); fig.tight_layout(); save(fig, 'rev_ref_emissions')
    keynum(RES / 'pareto' / 'ref_em_r2.txt', {'R2': round(r2, 4)})
def workflow():
    fig, ax = plt.subplots(figsize=(7.0, 1.75)); ax.axis('off'); ax.set_xlim(0, 102); ax.set_ylim(0, 30)
    boxes = [('Data', 'TAHMO weather,\nREopt load\n(2018, hourly)'), ('Stage 1:\nsizing', 'rule-based 8760 h\nsimulation in PSO\n(weighted sum)'),
             ('Pareto\nsearch', 'paretosearch,\ngamultiobj'), ('Design\nselection', 'extremes, knee,\nL2 compromise,\nTOPSIS'),
             ('Monte Carlo\nre-ranking', '500 scenarios;\nCVaR,\nP(DPSP > 1%)'), ('Stage 2:\ndispatch', 'day-ahead SQP\ndispatch;\nstress tests')]
    w, gap = 14.6, 2.4
    for i, (t, b) in enumerate(boxes):
        x = 0.5 + i * (w + gap); hl = i in (3, 4)
        ax.add_patch(FancyBboxPatch((x, 2), w, 26, boxstyle='round,pad=0.2,rounding_size=1.0', fc='#e8f1fb' if hl else 'white', ec=PAL[0] if hl else INK2, lw=1))
        ax.text(x + w / 2, 22.5, t, ha='center', va='center', fontsize=6.5, weight='bold', color=INK, linespacing=1.1)
        ax.text(x + w / 2, 9.5, b, ha='center', va='center', fontsize=5.6, color=INK, linespacing=1.15)
        if i < len(boxes) - 1: ax.annotate('', xy=(x + w + gap - 0.2, 15), xytext=(x + w + 0.4, 15), arrowprops=dict(arrowstyle='-|>', color=INK2, lw=0.9, mutation_scale=7))
    save(fig, 'rev_workflow')
def dgfront():
    E = pd.read_csv(RES / 'short_runs' / 'eps_front.csv').sort_values('value')
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.1)); x = E.value * 100
    ax[0].plot(x, E.LCOE_abs, color=PAL[0], marker='o', ms=4, lw=1.2); ax[0].set_ylabel('LCOE [USD/kWh]')
    ax[1].plot(x, E.PDE, color=PAL[1], marker='o', ms=4, lw=1.2); ax[1].set_ylabel('DE rating [kW]'); ax[1].set_ylim(0, None)
    ax[2].plot(x, E.Em_abs / 1000, color=PAL[2], marker='o', ms=4, lw=1.2, label='Emissions [t/y]')
    ax[2].plot(x, E.ns * 0.255, color=PAL[3], marker='s', ms=3.5, lw=1.2, label='PV [kW]')
    ax[2].plot(x, E.Eb / 10, color=PAL[6], marker='^', ms=3.5, lw=1.2, label='Battery [10 kWh]'); ax[2].legend(frameon=False, fontsize=5.5)
    for a, t in zip(ax, 'abc'): a.set_xlabel(r'DPSP limit $\varepsilon$ [%]'); a.set_title(f'({t})', loc='left')
    fig.tight_layout(); save(fig, 'rev_dg_front')

def windfig():
    W = RES / 'wind_design'; F = pd.read_csv(W / 'forced_nw.csv').sort_values('value')
    S = pd.read_csv(W / 'series_nw4.csv'); S['h'] = np.tile(np.arange(1, 25), 365)
    md = [31,28,31,30,31,30,31,31,30,31,30,31]; S['m'] = np.repeat(np.repeat(np.arange(1, 13), md), 24)
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.2))
    ax[0].plot(F.nw, F.LCOE_abs, color=PAL[0], marker='o', ms=3.5, lw=1.2); ax[0].set_ylabel('LCOE [USD/kWh]')
    a2 = ax[0]; a2.set_xlabel('Number of wind turbines (fixed)')
    ax[1].plot(F.nw, F.Dump, color=PAL[2], marker='o', ms=3.5, lw=1.2, label='Dump fraction'); ax[1].plot(F.nw, F.Em_abs / F.Em_abs.max(), color=PAL[1], marker='s', ms=3, lw=1.2, label='Emissions (rel. to max)')
    ax[1].plot(F.nw, F.Eb / F.Eb.max(), color=PAL[6], marker='^', ms=3, lw=1.2, label='Battery (rel. to max)'); ax[1].legend(frameon=False, fontsize=5.5); ax[1].set_xlabel('Number of wind turbines (fixed)'); ax[1].set_ylim(0, None)
    d = S.groupby('h')[['P_PV', 'P_WT', 'load']].mean()
    ax[2].plot(d.index, d.load, color=INK, lw=1.2, label='Load'); ax[2].plot(d.index, d.P_PV / 10, color=PAL[3], lw=1.2, label='PV / 10'); ax[2].plot(d.index, d.P_WT, color=PAL[2], lw=1.2, label='WT (4 turbines)')
    ax[2].set_xlabel('Hour of day (local time)'); ax[2].set_ylabel('Mean power [kW]'); ax[2].legend(frameon=False, fontsize=5.5); ax[2].set_xticks(range(0, 25, 6))
    for a, t in zip(ax, 'abc'): a.set_title(f'({t})', loc='left')
    fig.tight_layout(); save(fig, 'rev_wind_role')
def profiles():
    D = RES / 'dispatch'; b = pd.read_csv(D / 'dispatch_iii_8kW_8kWsizing.csv'); ls = pd.read_csv(D / 'dispatch_low_solar.csv'); lw = pd.read_csv(D / 'dispatch_low_wind.csv')
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.1)); h = b.hour
    ax[0].plot(h, b.irr, color=PAL[3], lw=1.2, label='Baseline'); ax[0].plot(h, ls.irr, color=PAL[3], lw=1.2, ls='--', label='Low (10%)'); ax[0].set_ylabel('Irradiance [kW/m$^2$]')
    ax[1].plot(h, b.wind, color=PAL[2], lw=1.2, label='Baseline'); ax[1].plot(h, lw.wind, color=PAL[2], lw=1.2, ls='--', label='Low (10%)'); ax[1].set_ylabel('Wind speed [m/s]')
    for c, lab, col in [('iii_8kW_8kWsizing', 'Baseline', INK), ('load_peaky', 'Peakier', PAL[7]), ('load_shift', 'Shifted', PAL[0]), ('load_shift_curtail', 'Shifted + 10% curtailed', PAL[6])]:
        d = pd.read_csv(D / f'dispatch_{c}.csv'); ax[2].plot(d.hour, d.load, color=col, lw=1.2, label=lab)
    ax[2].set_ylabel('Load [kW]')
    for a, t in zip(ax, 'abc'): a.set_xlabel('Hour (local time)'); a.set_title(f'({t})', loc='left'); a.legend(frameon=False, fontsize=5.5); a.set_xticks(range(0, 25, 6)); a.set_ylim(0, None)
    fig.tight_layout(); save(fig, 'rev_dispatch_profiles')
if __name__ == '__main__':
    for f in sys.argv[1:]: globals()[f]()
