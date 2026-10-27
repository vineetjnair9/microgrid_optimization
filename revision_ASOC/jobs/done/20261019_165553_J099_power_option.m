data = load_data(); lb = [0 0 0]; ub = [100 30 200];
for sc = [false true]
  p = default_params(); p.scale_bs_power = sc;
  [xb, Jb] = pso_best(@(x) obj_sizing(x,p,data), 3, lb, ub, 1:5, true);
  [J,F,in] = obj_sizing(xb,p,data);
  fprintf('scale_bs_power=%d: x=[%g %g %.2f] J=%.4f F=[%s] LCOE=%.4f base=%.4f Em=%.0f DEh=%d cycles/y=%.1f lost=%.1f dump=%.0f\n', sc, xb, J, num2str(F,'%.4f '), in.LCOE_abs, in.LCOE_base, in.Em_abs, in.DE_hours, in.BS_cycles, in.E_lost_kWh, in.E_dump_kWh);
  p8 = p; p8.P_DE_rated = 8; [x8, J8] = pso_best(@(x) obj_sizing(x,p8,data), 3, lb, ub, 1:3, true); [~,F8,in8] = obj_sizing(x8,p8,data);
  fprintf('   8 kW: x=[%g %g %.2f] J=%.4f DPSP=%.4f LCOE=%.4f\n', x8, J8, F8(3), in8.LCOE_abs);
end
