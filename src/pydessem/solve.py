"""
PyDessem Solver
===============

Interface to Solve PyDessem Cases.

Summary
-------
This module integrates case loading and Pyomo model building with
a solver call. It provides a simple API to solve a case and return
structured results for post-processing.

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Contents
--------
- solve_case: load, build, solve, and return results.

Notes
-----
This module is part of the activities of the discipline
EELT7030 - Planejamento da Operação Eletroenergética de Médio/Curto Prazo,
Federal University of Paraná (UFPR), Brazil.

Dependencies
------------
- pyomo.environ
- pydessem.io_loader
- pydessem.model_core
"""

from pyomo.environ import SolverFactory, value
from .io_loader import load_case
from .model_core import build_model

def solve_case(path_yaml, solver_name="glpk"):
    """
    Load, build, and solve a PyDessem case.

    Parameters
    ----------
    path_yaml : str
        Path to the YAML file describing the case.
    solver_name : str, optional
        Name of the solver to be used. Default is "glpk".

    Returns
    -------
    tuple
        (out, model, data)
        - out : dict
            Results including objective value and variable series
            (generation, flows, volumes, reserves, etc.).
        - model : pyomo.environ.ConcreteModel
            The solved Pyomo model object.
        - data : dict
            Original case data loaded from YAML.

    Notes
    -----
    - Requires the specified solver to be installed and accessible.
    - The output dictionary is designed for easy export to JSON.
    """
    
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
