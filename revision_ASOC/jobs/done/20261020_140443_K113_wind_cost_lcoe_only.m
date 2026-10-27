% Cost-only objective (w1 = 1): WT cost threshold at which wind enters.
data = load_data(); fs = fullfile('..','results','wind_design','threshold_lcoe_only.csv'); if isfile(fs), delete(fs); end
for c = [1500 1350 1200 1050 900 750 600]
  p = default_params(); p.C_WT = c; p.w = [1 0 0 0 0];
  xb = pso_best(@(x) obj_sizing(x,p,data), 3, [0 0 0], [400 40 400], 1:5, true);
  write_row(fs, 'C_WT_lcoe_only', c, xb, p, data); fprintf('LCOE-only C_WT %d -> [%g %g %.1f]\n', c, xb);
end
for ws = 1.1:0.1:1.6
  p = default_params(); p.wind_scale = ws; p.w = [1 0 0 0 0];
  xb = pso_best(@(x) obj_sizing(x,p,data), 3, [0 0 0], [400 40 400], 1:5, true);
  write_row(fs, 'wind_scale_lcoe_only', ws, xb, p, data); fprintf('LCOE-only wind %.1f -> [%g %g %.1f]\n', ws, xb);
end
