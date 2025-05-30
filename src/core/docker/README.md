# Docker - Core do Sistema

Este diretório contém os arquivos Docker base do sistema AutoCura.

## Arquivos

- `Dockerfile`: Dockerfile base do sistema, contendo as dependências e configurações comuns.
- `docker-compose.yml`: Compose file principal para desenvolvimento, incluindo:
  - API Principal
  - Prometheus
  - Grafana
  - Elasticsearch
  - Kibana
  - Jaeger
  - Redis
  - PostgreSQL
  - Ambiente de Testes

- `docker-compose.simple.yml`: Compose file simplificado para fase Alpha, incluindo:
  - API Principal
  - Redis
  - Grafana
  - Dashboard Nginx

## Uso

Para iniciar o ambiente de desenvolvimento:

```bash
docker-compose -f docker-compose.yml up -d
```

Para iniciar o ambiente Alpha:

```bash
docker-compose -f docker-compose.simple.yml up -d
```

Para parar:

```bash
docker-compose -f docker-compose.yml down
# ou
docker-compose -f docker-compose.simple.yml down
```

## Configuração

O ambiente de desenvolvimento requer as seguintes variáveis de ambiente:

- `ENVIRONMENT`: development
- `DEBUG`: true
- `LOG_LEVEL`: DEBUG

O ambiente Alpha requer:

- `ENVIRONMENT`: alpha
- `DEBUG`: true
- `LOG_LEVEL`: DEBUG
- `FASE_ATUAL`: ALPHA
- `ETAPA_ATUAL`: A2_CORRIGIDA 