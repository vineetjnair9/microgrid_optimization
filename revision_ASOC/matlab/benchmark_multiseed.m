function benchmark_multiseed(solvers, seeds, budget, outdir, intcoded)
if nargin < 5, intcoded = false; end
% Equal-budget multi-seed benchmark (T1.3). Serial evaluation for all solvers (one evaluation ~2 ms,
% so parallel overhead would dominate). Integer handling: relax-and-round + int_polish (counted in budget).
data = load_data(); p = default_params();
lb = [0 0 0]; ub = [400 40 400]; nvars = 3;
if intcoded   % integer-coded search: n_s, n_w rounded inside the objective
  f = @(x) obj_sizing([round(x(1)) round(x(2)) x(3)], p, data);
else
  f = @(x) obj_sizing(x, p, data);
end
polish_budget = 80; cap = budget - polish_budget;
if ~isfolder(outdir), mkdir(outdir); end
tdir = fullfile(outdir,'traces'); if ~isfolder(tdir), mkdir(tdir); end
for s = seeds
  for k = 1:numel(solvers)
    name = solvers{k};
    fn = fullfile(outdir, sprintf('%s_seed%02d.mat', name, s));
    if isfile(fn), continue; end
    R = run_one(name, s);
    save(fn, '-struct', 'R');
    writematrix(R.trace, fullfile(tdir, sprintf('%s_seed%02d.csv', name, s)));
    append_summary(fullfile(outdir,'summary.csv'), R);
    fprintf('%-6s seed %2d  J_cont=%.6f J_int=%.6f x_int=[%g %g %.2f] evals=%d t=%.2fs\n', name, s, R.J_cont, R.J_int, R.x_int, R.evals, R.wall_s);
  end
end

  function R = run_one(name, s)
    trace = zeros(0,2); nev = 0; bestf = inf; bestx = nan(1,nvars); cap1 = round(0.8*cap);
    rng(s, 'twister');
    x0 = lb + rand(1,nvars).*(ub - lb);
    t0 = tic;
    switch name
      case 'PSO'
        o = optimoptions('particleswarm','Display','off','OutputFcn',@psoStop);
        [~, ~, flag] = particleswarm(@fw, nvars, lb, ub, o);
      case 'GA'
        o = optimoptions('ga','Display','off','OutputFcn',@gaStop);
        [~, ~, flag] = ga(@fw, nvars, [],[],[],[], lb, ub, [], o);
      case 'SA'
        o = optimoptions('simulannealbnd','Display','off','MaxFunctionEvaluations',cap);
        [~, ~, flag] = simulannealbnd(@fw, x0, lb, ub, o);
      case 'SO'
        o = optimoptions('surrogateopt','Display','off','MaxFunctionEvaluations',cap,'PlotFcn',[]);
        [~, ~, flag] = surrogateopt(@fw, lb, ub, o);
      case {'MS','GS'}
        fo = optimoptions('fmincon','Algorithm','active-set','Display','off','OutputFcn',@fmcStop);
        prob = createOptimProblem('fmincon','objective',@fw,'x0',x0,'lb',lb,'ub',ub,'options',fo);
        if strcmp(name,'MS')
          ms = MultiStart('OutputFcn',@msStop,'Display','off');
          [~, ~, flag] = run(ms, prob, 1000);
        else
          gs = GlobalSearch('NumTrialPoints',400,'NumStageOnePoints',100,'OutputFcn',@msStop,'Display','off');
          [~, ~, flag] = run(gs, prob);
        end
      case 'DPS'
        flag = 0; xs = x0;
        while nev < cap
          o = optimoptions('patternsearch','UseCompletePoll',true,'Display','off','MaxFunctionEvaluations',cap-nev);
          [~, ~, flag] = patternsearch(@fw, xs, [],[],[],[], lb, ub, [], o);
          xs = lb + rand(1,nvars).*(ub - lb);
        end
      case 'PSOPS'
        o = optimoptions('particleswarm','Display','off','OutputFcn',@psoStop1);
        particleswarm(@fw, nvars, lb, ub, o);
        o2 = optimoptions('patternsearch','UseCompletePoll',true,'Display','off','MaxFunctionEvaluations',max(cap-nev,1));
        [~, ~, flag] = patternsearch(@fw, bestx, [],[],[],[], lb, ub, [], o2);
    end
    used = nev; xb = bestx; fb = bestf;
    wall_search = toc(t0);
    [xi, fi, npol] = int_polish(f, xb, lb, ub);
    wall = toc(t0);
    R = struct('solver',name,'seed',s,'J_cont',fb,'x_cont',xb,'J_int',fi,'x_int',xi, ...
               'evals',used+npol,'evals_search',used,'wall_s',wall,'wall_search_s',wall_search,'exitflag',flag,'trace',trace);

    function y = fw(x)              % counting wrapper: every evaluation is logged
      y = f(x); nev = nev + 1; if ~isfinite(y), y = 10; end   % guard (objective is normally in [0,1])
      if y < bestf, bestf = y; bestx = x; trace(end+1,:) = [nev, y]; end
    end
    function stop = psoStop(~, ~), stop = nev >= cap; end
    function stop = psoStop1(~, ~), stop = nev >= cap1; end
    function [state, opts, changed] = gaStop(opts, state, ~)
      changed = false; if nev >= cap, state.StopFlag = 'budget'; end
    end
    function stop = fmcStop(~, ~, ~), stop = nev >= cap; end
    function stop = msStop(~, ~), stop = nev >= cap; end
  end
end

function append_summary(fn, R)
hdr = ~isfile(fn); fid = fopen(fn,'a');
if hdr, fprintf(fid,'solver,seed,J_cont,J_int,ns_cont,nw_cont,Eb_cont,ns,nw,Eb,evals,evals_search,wall_s,wall_search_s,exitflag\n'); end
fprintf(fid,'%s,%d,%.8f,%.8f,%.4f,%.4f,%.4f,%d,%d,%.4f,%d,%d,%.4f,%.4f,%d\n', R.solver, R.seed, R.J_cont, R.J_int, ...
        R.x_cont, R.x_int(1), R.x_int(2), R.x_int(3), R.evals, R.evals_search, R.wall_s, R.wall_search_s, R.exitflag);
fclose(fid);
end
