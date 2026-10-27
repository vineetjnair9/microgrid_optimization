% Energy-balance and sanity checks after the revision fixes
data = load_data(); p = default_params(); p.return_series = true;
for x = {[32 4 107.27], [15 4 106.53], [0 0 0], [40 10 200]}
  [J,F,in] = obj_sizing(x{1}, p, data); s = in.series;
  % AC supply: inverter output of DC sources + DE (AC); demand served = load - lost
  dc_out = s.P_PV + s.P_WT*0.9 + s.P_b + s.P_DE*0.9 - s.P_dump;   % DC bus net (DE rectified only for surplus; approximate check)
  served = s.load - s.P_lost;
  fprintf('x=[%s] J=%.4f F=[%s] LCOE=%.4f DEh=%d cyc=%d lost_kWh=%.1f dump_kWh=%.1f\n', num2str(x{1}), J, num2str(F,'%.4f '), in.LCOE_abs, in.DE_hours, in.BS_cycles, in.E_lost_kWh, in.E_dump_kWh);
  d = s.load/0.9 - (s.P_PV + s.P_WT*0.9) - max(s.P_b,0) - s.P_DE/0.9 + s.P_lost/0.9;
  fprintf('   max unexplained deficit (DC kW) in deficit hours: %.4f; hours with SOC jump < -0.2: %d\n', max(d(s.P_DE==0 & s.P_b>=0)), sum(diff(s.soc) < -0.2));
end
