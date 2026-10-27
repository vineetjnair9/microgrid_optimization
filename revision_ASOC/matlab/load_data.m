function data = load_data(shift_h)
% Station series (irradiance, temperature, wind) are shifted by shift_h hours so that they are in local
% time like the load profile. The comparison with NASA POWER (LST) gives a best alignment of +2 h (revision).
if nargin < 1, shift_h = 2; end
root = fullfile(fileparts(mfilename('fullpath')), '..', '..');
a = load(fullfile(root,'irradiance.mat')); data.irradiance = circshift(a.irradiance(:), shift_h);
a = load(fullfile(root,'temp.mat'));       data.temp = circshift(a.temp(:), shift_h);
a = load(fullfile(root,'wind_speed.mat')); data.wind_speed = circshift(a.wind_speed(:), shift_h);
a = load(fullfile(root,'Load.mat'));       data.Load = a.Load;
data.shift_h = shift_h;
end
