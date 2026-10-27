function job_daemon()
% Runs MATLAB job scripts dropped into revision_ASOC/jobs/ one at a time (alphabetical order).
% Each job's console output goes to revision_ASOC/logs/<job>.log and a status file <job>.status.
% Stop by creating an empty file revision_ASOC/jobs/STOP.
here = fileparts(mfilename('fullpath'));
addpath(here); addpath(fullfile(here,'..','..')); cd(here);
jobs = fullfile(here,'..','jobs'); done = fullfile(jobs,'done'); logs = fullfile(here,'..','logs');
if ~isfolder(done), mkdir(done); end
if ~isfolder(logs), mkdir(logs); end
fprintf('job_daemon started %s, watching %s\n', datestr(now), jobs);
hb = fullfile(logs,'daemon_heartbeat.txt');
while true
  fid = fopen(hb,'w'); fprintf(fid,'%s idle\n', datestr(now)); fclose(fid);
  if isfile(fullfile(jobs,'STOP')), delete(fullfile(jobs,'STOP')); fprintf('job_daemon stopped\n'); break; end
  d = dir(fullfile(jobs,'*.m'));
  if isempty(d), pause(10); continue; end
  [~,ix] = sort({d.name}); d = d(ix); f = d(1).name; [~,nm] = fileparts(f);
  rehash;
  logf = fullfile(logs,[nm '.log']); if isfile(logf), delete(logf); end
  fid = fopen(hb,'w'); fprintf(fid,'%s running %s\n', datestr(now), nm); fclose(fid);
  diary(logf); fprintf('=== %s start %s\n', nm, datestr(now)); t0 = tic;
  try
    run_job(fullfile(jobs,f)); status = 'OK';
  catch ME
    status = ['ERROR: ' getReport(ME,'extended','hyperlinks','off')];
  end
  fprintf('=== %s end %s (%.1f s) %s\n', nm, datestr(now), toc(t0), status); diary off;
  movefile(fullfile(jobs,f), fullfile(done,[datestr(now,'yyyymmdd_HHMMSS_') f]));
  fid = fopen(fullfile(logs,[nm '.status']),'w'); fprintf(fid,'%s\n',status); fclose(fid);
end
end

function run_job(path)
run(path);   % runs the script in this function's own workspace
end
