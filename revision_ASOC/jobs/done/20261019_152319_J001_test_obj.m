% T1.1 reproduction tests
fprintf('%s | %s | %s\n', version, computer, datestr(now));
data = load_data(); p = default_params();
out = fullfile('..','results'); 
[J,F,info] = obj_sizing([15 4 106.53], p, data);
fprintf('TEST1 J=%.4f F=[%s] DEh=%d cyc=%d LCOEabs=%.4f Em=%.1f LCOEbase=%.4f TAC=%.1f fuelL=%.0f\n', J, num2str(F,'%.4f '), info.DE_hours, info.BS_cycles, info.LCOE_abs, info.Em_abs, info.LCOE_base, info.TAC, info.fuel_L);
rng(1); X = [100 30 200].*rand(10,3); md = 0;
for k=1:10
  [~,Fn] = obj_sizing(X(k,:), p, data);
  Fo = Objective_LI_DE_v10_1h_ind_VaryParams_output(X(k,:), 0);
  md = max(md, abs(mean(Fn)-mean(Fo)));
end
fprintf('TEST2 max |meanF_new - meanF_orig| = %.3e\n', md);
p3 = p; p3.replace_by_cycles = false;
[J3,F3] = obj_sizing([11 4 70.29], p3, data); fprintf('TEST3 strat1 J=%.4f F=[%s]\n', J3, num2str(F3,'%.4f '));
p4 = p; p4.de_charge = false; p4.replace_by_cycles = false;
[J4,F4] = obj_sizing([7 4 77.49], p4, data); fprintf('TEST3b strat2 J=%.4f F=[%s]\n', J4, num2str(F4,'%.4f '));
p5 = p; p5.de_charge = false;
[J5,F5] = obj_sizing([0 4 120.98], p5, data); fprintf('TEST3c strat4 J=%.4f F=[%s]\n', J5, num2str(F5,'%.4f '));
pf = p; pf.noload_fix = true;
[Jf,Ff,infof] = obj_sizing([15 4 106.53], pf, data);
fprintf('NOLOAD_FIX J=%.4f F=[%s] LCOEabs=%.4f fuelL=%.0f TAC=%.1f\n', Jf, num2str(Ff,'%.4f '), infof.LCOE_abs, infof.fuel_L, infof.TAC);
tic; for k=1:20, obj_sizing(X(mod(k-1,10)+1,:), p, data); end; t_eval = toc/20;
fprintf('TIMING t_eval=%.4f s\n', t_eval);
v = load(fullfile('..','..','Sizing_Vary_DE_price.mat')); 
fprintf('Stored DE price sweep fval(1:3)=%s\n', num2str(v.fval(1:3)','%.4f '));
