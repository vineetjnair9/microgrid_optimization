% Pareto approximations on the corrected model (Secs. 5.3-5.4).
data = load_data(); out = fullfile('..','results','rerun'); if ~isfolder(out), mkdir(out); end
% (a) 16 kW, five objectives, unit-count variables
p = default_params(); rng default;
o = optimoptions('paretosearch','ParetoSetSize',200,'Display','off');
fv = @(x) Fonly([round(x(1)) round(x(2)) x(3)],p,data,1:5);   % integer-coded unit counts
[x_p, fval] = paretosearch(fv, 3, [],[],[],[], [0 0 0], [50 20 150], [], o);
x_p(:,1:2) = round(x_p(:,1:2));
save(fullfile(out,'pareto_16kW_5obj.mat'),'x_p','fval'); writematrix([x_p fval], fullfile(out,'pareto_16kW_5obj.csv'));
fprintf('16 kW front: %d points\n', size(x_p,1));
% (b) 16 kW, five objectives, rated-power variables (gamultiobj, for the input-space figure)
q = p; q.vars_kW = true; rng default;
og = optimoptions('gamultiobj','ParetoFraction',0.5,'Display','off');
[x_g, f_g] = gamultiobj(@(x) Fonly(x,q,data,1:5), 3, [],[],[],[], [0 0 0], [25 25 200], [], og);
save(fullfile(out,'pareto_16kW_5obj_kW_gamultiobj.mat'),'x_g','f_g'); writematrix([x_g f_g], fullfile(out,'pareto_16kW_5obj_kW_gamultiobj.csv'));
% (c) 7 kW, four objectives (LCOE, Em, DPSP, Dump), rated-power variables
r = default_params(); r.P_DE_rated = 7; r.vars_kW = true; rng default;
[x7, f7] = paretosearch(@(x) Fonly(x,r,data,1:4), 3, [],[],[],[], [0 0 0], [25 25 200], [], o);
save(fullfile(out,'pareto_7kW_4obj.mat'),'x7','f7'); writematrix([x7 f7], fullfile(out,'pareto_7kW_4obj.csv'));
fprintf('7 kW front: %d points\n', size(x7,1));
% absolute LCOE for every front point (for figures)
A = zeros(size(x_p,1),3); for k=1:size(x_p,1), [~,~,in]=obj_sizing(x_p(k,:),p,data); A(k,:)=[in.LCOE_abs in.Em_abs in.DE_hours]; end
writematrix(A, fullfile(out,'pareto_16kW_5obj_abs.csv'));
B = zeros(size(x7,1),3); for k=1:size(x7,1), [~,~,in]=obj_sizing(x7(k,:),r,data); B(k,:)=[in.LCOE_abs in.Em_abs in.DE_hours]; end
writematrix(B, fullfile(out,'pareto_7kW_4obj_abs.csv'));

function F = Fonly(x,p,data,idx)
[~,Fa] = obj_sizing(x,p,data); F = Fa(idx);
end
