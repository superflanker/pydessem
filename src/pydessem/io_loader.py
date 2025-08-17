"""
PyDessem I/O Loader
===================

YAML-based Input Loader for PyDessem Framework

Summary
-------
This module provides utility functions to read and validate
case data from YAML files for the PyDessem framework. The
data includes model metadata, sets, mappings, and parameters,
which are required to build and solve hydrothermal scheduling
problems in Pyomo.

Author
------
Augusto Mathias Adams <augusto.adams@ufpr.br>

Contents
--------
- load_case: read and validate YAML case data.

Notes
-----
This module is part of the activities of the discipline
EELT7030 - Short/Medium-Term Power System Operation Planning,
Federal University of Paraná (UFPR), Brazil.

Dependencies
------------
- pathlib
- pyyaml
"""
from pathlib import Path
import yaml

def load_case(path_yaml: str):
    """
    Load and validate case data from a YAML file.

    The function reads a YAML file containing model metadata,
    sets, mappings, and parameters, and returns its content
    as a Python dictionary. It ensures that the required
    top-level keys are present.

    Parameters
    ----------
    path_yaml : str
        Path to the YAML file containing case data.

    Returns
    -------
    dict
        Dictionary with the parsed YAML content, including
        "meta", "sets", "map", and "params" sections.

    Raises
    ------
    ValueError
        If any of the required keys ("meta", "sets", "map", "params")
        are missing from the YAML file.

    Examples
    --------
    >>> data = load_case("examples/case_tiny.yaml")
    >>> list(data.keys())
    ['meta', 'sets', 'map', 'params']
    """
    
    p = Path(path_yaml)
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # Validações simples
    required = ["meta", "sets", "map", "params"]
    for k in required:
        if k not in data:
            raise ValueError(f"Chave obrigatória ausente no YAML: {k}")
    return data
