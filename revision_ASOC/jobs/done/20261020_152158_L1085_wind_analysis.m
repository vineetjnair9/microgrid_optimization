% Wind analysis (requested 20 Oct): (1) cost of forcing n_w turbines, (2) thresholds at which wind enters, (3) complementarity.
data = load_data(); out = fullfile('..','results','wind_design'); if ~isfolder(out), mkdir(out); end
p = default_params();
% (1)+(3) forced number of turbines: optimize n_s and E_b for fixed n_w (integer-coded PSO, 5 seeds, local Eb polish)
fn = fullfile(out,'forced_nw.csv'); if isfile(fn), delete(fn); end
opt = optimset('TolX',0.01,'Display','off');
for nw = [0 1 2 4 6 8 12 16]
  g = @(y) obj_sizing([round(y(1)) nw y(2)], p, data);
  best = inf; yb = [];
  for s = 1:5
    rng(s,'twister'); o = optimoptions('particleswarm','Display','off');
    [y, fy] = particleswarm(g, 2, [0 0], [400 400], o);
    if fy < best, best = fy; yb = [round(y(1)) y(2)]; end
  end
  for ns = max(0, yb(1)-2):min(400, yb(1)+2)          % local polish
    [e, fe] = fminbnd(@(e) obj_sizing([ns nw e], p, data), max(0, yb(2)-40), min(400, yb(2)+40), opt);
    if fe < best, best = fe; yb = [ns e]; end
  end
  write_row(fn, sprintf('nw%d', nw), nw, [yb(1) nw yb(2)], p, data);
  fprintf('forced nw=%2d: ns=%d Eb=%.1f J=%.5f\n', nw, yb(1), yb(2), best);
end
% hourly series for the n_w = 0 optimum and the n_w = 4 forced design (complementarity)
T = readtable(fn, 'TextType', 'string'); q = p; q.return_series = true;
for nw = [0 4]
  r = T(T.tag == "nw" + nw, :);
  [~,~,in] = obj_sizing([r.ns r.nw r.Eb], q, data); writetable(in.series, fullfile(out, sprintf('series_nw%d.csv', nw)));
end
% single-unit capacity factors at each wind scale (for the threshold in hub-height wind)
fc = fullfile(out,'unit_cf.csv'); fid = fopen(fc,'w'); fprintf(fid,'wind_scale,E_WT_1unit,CF_WT,E_PV_1module,CF_PV\n');
for ws = 1.0:0.1:2.0
  q = p; q.wind_scale = ws; [~,~,a] = obj_sizing([0 1 0], q, data); [~,~,b] = obj_sizing([1 0 0], q, data);
  fprintf(fid,'%.2f,%.1f,%.4f,%.2f,%.4f\n', ws, a.E_WT_kWh, a.E_WT_kWh/0.9/(3.5*8760), b.E_PV_kWh, b.E_PV_kWh/(0.255*8760));
end
fclose(fid);
% (2) thresholds: wind scale sweep and WT cost sweep (best of 3 integer-coded PSO runs + polish)
fs = fullfile(out,'threshold_sweeps.csv'); if isfile(fs), delete(fs); end
for ws = 1.0:0.1:2.0
  q = p; q.wind_scale = ws; xb = pso_best(@(x) obj_sizing(x,q,data), 3, [0 0 0], [400 40 400], 1:3, true);
  write_row(fs, 'wind_scale', ws, xb, q, data); fprintf('wind scale %.1f -> [%g %g %.1f]\n', ws, xb);
end
for c = [1500 1350 1200 1050 900 750 600 450 300]
  q = p; q.C_WT = c; xb = pso_best(@(x) obj_sizing(x,q,data), 3, [0 0 0], [400 40 400], 1:3, true);
  write_row(fs, 'C_WT', c, xb, q, data); fprintf('C_WT %d -> [%g %g %.1f]\n', c, xb);
end
