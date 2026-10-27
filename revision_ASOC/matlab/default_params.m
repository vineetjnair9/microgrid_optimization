function p = default_params()
% Defaults reproduce the paper's chosen configuration (strategy 3, 16 kW DE, equal weights).
p.P_DE_rated = 16;        % kW (overridden by x(4))
p.P_DE_min_frac = 0.3;    % minimum stable output fraction
p.C_DE = 3.20;            % USD/US gal
p.i_nom = 0.09;           % nominal interest rate
p.f_infl = 0.057;         % inflation rate
p.C_LI = 300;             % USD/kWh
p.t_LI_cycles = 5475;     % replacement after N cycles
p.replace_by_cycles = true;
p.t_LI_years = 15;
p.de_charge = true;       % DE minimum-load surplus may charge the battery
p.w = [0.2 0.2 0.2 0.2 0.2];
p.wind_scale = 1.0;       % multiplies stored wind data (already x3.70)
p.noload_fix = true;      % audit A16: corrected (D8 = fix, 19 Oct 2026)
p.base_P_DE_rated = 16;   % reference DG for LCOE_base/Em_base
p.fixed_base = false;
p.scale_bs_power = true;  % LI power rating 3.68 kW per 13.5 kWh unit (revision)
p.C_WT = 1500;            % installed WT cost (USD/kW), IRENA 2018
p.LCOE_base_nom = NaN; p.Em_base_nom = NaN;
end
