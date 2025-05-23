# Módulo de Monitoramento e Observabilidade

Este módulo é responsável por monitoramento, métricas e observabilidade do sistema.

## Estrutura

- `coletores/`: Coletores de métricas e dados
  - `base_coletor.py`: Interface base para coletores
  - `coletor_sistema.py`: Métricas do sistema
  - `coletor_aplicacao.py`: Métricas da aplicação
  - `coletor_rede.py`: Métricas de rede

- `processadores/`: Processamento de dados coletados
  - `agregador.py`: Agregação de métricas
  - `normalizador.py`: Normalização de dados
  - `filtro.py`: Filtros de dados

- `storage/`: Armazenamento de métricas
  - `timeseries_storage.py`: Armazenamento de séries temporais
  - `cache_storage.py`: Cache de métricas

- `api/`: APIs de acesso
  - `rest_api.py`: API REST
  - `grpc_api.py`: API gRPC

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```python
from modulos.monitoramento import MonitorManager

monitor = MonitorManager()
monitor.iniciar_coleta()
```

## Testes

```bash
pytest tests/
```

