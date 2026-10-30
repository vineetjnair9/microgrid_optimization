% L111 (stage H, 30 Oct 2026): day-ahead dispatch on a low-resource day from the 2018 record.
% Day 168 = 17 June 2018 (local time): the day with the largest DE energy under rule-based operation of the
% equal-weight design (122 kWh over 19 h; PV output 38% of the annual daily mean; SOC at 00:00 = 0.11).
% Each configuration starts the day at the SOC its own rule-based annual simulation reaches at 00:00.
% Writes results/dispatch_lowres/: dispatch_d168_<case>.csv, rule_<cfg>.csv, dispatch_cases_d168.csv
root = fullfile('..','..'); out = fullfile('..','results','dispatch_lowres'); if ~isfolder(out), mkdir(out); end
data = load_data();
T = readtable(fullfile('..','results','rerun','main_tables.csv'),'TextType','string');
x16 = T{T.tag=="S3",{'ns','nw','Eb'}}; x8 = T{T.tag=="DG8kW",{'ns','nw','Eb'}};
day = 168; hh = (day-1)*24 + (1:24);
Lyr = reshape(data.Load', [], 1);                 % Load is 365x24 (day x hour)
base = struct('irr',data.irradiance(hh)','temp',data.temp(hh)','wind',data.wind_speed(hh)','load',Lyr(hh)');
Ld = load(fullfile(root,'Load_day.mat')); Lb = Ld.Load_day(:)';
pk = load(fullfile(root,'load_peaky.mat')); sh = load(fullfile(root,'load_shift_v2.mat')); sc = load(fullfile(root,'load_shift_curtail.mat'));
cfg = {'i_16kW', x16, 16; 'ii_8kW_16kWsizing', x16, 8; 'iii_8kW_8kWsizing', x8, 8};
soc0 = zeros(1,3);
for k = 1:3
  p = default_params(); p.return_series = true; p.P_DE_rated = cfg{k,3};
  [~,~,in] = obj_sizing(cfg{k,2}, p, data); S = in.series; S.Properties.VariableNames = {'load','P_PV','P_WT','P_DE','P_b','P_dump','P_lost','soc'};
  soc0(k) = S.soc(hh(1));
  writetable(S(hh,:), fullfile(out, ['rule_' cfg{k,1} '.csv']));
  fprintf('%-20s rule-based day %d: soc0=%.4f DE_h=%d E_DE=%.2f kWh lost=%.3f kWh dump=%.2f kWh |load-base|max=%.2g\n', ...
     cfg{k,1}, day, soc0(k), sum(S.P_DE(hh)>0), sum(S.P_DE(hh)), sum(S.P_lost(hh)), sum(S.P_dump(hh)), max(abs(S.load(hh)'-base.load)));
end
mk = @(x,P,dd,s0) struct('x',x,'P_DE_rated',P,'irr',dd.irr,'temp',dd.temp,'wind',dd.wind,'load',dd.load, ...
     'soc0',s0,'noload_fix',true,'C_DE',3.20,'base_P_DE_rated',16,'w',[0.25 0.25 0.25 0.25],'DPSP_max',0.01);
cases = {};
for k = 1:3, cases(end+1,:) = {cfg{k,1}, mk(cfg{k,2}, cfg{k,3}, base, soc0(k))}; end %#ok<SAGROW>
% Demand profiles on the same day (8 kW DE design): hour-by-hour ratio of each alternative profile to the
% representative-day load, applied to this day's load and rescaled to its daily energy (x0.9 with curtailment).
E = sum(base.load);
vv = {'load_peaky', pk.load_peaky, 1.0; 'load_shift', sh.load_shift_v2, 1.0; 'load_shift_curtail', sc.load_shift_curtail, 0.9};
for k = 1:3
  r = vv{k,2}(:)' ./ Lb; l = base.load .* r; l = l * (vv{k,3}*E/sum(l));
  dd = base; dd.load = l; cases(end+1,:) = {vv{k,1}, mk(x8, 8, dd, soc0(3))}; %#ok<SAGROW>
end
R = [];
for k = 1:size(cases,1)
  [r, z] = run_dispatch(cases{k,2}); r.case = string(cases{k,1}); r.soc0 = cases{k,2}.soc0; R = [R; r]; %#ok<AGROW>
  [~,~,soc,~,o] = dispatch_obj(z, cases{k,2}); dd = cases{k,2};
  writetable(table((1:24)', o.load(:), o.P_RES(:), o.P_DE(:), o.P_b(:), o.P_dump(:), o.P_lost(:), soc(1:24)', soc(2:25)', dd.irr(:), dd.wind(:), ...
     'VariableNames', {'hour','load','P_RES','P_DE','P_b','P_dump','P_lost','soc','soc_end','irr','wind'}), fullfile(out, ['dispatch_d168_' cases{k,1} '.csv']));
  fprintf('%-20s feas=%d J=%.4f COE_n=%.4f Em_n=%.4f DPSP=%.4f Dump=%.4f REF=%.4f COE=%.3f USD/kWh Em=%.1f kg DE_h=%d fuel=%.1f L flag=%d (%.1fs)\n', ...
     cases{k,1}, r.feasible, r.J, r.COE_n, r.Em_n, r.DPSP, r.Dump, r.REF, r.COE, r.Em_kg, r.DE_hours, r.fuel_L, r.exitflag, r.time_s);
end
writetable(struct2table(R), fullfile(out,'dispatch_cases_d168.csv'));
