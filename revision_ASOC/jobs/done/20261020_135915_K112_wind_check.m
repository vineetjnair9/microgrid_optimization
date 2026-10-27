% Check that the C_WT sweep result (no wind even when cheap) is not a PSO artefact; decompose J.
data = load_data(); T = readtable(fullfile('..','results','wind_design','forced_nw.csv'),'TextType','string');
for c = [1500 600 300]
  for k = 1:height(T)
    p = default_params(); p.C_WT = c; x = [T.ns(k) T.nw(k) T.Eb(k)];
    [J,F,in] = obj_sizing(x,p,data);
    fprintf('C_WT=%4d nw=%2d x=[%g %g %.1f] J=%.5f F=[%s] LCOE=%.4f\n', c, x(2), x, J, num2str(F,'%.4f '), in.LCOE_abs);
  end
end
% cost-only objective with cheap turbines
for c = [1500 600 300]
  p = default_params(); p.C_WT = c; p.w = [1 0 0 0 0];
  xb = pso_best(@(x) obj_sizing(x,p,data), 3, [0 0 0], [400 40 400], 1:3, true); [J,F,in] = obj_sizing(xb,p,data);
  fprintf('LCOE-only C_WT=%4d -> x=[%g %g %.1f] LCOE=%.4f REF=%.3f DEh=%d\n', c, xb, in.LCOE_abs, 1-F(5), in.DE_hours);
end
