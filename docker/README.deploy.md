# Deploy dos Módulos Testados - AutoCura

Este documento descreve o processo de deploy dos módulos já testados e aprovados do sistema AutoCura.

## 🚀 Módulos Disponíveis para Deploy

1. **Monitor** (`autocura/monitor:latest`)
   - Sistema de monitoramento e métricas
   - Porta: 9090
   - Integração com Prometheus

2. **Observador** (`autocura/observador:latest`)
   - Sistema de observabilidade e logs
   - Porta: 8080
   - Integração com Elasticsearch

3. **Validador** (`autocura/validador:latest`)
   - Sistema de validação ética
   - Integração com Redis

4. **Guardião** (`autocura/guardiao:latest`)
   - Sistema de proteção e segurança
   - Integração com Redis

## 📋 Pré-requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM disponível
- 10GB espaço em disco

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/autocura.git
cd autocura
```

2. Execute o script de deploy:
```bash
chmod +x scripts/deploy_modulos.sh
./scripts/deploy_modulos.sh
```

## 🛠️ Configuração

Os módulos podem ser configurados através de variáveis de ambiente no arquivo `docker/docker-compose.testados.yml`:

- `LOG_LEVEL`: Nível de log (INFO, DEBUG, ERROR)
- `REDIS_HOST`: Host do Redis
- `ELASTICSEARCH_HOSTS`: Hosts do Elasticsearch
- `PROMETHEUS_MULTIPROC_DIR`: Diretório para métricas do Prometheus

## 📊 Monitoramento

- Prometheus: http://localhost:9091
- Elasticsearch: http://localhost:9200
- Redis: localhost:6379

## 🔍 Verificação do Deploy

Para verificar o status dos containers:

```bash
docker-compose -f docker/docker-compose.testados.yml ps
```

Para ver os logs de um módulo específico:

```bash
docker-compose -f docker/docker-compose.testados.yml logs -f [nome-do-modulo]
```

## 🛡️ Segurança

- Todos os módulos rodam em containers isolados
- Comunicação via rede Docker dedicada
- Volumes persistentes para dados críticos
- Logs centralizados no Elasticsearch

## 🔄 Manutenção

Para atualizar um módulo específico:

```bash
docker-compose -f docker/docker-compose.testados.yml pull [nome-do-modulo]
docker-compose -f docker/docker-compose.testados.yml up -d [nome-do-modulo]
```

Para parar todos os módulos:

```bash
docker-compose -f docker/docker-compose.testados.yml down
```

## 📝 Notas Importantes

1. Os módulos são versionados com tags específicas
2. Backup dos volumes é recomendado antes de atualizações
3. Monitoramento de recursos é essencial
4. Logs devem ser rotacionados periodicamente 