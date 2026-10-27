"""Stage C3: battery model text matches the corrected code (efficiency on charge only, energy/headroom limits, power scaling)."""
from texedit import Ed
e = Ed()
e.rep(r"""\begin{equation}
    SOC(t+1) = (1-\delta) SOC(t) - \frac{1000 \cdot P_{BS} \; \Delta t \; \eta_{overall}}{E_C}
\end{equation}""", r"""\begin{equation}
    SOC(t+1) = (1-\delta) SOC(t) - \frac{1000 \cdot P_{BS} \; \Delta t \; \eta_{BS}(t)}{E_C}, \qquad \eta_{BS}(t) = \begin{cases} \eta_{overall} & P_{BS} < 0 \text{ (charging)} \\ 1 & P_{BS} \geq 0 \text{ (discharging)} \end{cases}
\end{equation}""")
e.rep(r"""an overall round-trip Coulombic efficiency $\eta_{overall}$ for the battery is used, which applies to both stages.""",
      r"""an overall round-trip Coulombic efficiency $\eta_{overall}$ for the battery is used and applied once, when charging. In each hour the controller limits charging to the headroom below $SOC_{max}$ and discharging to the energy above $SOC_{min}$, in addition to the power rating $P_{BS,\;r}$. The power rating scales with installed capacity, as for stacked modules: 3.68~kW per 13.5~kWh Powerwall module for Li-ion (0.273~kW per kWh) and a C-rate of 0.2 for lead-acid.""")
e.rep(r"""$P_{BS, \; r}$ [kW]                    & 3.68            & 0.42             \\""",
      r"""$P_{BS, \; r}$ [kW per kWh installed]  & 0.273           & 0.20             \\""")
e.rep(r"203 & 74,251 & 12.52 & 3.21 & 8.48 \\ \bottomrule", r"203 & 74,086 & 12.52 & 3.21 & 8.48 \\ \bottomrule")
e.rep(r"with a power rating equal to the peak load (12.52 kW).", r"with a power rating equal to the representative-day peak load (12.52 kW); the converter is costed at this rating, and its power limit is not enforced in the hourly simulation.")
e.save()
