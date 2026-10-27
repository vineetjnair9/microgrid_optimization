function [J, Costs, info] = obj_sizing(x, p, data)
% Parameterised sizing objective for the ASOC revision (derived from
% Objective_LI_DE_v10_1h_ind_VaryParams_output.m; logic unchanged unless a flag in p says otherwise).
% x    = [n_s, n_w, E_b_kWh] or [n_s, n_w, E_b_kWh, P_DE_rated_kW]
% p    = default_params() struct;  data = load_data() struct
% J    = p.w * Costs'  (weighted-sum scalarisation)
% Costs= [LCOE/LCOE_base, Em/Em_base, DPSP, Dump, 1-REF]
% info = absolute values and diagnostics
% Outputs individual objective values instead of weighted multiobjective
% Also used for pareto set/front calculation
% Returns normalized LCOE/emissions, DPSP, Dump and REF
% Updated Dec 2025

% Function performs optimal dispatch to output overall weighted cost function that needs to be minimized
% Variable inputs (that we minimize w.r.t) are: 
% no. of solar PV arrays, no. of wind turbines, initial battery capacity (in kWh)
n_s = x(1);
n_w = x(2);
Eb_init = x(3);
if isfield(p,'vars_kW') && p.vars_kW   % approach (ii): x(1), x(2) are total PV and WT ratings in kW
    n_s = x(1)/0.255; n_w = x(2)/3.5;
end

% Given fixed inputs: Wind speed, ambient external air temperature, solar radiation, electricity demand
% Have all of this data available over a whole year with hourly resolution

% LOAD ALL FIXED EXTERNAL/EXOGENOUS INPUT VARIABLES
irradiance = data.irradiance; % Solar insolation/irradiance (kW/m^2)
temp = data.temp; % Ambient air temperature (C)
wind_speed = data.wind_speed * p.wind_scale; % (m/s), already scaled x3.70 in the stored data
Load = data.Load; % Hourly power (kW) demand profiles (365x24)
% Hourly energy demand profile = power demand * time interval

% Initialize variables
P_s = zeros(1,8760); % (kW) - DC
P_w = zeros(1,8760); % (kW) - AC
P_DE = zeros(1,8760); % (kW) - AC
P_b_LI = zeros(1,8760); % (kW) - DC
P_RES = zeros(1,8760); % (kW) - DC
P_dump = zeros(1,8760); % Excess power (RES output) sent to dump loads/ground as DC (kW)
soc_LI = zeros(1,8761); % between 0 and 1
DE_ON = zeros(1,8760); % Boolean variable to keep track of whether DE is online/committed during that hour
% Lost load or Amount of demand response (curtailment/shifting) needed to balance MG
P_lost = zeros(1,8760); % (kW) - AC

