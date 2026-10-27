function data = load_data()
root = fullfile(fileparts(mfilename('fullpath')), '..', '..');
a = load(fullfile(root,'irradiance.mat')); data.irradiance = a.irradiance;
a = load(fullfile(root,'temp.mat'));       data.temp = a.temp;
a = load(fullfile(root,'wind_speed.mat')); data.wind_speed = a.wind_speed;
a = load(fullfile(root,'Load.mat'));       data.Load = a.Load;
end
