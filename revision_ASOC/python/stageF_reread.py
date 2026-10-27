"""Stage F2: fixes from the full re-read of Secs 1-4 and Appendices A-G (21 Oct 2026)."""
from texedit import Ed
e = Ed()
R = e.rep
# Sec 2: cross-references point straight at the appendices
R(r"individual cost terms will be provided in \cref{chap:methods}", r"individual cost terms is given in \cref{app:costs}")
R(r"a detailed overview of the main tools is provided in \cref{app:design_tools}", r"a detailed overview of the main tools is provided in \cref{app:tools}.")
R(r"As described in more detail in \cref{sec:control_survey},", r"As described in more detail in \cref{app:control},")
# Sec 2.3: solver remarks consistent with the benchmark
R(r"which is more robust to non-smoothness but considerably slower due to fine mesh resolution requirements.",
  r"which is more robust to non-smoothness but can need many evaluations when the mesh must be refined; on our problem it reached the target in every run but used nearly the full evaluation budget (\cref{tab:bench_stats}).")
R(r"In practice, however, it is slow because a large number of evaluations are needed to build an accurate surrogate, and it lacks",
  r"In practice, however, refitting the surrogate adds a large overhead per evaluation, which dominates the run time when the true objective is cheap, as here (\cref{tab:bench_stats}), and it lacks")
# Sec 4: objective list
R(r"(iv) Dumped or Relative excess or power generated (REPG)", r"(iv) Relative excess or dump power generated (REPG)")
# Sec 4.2 and App B: normalized LCOE and emissions can exceed 1
R(r"Thus, the value of both the sizing and dispatch objective functions always lie between 0 and 1.",
  r"Because each objective is normalized (\cref{app:costs}), the objective values are dimensionless: DPSP, dump and $1-REF$ lie between 0 and 1, while normalized LCOE and emissions exceed 1 only for a design that costs more or emits more than the diesel-only baseline.")
R(r"In order to normalize both $LCOE$ and emissions so that they always lie between 0 and 1 (like the other three objectives),",
  r"In order to put $LCOE$ and emissions on a scale comparable to the other three objectives, which lie between 0 and 1,")
# App A.1.3: figures use station time stamps
R(r"Daily averaged profiles are shown in \cref{fig:chap3_daily}.",
  r"Daily averaged profiles are shown in \cref{fig:chap3_daily}. Both figures use the station time stamps, before the 2-h alignment described above.")
# App A.3: DG rating
R(r"The sizing of the diesel generator or micro turbine was not considered as a variable in the optimization problem. Instead, the rated power of the DG",
  r"In the sizing problem the rating of the diesel generator or micro turbine is fixed rather than optimized; \cref{sec:pareto_rel} treats the DE rating as a decision variable. The rated power of the DG")
# App A.3.1: grammar and units
R(r"based on compression ignition that diesel as their fuel", r"based on compression ignition that use diesel as their fuel")
R(r"where $P(t)_{DE,\;gen}$ [in $L/h$] is power output level needed by the load \cite{kaabeche2014}",
  r"where $Fuel_{DE}(t)$ is in $L/h$, $P(t)_{DE,\;gen}$ [$kW$] is the power output needed by the load and $P(t)_{DE,\;r}$ [$kW$] is the rated power \cite{kaabeche2014}")
# App A.4: battery
R(r"while the much higher peak power allows for faster discharge to meet more of the demand.",
  r"while its higher power rating per kWh of capacity (\cref{tab:bs_params}) allows faster discharge to meet more of the demand.")
R(r"Here, $n_{cycles}$ is the cumulative number of charge-discharge cycles so far, a variable that is updated at each iteration in the dispatch algorithm.",
  r"Here, $n_{cycles}$ is the cumulative number of equivalent full cycles so far, computed as the energy discharged divided by the usable capacity $(SOC_{max}-SOC_{min})\,E_{b,\;init}$ and updated at every time step of the simulation.")
# App B.2: battery wear in dispatch
R(r"OM_{var, \; DG,\; daily} & = \Sigma_{t=1}^{t=24} \; DG_{ON}(t) \cdot OM_{var, \; DG}, \; C_{fuel,\; DG,\; daily} = \Sigma_{t=1}^{t=24} \; C_{fuel,\; DG}(t). " + "\n" + r"\end{align*}",
  r"OM_{var, \; DG,\; daily} & = \Sigma_{t=1}^{t=24} \; DG_{ON}(t) \cdot OM_{var, \; DG}, \; C_{fuel,\; DG,\; daily} = \Sigma_{t=1}^{t=24} \; C_{fuel,\; DG}(t). " + "\n" + r"\end{align*}" + "\n" + r"In the dispatch optimization of \cref{sec:dispatch_opt}, a battery wear cost of 0.068~USD per kWh discharged is added to $C_{daily}$.")
