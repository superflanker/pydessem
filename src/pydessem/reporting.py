\
from collections import defaultdict

def summarize_dispatch(out):
    """Gera sumarização simples por gerador e hora."""
    P = out["P"]
    per_gen = defaultdict(list)
    for (g, t), val in P.items():
        per_gen[g].append((t, val))
    return {g: sorted(vals) for g, vals in per_gen.items()}
