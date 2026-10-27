"""T2.3: TAHMO vs NASA POWER (MERRA-2/CERES) for Timbila, 2018."""
from common import *
import scipy.io as sio, json
ROOT = REV.parent
w = sio.loadmat(ROOT / 'wind_speed.mat')['wind_speed'].ravel(); irr = sio.loadmat(ROOT / 'irradiance.mat')['irradiance'].ravel()
raw = w / 3.70
lines = (REV / 'data' / 'nasa_power_timbila_2018.csv').read_text().split('\n'); k = [i for i, l in enumerate(lines) if l.startswith('YEAR')][0]
P = pd.read_csv(REV / 'data' / 'nasa_power_timbila_2018.csv', skiprows=k)
lags = range(-3, 4); ci = [np.corrcoef(np.roll(irr, L), P.ALLSKY_SFC_SW_DWN)[0, 1] for L in lags]
lag = list(lags)[int(np.argmax(ci))]
r = np.roll(raw, lag); ri = np.roll(irr, lag)
df = pd.DataFrame({'mo': P.MO, 'day': np.repeat(np.arange(365), 24), 'hr': P.HR, 'tahmo_raw': r, 'tahmo_scaled': r * 3.70,
                   'ws2': P.WS2M, 'ws10': P.WS10M, 'ws50': P.WS50M, 'irr_t': ri * 1000, 'irr_p': P.ALLSKY_SFC_SW_DWN})
d = df.groupby('day').mean(numeric_only=True); m = df.groupby('mo').mean(numeric_only=True); dh = df.groupby('hr').mean(numeric_only=True)
beta = 1 / 7; alpha = np.log(df.ws50.mean() / df.ws10.mean()) / np.log(5)
res = dict(lag_h=lag, r_irr_hourly=np.corrcoef(df.irr_t, df.irr_p)[0, 1], irr_daily_tahmo=df.irr_t.sum() / 1e3 / 365, irr_daily_power=df.irr_p.sum() / 1e3 / 365,
    r_wind_hourly=np.corrcoef(df.tahmo_raw, df.ws2)[0, 1], r_wind_daily=np.corrcoef(d.tahmo_raw, d.ws2)[0, 1], r_wind_monthly=np.corrcoef(m.tahmo_raw, m.ws2)[0, 1],
    mean_tahmo_raw=df.tahmo_raw.mean(), mean_ws2=df.ws2.mean(), mean_ws10=df.ws10.mean(), mean_ws50=df.ws50.mean(), s_P=df.ws2.mean() / df.tahmo_raw.mean(),
    ratio_min=(m.ws2 / m.tahmo_raw).min(), ratio_max=(m.ws2 / m.tahmo_raw).max(),
    hub_model=(df.tahmo_scaled * 14.5 ** beta).mean(), hub_model_href2=(df.tahmo_scaled * (14.5 / 2) ** beta).mean(),
    hub_power_pl=(df.ws10 * (14.5 / 10) ** beta).mean(), hub_power_shear=(df.ws10 * (14.5 / 10) ** alpha).mean(), shear_alpha=alpha)
res['hub_ratio_power_to_model'] = res['hub_power_shear'] / res['hub_model']
out = RES / 'wind'; out.mkdir(exist_ok=True)
json.dump({k: float(v) for k, v in res.items()}, open(out / 'wind_validation.json', 'w'), indent=1)
pd.DataFrame({'month': m.index, 'tahmo_raw': m.tahmo_raw, 'ws2': m.ws2, 'ratio': m.ws2 / m.tahmo_raw}).to_csv(out / 'monthly_ratios.csv', index=False)
with open(out / 'monthly_ratios.tex', 'w') as f:
    f.write('\\begin{tabular}{l' + 'r' * 12 + '}\n\\toprule\nMonth & ' + ' & '.join(['J','F','M','A','M','J','J','A','S','O','N','D']) + '\\\\\n\\midrule\n')
    f.write('TAHMO raw [m/s] & ' + ' & '.join(f'{v:.2f}' for v in m.tahmo_raw) + '\\\\\n')
    f.write('POWER 2 m [m/s] & ' + ' & '.join(f'{v:.2f}' for v in m.ws2) + '\\\\\n')
    f.write('Ratio & ' + ' & '.join(f'{v:.2f}' for v in m.ws2 / m.tahmo_raw) + '\\\\\n\\bottomrule\n\\end{tabular}\n')
keynum(out / 'key_numbers.txt', {k: round(float(v), 3) for k, v in res.items()})
for k_, v in res.items(): print(k_, round(float(v), 3))
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5))
mo = np.arange(1, 13)
ax[0].plot(mo, m.tahmo_scaled, marker='o', ms=3, color=PAL[0], label='TAHMO $\\times$3.70 (model input)')
ax[0].plot(mo, m.tahmo_raw, marker='o', ms=3, color=PAL[0], ls=':', label='TAHMO raw')
ax[0].plot(mo, m.ws2, marker='s', ms=3, color=PAL[1], label='POWER 2 m')
ax[0].plot(mo, m.ws10, marker='^', ms=3, color=PAL[2], label='POWER 10 m')
ax[0].set_xticks(mo); ax[0].set_xlabel('Month (2018)'); ax[0].set_ylabel('Mean wind speed [m/s]'); ax[0].set_ylim(0, None)
ax[0].legend(frameon=False, fontsize=6); ax[0].set_title('(a) Monthly means', loc='left')
h = np.arange(24)
ax[1].plot(h, dh.tahmo_scaled, color=PAL[0], label='TAHMO $\\times$3.70'); ax[1].plot(h, dh.ws2, color=PAL[1], label='POWER 2 m'); ax[1].plot(h, dh.ws10, color=PAL[2], label='POWER 10 m')
ax[1].set_xlabel('Hour of day (aligned)'); ax[1].set_ylabel('Mean wind speed [m/s]'); ax[1].set_ylim(0, None); ax[1].set_xticks(range(0, 24, 4))
ax[1].legend(frameon=False, fontsize=6); ax[1].set_title('(b) Diurnal profiles', loc='left')
fig.tight_layout(); save(fig, 'rev_wind_validation')
