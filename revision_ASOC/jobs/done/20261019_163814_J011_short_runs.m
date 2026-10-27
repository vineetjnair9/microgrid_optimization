% Short runs: DG rating as a decision variable, eps-constraint on DPSP, strategy stress test, wind factor sweep.
data = load_data(); out = fullfile('..','results','short_runs'); if ~isfolder(out), mkdir(out); end
% (a) 4-variable PSO, budget via default stopping, 10 seeds
p = default_params();
fn = fullfile(out,'dg_variable.csv'); if isfile(fn), delete(fn); end
for s = 1:10
  rng(s,'twister'); o = optimoptions('particleswarm','Display','off');
  x = particleswarm(@(x) obj_sizing([round(x(1:2)) x(3:4)],p,data), 4, [0 0 0 0], [100 30 200 20], o); x(1:2) = round(x(1:2));
  g = @(y) obj_sizing([y x(4)],p,data); xi = int_polish(g, x(1:3), [0 0 0], [100 30 200]);
  xx = [xi x(4)]; q = p; q.P_DE_rated = x(4);
  write_row(fn, sprintf('seed%d',s), x(4), xx(1:3), q, data);
end
% (b) eps-constraint: minimise mean of (LCOE, Em, Dump, 1-REF) s.t. DPSP <= eps, DG rating free
fn = fullfile(out,'eps_front.csv'); if isfile(fn), delete(fn); end
for e = [0 0.001 0.002 0.005 0.01 0.02 0.05]
  best = inf; xb = [];
  for s = 1:5
    rng(s,'twister'); o = optimoptions('particleswarm','Display','off');
    h = @(x) epsobj(x,p,data,e);
    [x, fv] = particleswarm(@(y) h([round(y(1:2)) y(3:4)]), 4, [0 0 0 0], [100 30 200 20], o); x(1:2) = round(x(1:2));
    if fv < best, best = fv; xb = x; end
  end
  q = p; q.P_DE_rated = xb(4);
  write_row(fn, sprintf('eps_%g',e), e, xb(1:3), q, data);
end
% (c) Strategy 3 vs 4 under stress
fn = fullfile(out,'strategy_stress.csv'); if isfile(fn), delete(fn); end
for dc = [true false]
  for c = [3.20 5.00 7.57]
    for tl = [5475 3000]
      q = default_params(); q.de_charge = dc; q.C_DE = c; q.t_LI_cycles = tl;
      xb = pso_best(@(x) obj_sizing(x,q,data), 3, [0 0 0], [100 30 200], 1:5, true);
      write_row(fn, sprintf('S%d_C%.2f_L%d', 4-dc, c, tl), c, xb, q, data);
    end
  end
end
% (d) wind correction factor sweep
fn = fullfile(out,'wind_sweep.csv'); if isfile(fn), delete(fn); end
for ws = [0.75 1.00 1.25]
  q = default_params(); q.wind_scale = ws;
  xb = pso_best(@(x) obj_sizing(x,q,data), 3, [0 0 0], [100 30 200], 1:5, true);
  write_row(fn, sprintf('wind_%.2f',ws), 3.70*ws, xb, q, data);
end

function y = epsobj(x,p,data,e)
q = p; q.P_DE_rated = x(4);
[~,F] = obj_sizing(x(1:3),q,data);
y = mean(F([1 2 4 5])) + 100*max(0, F(3) - e);
end
