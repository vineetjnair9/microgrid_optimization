function [xb, Jb, allJ, allX] = pso_best(fJ, nvars, lb, ub, seeds, polish)
% Best of several PSO runs (default options, serial) on scalar objective fJ.
% polish = true: integer-coded search (x(1:2) rounded inside the objective) followed by int_polish.
if polish, g = @(x) fJ([round(x(1)) round(x(2)) x(3:end)]); else, g = fJ; end
Jb = inf; xb = nan(1,nvars); allJ = nan(numel(seeds),1); allX = nan(numel(seeds),nvars);
for k = 1:numel(seeds)
  rng(seeds(k),'twister');
  o = optimoptions('particleswarm','Display','off');
  [x, fv] = particleswarm(g, nvars, lb, ub, o);
  if polish
    x(1:2) = round(x(1:2)); [x, fv] = int_polish(fJ, x, lb, ub);
  end
  allJ(k) = fv; allX(k,:) = x;
  if fv < Jb, Jb = fv; xb = x; end
end
end
