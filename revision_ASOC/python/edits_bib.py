from texedit import Ed
e = Ed()
e.rep('The DE consumes no fuel in hours when it is off\n', 'The DE consumes no fuel in hours when it is off.\n')
new = r'''
\bibitem{wang2024nsga}
Wang, X., Zhu, H., Luo, X., Chang, S., \& Guan, X. (2024). A novel optimal dispatch strategy for hybrid energy ship power system based on the improved NSGA-II algorithm. \textit{Electric Power Systems Research}, 232, 110385. \url{https://doi.org/10.1016/j.epsr.2024.110385}

\bibitem{zhu2020imogwo}
Zhu, W., Guo, J., Zhao, G., \& Zeng, B. (2020). Optimal sizing of an island hybrid microgrid based on improved multi-objective grey wolf optimizer. \textit{Processes}, 8(12), 1581. \url{https://doi.org/10.3390/pr8121581}

\bibitem{geleta2022gwo}
Geleta, D. K., Manshahia, M. S., Vasant, P., \& Banik, A. (2022). Grey wolf optimizer for optimal sizing of hybrid wind and solar renewable energy system. \textit{Computational Intelligence}, 38(3), 1133--1162. \url{https://doi.org/10.1111/coin.12349}

\bibitem{javidrad2017psosa}
Javidrad, F., \& Nazari, M. (2017). A new hybrid particle swarm and simulated annealing stochastic optimization method. \textit{Applied Soft Computing}, 60, 634--654. \url{https://doi.org/10.1016/j.asoc.2017.07.023}

\bibitem{muhsen2019mode}
Muhsen, D. H., Nabil, M., Haider, H. T., \& Khatib, T. (2019). A novel method for sizing of standalone photovoltaic system using multi-objective differential evolution algorithm and hybrid multi-criteria decision making methods. \textit{Energy}, 174, 1158--1175. \url{https://doi.org/10.1016/j.energy.2019.03.046}

\bibitem{karimi2019madm}
Karimi, H., \& Jadid, S. (2019). Optimal microgrid operation scheduling by a novel hybrid multi-objective and multi-attribute decision-making framework. \textit{Energy}, 186, 115912. \url{https://doi.org/10.1016/j.energy.2019.115912}

\bibitem{bakhtiari2021mcmc}
Bakhtiari, H., Zhong, J., \& Alvarez, M. (2021). Predicting the stochastic behavior of uncertainty sources in planning a stand-alone renewable energy-based microgrid using Metropolis--coupled Markov chain Monte Carlo simulation. \textit{Applied Energy}, 290, 116719. \url{https://doi.org/10.1016/j.apenergy.2021.116719}

\bibitem{calabrese2026tssp}
Calabrese, M., Ademollo, A., \& Carcasci, C. (2026). Designing off-grid hybrid renewable energy systems under uncertainty: A two-stage stochastic programming approach. \textit{Renewable Energy}, 256, 124193. \url{https://doi.org/10.1016/j.renene.2025.124193}

\bibitem{derrac2011tutorial}
Derrac, J., Garc\'{i}a, S., Molina, D., \& Herrera, F. (2011). A practical tutorial on the use of nonparametric statistical tests as a methodology for comparing evolutionary and swarm intelligence algorithms. \textit{Swarm and Evolutionary Computation}, 1(1), 3--18. \url{https://doi.org/10.1016/j.swevo.2011.02.002}

\bibitem{carrasco2020trends}
Carrasco, J., Garc\'{i}a, S., Rueda, M. M., Das, S., \& Herrera, F. (2020). Recent trends in the use of statistical tests for comparing swarm and evolutionary computing algorithms: Practical guidelines and a critical review. \textit{Swarm and Evolutionary Computation}, 54, 100665. \url{https://doi.org/10.1016/j.swevo.2020.100665}

\bibitem{hansen2021coco}
Hansen, N., Auger, A., Ros, R., Mersmann, O., Tu\v{s}ar, T., \& Brockhoff, D. (2021). COCO: a platform for comparing continuous optimizers in a black-box setting. \textit{Optimization Methods and Software}, 36(1), 114--144. \url{https://doi.org/10.1080/10556788.2020.1808977}

\bibitem{vargha2000a12}
Vargha, A., \& Delaney, H. D. (2000). A critique and improvement of the CL common language effect size statistics of McGraw and Wong. \textit{Journal of Educational and Behavioral Statistics}, 25(2), 101--132. \url{https://doi.org/10.3102/10769986025002101}

\bibitem{deb2011knee}
Deb, K., \& Gupta, S. (2011). Understanding knee points in bicriteria problems and their implications as preferred solution principles. \textit{Engineering Optimization}, 43(11), 1175--1204. \url{https://doi.org/10.1080/0305215X.2010.548863}

\bibitem{hwang1981topsis}
Hwang, C.-L., \& Yoon, K. (1981). \textit{Multiple Attribute Decision Making: Methods and Applications}. Lecture Notes in Economics and Mathematical Systems, Springer, Berlin. \url{https://doi.org/10.1007/978-3-642-48318-9}

\bibitem{gelaro2017merra2}
Gelaro, R., McCarty, W., Su\'{a}rez, M. J., Todling, R., Molod, A., Takacs, L., et al. (2017). The Modern-Era Retrospective Analysis for Research and Applications, Version 2 (MERRA-2). \textit{Journal of Climate}, 30(14), 5419--5454. \url{https://doi.org/10.1175/JCLI-D-16-0758.1}

\bibitem{nasapower}
NASA Langley Research Center. Prediction Of Worldwide Energy Resources (POWER) Project, hourly API, data for 2018 at 3.39\textdegree S, 37.72\textdegree E. \url{https://power.larc.nasa.gov/}. Accessed 19 October 2026.
'''
e.rep(r'\end{thebibliography}', new + '\n' + r'\end{thebibliography}')
e.save()
