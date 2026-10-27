% Monte Carlo robustness (T1.5): every point of the corrected 16 kW Pareto front + chosen designs, N = 500.
data = load_data(); out = fullfile('..','results','mc'); if ~isfolder(out), mkdir(out); end
p = default_params();
[~,~,in0] = obj_sizing([15 4 100], p, data); p.fixed_base = true; p.LCOE_base_nom = in0.LCOE_base; p.Em_base_nom = in0.Em_base;
T = readtable(fullfile('..','results','rerun','main_tables.csv'),'TextType','string');
xS3 = T{T.tag=="S3",{'ns','nw','Eb'}}; x8 = T{T.tag=="DG8kW",{'ns','nw','Eb'}};
P = load(fullfile('..','results','rerun','pareto_16kW_5obj.mat'));
X = [xS3; P.x_p]; ids = [{'chosen_S3'}; arrayfun(@(k) sprintf('front_%03d',k), (1:size(P.x_p,1))', 'UniformOutput', false)];
PDE = 16*ones(size(X,1),1);
X = [X; x8]; ids = [ids; {'DG8kW'}]; PDE = [PDE; 8];
writetable(table(ids, X(:,1), X(:,2), X(:,3), PDE, 'VariableNames', {'design_id','ns','nw','Eb','PDE'}), fullfile(out,'designs.csv'));
N = 500; rs = RandStream('mt19937ar','Seed',2026);
fid = fopen(fullfile(out,'mc_results.csv'),'w'); fprintf(fid,'design_id,scenario,J,LCOE_n,Em_n,DPSP,Dump,oneminusREF,LCOE_abs,Em_abs,DE_hours\n');
fs = fopen(fullfile(out,'scenario_summary.csv'),'w'); fprintf(fs,'scenario,aI,aW,irr_kWh_m2,wind_mean,load_kWh\n');
for w = 0:N
  if w == 0, ds = data; ds.aI = 1; ds.aW = 1; else, ds = mc_scenario(data, rs); end
  fprintf(fs,'%d,%.4f,%.4f,%.2f,%.4f,%.1f\n', w, ds.aI, ds.aW, sum(ds.irradiance), mean(ds.wind_speed), sum(ds.Load(:)));
  for k = 1:size(X,1)
    q = p; q.P_DE_rated = PDE(k);
    [J,F,in] = obj_sizing(X(k,:), q, ds);
    fprintf(fid,'%s,%d,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.2f,%d\n', ids{k}, w, J, F, in.LCOE_abs, in.Em_abs, in.DE_hours);
  end
end
fclose(fid); fclose(fs);
fprintf('MC done: %d designs x %d scenarios\n', size(X,1), N);
