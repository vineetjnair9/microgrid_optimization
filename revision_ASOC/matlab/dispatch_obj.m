function [cost, Costs, soc, DPSP, out] = dispatch_obj(z, d)
% Day-ahead dispatch objective (from Dispatch_obj_LI_DE_v3.m), parameterised.
% z = [P_DE(1:24), P_b(1:24)] (kW; P_b > 0 discharge). d: design and day data (see run_dispatch).
P_DE = z(1:24); P_b_LI = z(25:48);
n_s = d.x(1); n_w = d.x(2); Eb_init = d.x(3);
irradiance = d.irr; temp = d.temp; wind_speed = d.wind; P_load = d.load(:)';
delta_t = 3600; P_s = zeros(1,24); P_w = zeros(1,24); P_RES = zeros(1,24); P_dump = zeros(1,24);
soc = zeros(1,25); DE_ON = zeros(1,24); P_lost = zeros(1,24);
DE_startup = 0; DE_shutdown = 0; C_fuel_DE = 0; fuel_L = 0;
eta_r = 0.154; T_r = 25; I_PV_NOCT = 0.8; T_c_NOCT = 45.7; T_a_NOCT = 20; beta_s = 0.0045; Ps_rated = 255;
Ps_rated_total = n_s * Ps_rated; IC_s = (Ps_rated_total/1000) * 1210; OM_s = (1/100)*(IC_s/365);
beta_w = 1/7; h_ref = 1; h_hub = 14.5; Pw_rated = 3.5; IC_w = n_w*Pw_rated*1500; OM_w = (3/100)*(IC_w/365);
v_c = 2.8; v_r = 11; v_f = 22;
A = (1/(v_c - v_r)^2) * (v_c*(v_c + v_r) - 4*v_c*v_r*((v_c + v_r)/(2*v_r))^3); % revision fix: (v_c-v_r)^2, not (v_c^2-v_r^2)
B = (1/(v_c - v_r)^2) * (4*(v_c + v_r)*((v_c + v_r)/(2*v_r))^3 - (3*v_c + v_r)); % revision fix: (3v_c+v_r)
C = (1/(v_c - v_r)^2) * (2 - 4*((v_c + v_r)/(2*v_r))^3); % curve now gives 0 at v_c and 1 at v_r (old one gave 0.5 and 1.48)
SOC_min_LI = 0.1; SOC_max_LI = 0.9; delta = 0.075; IC_LI = 300 * Eb_init; OM_LI = (1/100) * (IC_LI/365);
delta_hour = delta/30.5; eta_overall = 0.90; cycles_LI = 0; Eb_init = Eb_init*3.6e6; E_C = Eb_init;
P_DE_rated = d.P_DE_rated; P_DE_min = 0.3*P_DE_rated; IC_DE = (12500/16)*P_DE_rated;
Fixed_OM_DE = (2/100)*(IC_DE/365); Variable_OM_DE = 0.24; SUC_DE = 0.45; SDC_DE = 0.23; eta_inv = 0.9; eta_rec = eta_inv;
k = 0.649 + (4.063288937 + 18.85658039 + 0.007381439 + 1.502443664 + 3*1.338208931)/1000; % kg per kWh of DE output
Emissions_base = k * sum(P_load);
CO2 = 0;
for t = 1:24
  I = irradiance(t); T_a = temp(t);
  eta_PV = eta_r * (1 - 0.9 * beta_s * (I/I_PV_NOCT) * (T_c_NOCT - T_a_NOCT) - beta_s * (T_a - T_r));
  A_c = 120 * 78e-3 * 156e-3; P_s(t) = min(n_s * eta_PV * A_c * I, Ps_rated_total);
  v_hub = wind_speed(t) * (h_hub/h_ref)^beta_w;
  if (v_hub < v_c || v_hub > v_f), P_w(t) = 0;
  elseif (v_hub <= v_r), P_w(t) = n_w * Pw_rated * (A + B * v_hub + C * v_hub^2);
  else, P_w(t) = n_w * Pw_rated; end
  P_RES(t) = P_w(t)*eta_rec + P_s(t);
  if (t == 1), soc(t) = d.soc0; end
  if (t ~= 1 && soc(t) == SOC_max_LI && soc(t-1) < SOC_max_LI)
    cycles_LI = cycles_LI + 1; E_C = Eb_init*(1 - (cycles_LI*0.055e-3)); end
  if (P_DE(t) >= P_DE_min), DE_ON(t) = 1; end
  if (P_DE(t) < P_DE_min), P_DE(t) = 0; end
  if (t == 1 && DE_ON(1) == 1), DE_startup = DE_startup + SUC_DE; end
  if (t ~= 1 && DE_ON(t) == 1 && DE_ON(t-1) == 0), DE_startup = DE_startup + SUC_DE; end
  if (t ~= 1 && DE_ON(t) == 0 && DE_ON(t-1) == 1), DE_shutdown = DE_shutdown + SDC_DE; end
  if d.noload_fix, fuel = DE_ON(t)*0.08145*P_DE_rated + 0.246*P_DE(t);
  else, fuel = 0.08145*P_DE_rated + 0.246*P_DE(t); end
  fuel_L = fuel_L + fuel; C_fuel_DE = C_fuel_DE + d.C_DE * (fuel / 3.78541);
  CO2 = CO2 + 0.649 * P_DE(t);
  soc(t+1) = soc(t)*(1-delta_hour) - P_b_LI(t)*1000*delta_t*((eta_overall*(P_b_LI(t)<0) + (P_b_LI(t)>=0))/E_C); % round-trip efficiency on charge only (revision fix)
  P_dump(t) = max(0, P_RES(t) + P_b_LI(t) + P_DE(t)*eta_rec - P_load(t)/eta_inv);
  P_lost(t) = max(0, P_load(t) - (P_RES(t) + P_b_LI(t)) * eta_inv - P_DE(t));
end
Emissions_abs = k * sum(P_DE); Emissions = Emissions_abs/Emissions_base;
Var_OM_DE = Variable_OM_DE * sum(DE_ON);
C_wear = 300/(5475*(SOC_max_LI - SOC_min_LI)); % battery wear cost per kWh discharged = replacement cost / lifetime throughput (revision)
Cost = C_fuel_DE + Var_OM_DE + OM_s + OM_w + OM_LI + Fixed_OM_DE + DE_startup + DE_shutdown + C_wear*sum(max(P_b_LI,0));
E_gen = sum(P_DE * eta_rec + P_RES); COE = Cost/sum(P_load);
% Baseline: one DG of the reference rating supplies the whole day
Pb = d.base_P_DE_rated; IC_b = (12500/16)*Pb;
Cost_base = d.C_DE*((24*0.08145*Pb + 0.246*sum(P_load))/3.78541) + Variable_OM_DE*24 + (2/100)*(IC_b/365) + SUC_DE + SDC_DE;
COE_base = Cost_base/sum(P_load);
DPSP = sum(P_lost)/sum(P_load); Dump = sum(P_dump)/E_gen; REF = sum(P_RES)/E_gen;
Costs = [COE/COE_base Emissions Dump 1-REF];
cost = d.w * Costs';
out = struct('COE',COE,'COE_base',COE_base,'Cost',Cost,'Em_kg',Emissions_abs,'DE_hours',sum(DE_ON),'fuel_L',fuel_L, ...
             'P_DE',P_DE,'P_b',P_b_LI,'P_RES',P_RES,'P_dump',P_dump,'P_lost',P_lost,'load',P_load);
end
