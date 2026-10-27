% Sensitivity sweeps on the corrected model (Sec. 6, App. C). Best of 3 PSO seeds + integer polish per point.
data = load_data(); out = fullfile('..','results','rerun'); if ~isfolder(out), mkdir(out); end
lb = [0 0 0]; ub = [100 30 200]; seeds = 1:3;
fn = fullfile(out,'sweeps.csv'); if isfile(fn), delete(fn); end
sw = {'DG_rating', 0:1:20; 'diesel_price', linspace(0.2,12,20); 'interest', linspace(0,0.2,20); ...
      'inflation', linspace(0,0.15,20); 'LI_price', linspace(50,300,20)};
for a = 1:size(sw,1)
  for v = sw{a,2}
    p = default_params();
    switch sw{a,1}
      case 'DG_rating', p.P_DE_rated = v;        % normalisation baseline stays at 16 kW
      case 'diesel_price', p.C_DE = v;           % baseline LCOE recomputed with the same price
      case 'interest', p.i_nom = v;
      case 'inflation', p.f_infl = v;
      case 'LI_price', p.C_LI = v;
    end
    xb = pso_best(@(x) obj_sizing(x,p,data), 3, lb, ub, seeds, true);
    write_row(fn, sw{a,1}, v, xb, p, data);
  end
  fprintf('sweep %s done %s\n', sw{a,1}, datestr(now));
end
for k = 1:5
  for v = linspace(0,1,11)
    p = default_params(); p.w = (1-v)/4*ones(1,5); p.w(k) = v;
    xb = pso_best(@(x) obj_sizing(x,p,data), 3, lb, ub, seeds, true);
    write_row(fn, sprintf('w%d',k), v, xb, p, data);
  end
  fprintf('weight sweep w%d done %s\n', k, datestr(now));
end
