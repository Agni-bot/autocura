# Decisão Híbrida

Sistema de tomada de decisão híbrida combinando IA e regras humanas.

## Estrutura

- `engines/`: Motores de decisão
  - `ai_engine.py`: Motor baseado em IA
  - `rule_engine.py`: Motor baseado em regras
  - `hybrid_engine.py`: Motor híbrido

- `validators/`: Validadores de decisões
  - `decision_validator.py`: Validação de decisões
  - `impact_analyzer.py`: Análise de impacto

- `explainers/`: Sistema de explicabilidade
  - `decision_explainer.py`: Explicação de decisões

## Uso

```python
from modulos.etica.decisao_hibrida import DecisaoHibrida

decisor = DecisaoHibrida()
resultado = decisor.tomar_decisao(contexto)
```

## Testes

```bash
pytest tests/
``` 