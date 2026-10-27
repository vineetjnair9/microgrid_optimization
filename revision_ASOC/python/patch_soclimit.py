import sys, re
for f in sys.argv[1:]:
    L = open(f).read().split('\n')
    X = 'LI' if any('soc_LI(t+1) = soc_LI(t)*(1-delta_hour); % carry SOC' in l for l in L) else 'LA'
    soc, pm, smax, smin = f'soc_{X}', f'P_max_{X}', f'SOC_max_{X}', f'SOC_min_{X}'
    def idx(pred, start=0):
        for i in range(start, len(L)):
            if pred(L[i]): return i
        raise SystemExit(f'{f}: anchor not found')
    i_carry = idx(lambda l: 'carry SOC forward' in l and l.strip().startswith(soc))
    ind = re.match(r'\s*', L[i_carry]).group(0)
    L.insert(i_carry + 1, f"{ind}s0_ = {soc}(t)*(1-delta_hour); P_lim_ch = min({pm}, max(0, {smax} - s0_)*E_C/(1000*delta_t*eta_overall)); P_lim_dis = min({pm}, max(0, s0_ - {smin})*E_C/(1000*delta_t*eta_overall)); % revision fix: battery cannot over-discharge or over-charge within an hour")
    i_ex = idx(lambda l: 'elseif (P_RES(t) > P_load/eta_inv)' in l, i_carry)
    i_def = idx(lambda l: 'Excess_demand = P_load/eta_inv - P_RES(t)' in l, i_ex)
    i_de = idx(lambda l: 'if (Excess_demand > 0)' in l, i_def)
    for i in range(i_ex, i_def): L[i] = L[i].replace(pm, 'P_lim_ch')
    for i in range(i_def, i_de): L[i] = L[i].replace(pm, 'P_lim_dis')
    i_dc = idx(lambda l: re.search(rf'if \((p\.de_charge && )?{soc}\(t\) < {smax}\)', l) is not None, i_de)
    i_end = idx(lambda l: f'P_dump(t) = P_dump(t) - {pm};' in l, i_dc)
    for i in range(i_dc + 1, i_end + 1): L[i] = L[i].replace(pm, 'P_lim_de')
    ind2 = re.match(r'\s*', L[i_dc]).group(0)
    L.insert(i_dc + 1, f"{ind2}    P_lim_de = min({pm}, max(0, {smax} - {soc}(t+1))*E_C/(1000*delta_t*eta_overall)); % headroom left this hour (revision fix)")
    open(f, 'w').write('\n'.join(L)); print('patched', f, X, 'lines', i_carry, i_ex, i_def, i_de, i_dc, i_end)
