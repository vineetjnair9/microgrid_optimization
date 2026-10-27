function ds = mc_scenario(data, rs)
% One Monte Carlo year: day-block bootstrap within calendar month (weather), inter-annual multipliers
% on irradiance N(1,0.05^2) and wind N(1,0.10^2) truncated at +-3 sd, and multiplicative
% Ornstein-Uhlenbeck noise on hourly load (theta = 0.3 /h, stationary sd = 0.10). rs = RandStream.
dpm = [31 28 31 30 31 30 31 31 30 31 30 31]; mo = repelem(1:12, dpm); days = 1:365;
donor = zeros(1,365);
for d = 1:365, pool = days(mo == mo(d)); donor(d) = pool(randi(rs, numel(pool))); end
hidx = reshape((donor - 1)*24 + (1:24)', [], 1);
aI = min(max(1 + 0.05*randn(rs), 0.85), 1.15); aW = min(max(1 + 0.10*randn(rs), 0.70), 1.30);
ds.irradiance = min(data.irradiance(hidx) * aI, 1.2);
ds.temp = data.temp(hidx);
ds.wind_speed = data.wind_speed(hidx) * aW;
th = 0.3; sg = 0.10; e = zeros(8760,1); e(1) = sg*randn(rs);
z = randn(rs, 8760, 1);
for t = 1:8759, e(t+1) = e(t)*exp(-th) + sg*sqrt(1 - exp(-2*th))*z(t); end
L = reshape(data.Load', [], 1) .* (1 + e); L = max(L, 0);
ds.Load = reshape(L, 24, 365)';
ds.aI = aI; ds.aW = aW;
end
