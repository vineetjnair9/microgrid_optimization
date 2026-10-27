% Re-run of main sizing tables on the corrected model (T1.7). Best of 10 PSO seeds + integer polish.
data = load_data(); out = fullfile('..','results','rerun'); if ~isfolder(out), mkdir(out); end
lb = [0 0 0]; ub = [100 30 200]; seeds = 1:10;
fn = fullfile(out,'main_tables.csv'); if isfile(fn), delete(fn); end
% Strategies 1-4
S = {'S1',true,false; 'S2',false,false; 'S3',true,true; 'S4',false,true};   % name, de_charge, replace_by_cycles
for k = 1:4
  p = default_params(); p.de_charge = S{k,2}; p.replace_by_cycles = S{k,3};
  [xb, Jb, allJ] = pso_best(@(x) obj_sizing(x,p,data), 3, lb, ub, seeds, true);
  write_row(fn, S{k,1}, median(allJ), xb, p, data);
  fprintf('%s best J=%.5f x=[%g %g %.2f] median over seeds %.5f\n', S{k,1}, Jb, xb, median(allJ));
end
% Strategy 3 with the original (uncorrected) fuel model, for the response letter
p = default_params(); p.noload_fix = false;
[xb, Jb] = pso_best(@(x) obj_sizing(x,p,data), 3, lb, ub, seeds, true);
write_row(fn, 'S3_original_fuel_model', 0, xb, p, data);
% Approach (ii): rated-power decision variables (continuous)
p = default_params(); p.vars_kW = true;
[xb, Jb] = pso_best(@(x) obj_sizing(x,p,data), 3, [0 0 0], [25 25 200], seeds, false);
write_row(fn, 'LIDE_ii_kW', 0, xb, p, data);
fprintf('LIDE (ii) x_kW=[%.3f %.3f %.2f] J=%.5f\n', xb, Jb);
% Technology combinations (LI+DE is S3 above)
T = {'LA_DE',@obj_LA_DE; 'LI_MT',@obj_LI_MT; 'LA_MT',@obj_LA_MT};
fid = fopen(fullfile(out,'tech_tables.csv'),'w');
fprintf(fid,'tech,ns,nw,Eb,J,LCOE_n,Em_n,DPSP,Dump,oneminusREF,J_median\n');
for k = 1:3
  g = T{k,2};
  [xb, Jb, allJ] = pso_best(@(x) g(x), 3, lb, ub, 1:5, true);
  [J, F] = g(xb);
  fprintf(fid,'%s,%g,%g,%.3f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n', T{k,1}, xb, J, F, median(allJ));
  fprintf('%s J=%.5f x=[%g %g %.2f]\n', T{k,1}, J, xb);
end
fclose(fid);
% 8 kW DG design (used for dispatch and Monte Carlo)
p = default_params(); p.P_DE_rated = 8;
[xb, Jb] = pso_best(@(x) obj_sizing(x,p,data), 3, lb, ub, seeds, true);
write_row(fn, 'DG8kW', 8, xb, p, data);
fprintf('8 kW design x=[%g %g %.2f] J=%.5f\n', xb, Jb);
