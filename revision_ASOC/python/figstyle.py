"""Shared figure style for the ASOC revision (stage H, 30 Oct 2026).

One style for every figure in the paper: Times-like serif text that matches the elsarticle `times`
option, figures drawn at their printed width (no scaling in LaTeX), hairline axes, and fixed colors
per entity (PV, WT, DE, battery, load) so a color means the same thing in every figure.
Colors come from a categorical palette checked for colour-vision deficiency; where two colors in one
panel are close under CVD the marks also differ in shape (line vs bar, marker, dash).
"""
import os, pathlib, shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

REV = pathlib.Path(__file__).resolve().parents[1]
RES = REV / 'results'; FIG = REV / 'figures'; FIG.mkdir(exist_ok=True)
ROOT = REV.parent
MS_DIR = pathlib.Path.home() / 'mnt' / 'Microgrids_paper_v2'

# Printed sizes for elsarticle [final,3p,times]: \textwidth = 468 pt
FULL = 468 / 72.27          # 6.48 in
HALF = 0.49 * FULL

INK, INK2, MUTED, GRID = '#1b1b1a', '#52514e', '#8a8984', '#e4e3df'
# Categorical palette (fixed order)
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948']
PAL8 = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
# Entities: the same color in every figure
C = dict(load=INK, PV=YELLOW, WT=AQUA, DE=RED, BS=VIOLET, dump='#b9b8b3', lost=MAGENTA, base=INK2)
# Objectives (line charts; each line also has its own marker)
OBJ = dict(LCOE_n=(BLUE, 'o', '-'), Em_n=(ORANGE, 's', '-'), Dump=(AQUA, '^', '-'), DPSP=(MAGENTA, 'D', '-'),
           oneminusREF=(INK2, 'v', '--'), J=(INK, None, '-'))
OBJLAB = dict(LCOE_n='LCOE (norm.)', Em_n='Emissions (norm.)', Dump='Dump fraction', DPSP='DPSP',
              oneminusREF=r'$1-$REF', J='Weighted objective $J$')
# Sequential ramps (one hue, light to dark; the lightest step stays visible on white)
SEQ_BLUE = LinearSegmentedColormap.from_list('seqblue', ['#b7d3f6', '#86b6ef', '#5598e7', '#2a78d6', '#1c5cab', '#104281', '#0d366b'])
SEQ_RED = LinearSegmentedColormap.from_list('seqred', ['#fcf3f2', '#f6c9c7', '#ee9391', '#e34948', '#b52f2e', '#7a1f1e'])
SEQ_VIOLET = LinearSegmentedColormap.from_list('seqviolet', ['#f3f1fc', '#cfc9f3', '#a49ae6', '#7a6cdc', '#6250d6', '#3f2f9e', '#271c6b'])

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Liberation Serif', 'Times', 'STIXGeneral', 'DejaVu Serif'],
    'mathtext.fontset': 'stix',
    'font.size': 8, 'axes.labelsize': 8, 'axes.titlesize': 8, 'legend.fontsize': 7,
    'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5,
    'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'text.color': INK,
    'xtick.color': INK2, 'ytick.color': INK2, 'xtick.labelcolor': INK, 'ytick.labelcolor': INK,
    'axes.linewidth': 0.6, 'xtick.major.width': 0.6, 'ytick.major.width': 0.6,
    'xtick.major.size': 2.5, 'ytick.major.size': 2.5, 'xtick.minor.size': 1.5, 'ytick.minor.size': 1.5,
    'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.45, 'grid.linestyle': '-',
    'axes.axisbelow': True, 'axes.spines.top': False, 'axes.spines.right': False,
    'lines.linewidth': 1.2, 'lines.markersize': 3.5, 'patch.linewidth': 0.5,
    'legend.frameon': False, 'legend.handlelength': 1.8, 'legend.borderaxespad': 0.3,
    'legend.handletextpad': 0.5, 'legend.columnspacing': 1.2, 'legend.labelspacing': 0.3,
    'axes.titlelocation': 'left', 'axes.titlepad': 4,
    'figure.dpi': 150, 'savefig.dpi': 300, 'pdf.fonttype': 42, 'ps.fonttype': 42,
    'savefig.bbox': 'tight', 'savefig.pad_inches': 0.02,
})


def panel(ax, letter, title=None, x=-0.02, y=1.0):
    """Panel tag '(a)' (and an optional title) above the top-left corner of the axes."""
    t = f'({letter})' + (f' {title}' if title else '')
    ax.set_title(t, loc='left', fontsize=8, pad=4)


def hourly_axis(ax, label=True):
    ax.set_xlim(0, 24); ax.set_xticks(range(0, 25, 6))
    if label: ax.set_xlabel('Hour of day')


def save(fig, name, copy=True):
    fig.savefig(FIG / f'{name}.pdf')
    fig.savefig(FIG / f'{name}.png', dpi=220)
    if copy and not os.environ.get('FIG_NO_COPY'):
        try:
            shutil.copy(FIG / f'{name}.pdf', MS_DIR / f'{name}.pdf')
        except Exception as e:
            print('copy to manuscript folder failed:', e)
    plt.close(fig)
    print('saved', name)
