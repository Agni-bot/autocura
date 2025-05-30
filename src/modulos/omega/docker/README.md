# Docker - Módulo Omega

Este diretório contém os arquivos Docker específicos para o módulo Omega do sistema AutoCura.

## Arquivos

- `Dockerfile.omega`: Dockerfile base para os serviços Omega, contendo todas as dependências e configurações necessárias.
- `docker-compose.omega.yml`: Compose file para orquestrar todos os serviços Omega, incluindo:
  - Banco de dados PostgreSQL
  - Cache Redis
  - API Principal
  - Nginx (Load Balancer & SSL)
  - Prometheus (Métricas)
  - Grafana (Dashboards)
  - Exportadores (Node, PostgreSQL, Redis)
  - Módulos Omega (Core, Monitor, Evolution, Integration)

## Uso

Para iniciar o ambiente Omega:

```bash
docker-compose -f docker-compose.omega.yml up -d
```

Para parar:

```bash
docker-compose -f docker-compose.omega.yml down
```

## Configuração

As variáveis de ambiente necessárias devem ser configuradas em um arquivo `.env`:

- `DB_PASSWORD`: Senha do PostgreSQL
- `REDIS_PASSWORD`: Senha do Redis
- `SECRET_KEY`: Chave secreta da aplicação
- `JWT_SECRET`: Chave JWT
- `OPENAI_API_KEY`: Chave da API OpenAI
- `GRAFANA_PASSWORD`: Senha do Grafana 