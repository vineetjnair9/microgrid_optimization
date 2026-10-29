"""Stage G: Introduction electricity-access statistics updated to Tracking SDG 7 2025 (28 Oct 2026)."""
from texedit import Ed
e = Ed()
e.rep(r"Over 1 billion people or 13\% of the world's population still lacks access to electricity, with most of these people living in Africa, India and other parts of southeast Asia. In particular, sub-Saharan Africa (SSA) suffers from low electrification rates and hosts over 621 million people (i.e., approximately two in every three persons in Africa) who currently do not have reliable electrical power \cite{SSA_decent}.",
      r"Sub-Saharan Africa (SSA) suffers from low electrification rates \cite{SSA_decent}. In 2023, 666 million people, about 8\% of the world's population, still lacked access to electricity, and 565 million of them lived in SSA \cite{sdg7_2025}.")
e.rep(r"\end{thebibliography}", r"""\bibitem{sdg7_2025}
IEA, IRENA, UNSD, World Bank, WHO (2025). \textit{Tracking SDG 7: The Energy Progress Report 2025}. World Bank, Washington, DC. \url{https://trackingsdg7.esmap.org/}

\end{thebibliography}""")
e.save()