% COSTS
i = p.i_nom; % Nominal interest/discount rate (https://tradingeconomics.com/kenya/interest-rate)
f = p.f_infl; % Inflation/escalation rate (https://tradingeconomics.com/kenya/inflation-cpi)
r = (i-f)/(1+f); % Real discount/interest rate
t_overall = 25; % Overall system lifetime (y) = lifetime of solar (longest surviving components)
CRF = (r*(1+r)^t_overall)/((1+r)^t_overall - 1); % Capital recovery factor

% Startup and shutdown costs of conventional generators
DE_startup = 0;
DE_shutdown = 0;

% Fuel costs
C_fuel_DE = 0; 
fuel_L_total = 0;

% Fixed system parameters
% SOLAR 
% PV panel specs from https://www.mitsubishielectricsolar.com/images/uploads/documents/specs/MLU_spec_sheet_250W_255W.pdf
% For 255 W system - Monocrystalline Si
eta_r = 0.154; % Manufacturer rated efficiency
T_r = 25; % Standard test conditions (reference cell temperature)
I_PV_NOCT = 0.8; % Hourly solar irradiance at NOCT - Normal/nominal operating cell temp (in kW/m^2) 
T_c_NOCT = 45.7; % PV cell temp at NOCT (Celsius)
T_a_NOCT = 20; % Ambient temp at NOCT (Celsius)
beta_s = 0.0045; % Temp coefficient of module/generator efficiency (of Pmax)
t_s = 25; % Lifetime of solar PV array (y)
Ps_rated = 255; % Rated max power of each module (W)
eta_pc = 1; % Power conditioning efficiency (= 1 or 100% since it's assumed that a perfect MPPT is used)
Ps_rated_total = n_s * Ps_rated; % Total solar PV installed capacity in microgrid (W)
IC_s = (Ps_rated_total/1000) * 1210; % Assuming installed PV costs of $1210/kW (source: IRENA costs report 2018, total installed costs)
% likely to be a slight underestimate since this is the global weighted
% average for larger utility scale projects
OM_s = (1/100)*IC_s; % Fixed annual O&M costs ($/y) - from Kaabeche et al. 2011a

% WIND
beta_w = 1/7; % Typical value of power law exponent for open land
% Use data from this spec sheet: https://farm-energy.extension.org/wp-content/uploads/2019/04/3.5kW_Spec_Sheet.pdf
h_ref = 1; % Installation height of TAHMO measurement stations (m) - wind speed measured approx. at sea level
h_hub = 14.5; % Tower height to hub/nacelle (m)
Pw_rated = 3.5; % Rated power of each WT (kW)
Pw_rated_total = n_w * Pw_rated;
IC_w = Pw_rated_total * 1500; % Global weighted average total installed costs of onshore wind ($/kW) - IRENA 2018
% This figure is likely to be an underestimate since it averages over both
% large and small-scale turbines, but the initial capital cost per kW of
% installed capacity likely to be higher for the small WT used in this
% project (lacks economies of scale)

OM_w = (3/100)*IC_w; % Fixed annual O&M costs ($/y)
t_w = 20; % Lifetime of wind turbine system (y)
v_c = 2.8; % Cut-in or start-up wind speed (m/s)
v_r = 11; % Rated wind speed (m/s)
v_f = 22; % Cut-out or failure/braking speed (m/s)
A = (1/(v_c - v_r)^2) * (v_c*(v_c + v_r) - 4*v_c*v_r*((v_c + v_r)/(2*v_r))^3); % revision fix: (v_c-v_r)^2, not (v_c^2-v_r^2)
B = (1/(v_c - v_r)^2) * (4*(v_c + v_r)*((v_c + v_r)/(2*v_r))^3 - (3*v_c + v_r)); % revision fix: (3v_c+v_r)
C = (1/(v_c - v_r)^2) * (2 - 4*((v_c + v_r)/(2*v_r))^3); % curve now gives 0 at v_c and 1 at v_r (old one gave 0.5 and 1.48)

% Li-ion battery system - from https://www.nrel.gov/docs/fy16osti/64987.pdf 
% Updated parameters for powerwall - https://www.tesla.com/en_GB/powerwall
SOC_min_LI = 0.1;
SOC_max_LI = 0.9; % DoD for LI = 80% (https://www.spiritenergy.co.uk/kb-batteries-understanding-batteries) 
delta = 0.075; % Self-discharge rate of battery (7.5%/month)
P_max_LI = 3.68; % Max continuous real power (kW), 5 kW peak
delta_hour = delta/30.5; % Hourly self-discharge rate (%/h)
eta_overall = 0.90; % Battery round trip coulombic efficiency (accounts for both charge & discharge) - from Hu et al. 2017
cycles_LI = 0; % Keeps track of cumulative no. of charge/discharge cycles so far
cycled = 0; % Keeps track of whether the BS has already been self-discharged in the current time step
% IC1_LI = 300; % Initial energy/capacity capital costs ($/kWh) - NREL
% IC2_LI = 120; % Initial power capital costs ($/kW) 
% IC_LI = IC1_LI * Eb_init + IC2_LI * P_max_LI; % Total initial capital costs for LI 
C_LI = p.C_LI;
IC_LI = C_LI * Eb_init;
Eb_kWh = Eb_init; E_dis_kWh = 0; % for throughput-based cycle counting (revision fix)
if p.scale_bs_power, P_max_LI = 0.272593 * Eb_init; end % power rating scales with installed energy capacity (revision)
OM_LI = (1/100) * IC_LI; % from Kaabeche et al. 2011a ($/y)
RC_LI = 0.9*IC_LI; % Replacement cost at end of service period/lifetime - assumed to be 90% of IC since new installation and permitting fees aren't incurred
Eb_init = Eb_init*3.6e6; % 1 W = 1 J/s
E_C = Eb_init; % Actual capacity is initially at rated maximum (J)
%t_LI = 15; % Average lifetime of Li-ion battery (y) - 5 years beyond Tesla powerwall warranty period
t_LI = p.t_LI_cycles; % cycles

% Diesel generator specs from Moshi et al. 2016
P_DE_rated = p.P_DE_rated; if numel(x) >= 4, P_DE_rated = x(4); end % Rated maximum power of diesel generator (kW) = approx. peak load * 1.5
P_DE_rated_hyb = P_DE_rated;
P_DE_min = p.P_DE_min_frac*P_DE_rated; % Lower limit on power (kW) or k_gen * P_rated (k_gen = 0.3) from Fathima et al. 
IC_DE = (12500/16)*P_DE_rated; % Initial capital cost ($) 
RC_DE = 0.88*IC_DE; % Replacement cost ($)
Fixed_OM_DE = (2/100)*IC_DE; % Fixed O&M costs ($/y)
Variable_OM_DE = 0.24; % Variable O&M costs ($/h of operation online)
SUC_DE = 0.45; % Start-up cost ($)
SDC_DE = 0.23; % Shut-down cost ($)
% t_DE = 14; % Average lifetime of diesel engine (y) - avg expected life expectancy (https://www.wpowerproducts.com/news/diesel-engine-life-expectancy/)
t_DE = 15000; % Lifetime (h), from Moshi et al. 2016
C_DE = p.C_DE; % Diesel price (in $/US gal)

% Bidirectional converter between AC and DC buses (can act as either rectifier or inverter)
eta_inv = 0.9; % Inverter efficiency (Ogunjuyigbe et al. 2016)
eta_rec = eta_inv; % Both rectifier and inverter assumed to have same parameters (Moshi et al. 2016)
t_inv = 20; % Lifetime of converter (y) - Moshi et al. 2016
P_inv_rated = 12.52; % Maximum rated power of inverter (kW)
IC_inv = 2800; % ($)
% Assume converter has zero maintenance costs

% Start with delta_t = 1 h and then maybe discretize over smaller time intervals
delta_t = 3600; % Calculation period (s) = 1 hour

hour = 0; % Keeps track of the hour in the day

% Normalize emissions wrt a base case where the DE is continuously run for the whole year to meet all the load
CO2 = 0.649 * sum(sum(Load));
CO = 4.063288937 * sum(sum(Load));
NOx = 18.85658039 * sum(sum(Load));
SO2 = 0.007381439 * sum(sum(Load));
VOC = 1.502443664 * sum(sum(Load));
PM = 1.338208931 * sum(sum(Load));
PM10 = 1.338208931 * sum(sum(Load));
PM25 = 1.338208931 * sum(sum(Load));
Emissions_base = CO2 + (CO + NOx + SO2 + VOC + PM + PM10 + PM25)/1000; % (kg)

CO2 = 0;

for t = 1:1:8760 % Simulate over one year with a time-step of 1 h
    
    Excess_demand = 0;
    
    % SOLAR
    I = irradiance(t); % Hourly solar irradiance (kW/m^2)
    T_a = temp(t);
    eta_PV = eta_r * (1 - 0.9 * beta_s * (I/I_PV_NOCT) * (T_c_NOCT - T_a_NOCT) - beta_s * (T_a - T_r)); % Tazvinga et al. 2013
    % Alternative model - Kaabeche et al. 2011b
    % T_c = T_a + ((T_c_NOCT - 20)/0.8)*I; % Cell temp (C)
    % eta_PV = eta_r * eta_pc * (1 - beta_s*(T_c - T_r));
    A_c = 120 * 78e-3 * 156e-3; % Surface area of 1 panel rated at 255 W (m^2)
    P_s(t) = n_s * eta_PV * A_c * I; % Solar power output (kW) - DC
    
    if (P_s(t) > Ps_rated_total)
        P_s(t) = Ps_rated_total;
    end
    
    % WIND
    v_ref = wind_speed(t);
    v_hub = v_ref * (h_hub/h_ref)^beta_w; % Wind speed at hub calculated from measured speed at reference anemometer height
    
    if (v_hub < v_c || v_hub > v_f)
        P_w(t) = 0;
    elseif (v_c <= v_hub && v_hub <= v_r)
        P_w(t) = n_w * Pw_rated * (A + B * v_hub + C * v_hub^2); % Source?
        % Alternative formula - Borhanazad et al. 2014
        % Pw = ((v_hub^3)*P_rated - P_rated*v_cutin^3)/(v_rated^3 - v_cutin^3);
        % Also include commonly known formula using Cp and swept area? 
        % But need to know variation of Cp with TSR for my specific WT model
       
    else
        P_w(t) = n_w * Pw_rated; % Wind power output (kW) - AC
    end
    
    % Rectify AC power from WT to DC
    P_RES(t) = P_w(t)*eta_rec + P_s(t); % Total renewable power output available at DC bus (kW)
    
    % BATTERY
    % Assume battery starts out fully charged (at max safe SOC)
    if (t == 1)
        soc_LI(t) = 0.9;
    end
    
    if (soc_LI(t) > SOC_max_LI)
        soc_LI(t) = SOC_max_LI;
    end
    
    if (soc_LI(t) < SOC_min_LI)
        soc_LI(t) = SOC_min_LI;
    end
    
    cycles_LI = E_dis_kWh / max((SOC_max_LI - SOC_min_LI) * Eb_kWh, eps); % equivalent full cycles so far (revision fix)
    
    E_C = Eb_init*(1 - (cycles_LI*0.055e-3)); % Capacity fading with cycling - https://www.nrel.gov/docs/fy16osti/64987.pdf
      
    day_number = ceil(t/24);
    if (hour >= 24)
        hour = 0;
    end
    hour = hour + 1;
    P_load = Load(day_number,hour); % (kW) - AC
       
    soc_LI(t+1) = soc_LI(t)*(1-delta_hour); % carry SOC forward when the battery is idle (revision fix)
    if (P_RES(t) == P_load/eta_inv) % Since RES power needs to inverted to meet AC load
        continue
    elseif (P_RES(t) > P_load/eta_inv) % Excess supply/generation
        if (soc_LI(t) >= SOC_max_LI) % Battery can't be charged further
            P_dump(t) = P_RES(t) - P_load/eta_inv; % Send excess power to dump loads/ground - DC
        else % Charge battery system
            if (P_RES(t) - P_load/eta_inv <= P_max_LI) 
                P_b_LI(t) = -(P_RES(t) - P_load/eta_inv); % (kW)
                soc_LI(t+1) = soc_LI(t)*(1-delta_hour) - P_b_LI(t)*1000*delta_t*(eta_overall/E_C);
                cycled = 1;
            else
                P_b_LI(t) = -P_max_LI;
                soc_LI(t+1) = soc_LI(t)*(1-delta_hour) - P_b_LI(t)*1000*delta_t*(eta_overall/E_C);
                P_dump(t) = P_RES(t) - P_load/eta_inv - P_max_LI;
                cycled = 1;
            end
        end
    else % Insufficient supply/generation
        Excess_demand = P_load/eta_inv - P_RES(t); % DC
        if (soc_LI(t) > SOC_min_LI) % Discharge battery
            if (Excess_demand <= P_max_LI)
                P_b_LI(t) = Excess_demand;
                soc_LI(t+1) = soc_LI(t)*(1-delta_hour) - P_b_LI(t)*1000*delta_t*(eta_overall/E_C);
                Excess_demand = 0; % All load has been met/satisfied
                cycled = 1;
            else
                P_b_LI(t) = P_max_LI;
                soc_LI(t+1) = soc_LI(t)*(1-delta_hour) - P_b_LI(t)*1000*delta_t*(eta_overall/E_C);
                Excess_demand = Excess_demand - P_max_LI;
                cycled = 1;
            end
        end
        if (Excess_demand > 0) % Need to use backup DE to meet excess load (revision fix: also after battery discharge at its power limit)
            DE_ON(t) = 1; % Turn DE on
            % Power produced by DE is already AC - so can directly meet load
            Excess_demand = Excess_demand * eta_inv; % AC
            if (Excess_demand <= P_DE_rated)
                if (Excess_demand >= P_DE_min)
                    P_DE(t) = Excess_demand;
                    % No dumped load
                else
                    P_DE(t) = P_DE_min;
                    P_dump(t) = (P_DE_min - Excess_demand) * eta_rec; % (kW) - DC
                    % If we allow excess generator output to charge battery
                    % DE output must 1st be rectified to DC before charging battery
                    if (p.de_charge && soc_LI(t) < SOC_max_LI)
                        if (P_dump(t) <= P_max_LI)
                            if (cycled == 0) % Battery hasn't been cycled/operated yet before in this time step
                                soc_LI(t+1) = soc_LI(t)*(1-delta_hour) + P_dump(t)*1000*delta_t*(eta_overall/E_C); 
                            else % Battery has already been cycled so don't include self-discharge again
                                soc_LI(t+1) = soc_LI(t+1) + P_dump(t)*1000*delta_t*(eta_overall/E_C);
                            end
                            P_dump(t) = 0;
                        else
                            if (cycled == 0) % Battery hasn't been cycled/operated yet before in this time step
                                soc_LI(t+1) = soc_LI(t)*(1-delta_hour) + P_max_LI*1000*delta_t*(eta_overall/E_C); 
                            else % Battery has already been cycled so don't include self-discharge again
                                soc_LI(t+1) = soc_LI(t+1) + P_max_LI*1000*delta_t*(eta_overall/E_C);
                            end                           
                            P_dump(t) = P_dump(t) - P_max_LI;
                        end
                    end
                end
            else
                P_DE(t) = P_DE_rated;
                P_lost(t) = Excess_demand - P_DE_rated;
            end
                        
            if (t ~= 1 && DE_ON(t-1) == 0) % i.e. DE was offline in the last/most recent time step
                DE_startup = DE_startup + SUC_DE;
                % Ramp_actual = (Excess_Demand - P_DE(t-1))/60 % actual ramp rate (W/min)
            end
        else
            DE_ON(t) = 0; % Turn DE off
            if (t ~= 1 && DE_ON(t-1) == 1) % i.e. DE was online in the last/most recent time step
                DE_shutdown = DE_shutdown + SDC_DE;
            end
        end
    end
    
    % Also need to account for (varying) DE efficiency while calculating its fuel consumption!    
    if p.noload_fix
        fuel_DE = DE_ON(t) * 0.08145 * P_DE_rated + 0.246 * P_DE(t); % no-load fuel only when committed
    else
        fuel_DE = 0.08145 * P_DE_rated + 0.246 * P_DE(t); % original: fuel consumption (L/h) where P is in kW - Kaabeche and Ibtiouen 2014
    end
    fuel_L_total = fuel_L_total + fuel_DE;
    C_fuel_DE = C_fuel_DE + C_DE * (fuel_DE / 3.78541); % Diesel fuel cost assuming a price of $3.20/US liquid gallon (value for east Africa from NREL ReOpt)
    % Alternatively, can model assume fuel consumption cost to be quadratic function of DE power output (Parisio et al. 2014 and others)
    % But need to find right coefficients by data fitting
    
    % CO2 = CO2 + 3.5 * fuel_DE; % Total CO2 emissions (kg) using emission factor of 3.5 kg/L of diesel - source?
    CO2 = CO2 + 0.649 * P_DE(t); % Using emission coefficient of 0.649 kg/kWh - Wu et al. 2016
    E_dis_kWh = E_dis_kWh + max(P_b_LI(t), 0); % discharge throughput (kWh, DC)
    cycled = 0; % Reset
end

if (DE_ON(1) == 1)
    DE_startup = DE_startup + SUC_DE;
end

% Upon completion of for loop i.e. after iterating through all hours of the year, C_fuel_DE now gives the total fuel cost over the 1st year of MG operation
% It is assumed that on average, the annual fuel cost remains constant for all subsequent years of the system's lifetime
Var_OM_DE = Variable_OM_DE * sum(DE_ON);

% Total initial capital/installed cost
IC = IC_s + IC_w + IC_LI + IC_DE + IC_inv;
% Total annual recurring costs each year
C_rec = OM_s + OM_w + OM_LI + Fixed_OM_DE + Var_OM_DE + C_fuel_DE + DE_startup + DE_shutdown;

% Present worth of recurring costs 
PW_rec = C_rec * (((1+f)/(1+i))*(((1+f)/(1+i))^t_overall - 1))/(((1+f)/(1+i)) - 1);

% Battery replaced every 15 years
% i_adj_LI = (((1+i)^t_LI)/(1+f)^(t_LI - 1)) - 1; % Adjusted nominal interest rate
% PW_LI_rep = RC_LI * (((1+f)/(1+i_adj_LI))*(((1+f)/(1+i_adj_LI))^t_overall - 1))/(((1+f)/(1+i_adj_LI)) - 1);

% Alternatively, determine frequency of BS replacement based on actual no. of cycles
if p.replace_by_cycles
    t_LI_rep = (t_LI/cycles_LI);
else
    t_LI_rep = p.t_LI_years; % fixed-interval replacement (strategies 1, 2)
end
i_adj_LI = (((1+i)^t_LI_rep)/(1+f)^(t_LI_rep - 1)) - 1; % Adjusted nominal interest rate
PW_LI_rep = RC_LI * (((1+f)/(1+i_adj_LI))*(((1+f)/(1+i_adj_LI))^t_overall - 1))/(((1+f)/(1+i_adj_LI)) - 1);
if ~isfinite(PW_LI_rep) || t_LI_rep >= t_overall, PW_LI_rep = 0; end   % no replacement within the project life (revision fix)
if ~isfinite(PW_LI_rep) || (p.replace_by_cycles && cycles_LI == 0), PW_LI_rep = 0; end   % no cycling -> no replacement within the horizon

% % DE replaced every 14 years
% i_adj_DE = (((1+i)^t_DE)/(1+f)^(t_DE - 1)) - 1; % Adjusted nominal interest rate
% PW_DE_rep = RC_DE * (((1+f)/(1+i_adj_DE))*(((1+f)/(1+i_adj_DE))^t_overall - 1))/(((1+f)/(1+i_adj_DE)) - 1);

% Alternatively, determine frequency of DE replacement based on actual no. of operating hours per year
t_DE_rep = (t_DE/sum(DE_ON)); % No. of years after which DE needs to be replaced
i_adj_DE = (((1+i)^t_DE_rep)/(1+f)^(t_DE_rep - 1)) - 1; % Adjusted nominal interest rate
PW_DE_rep = RC_DE * (((1+f)/(1+i_adj_DE))*(((1+f)/(1+i_adj_DE))^t_overall - 1))/(((1+f)/(1+i_adj_DE)) - 1);
if ~isfinite(PW_DE_rep) || t_DE_rep >= t_overall, PW_DE_rep = 0; end   % no replacement within the project life (revision fix)
if ~isfinite(PW_DE_rep) || sum(DE_ON) == 0, PW_DE_rep = 0; end   % DG never runs -> no replacement

% Present worth of non-recurring costs 
PW_nonrec = PW_LI_rep + PW_DE_rep;

TNPC = IC + PW_rec + PW_nonrec; % Total (lifecycle) net present cost of system ($)
TAC = TNPC * CRF; % Total annualized cost ($) 
TAC_hyb = TAC; C_fuel_hyb = C_fuel_DE;
LCOE = TAC/sum(sum(Load)); % Energy cost/Levelized cost of electricity ($/kWh) = total annual costs / total load served
% https://www.homerenergy.com/products/pro/docs/3.11/levelized_cost_of_energy.html

% Base case for LCOE same as that for emissions - entire MG is run solely on a single DE 
P_DE_rated = p.base_P_DE_rated; % fixed reference rating so normalisation does not move with x(4)
IC_DE = (12500/16)*P_DE_rated; RC_DE = 0.88*IC_DE; Fixed_OM_DE = (2/100)*IC_DE;
% Total annual recurring costs each year
Var_OM_DE = Variable_OM_DE * 8760;
fuel_DE = 8760 * 0.08145 * P_DE_rated + 0.246 * sum(sum(Load));
C_fuel_DE = C_DE * (fuel_DE / 3.78541);
DE_startup = SUC_DE;
DE_shutdown = SDC_DE;
C_rec = Fixed_OM_DE + Var_OM_DE + C_fuel_DE + DE_startup + DE_shutdown;

% Present worth of recurring costs 
PW_rec = C_rec * (((1+f)/(1+i))*(((1+f)/(1+i))^t_overall - 1))/(((1+f)/(1+i)) - 1);

t_DE_rep = (t_DE/8760); % No. of years after which DE needs to be replaced
i_adj_DE = (((1+i)^t_DE_rep)/(1+f)^(t_DE_rep - 1)) - 1; % Adjusted nominal interest rate
PW_DE_rep = RC_DE * (((1+f)/(1+i_adj_DE))*(((1+f)/(1+i_adj_DE))^t_overall - 1))/(((1+f)/(1+i_adj_DE)) - 1);
if ~isfinite(PW_DE_rep) || t_DE_rep >= t_overall, PW_DE_rep = 0; end   % no replacement within the project life (revision fix)

% Present worth of non-recurring costs 
PW_nonrec = PW_DE_rep;

IC =  IC_DE; % Don't need inverter since DE can directly supply AC loads
TNPC = IC + PW_rec + PW_nonrec; % Total (lifecycle) net present cost of system ($)
TAC = TNPC * CRF; % Total annualized cost ($) 
LCOE_base = TAC/sum(sum(Load)); % Energy cost/Levelized cost of electricity ($/kWh)
if p.fixed_base
    LCOE_base = p.LCOE_base_nom; Emissions_base = p.Em_base_nom;
end

% Emissions factors - EPA database (all in g)
CO = 4.063288937 * sum(P_DE);
NOx = 18.85658039 * sum(P_DE);
SO2 = 0.007381439 * sum(P_DE);
VOC = 1.502443664 * sum(P_DE);
PM = 1.338208931 * sum(P_DE);
PM10 = 1.338208931 * sum(P_DE);
PM25 = 1.338208931 * sum(P_DE);
Emissions = CO2 + (CO + NOx + SO2 + VOC + PM + PM10 + PM25)/1000; % Total (kg)

% Reliability measure - % of load that's not met
DPSP = sum(P_lost)/sum(sum(Load));

% Excess/dump energy as a fraction of total generation
E_gen = sum(P_DE * eta_rec + P_RES); % Total annual DC electrical energy output = P_gen * delta_t = P_gen (in kWh) since delta_t = 1 h
Dump = sum(P_dump)/E_gen; 
% Dump power ratio to total generation
% OR relative excess power generated (= dump) ratio to total load

% Renewable penetration
REF = sum(P_RES)/E_gen;

Costs = [LCOE/LCOE_base Emissions/Emissions_base DPSP Dump 1-REF];
J = p.w * Costs';
info = struct('LCOE_abs', LCOE, 'LCOE_base', LCOE_base, 'Em_abs', Emissions, 'Em_base', Emissions_base, ...
    'DE_hours', sum(DE_ON), 'BS_cycles', sum(cycles_LI), 'fuel_L', fuel_L_total, 'C_fuel', C_fuel_hyb, ...
    'TAC', TAC_hyb, 'E_dump_kWh', sum(P_dump), 'E_lost_kWh', sum(P_lost), 'E_RES_kWh', sum(P_RES), ...
    'E_WT_kWh', sum(P_w)*eta_rec, 'E_PV_kWh', sum(P_s), 'P_DE_rated', P_DE_rated_hyb, 'CRF', CRF);
if isfield(p,'return_series') && p.return_series
    info.series = table(reshape(Load',[],1), P_s(:), P_w(:), P_DE(:), P_b_LI(:), P_dump(:), P_lost(:), soc_LI(1:8760)', ...
        'VariableNames', {'load','P_PV','P_WT','P_DE','P_b','P_dump','P_lost','soc'});
end

end