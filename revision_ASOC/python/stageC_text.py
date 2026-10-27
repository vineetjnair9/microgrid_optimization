"""Stage C: text-only edits (no result numbers). A2 Pareto wording, Discussion and limitations, future work, data availability.
Re-runnable on AAMain_backup_before_stageB.tex + stage B."""
from texedit import Ed
e = Ed()
# --- A2: Sec 5.3 opening
e.between(r"Although a global optimum does exist in the sense that there is a single lowest possible value",
          r"The colors simply indicate the value of the z-axis variable i.e., the BS capacity. ",
          r"""The weighted-sum problem in Eq.~(\ref{eq:sizing}) has a single minimum value, but the five-objective problem behind it has no single optimum: along the Pareto front, any improvement in one objective worsens at least one other. The Pareto set contains the designs that no other design matches or beats in every objective while beating them in at least one. We approximate this set with the genetic (\texttt{gamultiobj}) and pattern-search (\texttt{paretosearch}) multiobjective solvers in MATLAB's Global Optimization Toolbox. \Cref{fig:pareto_inputs} shows how the three decision variables vary across the non-dominated set found by \texttt{gamultiobj}: black dots are the non-dominated designs returned by the solver, the surface interpolates between them, and the colour shows battery capacity. These points are mutually non-dominated: they represent different trade-offs, not equally good designs, and choosing among them requires stated preferences or a selection rule (\cref{sec:pareto_select}). """)
e.rep("Although all these combinations of input variables are equally optimal in the Pareto sense, a designer would still prefer",
      "Although none of these combinations dominates another, a designer may still prefer")
# --- Discussion and limitations (before Conclusions); transferability paragraph moved and corrected
i = e.s.find("Some findings in this study are specific to the Timbila, Kenya case study")
j = e.s.find("\n", i)
assert i > 0 and e.s.count("Some findings in this study are specific to the Timbila, Kenya case study") == 1
e.s = e.s[:i] + e.s[j+1:]
disc = r"""\section{Discussion and limitations\label{sec:discussion}}

\subsection{Site-specific and transferable findings}
Some findings are specific to the Timbila, Kenya case study and reflect the region's conditions. The PV--WT balance of the optimal mix follows from the local resource: 2018 irradiation at the site averaged 4.4~kWh/m$^2$/day in the station record (5.3~kWh/m$^2$/day in NASA POWER), while the wind resource is moderate and uncertain (\cref{app:climate}). In windier locations, such as coastal East Africa or the Sahel, or where the wind blows more at night, the balance would shift toward wind; \cref{sec:wind_role} gives the wind resource and turbine cost at which turbines enter the mix. The strong sensitivity of cost to diesel price reflects the elevated and volatile fuel costs of remote sub-Saharan sites; where fuel is cheaper or more stable, the economic case for high renewable penetration weakens.

Other findings depend on the structure of the problem rather than on the site. The design workflow (equal-budget multi-run benchmarking, Pareto search, rule-based selection from the front and Monte Carlo re-ranking) applies to any simulation-based sizing problem once the weather, load and cost inputs are replaced. The solver ranking in \cref{sec:results} is an empirical result for this problem class at a budget of 2,000 evaluations; other formulations or budgets may rank solvers differently, which is why we report the full protocol. The trade-off between generator rating and renewable and storage capacity, and the cost of tighter reliability targets traced by the $\varepsilon$-constraint front, hold for any islanded system that relies on a dispatchable backup unit. Practitioners at other off-grid sites can reuse the workflow and these relationships after recalibrating irradiance, wind, load, fuel price and financing inputs.

\subsection{Limitations\label{sec:limitations}}
Five modeling choices limit these conclusions. First, Stage~2 schedules the generator and battery with exact knowledge of the next 24 hours of load and weather. The dispatch costs, emissions and DPSP in \cref{sec:dispatch_opt} are therefore optimistic relative to a controller that acts on forecasts. Stage~1 does not share this bias, because its rule-based controller uses only current-hour information. Second, sizing and dispatch are decoupled (\cref{sec:opt_prob}): a design ranked best under rule-based operation may rank differently under optimized dispatch, although its Stage-1 cost bounds its cost under any better operating policy. Third, sizing uses one meteorological year (2018) and one load profile. The Monte Carlo analysis perturbs both, but it cannot represent multi-year wind droughts or long-term load growth. Fourth, the wind resource rests on station data scaled by a single factor (\cref{app:climate}); \cref{sec:sizing_sensitivity} shows how the design responds when that factor changes by $\pm$25\%, and on-site hub-height measurements would be needed before construction. Fifth, all solvers run with default settings; tuned settings could change the margins between them, although the equal evaluation budget removes the effect of differing stopping rules.

"""
e.rep(r"\section{Conclusions}", disc + r"\section{Conclusions}")
# --- Future work: add integrated / stochastic operation first
e.rep(r"""\subsection{Future work \label{sec:future}}

There are several model refinements""", r"""\subsection{Future work \label{sec:future}}

The limitations in \cref{sec:limitations} point to three extensions: integrated or bilevel sizing and dispatch, in which the design is scored under optimized operation; receding-horizon or stochastic dispatch that acts on forecasts rather than perfect foresight; and multi-year resource records with on-site wind measurements. There are several further model refinements""")
# --- Data and code availability
e.rep(r"All the original code and data used for this study can be found in this public GitHub repository: \url{https://github.com/vineetjnair9/microgrid_optimization}.",
      r"All code and data used for this study are in the public GitHub repository \url{https://github.com/vineetjnair9/microgrid_optimization}. Release \texttt{v2.0-asoc} (branch \texttt{asoc-revision}, folder \texttt{revision\_ASOC}) contains the corrected simulation model, the benchmark, Pareto, sensitivity, Monte Carlo and dispatch scripts, the random seeds and all result files used in this revision.")
e.save()
