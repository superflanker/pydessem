\
from pyomo.environ import SolverFactory, value
from .io_loader import load_case
from .model_core import build_model

def solve_case(path_yaml, solver_name="glpk"):
    data = load_case(path_yaml)
    m = build_model(data)

    opt = SolverFactory(solver_name)
    res = opt.solve(m, tee=False)

    out = {
        "objective": float(value(m.OBJ)),
        "P": {(g,t): float(value(m.P[g,t])) for g in m.G for t in m.T},
        "LS": {(b,t): float(value(m.LS[b,t])) for b in m.B for t in m.T},
        "F": {(ell,t): float(value(m.F[ell,t])) for ell in m.L for t in m.T},
        "V": {(r,t): float(value(m.V[r,t])) for r in m.R for t in m.T},
        "Q_t": {(r,t): float(value(m.Q_t[r,t])) for r in m.R for t in m.T},
        "Q_s": {(r,t): float(value(m.Q_s[r,t])) for r in m.R for t in m.T},
        "P_h": {(r,t): float(value(m.P_h[r,t])) for r in m.R for t in m.T},
        "R": {(g,t): float(value(m.Rg[g,t])) for g in m.GT for t in m.T},
    }
    return out, m, data
