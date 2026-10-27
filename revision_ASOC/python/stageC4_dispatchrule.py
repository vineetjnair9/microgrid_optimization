from texedit import Ed
e = Ed()
e.rep(r"5 & If batteries are fully discharged up to their lower limit or $DoD$ (i.e., $SOC = SOC_{min}$) and there’s still some unsatisfied load, then dispatch",
      r"5 & If the BS reaches its lower limit or $DoD$ (i.e., $SOC = SOC_{min}$) or its power rating and some load is still unsatisfied, then dispatch")
e.rep(r"then the extra DG output is inverted from AC to DC and then", r"then the extra DG output is rectified from AC to DC and then")
e.save()
