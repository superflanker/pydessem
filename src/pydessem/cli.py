\
import argparse, json
from .solve import solve_case

def main():
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
