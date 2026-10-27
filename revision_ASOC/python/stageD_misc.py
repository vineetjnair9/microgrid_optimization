"""Stage D misc: workflow figure placement."""
from texedit import Ed
e = Ed()
i = e.s.index(r'\textbf{Two-stage sequential framework.}'); j = e.s.index('\n', i)
if r'\label{fig:workflow}' not in e.s:
    fig = r'''

\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{rev_workflow.pdf}
  \caption{\label{fig:workflow} Design workflow. Stage~1 sizes the system under a rule-based controller; Pareto search, rule-based selection from the front and Monte Carlo re-ranking choose among candidate designs; Stage~2 optimizes day-ahead dispatch of a selected design and tests it on stress days.}
\end{figure}'''
    e.s = e.s[:j] + fig + e.s[j:]; e.log.append('workflow fig')
e.save()
