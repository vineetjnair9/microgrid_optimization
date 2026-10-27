import pathlib, numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
REV = pathlib.Path(__file__).resolve().parents[1]
RES = REV / 'results'; FIG = REV / 'figures'; FIG.mkdir(exist_ok=True)
MS_DIR = pathlib.Path.home() / 'mnt' / 'Microgrids_paper_v2'
PAL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948']
INK, INK2, GRID = '#0b0b0b', '#52514e', '#d9d8d4'
plt.rcParams.update({'font.size': 8, 'axes.labelsize': 8, 'axes.titlesize': 8, 'legend.fontsize': 7,
    'xtick.labelsize': 7, 'ytick.labelsize': 7, 'axes.edgecolor': INK2, 'axes.labelcolor': INK,
    'xtick.color': INK2, 'ytick.color': INK2, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.5,
    'axes.spines.top': False, 'axes.spines.right': False, 'lines.linewidth': 1.5, 'font.family': 'serif',
    'pdf.fonttype': 42, 'savefig.bbox': 'tight', 'savefig.dpi': 300})
OBJ5 = ['LCOE_n', 'Em_n', 'DPSP', 'Dump', 'oneminusREF']
def save(fig, name):
    fig.savefig(FIG / f'{name}.pdf'); fig.savefig(FIG / f'{name}.png', dpi=200)
    try:
        import shutil; shutil.copy(FIG / f'{name}.pdf', MS_DIR / f'{name}.pdf')
    except Exception as e:
        print('copy to manuscript folder failed:', e)
    plt.close(fig)
def keynum(path, d):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        for k, v in d.items(): f.write(f'{k} = {v}\n')
