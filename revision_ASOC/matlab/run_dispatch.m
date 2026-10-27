function [res, zopt] = run_dispatch(d)
% Day-ahead dispatch: global search + local polish (revision).
% 1) PSO on a penalty form (5 seeds), 2) fmincon (SQP) with the hard constraints from the PSO best
% and from the original start point; the best feasible solution is kept.
Pb = 3.68; if ~isfield(d,'scale_bs_power') || d.scale_bs_power, Pb = 0.272593*d.x(3); end % battery power scales with capacity (revision)
lb = [zeros(1,24), -Pb*ones(1,24)]; ub = [d.P_DE_rated*ones(1,24), Pb*ones(1,24)];
z0 = [min(7, d.P_DE_rated)*ones(1,24), min(1,Pb)*ones(1,24)];
f = @(z) dispatch_obj(z, d); nl = @(z) cons(z, d);
pen = @(z) penobj(z, d);
t0 = tic; [~,~,~,~,o0] = dispatch_obj(z0, d);
zr = rule_start(o0.load(:)', o0.P_RES(:)', Pb, d);   % load-following start that respects the SOC limits, DE off
cands = [z0; zr]; 
for s = 1:5
  rng(s,'twister'); o = optimoptions('particleswarm','Display','off','SwarmSize',100,'MaxIterations',600);
  zp = particleswarm(pen, 48, lb, ub, o); cands = [cands; zp]; %#ok<AGROW>
end
o = optimoptions('fmincon','Algorithm','sqp','MaxFunctionEvaluations',2e4,'MaxIterations',2e3,'Display','off');
best = inf; zopt = z0; flag = NaN;
for k = 1:size(cands,1)
  [zk, ~, fk] = fmincon(f, cands(k,:), [],[],[],[], lb, ub, nl, o);
  for zz = {zk, cands(k,:)}
    z = zz{1}; [c] = nl(z);
    if max(c) <= 1e-6 && f(z) < best, best = f(z); zopt = z; flag = fk; end
  end
end
if ~isfinite(best)   % no feasible point: keep the least-violating candidate
  v = arrayfun(@(k) max(nl(cands(k,:))), 1:size(cands,1)); [~,k] = min(v); zopt = cands(k,:); flag = -2;
end
tt = toc(t0);
[J, Costs, soc, DPSP, out] = dispatch_obj(zopt, d);
res = struct('J',J,'COE_n',Costs(1),'Em_n',Costs(2),'Dump',Costs(3),'REF',1-Costs(4),'DPSP',DPSP, ...
             'COE',out.COE,'COE_base',out.COE_base,'Em_kg',out.Em_kg,'DE_hours',out.DE_hours,'fuel_L',out.fuel_L, ...
             'socmin',min(soc),'socmax',max(soc),'exitflag',flag,'feasible',isfinite(best),'time_s',tt);
end
function [c, ceq] = cons(z, d)
[~,~,soc,DPSP] = dispatch_obj(z, d);
c = [0.1 - soc, soc - 0.9, DPSP - d.DPSP_max]; ceq = [];
end
function y = penobj(z, d)
[J,~,soc,DPSP] = dispatch_obj(z, d);
v = [0.1 - soc, soc - 0.9, DPSP - d.DPSP_max];
y = J + 100*sum(max(0, v));
end

function z = rule_start(load, res, Pb, d)
% Load-following schedule with the battery only (DE off), respecting the SOC limits (same SOC model as dispatch_obj).
EC = d.x(3)*3.6e6; dh = 0.075/30.5; soc = d.soc0; pb = zeros(1,24);
for t = 1:24
  s0 = soc*(1-dh); net = load(t)/0.9 - res(t);
  if net > 0, p = min([net, Pb, max(0, s0 - 0.1)*EC/(1000*3600)]); soc = s0 - p*1000*3600/EC;
  else, p = -min([-net, Pb, max(0, 0.9 - s0)*EC/(1000*3600*0.9)]); soc = s0 - p*1000*3600*0.9/EC; end
  pb(t) = p;
end
z = [zeros(1,24), pb];
end
