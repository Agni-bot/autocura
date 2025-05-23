# Módulo Ético-Operacional

Este módulo é responsável por todas as operações éticas e de governança do sistema.

## Estrutura

- `circuitos-morais/`: Implementação dos circuitos morais e princípios éticos
- `decisao-hibrida/`: Sistema de tomada de decisão híbrida
- `auditoria/`: Sistema de auditoria e conformidade
- `governanca/`: Mecanismos de governança adaptativa
- `fluxo-autonomia/`: Controle de fluxo de autonomia
- `validadores-eticos/`: Validadores de decisões éticas
- `priorizacao-financeira/`: Sistema de priorização financeira
- `registro-decisoes/`: Registro e rastreamento de decisões

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```python
from modulos.etica import EticaManager

etica = EticaManager()
etica.validar_decisao(decisao)
```

## Testes

```bash
pytest tests/
```

