fid = fopen(fullfile('..','results','run_info.txt'),'w');
[~,cpu] = system('sysctl -n machdep.cpu.brand_string'); [~,mem] = system('sysctl -n hw.memsize'); [~,os] = system('sw_vers -productVersion');
fprintf(fid,'matlab = %s\ncpu = %s\nmem_GB = %.0f\nmacos = %s\ncomputer = %s\n', version, strtrim(cpu), str2double(mem)/2^30, strtrim(os), computer);
fclose(fid); type(fullfile('..','results','run_info.txt'));
