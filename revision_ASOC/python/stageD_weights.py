"""Stage D: Appendix C (weight sweeps) rewritten from sweeps.csv."""
from texedit import Ed
from common import RES
import pandas as pd
S = pd.read_csv(RES / 'rerun' / 'sweeps.csv'); W = S[S.tag.str.startswith('w')]
g = lambda k, v: W[(W.tag == f'w{k}') & ((W.value - v).abs() < 1e-6)].iloc[0]
eq = g(1, 0.2); l1 = g(1, 1.0); e9 = g(2, 0.9); e1 = g(2, 1.0); d1 = g(3, 1.0); u1 = g(4, 1.0); u8 = g(4, 0.8)
lcoe_min = W[W.tag == 'w1'].LCOE_abs.min()
def d(r): return f"[{r.ns:.0f}, {r.nw:.0f}, {r.Eb:.0f}]"
new = rf'''\section{{Effects of varying relative objective weights on the sizing results \label{{app:weights}}}}

The weighted-sum design depends on the weights. We varied each weight $w_k$ from 0 to 1 while the other four shared the remainder equally ($w_j = (1-w_k)/4$), re-optimizing the design at each value (best of three integer-coded PSO runs, 16~kW DE). \cref{{fig:vary_weights}} shows the normalized objectives and the resulting capacities; the equal-weight design ($w_k = 0.2$) is {d(eq)} with LCOE {eq.LCOE_abs:.3f}~USD/kWh.

Weighting cost more heavily moves the design little: for $w_1 \geq 0.3$ the optimum stays near {d(l1)}, with LCOE of {lcoe_min:.3f}~USD/kWh, close to the equal-weight value. Weighting emissions ($w_2$) or the renewable fraction ($w_5$) enlarges the PV array and battery and cuts DE operation, from {eq.DE_hours:.0f}~h per year at equal weights to {e9.DE_hours:.0f}~h at $w_2 = 0.9$, at an LCOE of {e9.LCOE_abs:.3f}~USD/kWh. At $w_2 = 1$ or $w_5 = 1$ the problem only rewards eliminating diesel, and the optimum moves to the upper bounds ({d(e1)}) at {e1.LCOE_abs:.3f}~USD/kWh. Weighting dumped energy ($w_4$) shrinks the renewable array and runs the DE more ({u8.DE_hours:.0f}~h per year at $w_4 = 0.8$); at $w_4 = 1$ the design degenerates to a nearly diesel-only system ({d(u1)}). The DPSP weight $w_3$ has no effect below 1 because DPSP is zero for every design with a 16~kW DE; at $w_3 = 1$ the objective is flat and the returned design ({d(d1)}) is arbitrary. These extremes show why single-objective weights are a poor basis for design and why \cref{{sec:pareto_select}} selects designs from the Pareto set instead.

\begin{{figure}}[htbp]
  \centering
  \includegraphics[width=\linewidth]{{rev_vary_weights.pdf}}
  \caption{{\label{{fig:vary_weights}} Effect of the objective weights. Top: normalized objectives; bottom: rated PV and WT capacity and battery capacity (in units of 10~kWh). In each column one weight varies from 0 to 1 and the others share the remainder equally.}}
\end{{figure}}

'''
e = Ed()
e.between(r'\section{Effects of varying relative objective weights on the sizing results \label{app:weights}}', r'\section{\label{app:improv} Model caveats, potential refinements and extensions}', new, keep_end=True)
e.save()
