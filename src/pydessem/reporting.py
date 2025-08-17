"""
PyDessem Reporting
==================

Post-processing utilities for PyDessem results.

Summary
-------
This module provides basic functions for summarizing
and presenting results from PyDessem simulations.

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Contents
--------
- summarize_dispatch: group generation by unit and time.

Notes
-----
This module is part of the activities of the discipline
EELT7030 - Planejamento da Operação Eletroenergética de Médio/Curto Prazo,
Federal University of Paraná (UFPR), Brazil.

Dependencies
------------
- collections
"""

from collections import defaultdict

def summarize_dispatch(out):
    """
    Summarize generation dispatch by unit and time.

    Parameters
    ----------
    out : dict
        Results dictionary returned by `solve_case`.

    Returns
    -------
    dict
        A dictionary mapping each generator to a sorted list
        of (time, generation) tuples.

    Examples
    --------
    >>> from pydessem.reporting import summarize_dispatch
    >>> summary = summarize_dispatch(out)
    >>> summary["G1"]
    [(1, 20.0), (2, 25.0), ...]
    """
    P = out["P"]
    per_gen = defaultdict(list)
    for (g, t), val in P.items():
        per_gen[g].append((t, val))
    return {g: sorted(vals) for g, vals in per_gen.items()}
