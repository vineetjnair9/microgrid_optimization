from texedit import Ed
e = Ed()
# --- A6 representative day
e.rep(r'(selected as the day of peak load in the annual profile)',
      r'(1 January 2018, whose daily irradiation is 136\% and mean wind speed 88\% of the annual daily means; the same load, irradiance and wind data are used throughout \cref{sec:dispatch_opt})')
# --- two-stage paragraph
e.between(r'\textbf{Two-stage sequential framework.}', r'is discussed in \cref{sec:dispatch_opt}.',
r'''\textbf{Two-stage sequential framework.} The overall optimization is solved in two stages (\cref{fig:workflow}). In Stage~1 (sizing), an annual hourly simulation with a rule-based dispatch inner loop is embedded in an outer global optimization loop that chooses the PV, WT and battery capacities. In Stage~2 (dispatch), the sized system is taken as given and a multi-objective economic-environmental dispatch problem is solved for a representative day. The Stage-1 controller is non-anticipative: it uses only the current hour's load, renewable output and state of charge, and it follows the load-following logic of most deployed off-grid controllers and of HOMER Pro's default strategy. Each candidate design is therefore scored under an operating policy that an operator can implement without forecasts. Embedding a 24-hour dispatch optimization inside every sizing evaluation would multiply the cost of each of the thousands of evaluations per run by 365 daily solves. The decoupling has a price: the design ranked best under rule-based operation need not be best under optimized dispatch. \cref{sec:limitations} discusses this limitation, and \cref{sec:dispatch_opt} reports how optimized dispatch changes daily cost and emissions for the selected design.''')
# --- runtime claim in Stage 1 description
e.rep(r'This design choice enables the 8760-hour sizing problem to converge in under 90 seconds on a standard laptop (see \cref{sec:results}).',
      r'One evaluation of the 8,760-hour simulation takes about 2\,ms on a current laptop, so a sizing run of 2,000 evaluations completes in seconds (\cref{sec:results}).')
