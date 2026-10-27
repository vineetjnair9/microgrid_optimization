function [xi, fi, nev] = int_polish(f, x, lb, ub)
% Round n_s, n_w to the 4 integer neighbours of x and re-optimise E_b for each (fminbnd, <= 19 evals).
cand = unique([floor(x(1)) floor(x(2)); floor(x(1)) ceil(x(2)); ceil(x(1)) floor(x(2)); ceil(x(1)) ceil(x(2))], 'rows');
cand = min(max(cand, lb(1:2)), ub(1:2));
fi = inf; xi = x; nev = 0;
opt = optimset('MaxFunEvals', 18, 'TolX', 0.05, 'Display', 'off');
for k = 1:size(cand,1)
  g = @(e) f([cand(k,:) e]);
  f0 = g(x(3)); nev = nev + 1;
  lo = max(lb(3), x(3) - 30); hi = min(ub(3), x(3) + 30);
  [e, fe, ~, out] = fminbnd(g, lo, hi, opt); nev = nev + out.funcCount;
  if f0 <= fe, e = x(3); fe = f0; end
  if fe < fi, fi = fe; xi = [cand(k,:) e]; end
end
end
