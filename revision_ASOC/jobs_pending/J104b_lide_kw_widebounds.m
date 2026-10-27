% LIDE approach (ii) with wider rated-power bounds (the [25 25 200] run hit the PV bound).
data = load_data(); out = fullfile('..','results','rerun'); fn = fullfile(out,'main_tables.csv');
p = default_params(); p.vars_kW = true;
[xb, Jb] = pso_best(@(x) obj_sizing(x,p,data), 3, [0 0 0], [40 40 200], 1:10, false);
write_row(fn, 'LIDE_ii_kW_wide', 0, xb, p, data);
fprintf('LIDE (ii) wide x_kW=[%.3f %.3f %.2f] J=%.5f\n', xb, Jb);
