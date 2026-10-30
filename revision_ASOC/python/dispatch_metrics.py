"""Daily cost, emissions and related metrics of an hourly schedule, with the same cost terms as
matlab/dispatch_obj.m (stage H). Used to score the rule-based (sizing-stage) schedule of a day on the same
basis as the optimized day-ahead schedule. Validated against the MATLAB results by `python3 dispatch_metrics.py`."""
import numpy as np, pandas as pd
from figstyle import RES

K_EM = 0.649 + (4.063288937 + 18.85658039 + 0.007381439 + 1.502443664 + 3 * 1.338208931) / 1000  # kg per kWh of DE output


def day_metrics(load, P_RES, P_DE, P_b, P_dump, x, P_rated, C_DE=3.20, base_rating=16):
    load, P_RES, P_DE, P_b, P_dump = (np.asarray(v, float) for v in (load, P_RES, P_DE, P_b, P_dump))
    ns, nw, Eb = x
    on = P_DE > 1e-9
    starts = int(on[0]) + int(np.sum(on[1:] & ~on[:-1])); stops = int(np.sum(~on[1:] & on[:-1]))
    fuel_L = np.sum(on * 0.08145 * P_rated + 0.246 * P_DE)
    om_fix = (0.01 * ns * 0.255 * 1210 + 0.03 * nw * 3.5 * 1500 + 0.01 * 300 * Eb + 0.02 * 12500 / 16 * P_rated) / 365
    wear = 300 / (5475 * 0.8) * np.sum(np.maximum(P_b, 0))
    cost = C_DE * fuel_L / 3.78541 + 0.24 * on.sum() + om_fix + 0.45 * starts + 0.23 * stops + wear
    E_gen = np.sum(P_DE * 0.9 + P_RES)
    Pb_ = base_rating; cost_base = C_DE * (24 * 0.08145 * Pb_ + 0.246 * load.sum()) / 3.78541 + 0.24 * 24 + 0.02 * 12500 / 16 * Pb_ / 365 + 0.45 + 0.23
    return dict(COE=cost / load.sum(), COE_n=cost / cost_base, cost=cost, Em_kg=K_EM * P_DE.sum(), Em_n=P_DE.sum() / load.sum(),
                DE_hours=int(on.sum()), E_DE=P_DE.sum(), fuel_L=fuel_L, Dump=P_dump.sum() / E_gen, REF=P_RES.sum() / E_gen,
                starts=starts, wear=wear)


if __name__ == '__main__':
    T = pd.read_csv(RES / 'rerun' / 'main_tables.csv').set_index('tag')
    X = {'i_16kW': (T.loc['S3', ['ns', 'nw', 'Eb']].to_numpy(float), 16), 'ii_8kW_16kWsizing': (T.loc['S3', ['ns', 'nw', 'Eb']].to_numpy(float), 8),
         'iii_8kW_8kWsizing': (T.loc['DG8kW', ['ns', 'nw', 'Eb']].to_numpy(float), 8), 'low_solar': (T.loc['DG8kW', ['ns', 'nw', 'Eb']].to_numpy(float), 8)}
    R = pd.read_csv(RES / 'dispatch' / 'dispatch_cases.csv').set_index('case')
    for c, (x, P) in X.items():
        d = pd.read_csv(RES / 'dispatch' / f'dispatch_{c}.csv')
        m = day_metrics(d.load, d.P_RES, d.P_DE, d.P_b, d.P_dump, x, P)
        print(f'{c:20s} COE py {m["COE"]:.5f} matlab {R.loc[c, "COE"]:.5f} | Em py {m["Em_kg"]:.3f} matlab {R.loc[c, "Em_kg"]:.3f} | DEh {m["DE_hours"]} {R.loc[c, "DE_hours"]} | dump {m["Dump"]:.4f} {R.loc[c, "Dump"]:.4f}')
