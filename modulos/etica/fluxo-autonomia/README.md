# Fluxo de Autonomia

Controle e gerenciamento do fluxo de autonomia do sistema.

## Estrutura

- `controllers/`: Controladores de autonomia
  - `base_controller.py`: Controlador base
  - `autonomy_controller.py`: Controlador de autonomia
  - `safety_controller.py`: Controlador de segurança

- `validators/`: Validadores de autonomia
  - `autonomy_validator.py`: Validação de níveis de autonomia
  - `safety_validator.py`: Validação de segurança

- `monitors/`: Monitores de autonomia
  - `autonomy_monitor.py`: Monitor de níveis de autonomia
  - `safety_monitor.py`: Monitor de segurança

## Uso

```python
from modulos.etica.fluxo_autonomia import FluxoAutonomia

fluxo = FluxoAutonomia()
nivel = fluxo.ajustar_autonomia(contexto)
```

## Testes

```bash
pytest tests/
``` 