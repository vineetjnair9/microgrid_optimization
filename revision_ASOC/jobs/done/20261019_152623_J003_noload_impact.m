data = load_data();
fid = fopen(fullfile('..','results','noload_fix_impact.csv'),'w');
fprintf(fid,'P_DE,noload_fix,seed,ns,nw,Eb,J,LCOE_n,Em_n,DPSP,Dump,oneminusREF,LCOE_abs,Em_abs,DE_hours,BS_cycles,TAC,fuel_L\n');
for PDE = [16 8]
 for fix = [false true]
  p = default_params(); p.noload_fix = fix; p.P_DE_rated = PDE;
  f = @(x) obj_sizing(x, p, data);
  for s = 1:5
    rng(s); o = optimoptions('particleswarm','Display','off');
    [x,fv] = particleswarm(f,3,[0 0 0],[100 30 200],o);
    [J,F,in] = obj_sizing(x,p,data);
    fprintf(fid,'%d,%d,%d,%.4f,%.4f,%.4f,%.6f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.1f,%d,%d,%.1f,%.0f\n',PDE,fix,s,x,J,F,in.LCOE_abs,in.Em_abs,in.DE_hours,in.BS_cycles,in.TAC,in.fuel_L);
  end
 end
end
fclose(fid);
