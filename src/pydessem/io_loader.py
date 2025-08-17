\
from pathlib import Path
import yaml

def load_case(path_yaml: str):
    """Carrega o dicionário de dados a partir de um YAML."""
    p = Path(path_yaml)
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # Validações simples
    required = ["meta", "sets", "map", "params"]
    for k in required:
        if k not in data:
            raise ValueError(f"Chave obrigatória ausente no YAML: {k}")
    return data