# --- equation labels
e.resub(r'\\begin\{equation\}(\s*\n\s*)\\min_\{n_s, \\; n_w, \\; E_\{b,\\;init\}\}', r'\\begin{equation}\1\\label{eq:sizing}\1\\min_{n_s, \\; n_w, \\; E_{b,\\;init}}')
e.resub(r'\\begin\{equation\}(\s*\n\s*)\\min_\{P_\{DG\}, \\; P_\{BS\}\}', r'\\begin{equation}\1\\label{eq:dispatch}\1\\min_{P_{DG}, \\; P_{BS}}')
# --- weighted-sum clarification + reliability
e.rep(r'Thus, these are already enforced implicitly. Similarly, the optimization problem for day-ahead dispatch can be written as:',
r'''Thus, these are already enforced implicitly.

Eq.~(\ref{eq:sizing}) is a weighted-sum scalarization of the five objectives. For strictly positive weights its minimizer is Pareto-optimal, but the method can only reach supported Pareto points, those on the convex hull of the Pareto front. We therefore use it as an a-priori method for a decision-maker with stated preferences (equal weights by default; \cref{app:weights} varies them) and complement it with the a-posteriori Pareto analysis of \cref{sec:pareto_opt,sec:pareto_select}. Reliability enters through the DPSP objective. With the default 16~kW DG the rule-based controller meets all load, so DPSP is zero for every candidate design; \cref{sec:pareto_rel} therefore also treats the DG rating as a decision variable to expose the cost--reliability trade-off.

Similarly, the optimization problem for day-ahead dispatch can be written as:''')
# --- integer handling (Sec. 4.3)
e.rep(r'The decision variables $n_s$ and $n_w$ in the sizing problem are restricted to being integers, and such mixed integer programs (MIP) have been demonstrated to be NP-hard \cite{parisio2013}.',
r'''The numbers of PV modules $n_s$ and wind turbines $n_w$ are integers. Our sizing runs search an integer-coded space: the solvers move in the continuous box, the objective rounds $n_s$ and $n_w$ to the nearest integers before simulating, so every evaluated design can be built, and a final one-dimensional search re-optimizes $E_{b,\;init}$ for the rounded design. \cref{sec:results} also reports the alternative relax-and-round strategy, in which the solvers optimize the continuous relaxation and only the returned point is rounded. Mixed-integer formulations of such problems are NP-hard \cite{parisio2013}.''')
# --- control/tools surveys -> appendix pointers
e.between(r'\subsection{Survey of microgrid control strategies \label{sec:control_survey}}', r'\subsection{Novelties in current study and contributions}',
r'''\subsection{Control strategies and design tools \label{sec:control_survey}\label{app:design_tools}}
Real-time microgrid control (hierarchical primary, secondary and tertiary levels; centralized, decentralized and distributed architectures; model predictive control) lies outside the scope of this paper and is surveyed in \cref{app:control}. Widely used design tools (HOMER Pro, DER-CAM, REopt and the Microgrid Design Toolkit) are compared in \cref{app:tools}.

''', keep_end=True)
# --- recent literature paragraph (Sec. 2.3)
e.rep(r'which is more robust to non-smoothness but considerably slower due to fine mesh resolution requirements.',
r'''which is more robust to non-smoothness but considerably slower due to fine mesh resolution requirements.

Recent work extends these methods in three directions relevant here. Improved multiobjective variants of evolutionary and swarm algorithms return Pareto sets rather than single designs, for example an improved NSGA-II for the dispatch of hybrid ship power systems \cite{wang2024nsga} and an improved multiobjective grey wolf optimizer for sizing an island microgrid \cite{zhu2020imogwo}; grey wolf optimization has also been compared with PSO for wind--solar sizing \cite{geleta2022gwo}, and hybrids of PSO with other heuristics aim to balance exploration and exploitation \cite{javidrad2017psosa}. Several studies pair multiobjective search with multi-criteria decision making to choose one design from the Pareto set, such as multiobjective differential evolution followed by AHP--TOPSIS for stand-alone PV sizing \cite{muhsen2019mode} and weighted-sum Pareto sets ranked with ELECTRE for microgrid scheduling \cite{karimi2019madm}. Resource and load uncertainty is also increasingly propagated into the design stage, through Markov chain Monte Carlo scenario generation for stand-alone microgrid planning \cite{bakhtiari2021mcmc} or two-stage stochastic programming for off-grid hybrid systems \cite{calabrese2026tssp}. For stochastic solvers, the computational-intelligence literature recommends comparing result distributions over repeated independent runs with non-parametric tests rather than single runs \cite{derrac2011tutorial,carrasco2020trends}; we follow that practice in \cref{sec:results}.''')
# --- gaps + SSA conditions + contributions
e.between(r'Although a great deal of work has been conducted in microgrid optimization and control, three important gaps persist', r'directly motivate the break-even distance analysis presented in \cref{sec:results}. These factors are not incidental --- they motivate specific modeling choices throughout the paper.',
r'''Three gaps motivate this work. First, most multi-objective microgrid studies treat grid-connected systems that island only under faults; permanently isolated systems, which must meet all load from local resources, receive less attention. Second, comparisons of stochastic solvers for microgrid sizing often rest on one run per solver, so differences between solvers cannot be separated from run-to-run variation. Third, studies that compute Pareto sets often stop short of a rule for choosing one design from them, and robustness is commonly checked with a few deterministic scenarios rather than by propagating resource and load uncertainty.

Sub-Saharan African conditions shape the parameter ranges and the design questions in this study. Diesel prices in remote areas are high and volatile (our default of 3.20 USD per US gallon, about 0.85 USD/L, is conservative for remote sites, and \cref{sec:sizing_sensitivity} spans 0.2--12 USD/gal); nominal interest and inflation rates are high (9\% and 5.7\% for Kenya in the base case), which penalizes capital-intensive storage; measured climate data are scarce, so we draw on the TAHMO station network and check it against reanalysis (\cref{app:climate}); and grid extension is expensive, which motivates the break-even distance analysis in \cref{sec:results}.''')
e.between(r'The contributions of the present work are as follows.', r'and the breadth of objectives and analyses included.',
r'''This paper makes four contributions. (i) We formulate the sizing of an islanded PV--wind--battery--diesel microgrid as a simulation-based, non-smooth optimization problem in which an 8,760-hour rule-based operating simulation scores each candidate on five normalized objectives, and we state how integrality, normalization and reliability enter the formulation. (ii) We benchmark seven global metaheuristic and direct-search solvers and a PSO--pattern-search hybrid on this problem at an equal budget of 2,000 evaluations over 30 independent runs each, using success rates against the integer optimum found by exhaustive enumeration, expected running time and non-parametric tests. (iii) We pair a-priori weighted-sum sizing with a-posteriori Pareto search, select designs from the Pareto set with knee-point, compromise and TOPSIS rules, and re-rank the candidates by expected cost, conditional value-at-risk of cost and loss-of-load probability over 500 Monte Carlo resource and load scenarios. (iv) We apply this workflow to an off-grid community in Timbila, Kenya, with fuel price, interest, inflation and storage cost ranges drawn from sub-Saharan African conditions, and identify which design rules carry over to other sites once local inputs are recalibrated. \cref{tab:litcomp} places the work relative to representative prior studies.''')
# --- Table 1
e.between(r'\begin{table}[htbp]' + '\n' + r'\centering' + '\n' + r'\small' + '\n' + r'\caption{\label{tab:litcomp}', r'\end{table}',
r'''\begin{table}[htbp]
\centering
\footnotesize
\setlength{\tabcolsep}{3pt}
\caption{\label{tab:litcomp} Comparison of representative prior works on multi-objective hybrid microgrid optimization. \textbf{Obj}: objectives (C = cost, E = emissions, R = reliability, D = dump/curtailment; multi = several, not detailed in the abstract). \textbf{Isl.}: islanded/off-grid. \textbf{Size}/\textbf{Disp.}: sizing/dispatch performed. \textbf{R/S}: robustness or sensitivity analysis. \textbf{Sel.}: explicit rule for selecting a design from a Pareto set. \textbf{UQ}: probabilistic uncertainty propagation. \textbf{Stats}: repeated-run statistical comparison of solvers. \textbf{SSA}: sub-Saharan Africa case.}
\begin{tabular}{p{2.7cm} p{1.1cm} p{2.6cm} cccccccc}
\toprule
\textbf{Study} & \textbf{Obj.} & \textbf{Method} & \textbf{Isl.} & \textbf{Size} & \textbf{Disp.} & \textbf{R/S} & \textbf{Sel.} & \textbf{UQ} & \textbf{Stats} & \textbf{SSA} \\
\midrule
Kaabeche et al.~\cite{kaabeche2014} & C, E & Iterative & \checkmark & \checkmark & & & & & & \\
Bhandari et al.~\cite{bhandari2014} & C & HOMER & & \checkmark & & & & & & \\
Tazvinga et al.~\cite{tazvinga2013} & C, E & GA & \checkmark & \checkmark & \checkmark & & & & & \checkmark \\
Logenthiran et al.~\cite{logenthiran2010} & C & GA & \checkmark & \checkmark & \checkmark & & & & & \\
Moshi et al.~\cite{moshi2016} & C & GA & \checkmark & \checkmark & \checkmark & & & & & \checkmark \\
Zachar \& Daoutidis~\cite{zachar2016} & C & MPC & & & \checkmark & \checkmark & & & & \\
Parisio et al.~\cite{parisio2014} & C & MILP & \checkmark & & \checkmark & & & & & \\
Nwulu \& Xia~\cite{nwulu2017} & C, E & DR/MPC & & & \checkmark & & & & & \\
Weng et al.~\cite{weng2016} & C & DER-CAM & & \checkmark & & & & & & \\
Gu et al.~\cite{gu2014} & C & MPC & \checkmark & & \checkmark & & & & & \\
Karimi \& Jadid~\cite{karimi2019madm} & multi & Weighted sum + ELECTRE & & & \checkmark & & \checkmark & & & \\
Muhsen et al.~\cite{muhsen2019mode} & C, R & MODE + AHP--TOPSIS & \checkmark & \checkmark & & & \checkmark & & & \\
Zhu et al.~\cite{zhu2020imogwo} & C, R & Improved MOGWO & \checkmark & \checkmark & & & & & & \\
Bakhtiari et al.~\cite{bakhtiari2021mcmc} & multi & MCMC scenarios & \checkmark & \checkmark & & & & \checkmark & & \\
Wang et al.~\cite{wang2024nsga} & multi & Improved NSGA-II & \checkmark & & \checkmark & & & & & \\
Calabrese et al.~\cite{calabrese2026tssp} & C, E & Two-stage SP, $\varepsilon$-constraint & \checkmark & \checkmark & \checkmark & \checkmark & & \checkmark & & \\
\textbf{This work} & C, E, R, D & Seven solvers + PSO--PS; \texttt{paretosearch}; TOPSIS & \checkmark & \checkmark & \checkmark & \checkmark & \checkmark & \checkmark & \checkmark & \checkmark \\
\bottomrule
\end{tabular}
\end{table}''')
# --- DE fuel model and peak load (App. A)
e.rep(r'Based on a peak load of 12.52 kW, the maximum power rating of the DE was set to 16 kW, thus oversizing by $\approx$ 28\% ($SF \approx 0.278$).',
      r'The load peaks at 12.52~kW on the representative day used for dispatch and at 15.0~kW over the year (26 June, 11:00). The DE is rated at 16~kW, 28\% above the representative-day peak ($SF \approx 0.278$) and 6.6\% above the annual peak.')
