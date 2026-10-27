"""Stage F: verified sources for the Monte Carlo inter-annual spreads and the TAHMO sensor height (21 Oct 2026)."""
from texedit import Ed
e = Ed()
e.rep(r"The inter-annual spreads are assumptions of the order reported for East African sites;",
      r"The inter-annual spreads are deliberately conservative: satellite records give year-to-year coefficients of variation of 1--5\% for annual global horizontal irradiation over most of Kenya (5--6\% in the central and western highlands)~\cite{kariuki2018solar}, and wind resource studies report 3--6\% for annual mean wind speed, up to 10\% at some sites~\cite{lee2018wes};")
e.rep(r"A 2~m reference height would lower the model's hub-height mean by 9\%",
      r"TAHMO stations use the METER ATMOS~41 all-in-one sensor~\cite{meter_tahmo}, which is commonly mounted 2~m above ground~\cite{tahmo_install}; the mounting height of the Timbila sensor is not recorded in the data we used. A 2~m reference height would lower the model's hub-height mean by 9\%")
new = r"""\bibitem{kariuki2018solar}
Kariuki, B. W., \& Sato, T. (2018). Interannual and spatial variability of solar radiation energy potential in Kenya using Meteosat satellite. \textit{Renewable Energy}, 116, 88--96. \url{https://doi.org/10.1016/j.renene.2017.09.069}

\bibitem{lee2018wes}
Lee, J. C. Y., Fields, M. J., \& Lundquist, J. K. (2018). Assessing variability of wind speed: comparison and validation of 27 methodologies. \textit{Wind Energy Science}, 3, 845--868. \url{https://doi.org/10.5194/wes-3-845-2018}

\bibitem{meter_tahmo}
METER Group. Transforming Africa's future: a revolutionary weather network empowers communities (TAHMO case study). \url{https://metergroup.com/case-studies/10-years-of-weather-network-building-in-africa/}. Accessed 21 October 2026.

\bibitem{tahmo_install}
TAHMO. Installation resources. \url{https://tahmo.org/installation-resources/}. Accessed 21 October 2026.

"""
e.rep(r"\end{thebibliography}", new + r"\end{thebibliography}")
e.save()
