# PyDessem: Didactic Hydrothermal Scheduling with Pyomo

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![CI](https://github.com/superflanker/pydessem/actions/workflows/ci.yml/badge.svg)](https://github.com/superflanker/pydessem/actions/workflows/ci.yml)
[![Docs](https://github.com/superflanker/pydessem/actions/workflows/docs.yml/badge.svg)](https://superflanker.github.io/pydessem/)

PyDessem is a Python package for **short-term hydrothermal scheduling** inspired by the **DESSEM model** (used in Brazil by ONS).  
It provides a **didactic, modular, and extensible** implementation using [Pyomo](http://www.pyomo.org/) for optimization.

---

## 🔍 Overview

This project models a simplified **hydrothermal system** with:
- **DC power flow constraints**
- **Hydro reservoirs with piecewise production functions**
- **Thermal unit commitment (UC)**
- **Ramping constraints**
- **Reserves and penalties (load shedding, spillage)**

The goal is to provide a **clean teaching tool** for courses such as *EELT7030 – Short/Medium-Term Power System Operation Planning*.

---

## 📦 Main Components

- `io_loader.py` – YAML/CSV input loader and validator.
- `model_core.py` – Pyomo model builder (hydro, thermal, UC, DC flow).
- `solve.py` – Solver wrapper and post-processing.
- `reporting.py` – Tables and plots for results.
- `cli.py` – Command-line interface (`pydessem-solve`).

---

## 🛠 Dependencies

PyDessem relies on the following Python libraries:

- [Pyomo](https://pypi.org/project/pyomo/)
- [PyYAML](https://pypi.org/project/PyYAML/)
- [Pandas](https://pypi.org/project/pandas/) (optional, reporting)
- [Matplotlib](https://pypi.org/project/matplotlib/) (optional, reporting)
- [GLPK](https://www.gnu.org/software/glpk/) or another MILP solver (CBC, Gurobi, CPLEX, ...)

---

## 📁 Project Structure

```
pydessem/
├── pydessem/
│   ├── __init__.py
│   ├── io_loader.py
│   ├── model_core.py
│   ├── solve.py
│   ├── reporting.py
│   └── cli.py
├── data/
│   ├── inputs/
│   │   └── case_tiny.yaml
│   └── outputs/
├── tests/
│   └── test_solver.py
├── LICENSE
├── README.md
└── pyproject.toml
```

---

## ▶️ Usage

Solve a case from the command line:

```bash
pydessem-solve data/inputs/case_tiny.yaml --solver glpk
```

Output (human-readable):

```
Objective: 1234.56
Generation (P[g,t]) - first 10:
   G1 t=0: 20.00
   G2 t=0: 30.00
```

Output (JSON):

```bash
pydessem-solve data/inputs/case_tiny.yaml --solver glpk --json
```

```json
{
  "objective": 1234.56,
  "P": {
    "('G1', 0)": 20.0,
    "('G2', 0)": 30.0,
    ...
  }
}
```

---

## 📄 References

This implementation is based on academic material from **UFPR (Federal University of Paraná)** and ONS:

- Clodomiro Unsihuay–Vila, *Introdução aos Sistemas de Energia Elétrica* (EELT7030, 2025)  
- Clodomiro Unsihuay–Vila, *O Custo Marginal de Operação em Sistemas com Predominância Termoelétrica* (EELT7030, 2025)  
- ONS, *DESSEM – Manual de Metodologia*, 2023  

---

## 📚 Documentation

Full API and usage documentation is built with **Sphinx** and available here:  
👉 [PyDessem Documentation](https://superflanker.github.io/pydessem/)

---

## 📚 How to Cite

If you use **PyDessem** in teaching or research, please cite:

```bibtex
@misc{adams2025pydessem,
  author    = {Augusto Mathias Adams},
  title     = {PyDessem: Didactic Hydrothermal Scheduling with Pyomo},
  year      = {2025},
  howpublished = {\url{https://github.com/superflanker/pydessem}}
}
```
