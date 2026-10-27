data = load_data(); p = default_params();
R = load(fullfile('..','..','Sizing_Vary_DE_Rating_0-20.mat'));
for k = [9 17 21]
  q = p; q.P_DE_rated = k-1; q.base_P_DE_rated = k-1;
  [J,F,info] = obj_sizing(R.x(k,:), q, data);
  fprintf('DErating %2d kW: x=[%s] stored=%.4f  new=%.4f F=[%s] DEh=%d\n', k-1, num2str(R.x(k,:),'%.3f '), R.fval(k), J, num2str(F,'%.4f '), info.DE_hours);
end
W = load(fullfile('..','..','Sizing_Vary_w1.mat'));
[J,F,info] = obj_sizing(W.x(3,:), p, data);
fprintf('w1=0.2 row: x=[%s] stored=%.4f new=%.4f F=[%s] DEh=%d cyc=%d\n', num2str(W.x(3,:),'%.3f '), W.fval(3), J, num2str(F,'%.4f '), info.DE_hours, info.BS_cycles);
% quick PSO, serial, 5 seeds
f = @(x) obj_sizing(x, p, data);
for s = 1:5
  rng(s); o = optimoptions('particleswarm','Display','off');
  [x,fv,~,out] = particleswarm(f,3,[0 0 0],[100 30 200],o);
  [~,F,info] = obj_sizing(x,p,data);
  fprintf('PSO seed %d: x=[%s] J=%.5f evals=%d F=[%s] DEh=%d cyc=%d LCOEabs=%.4f\n', s, num2str(x,'%.3f '), fv, out.funccount, num2str(F,'%.4f '), info.DE_hours, info.BS_cycles, info.LCOE_abs);
end
