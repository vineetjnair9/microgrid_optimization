% Hourly series of the chosen design (sizing-stage operation figures) and exact values at rounded Pareto representatives.
data = load_data(); out = fullfile('..','results','rerun');
T = readtable(fullfile(out,'main_tables.csv'),'TextType','string');
p = default_params(); p.return_series = true;
x = T{T.tag=="S3",{'ns','nw','Eb'}}; [~,~,in] = obj_sizing(x, p, data);
writetable(in.series, fullfile(out,'series_S3_16kW.csv'));
R = readtable(fullfile('..','results','pareto','representatives_to_evaluate.csv'),'TextType','string');
fn = fullfile('..','results','pareto','representatives_exact.csv'); if isfile(fn), delete(fn); end
for k = 1:height(R)
  q = default_params(); q.P_DE_rated = R.PDE(k);
  write_row(fn, R.front(k) + "_" + R.label(k), R.PDE(k), [R.ns_int(k) R.nw_int(k) R.Eb(k)], q, data);
end
