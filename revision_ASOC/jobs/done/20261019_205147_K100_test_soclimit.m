% Checks after wind-curve, SOC-limit and discharge-efficiency fixes.
data = load_data(); p = default_params(); p.return_series = true;
for x = {[100 16 160.96], [200 8 250], [0 0 0], [400 40 400]}
  [J,F,in] = obj_sizing(x{1}, p, data); s = in.series;
  fprintf('x=[%s] J=%.4f F=[%s] LCOE=%.4f DEh=%d cyc=%.0f lost=%.1f dump=%.0f E_PV=%.0f E_WT=%.0f socmin=%.3f socmax=%.3f\n', num2str(x{1}), J, num2str(F,'%.4f '), in.LCOE_abs, in.DE_hours, in.BS_cycles, in.E_lost_kWh, in.E_dump_kWh, in.E_PV_kWh, in.E_WT_kWh, min(s.soc), max(s.soc));
  % DC-bus balance in hours without DE: PV + 0.9 WT + P_b - dump = load/0.9
  k = s.P_DE==0; r = s.P_PV(k) + 0.9*s.P_WT(k) + s.P_b(k) - s.P_dump(k) - s.load(k)/0.9;
  fprintf('   DC balance residual (no-DE hours): max|r| = %.4f kW over %d h\n', max(abs(r)), nnz(k));
end
wt1 = obj_sizing([0 1 0], p, data); [~,~,i1] = obj_sizing([0 1 0], p, data); fprintf('1 WT: E_WT=%.0f kWh/y, CF=%.3f\n', i1.E_WT_kWh, i1.E_WT_kWh/0.9/(3.5*8760));
[~,~,i2] = obj_sizing([1 0 0], p, data); fprintf('1 PV module: E_PV=%.0f kWh/y, CF=%.3f\n', i2.E_PV_kWh, i2.E_PV_kWh/(0.255*8760));
q = default_params();
[xb, Jb, allJ, allX] = pso_best(@(x) obj_sizing(x,q,data), 3, [0 0 0], [400 40 400], 1:3, true);
[J,F,in] = obj_sizing(xb,q,data);
fprintf('PSO wide bounds: x=[%g %g %.2f] J=%.5f F=[%s] LCOE=%.4f DEh=%d cyc=%.0f REF=%.3f\n', xb, J, num2str(F,'%.4f '), in.LCOE_abs, in.DE_hours, in.BS_cycles, 1-F(5));
disp(allX); disp(allJ(:)');
