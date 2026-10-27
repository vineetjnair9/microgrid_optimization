% Ground truth for the benchmark: exhaustive search over integer (n_s, n_w), E_b by grid + fminbnd.
data = load_data(); p = default_params();
f = @(x) obj_sizing(x, p, data);
NS = 0:400; NW = 0:40; Eg = 0:10:400;
best = inf(numel(NS), numel(NW)); bestE = nan(numel(NS), numel(NW));
opt = optimset('TolX',0.01,'Display','off');
t0 = tic;
for a = 1:numel(NS)
  for b = 1:numel(NW)
    v = arrayfun(@(e) f([NS(a) NW(b) e]), Eg);
    [~,k] = min(v); lo = Eg(max(k-1,1)); hi = Eg(min(k+1,numel(Eg)));
    [e, fe] = fminbnd(@(e) f([NS(a) NW(b) e]), lo, hi, opt);
    if v(k) < fe, e = Eg(k); fe = v(k); end
    best(a,b) = fe; bestE(a,b) = e;
  end
end
[fstar, idx] = min(best(:)); [a,b] = ind2sub(size(best), idx);
xstar = [NS(a) NW(b) bestE(a,b)];
[J,F,info] = obj_sizing(xstar, p, data);
fprintf('EXHAUSTIVE f*_int = %.8f at x = [%d %d %.3f]  F=[%s] LCOE_abs=%.4f DEh=%d cyc=%d (%.0f s)\n', fstar, xstar, num2str(F,'%.4f '), info.LCOE_abs, info.DE_hours, info.BS_cycles, toc(t0));
save(fullfile('..','results','benchmark','exhaustive_int.mat'), 'best','bestE','NS','NW','fstar','xstar');
writematrix(best, fullfile('..','results','benchmark','exhaustive_int_bestJ.csv'));
% how many integer designs lie within 0.5% of f*
fprintf('designs within 0.5%% of f*: %d; within 1%%: %d\n', nnz(best(:) <= 1.005*fstar), nnz(best(:) <= 1.01*fstar));
[r,c] = find(best <= 1.005*fstar); disp([NS(r)' NW(c)' bestE(sub2ind(size(best),r,c)) best(sub2ind(size(best),r,c))]);