e.rep(r'The hourly volumetric fuel consumption of the DE can be calculated using the linear law',
      r'In every hour in which the DE is committed ($DE_{ON}(t) = 1$), its volumetric fuel consumption follows the linear law')
e.rep(r'as $C_{fuel,\; DE}(t) = 3.20 \cdot \frac{Fuel_{DE}(t)}{3.78541}$',
      r'as $C_{fuel,\; DE}(t) = 3.20 \cdot \frac{Fuel_{DE}(t)}{3.78541}$. The DE consumes no fuel in hours when it is off')
# --- normalisation clarification (App. B)
e.rep(r'The base emissions $Em_{base}$ are also calculated assuming that the DG meets all the power demand, on a daily and annual basis.',
r'''The base emissions $Em_{base}$ are also calculated assuming that the DG meets all the power demand, on a daily and annual basis. The baseline DG follows the load in every hour, so its annual fuel use is $8760\,\beta_{DE} P_{DG,\;r} + \alpha_{DE} \sum_t P_{load}(t)$; it does not run at rated power for 8,760~h. In every sensitivity case we recompute $LCOE_{base}$ with the same fuel price, interest and inflation rates as the hybrid system, so the normalized LCOE compares the two systems under identical economic conditions, while the baseline DG rating stays at 16~kW so that the normalization does not move with the hybrid system's DG rating. Because the baseline itself moves with fuel price and financial parameters, the normalized LCOE can fall while the absolute LCOE rises; \cref{sec:sizing_sensitivity} therefore reports both.''')
# --- appendix label for weights
e.rep(r'\section{Effects of varying relative objective weights on the sizing results}', r'\section{Effects of varying relative objective weights on the sizing results \label{app:weights}}')
e.rep(r'\subsubsection{Climate data}', r'\subsubsection{Climate data \label{app:climate}}')
e.rep(r'\subsection{Future work}', r'\subsection{Future work \label{sec:future}}')
e.save()
