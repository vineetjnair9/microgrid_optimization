function write_row(fn, tag, val, x, p, data)
% Evaluate design x with obj_sizing and append one CSV row (creates header if needed).
[J,F,in] = obj_sizing(x, p, data);
hdr = ~isfile(fn); fid = fopen(fn,'a');
if hdr
  fprintf(fid,'tag,value,ns,nw,Eb,PDE,J,LCOE_n,Em_n,DPSP,Dump,oneminusREF,LCOE_abs,LCOE_base,Em_abs,Em_base,DE_hours,BS_cycles,TAC,fuel_L,E_WT_kWh,E_PV_kWh,E_dump_kWh\n');
end
fprintf(fid,'%s,%.6g,%.6g,%.6g,%.4f,%.4g,%.8f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.2f,%.2f,%d,%d,%.2f,%.1f,%.1f,%.1f,%.1f\n', ...
  tag, val, x(1), x(2), x(3), in.P_DE_rated, J, F, in.LCOE_abs, in.LCOE_base, in.Em_abs, in.Em_base, in.DE_hours, in.BS_cycles, in.TAC, in.fuel_L, in.E_WT_kWh, in.E_PV_kWh, in.E_dump_kWh);
fclose(fid);
end