# App E.2: PSO update equations and description
R(r"x_{i,d}^{k+1} & = x_{i,d}^{k} + v_{i,d}^{k} \\" + "\n" + r"        v_{i,d}^{k} & = \omega \cdot v_{i,d}^{k}",
  r"v_{i,d}^{k+1} & = \omega \cdot v_{i,d}^{k}")
R(r"c_2 \cdot rand_2^k \cdot (gbest_{i,d}^k - x_{i,d}^k)" + "\n" + r"    \end{align}",
  r"c_2 \cdot rand_2^k \cdot (gbest_{i,d}^k - x_{i,d}^k) \\" + "\n" + r"        x_{i,d}^{k+1} & = x_{i,d}^{k} + v_{i,d}^{k+1}" + "\n" + r"    \end{align}")
R(r"The velocity is calculated as a random weighted integer as in \cref{eq:pso} where $v_{i,d}^k$ is the speed",
  r"The velocity is updated as a randomly weighted sum of three terms (inertia, attraction to $pbest$ and attraction to $gbest$), as in \cref{eq:pso}, where $v_{i,d}^k$ is the velocity")
R(r" Additionally, GA is more efficient in cases where there are more than three components to the solution.", "")
# App E.3: surrogate speed claim
R(r"Such an approach can greatly speed up computational times for complex component sizing and economic dispatch problems with non-linear cost functions and a large number of variables and constraints.",
  r"Such an approach can greatly speed up computational times for complex component sizing and economic dispatch problems when each evaluation is expensive; when evaluations are cheap, as in our 8,760-hour simulation, the cost of fitting the surrogate dominates (\cref{tab:bench_stats}).")
# App F
R(r"due to their ability to better predict future system behavior, and compute control signals",
  r"due to their ability to use measurements of the actual system state to compute control signals")
R(r"In practice, this translates to maintaining grid frequency around a certain target value and stabilizing supply frequency by regulating real and reactive power flows in real-time, respectively.",
  r"In practice, it restores frequency and voltage to their nominal values after the deviations left by primary control, by adjusting real and reactive power set-points in real time.")
R(r"Decentralized systems can also be more stable than centralized alternatives having similar configurations, if some nodes",
  r"Decentralized systems can also be more robust than centralized alternatives with similar configurations: if some nodes")
R(r"The 1st condition ensures", r"The first condition ensures")
R(r"The 2nd, plug-and-play characteristic", r"The second, plug-and-play, characteristic")
R(r"is by far the most common method used in the literature for optimal microgrid operation",
  r"is one of the most widely used methods in the literature for optimal microgrid operation")
# App G
R(r"Based on literature surveyed, this is the most widely used commercial tool for microgrid design optimization in both academia and industry today. It is currently the global standard for optimizing microgrid design in all sectors, from village power and island utilities to grid-connected campuses and military bases.",
  r"In the literature we surveyed, it is the most widely used commercial tool for microgrid design optimization in both academia and industry, with applications ranging from village power and island utilities to grid-connected campuses and military bases.")
R(r"The full software is not publicly available and the accessible, rudimentary version is not very comprehensive since it offers only a small subset of free features.",
  r"REopt is free to use through a web tool for single-site analysis and an API for multisite analysis, and its code is open source~\cite{reopt_news}.")
R(r"From the sample results obtained by NREL comparing LCOE for multiple system configurations, it can be concluded that diesel-only systems are the cheapest option but may not meet other design objectives. Although the PV+battery system is more expensive, the inclusion of a diesel backup makes the combined system even cheaper than the diesel-only option.",
  r"In NREL's sample results comparing the LCOE of several system configurations, a PV+battery system is more expensive than a diesel-only system, but adding a diesel backup to it gives the lowest LCOE of the three.")
R(r"However, supporting NREL datasets obtained from REopt cost models", r"Supporting NREL datasets obtained from REopt cost models")
new = r"""\bibitem{reopt_news}
National Renewable Energy Laboratory (2022). REopt is not Lite anymore. \url{https://www.nrel.gov/news/program/2022/reopt-is-not-lite-anymore}. Accessed 21 October 2026.

"""
R(r"\end{thebibliography}", new + r"\end{thebibliography}")
e.save()
