\
from pyomo.environ import (
    ConcreteModel, Set, Param, Var,
    NonNegativeReals, Reals, Binary,
    Objective, Constraint, ConstraintList,
    RangeSet, minimize, value, Piecewise
)

def build_model(d: dict):
    m = ConcreteModel()

    # ----- Sets -----
    T = int(d["meta"]["horizon_hours"])
    m.T = RangeSet(1, T)
    m.B = Set(initialize=d["sets"]["B"])
    m.G = Set(initialize=d["sets"]["G"])
    m.GH = Set(within=m.G, initialize=d["sets"]["GH"])
    m.GT = Set(within=m.G, initialize=d["sets"]["GT"])
    m.R = Set(initialize=d["sets"]["R"])
    m.L = Set(initialize=[ell["name"] for ell in d["sets"]["L"]])

    # Maps
    gen_bus = d["map"]["gen_bus"]
    res_of_gen = d["map"]["res_of_gen"]
    line_i = {ell["name"]: ell["i"] for ell in d["sets"]["L"]}
    line_j = {ell["name"]: ell["j"] for ell in d["sets"]["L"]}
    line_data = d["map"]["line_data"]

    # ----- Params -----
    m.ref_bus = d["params"]["ref_bus"]

    m.D = Param(m.B, m.T, initialize=lambda m,b,t: d["params"]["demand"][b][t-1])
    m.Gmin = Param(m.G, initialize=d["params"]["g_min"])
    m.Gmax = Param(m.G, initialize=d["params"]["g_max"])
    m.Rup  = Param(m.G, initialize=d["params"]["ramp_up"])
    m.Rdn  = Param(m.G, initialize=d["params"]["ramp_dn"])

    # Custos variáveis térmicos ($/MWh)
    m.cT = Param(m.GT, initialize=d["params"]["therm_cost"])

    # Linhas
    m.Bline = Param(m.L, initialize={k: line_data[k]["b"] for k in line_data})
    m.Fmax  = Param(m.L, initialize={k: line_data[k]["fmax"] for k in line_data})

    # Hidráulicos por reservatório
    m.Vmin = Param(m.R, initialize=d["params"]["vol_min"])
    m.Vmax = Param(m.R, initialize=d["params"]["vol_max"])
    m.V0   = Param(m.R, initialize=d["params"]["vol0"])
    m.Inflow = Param(m.R, m.T, initialize=lambda m,r,t: d["params"]["inflow"][r][t-1])
    m.Qmin = Param(m.R, initialize=d["params"]["q_min"])
    m.Qmax = Param(m.R, initialize=d["params"]["q_max"])

    # Penalidades
    m.pen_ls = Param(initialize=d["params"]["penalties"]["load_shed"])
    m.pen_sp = Param(initialize=d["params"]["penalties"]["spill"])

    # UC
    uc = d["params"]["uc"]
    m.c0   = Param(m.GT, initialize=uc.get("no_load_cost", {}), default=0.0)
    m.cSU  = Param(m.GT, initialize=uc.get("startup_cost", {}), default=0.0)
    m.cSD  = Param(m.GT, initialize=uc.get("shutdown_cost", {}), default=0.0)
    m.MUT  = Param(m.GT, initialize=uc.get("min_up_time", {}), default=1)
    m.MDT  = Param(m.GT, initialize=uc.get("min_down_time", {}), default=1)
    m.u0   = Param(m.GT, initialize=uc.get("u0", {}), default=0)
    m.InitStatus = Param(m.GT, initialize=uc.get("init_status", {}), default=0)
    m.SUcap = Param(m.GT, initialize=uc.get("startup_ramp", {}), default=0.0)
    m.SDcap = Param(m.GT, initialize=uc.get("shutdown_ramp", {}), default=0.0)

    # Reservas (agregado no tempo, sem zonas)
    res = d["params"].get("reserves", {})
    req = res.get("requirement", [0]*T)
    m.ResReq = Param(m.T, initialize={t: req[t-1] for t in range(1, T+1)})
    m.cR = Param(m.GT, initialize=res.get("cost", {}), default=0.0)

    # ----- Variáveis -----
    m.P = Var(m.G, m.T, within=NonNegativeReals)             # geração
    m.Theta = Var(m.B, m.T, within=Reals)                    # ângulo
    m.F = Var(m.L, m.T, within=Reals)                        # fluxo na linha
    m.LS = Var(m.B, m.T, within=NonNegativeReals)            # déficit

    # Hidráulicas
    m.V = Var(m.R, m.T, within=NonNegativeReals)             # volume
    m.Q_t = Var(m.R, m.T, within=NonNegativeReals)           # vazão turbinada
    m.Q_s = Var(m.R, m.T, within=NonNegativeReals)           # vertedouro
    m.P_h = Var(m.R, m.T, within=NonNegativeReals)           # potência hidráulica agregada (PWL)

    # UC Térmico
    m.u = Var(m.GT, m.T, within=Binary)                      # ligada?
    m.y = Var(m.GT, m.T, within=Binary)                      # partida
    m.z = Var(m.GT, m.T, within=Binary)                      # parada

    # Reservas (por gerador térmico)
    m.Rg = Var(m.GT, m.T, within=NonNegativeReals)

    # ----- Objetivo -----
    def obj_rule(m):
        therm_var = sum(m.cT[g]*m.P[g,t] for g in m.GT for t in m.T)
        therm_uc  = sum(m.c0[g]*m.u[g,t] + m.cSU[g]*m.y[g,t] + m.cSD[g]*m.z[g,t]
                        for g in m.GT for t in m.T)
        shed  = sum(m.pen_ls*m.LS[b,t] for b in m.B for t in m.T)
        spill = sum(m.pen_sp*m.Q_s[r,t] for r in m.R for t in m.T)
        r_cost = sum(m.cR[g]*m.Rg[g,t] for g in m.GT for t in m.T)
        return therm_var + therm_uc + shed + spill + r_cost
    m.OBJ = Objective(rule=obj_rule, sense=minimize)

    # ----- Restrições -----
    # (1) Limites de geração
    m.GLoH = Constraint(m.GH, m.T, rule=lambda m,g,t: m.P[g,t] >= m.Gmin[g])
    m.GHiH = Constraint(m.GH, m.T, rule=lambda m,g,t: m.P[g,t] <= m.Gmax[g])
    m.GLoT = Constraint(m.GT, m.T, rule=lambda m,g,t: m.P[g,t] >= m.Gmin[g]*m.u[g,t])
    m.GHiT = Constraint(m.GT, m.T, rule=lambda m,g,t: m.P[g,t] <= m.Gmax[g]*m.u[g,t])

    # (2) Rampas
    def ramp_up_h(m, g, t):
        if t == 1: return Constraint.Skip
        return m.P[g,t] - m.P[g,t-1] <= m.Rup[g]
    def ramp_dn_h(m, g, t):
        if t == 1: return Constraint.Skip
        return m.P[g,t-1] - m.P[g,t] <= m.Rdn[g]
    m.RampUpH = Constraint(m.GH, m.T, rule=ramp_up_h)
    m.RampDnH = Constraint(m.GH, m.T, rule=ramp_dn_h)

    def ramp_up_t(m, g, t):
        if t == 1: return Constraint.Skip
        return m.P[g,t] - m.P[g,t-1] <= m.Rup[g]*m.u[g,t-1] + m.SUcap[g]*m.y[g,t]
    def ramp_dn_t(m, g, t):
        if t == 1: return Constraint.Skip
        return m.P[g,t-1] - m.P[g,t] <= m.Rdn[g]*m.u[g,t] + m.SDcap[g]*m.z[g,t]
    m.RampUpT = Constraint(m.GT, m.T, rule=ramp_up_t)
    m.RampDnT = Constraint(m.GT, m.T, rule=ramp_dn_t)

    # (3) Lógica de compromisso
    def commit_logic(m, g, t):
        if t == 1:
            return m.u[g,1] - m.u0[g] == m.y[g,1] - m.z[g,1]
        return m.u[g,t] - m.u[g,t-1] == m.y[g,t] - m.z[g,t]
    m.CommitLogic = Constraint(m.GT, m.T, rule=commit_logic)

    # (4) Fluxo DC
    def dc_flow(m, ell, t):
        i, j = line_i[ell], line_j[ell]
        return m.F[ell,t] == m.Bline[ell]*(m.Theta[i,t] - m.Theta[j,t])
    m.DCFlow = Constraint(m.L, m.T, rule=dc_flow)

    m.LineHi = Constraint(m.L, m.T, rule=lambda m,ell,t:  m.F[ell,t] <=  m.Fmax[ell])
    m.LineLo = Constraint(m.L, m.T, rule=lambda m,ell,t: -m.F[ell,t] <=  m.Fmax[ell])

    # (5) Referência angular
    m.Ref = Constraint(m.T, rule=lambda m,t: m.Theta[m.ref_bus, t] == 0.0)

    # (6) Balanço nodal
    gens_at_bus = {b: [g for g in d["sets"]["G"] if gen_bus[g]==b] for b in d["sets"]["B"]}
    def nodal_balance(m, b, t):
        gen = sum(m.P[g,t] for g in gens_at_bus[b])
        infl = sum(m.F[ell,t] for ell in m.L if line_j[ell]==b)
        out  = sum(m.F[ell,t] for ell in m.L if line_i[ell]==b)
        return gen + infl - out + m.LS[b,t] == m.D[b,t]
    m.Nodal = Constraint(m.B, m.T, rule=nodal_balance)

    # (7) Hidráulica: continuidade, limites de vazão e PWL
    m.VLo = Constraint(m.R, m.T, rule=lambda m,r,t: m.V[r,t] >= m.Vmin[r])
    m.VHi = Constraint(m.R, m.T, rule=lambda m,r,t: m.V[r,t] <= m.Vmax[r])

    def cont_rule(m, r, t):
        if t == 1:
            return m.V[r,t] == m.V0[r] + m.Inflow[r,t] - m.Q_t[r,t] - m.Q_s[r,t]
        return m.V[r,t] == m.V[r,t-1] + m.Inflow[r,t] - m.Q_t[r,t] - m.Q_s[r,t]
    m.Continuity = Constraint(m.R, m.T, rule=cont_rule)

    m.QLo = Constraint(m.R, m.T, rule=lambda m,r,t: m.Q_t[r,t] >= m.Qmin[r])
    m.QHi = Constraint(m.R, m.T, rule=lambda m,r,t: m.Q_t[r,t] <= m.Qmax[r])

    # PWL por reservatório
    m.PWL = ConstraintList()
    # Entrada: d["params"]["hydro_pwl"][r] = list of {"q":..,"p":..}
    for r in d["sets"]["R"]:
        pts = d["params"]["hydro_pwl"][r]
        qpts = [pt["q"] for pt in pts]
        ppts = [pt["p"] for pt in pts]
        # Closure para interp linear
        def f_rule(q, qpts=qpts, ppts=ppts):
            # interp linear simples
            import bisect
            if q <= qpts[0]: return ppts[0]
            if q >= qpts[-1]: return ppts[-1]
            k = bisect.bisect_left(qpts, q)
            q0,q1 = qpts[k-1], qpts[k]
            p0,p1 = ppts[k-1], ppts[k]
            lam = (q - q0) / (q1 - q0) if q1!=q0 else 0.0
            return p0 + lam*(p1 - p0)
        for t in range(1, T+1):
            Piecewise(
                m,
                m.P_h[r,t], m.Q_t[r,t],
                pw_pts=qpts,
                f_rule=f_rule,
                pw_constr_type="EQ",
                pw_repn="CC"
            )
        # Vincula soma das GUs hidro do reservatório à potência PWL
        for t in range(1, T+1):
            m.PWL.add(sum(m.P[g,t] for g in m.GH if res_of_gen[g]==r) == m.P_h[r,t])

    # (8) Min up / min down
    m.MinUp = ConstraintList()
    m.MinDn = ConstraintList()
    for g in d["sets"]["GT"]:
        MUT = int(value(m.MUT[g]))
        MDT = int(value(m.MDT[g]))
        for t in range(1, T+1):
            if MUT > 1:
                t_end = min(T, t + MUT - 1)
                m.MinUp.add(sum(m.u[g,tt] for tt in range(t, t_end+1)) >= (t_end - t + 1) * m.y[g,t])
            if MDT > 1:
                t_end = min(T, t + MDT - 1)
                m.MinDn.add(sum(1 - m.u[g,tt] for tt in range(t, t_end+1)) >= (t_end - t + 1) * m.z[g,t])

    # (9) Travamentos iniciais por InitStatus
    m.InitLocks = ConstraintList()
    for g in d["sets"]["GT"]:
        s = int(value(m.InitStatus[g]))  # >0: horas ligada; <0: desligada
        if s > 0:
            lock = max(0, int(value(m.MUT[g])) - s)
            for t in range(1, min(T, lock)+1):
                m.InitLocks.add(m.u[g,t] == 1)
        elif s < 0:
            lock = max(0, int(value(m.MDT[g])) - (-s))
            for t in range(1, min(T, lock)+1):
                m.InitLocks.add(m.u[g,t] == 0)

    # (10) Reservas: capacidade e requisito agregado no tempo
    # Capacidade: Rg <= Gmax*u - P (apenas térmicas)
    m.RCapT = Constraint(m.GT, m.T, rule=lambda m,g,t: m.Rg[g,t] <= m.Gmax[g]*m.u[g,t] - m.P[g,t])

    # Requisito por tempo: soma das reservas das térmicas >= requirement[t]
    m.RReq = Constraint(m.T, rule=lambda m,t: sum(m.Rg[g,t] for g in m.GT) >= m.ResReq[t])

    return m
