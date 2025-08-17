# pydessem

Modelo **didático** no espírito do DESSEM, implementado em **Pyomo**:

- **UC térmico** (binárias `u/y/z`, custos no-load/partida/parada, MUT/MDT, rampas com SU/SD).
- **Hidráulica PWL** (`Piecewise`) por reservatório com curva potência×vazão.
- **Reservas** com requisito horário agregado e custo opcional de oferta.
- **Rede DC**, balanço nodal, limites de linha e déficits/vertedura.

> Este pacote é voltado a ensino/prototipagem. Não lê casos nativos do DESSEM.

## Instalação
```bash
pip install -e .
# ou
pip install pydessem-0.1.0-py3-none-any.whl
```

## Uso rápido
```bash
pydessem-solve examples/case_tiny.yaml --solver glpk
```

## Estrutura de dados (YAML)
Veja `examples/case_tiny.yaml`.

## Saída
O script imprime custo objetivo e tabelas principais. Para manipular via API:

```python
from pydessem.solve import solve_case
out, model, data = solve_case("examples/case_tiny.yaml", solver_name="glpk")
print(out["objective"])
```
