% Technology combinations re-run after applying the 2 h time shift inside the legacy LA/MT objectives.
out = fullfile('..','results','rerun'); lb = [0 0 0]; ub = [400 40 400];
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
