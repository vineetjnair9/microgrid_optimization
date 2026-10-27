"""Stage F3: diesel SO2 factor typo in Table tab:emissions (23 Oct 2026)."""
from texedit import Ed
e = Ed()
e.rep(r"$SO_2$ [$g/kWh$] & 0.074 & 0.003\\", r"$SO_2$ [$g/kWh$] & 0.0074 & 0.003\\")
e.rep(r"\caption{Emissions factors for both DE and MT \cite{emissions}.}",
      r"\caption{Emissions factors for both DE and MT \cite{emissions}. The DE $SO_2$ factor assumes diesel with 15~ppm sulfur, all converted to $SO_2$ (AP-42 Table 3.4-1~\cite{ap42_34}); at 50~ppm, the limit for diesel in Kenya~\cite{bd_sulphur}, it is 0.025~$g/kWh$, which changes total emissions by less than 0.01\%.}")
new = r"""\bibitem{ap42_34}
U.S. Environmental Protection Agency (2025). AP-42, Fifth Edition, Volume I, Section 3.4: Large Stationary Diesel and All Stationary Dual-fuel Engines. \url{https://www.epa.gov/system/files/documents/2025-04/c03s04_april2025.pdf}. Accessed 23 October 2026.

\bibitem{bd_sulphur}
Business Daily Africa (2026, April 30). Kenya waives sulphur limits on petrol and diesel. \url{https://www.businessdailyafrica.com/bd/markets/commodities/kenya-waives-sulphur-limits-on-petrol-and-diesel-5442606}. Accessed 23 October 2026.

"""
e.rep(r"\end{thebibliography}", new + r"\end{thebibliography}")
e.save()
