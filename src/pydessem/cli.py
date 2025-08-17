"""
PyDessem CLI
============

PyDessem Command-Line Interface (CLI) - Didactic DESSEM-like Hydrothermal Scheduling

Summary
-------
This module implements the command-line interface for the PyDessem framework.
It allows solving didactic short-term hydrothermal scheduling problems with
unit commitment, piecewise-linear hydro production functions, and reserve
requirements, using Pyomo as the modeling environment.

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Contents
--------
- main function: entrypoint for command-line execution.
- Argument parsing (argparse) for YAML input, solver selection, and JSON output.
- Integration with `solve_case` from the core PyDessem API.

Notes
-----
This module is part of the activities of the discipline
EELT7030 - Planejamento da Operação Eletroenergética de Médio/Curto Prazo,
Federal University of Paraná (UFPR), Brazil.

Dependencies
------------
- argparse
- json
- pyomo
- pyyaml
- pydessem.solve

"""

import argparse, json
from .solve import solve_case

def main():
    """
    Executes the command-line interface to solve a didactic DESSEM-like
    problem using Pyomo.

    The user provides a YAML file describing the case
    (buses, generators, reservoirs, demands, etc.), and the function
    calls the specified solver to obtain the optimal dispatch.
    Results can be printed in a human-readable format or in JSON.

    Parameters
    ----------
    None
        The function does not take arguments directly; parameters are
        parsed from the command line using argparse.

    Other Parameters
    ----------------
    yaml : str
        Path to the YAML file containing the case data.
    --solver : str, optional
        Name of the solver to be used. Default is ``"glpk"``.
        Examples: "cbc", "gurobi", "cplex".
    --json : bool, optional
        If specified, prints the result in JSON format.
        Otherwise, prints a summarized output to the terminal.

    Returns
    -------
    None
        Does not return a value. The function prints the results of the
        solved problem (objective and dispatch) to the terminal.

    Notes
    -----
    - Requires the specified solver to be installed and accessible
    in the system PATH.
    - Uses the ``solve_case`` function defined in ``pydessem.solve``.
    - JSON output includes the objective value and variable series,
    such as generation per unit and time step.

    Examples
    --------
    Run from the command line:

    >>> pydessem-solve examples/case_tiny.yaml --solver glpk
    Objective: 1234.56
    Generation (P[g,t]) - first 10:
    G1 t=0: 20.00
    G2 t=0: 30.00

    Run with JSON output:

    >>> pydessem-solve examples/case_tiny.yaml --solver glpk --json
    {
    "objective": 1234.56,
    "P": {
        "('G1', 0)": 20.0,
        "('G2', 0)": 30.0,
        ...
    }
    }
    """

    p = argparse.ArgumentParser(description="Solve a didactic DESSEM-like problem with Pyomo.")
    p.add_argument("yaml", help="Caminho para o arquivo YAML do caso.")
    p.add_argument("--solver", default="glpk", help="Nome do solver (glpk, cbc, gurobi, cplex, ...)")
    p.add_argument("--json", action="store_true", help="Imprime resultado em JSON.")
    args = p.parse_args()

    out, m, data = solve_case(args.yaml, solver_name=args.solver)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print("Objetivo:", out["objective"])
        print("Geração (P[g,t]) - primeiros 10:")
        for i, ((g,t), v) in enumerate(out["P"].items()):
            if i >= 10: break
            print(f"  {g:>4s} t={t}: {v:.2f}")
