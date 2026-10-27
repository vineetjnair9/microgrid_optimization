% Day-ahead dispatch tables (Secs. 7-8) on the corrected model.
root = fullfile('..','..'); out = fullfile('..','results','dispatch'); if ~isfolder(out), mkdir(out); end
data = load_data();
T = readtable(fullfile('..','results','rerun','main_tables.csv'),'TextType','string');
x16 = T{T.tag=="S3",{'ns','nw','Eb'}}; x8 = T{T.tag=="DG8kW",{'ns','nw','Eb'}};
L = load(fullfile(root,'Load_day.mat')); base = struct('irr',data.irradiance(1:24),'temp',data.temp(1:24),'wind',data.wind_speed(1:24),'load',L.Load_day);
lo = load(fullfile(root,'irradiance_low.mat')); lw = load(fullfile(root,'wind_speed_low.mat'));
pk = load(fullfile(root,'load_peaky.mat')); sh = load(fullfile(root,'load_shift_v2.mat')); sc = load(fullfile(root,'load_shift_curtail.mat'));
mk = @(x,P,day) struct('x',x,'P_DE_rated',P,'irr',day.irr,'temp',day.temp,'wind',day.wind,'load',day.load, ...
     'soc0',0.9,'noload_fix',true,'C_DE',3.20,'base_P_DE_rated',16,'w',[0.25 0.25 0.25 0.25],'DPSP_max',0.01);
cases = {};
cases(end+1,:) = {'i_16kW', mk(x16,16,base)};
cases(end+1,:) = {'ii_8kW_16kWsizing', mk(x16,8,base)};
cases(end+1,:) = {'iii_8kW_8kWsizing', mk(x8,8,base)};
d = base; d.irr = lo.irradiance_low; cases(end+1,:) = {'low_solar', mk(x8,8,d)};
d = base; d.wind = lw.wind_speed_low; cases(end+1,:) = {'low_wind', mk(x8,8,d)};
d = base; d.irr = lo.irradiance_low; d.wind = lw.wind_speed_low; cases(end+1,:) = {'low_solar_wind', mk(x8,8,d)};
d = base; d.load = pk.load_peaky; cases(end+1,:) = {'load_peaky', mk(x8,8,d)};
d = base; d.load = sh.load_shift_v2; cases(end+1,:) = {'load_shift', mk(x8,8,d)};
d = base; d.load = sc.load_shift_curtail; cases(end+1,:) = {'load_shift_curtail', mk(x8,8,d)};
R = [];
for k = 1:size(cases,1)
  [r, z] = run_dispatch(cases{k,2}); r.case = string(cases{k,1}); R = [R; r]; %#ok<AGROW>
  [~,~,soc,~,o] = dispatch_obj(z, cases{k,2}); dd = cases{k,2};
  writetable(table((1:24)', o.load(:), o.P_RES(:), o.P_DE(:), o.P_b(:), o.P_dump(:), o.P_lost(:), soc(1:24)', dd.irr(:), dd.wind(:), ...
     'VariableNames', {'hour','load','P_RES','P_DE','P_b','P_dump','P_lost','soc','irr','wind'}), fullfile(out, ['dispatch_' cases{k,1} '.csv']));
  fprintf('%-20s J=%.4f COE_n=%.4f Em_n=%.4f DPSP=%.4f Dump=%.4f REF=%.4f COE=%.3f USD/kWh flag=%d (%.1fs)\n', cases{k,1}, r.J, r.COE_n, r.Em_n, r.DPSP, r.Dump, r.REF, r.COE, r.exitflag, r.time_s);
end
writetable(struct2table(R), fullfile(out,'dispatch_cases.csv'));
