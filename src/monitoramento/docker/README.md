# Docker - Monitoramento

Este diretório contém os arquivos Docker específicos para o módulo de Monitoramento do sistema AutoCura.

## Arquivos

- `docker-compose.dev.yml`: Compose file para ambiente de desenvolvimento com foco em monitoramento, incluindo:
  - Aplicação Principal
  - Redis
  - Prometheus
  - Grafana
  - Loki
  - Promtail

## Uso

Para iniciar o ambiente de monitoramento:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

Para parar:

```bash
docker-compose -f docker-compose.dev.yml down
```

## Acessos

- Grafana: http://localhost:3000
  - Usuário: admin
  - Senha: admin

- Prometheus: http://localhost:9090

- Loki: http://localhost:3100

## Configuração

O ambiente requer as seguintes variáveis de ambiente:

- `ENVIRONMENT`: development
- `REDIS_HOST`: redis
- `REDIS_PORT`: 6379

## Volumes

- `redis_data`: Dados do Redis
- `prometheus_data`: Dados do Prometheus
- `grafana_data`: Dados do Grafana
- `loki_data`: Dados do Loki 