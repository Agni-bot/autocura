# Circuitos Morais

Implementação dos circuitos morais e princípios éticos do sistema.

## Estrutura

- `pillars/`: Pilares éticos fundamentais
  - `base_pillar.py`: Interface base para pilares
  - `life_preservation.py`: Preservação da vida
  - `global_equity.py`: Equidade global
  - `transparency.py`: Transparência
  - `sustainability.py`: Sustentabilidade
  - `human_control.py`: Controle humano

- `validators/`: Validadores de princípios éticos
  - `ethical_validator.py`: Validação ética
  - `constraint_checker.py`: Verificação de restrições

- `explainers/`: Sistema de explicabilidade
  - `ethical_explainer.py`: Explicação de decisões éticas

## Uso

```python
from modulos.etica.circuitos_morais import CircuitosMorais

circuitos = CircuitosMorais()
resultado = circuitos.validar_acao(acao)
```

## Testes

```bash
pytest tests/
``` 