"""T2.1: representative designs from the corrected Pareto approximations."""
from common import *
def nondominated(F):
    keep = np.ones(len(F), bool)
    for i in range(len(F)):
        if keep[i]:
            dom = np.all(F <= F[i], 1) & np.any(F < F[i], 1)
            if dom.any(): keep[i] = False
    return keep
def topsis(F, w):
    R = F / np.sqrt((F**2).sum(0)); V = R * w
    b, wst = V.min(0), V.max(0)
    db = np.sqrt(((V - b)**2).sum(1)); dw = np.sqrt(((V - wst)**2).sum(1))
    return dw / (db + dw)
def knee(Z):
    m = Z.shape[1]; E = np.array([Z[np.argmin(Z[:, j])] for j in range(m)])
    n, *_ = np.linalg.lstsq(E, np.ones(m), rcond=None)    # hyperplane n.z = 1 through the extremes
    return int(np.argmax((1 - Z @ n) / np.linalg.norm(n)))
def select(X, F, names, weights):
    idx0 = np.arange(len(F)); nd = nondominated(F); X, F, idx0 = X[nd], F[nd], idx0[nd]
    _, uix = np.unique(np.round(F, 8), axis=0, return_index=True); uix = np.sort(uix); X, F, idx0 = X[uix], F[uix], idx0[uix]
    select.idx0 = idx0
    rng_ = F.max(0) - F.min(0); act = rng_ > 1e-9
    Z = (F[:, act] - F[:, act].min(0)) / rng_[act]
    reps = {}
    for j, nm in enumerate(names):
        if act[j]: reps[f'min_{nm}'] = int(np.argmin(F[:, j]))
    reps['knee'] = knee(Z); reps['compromise_L2'] = int(np.argmin(np.linalg.norm(Z, axis=1)))
    for wn, w in weights.items():
        ww = np.array([w[n] for n, a in zip(names, act) if a]); ww = ww / ww.sum()
        reps[f'TOPSIS_{wn}'] = int(np.argmax(topsis(F[:, act], ww)))
    return X, F, act, reps
out = RES / 'pareto'; out.mkdir(exist_ok=True)
# 16 kW, 5 objectives (DPSP constant 0 -> dropped automatically)
A = np.loadtxt(RES / 'rerun' / 'pareto_16kW_5obj.csv', delimiter=',')
X16, F16 = A[:, :3], A[:, 3:8]
eq = {n: 1 for n in OBJ5}; cost = dict(eq, LCOE_n=4); sus = dict(eq, Em_n=2.5, oneminusREF=2.5)
X16, F16, act16, rep16 = select(X16, F16, OBJ5, {'equal': eq, 'cost': cost, 'sustain': sus}); orig16 = select.idx0
# weighted-sum optimum (main_tables S3) vs the front
T = pd.read_csv(RES / 'rerun' / 'main_tables.csv'); s3 = T[T.tag == 'S3'].iloc[0]
fs = s3[OBJ5].to_numpy(float)
dom = int((np.all(F16 <= fs, 1) & np.any(F16 < fs, 1)).sum())
ws_front = F16.mean(1).min(); ws_s3 = fs.mean()
rows = []
for lab, i in rep16.items():
    rows.append(dict(front='16kW', label=lab, orig_row=int(orig16[i]) + 1, ns=X16[i, 0], nw=X16[i, 1], Eb=X16[i, 2], **{n: F16[i, k] for k, n in enumerate(OBJ5)}))
# 7 kW, 4 objectives, variables in kW
B = np.loadtxt(RES / 'rerun' / 'pareto_7kW_4obj.csv', delimiter=',')
X7, F7 = B[:, :3], B[:, 3:7]; n4 = OBJ5[:4]
eq4 = {n: 1 for n in n4}; cost4 = dict(eq4, LCOE_n=3); rel4 = dict(eq4, DPSP=3)
X7, F7, act7, rep7 = select(X7, F7, n4, {'equal': eq4, 'cost': cost4, 'reliability': rel4})
for lab, i in rep7.items():
    rows.append(dict(front='7kW', label=lab, ns=X7[i, 0] / 0.255, nw=X7[i, 1] / 3.5, Eb=X7[i, 2], **{n: F7[i, k] for k, n in enumerate(n4)}))
R = pd.DataFrame(rows); R['ns_int'] = R.ns.round().astype(int); R['nw_int'] = R.nw.round().astype(int)
R['PDE'] = np.where(R.front == '16kW', 16, 7)
R.to_csv(out / 'representatives_continuous.csv', index=False)
R[['front', 'label', 'ns_int', 'nw_int', 'Eb', 'PDE']].to_csv(out / 'representatives_to_evaluate.csv', index=False)
keynum(out / 'key_numbers.txt', {'N_FRONT_16': len(F16), 'N_FRONT_7': len(F7), 'WS_DOMINATED_BY': dom,
      'WS_SCORE': round(ws_s3, 4), 'FRONT_BEST_WS': round(ws_front, 4)})
print(R.round(4).to_string()); print('dominated by', dom, 'ws', ws_s3, 'front best', ws_front)
# figure: two panels
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.9))
sc = ax[0].scatter(F16[:, 0], F16[:, 1], c=F16[:, 3], cmap='Blues', s=10, edgecolors='none', vmin=0)
fig.colorbar(sc, ax=ax[0], label='Dump fraction', shrink=0.85)
mk = {'knee': ('D', PAL[1]), 'compromise_L2': ('s', PAL[2]), 'TOPSIS_equal': ('^', PAL[6]), 'TOPSIS_cost': ('v', PAL[3]), 'TOPSIS_sustain': ('P', PAL[5])}
for lab, (m, c) in mk.items():
    i = rep16[lab]; ax[0].scatter(F16[i, 0], F16[i, 1], marker=m, s=42, color=c, edgecolors='white', linewidths=0.8, label=lab.replace('_', ' '), zorder=3)
ax[0].scatter(fs[0], fs[1], marker='*', s=90, color=PAL[7], edgecolors='white', linewidths=0.8, label='weighted-sum PSO', zorder=4)
ax[0].set_xlabel('Normalized LCOE'); ax[0].set_ylabel('Normalized emissions'); ax[0].set_title('(a) 16 kW DE, five objectives', loc='left')
ax[0].legend(frameon=False, loc='upper right')
sc = ax[1].scatter(F7[:, 0], F7[:, 2], c=F7[:, 1], cmap='Blues', s=10, edgecolors='none', vmin=0)
fig.colorbar(sc, ax=ax[1], label='Normalized emissions', shrink=0.85)
mk7 = {'knee': ('D', PAL[1]), 'compromise_L2': ('s', PAL[2]), 'TOPSIS_equal': ('^', PAL[6]), 'TOPSIS_cost': ('v', PAL[3]), 'TOPSIS_reliability': ('P', PAL[5])}
for lab, (m, c) in mk7.items():
    i = rep7[lab]; ax[1].scatter(F7[i, 0], F7[i, 2], marker=m, s=42, color=c, edgecolors='white', linewidths=0.8, label=lab.replace('_', ' '), zorder=3)
ax[1].set_xlabel('Normalized LCOE'); ax[1].set_ylabel('DPSP'); ax[1].set_title('(b) 7 kW DE, four objectives', loc='left')
ax[1].legend(frameon=False, loc='upper left')
fig.tight_layout(); save(fig, 'rev_pareto_representatives')
