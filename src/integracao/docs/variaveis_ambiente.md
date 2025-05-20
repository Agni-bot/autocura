# Variáveis de Ambiente

Este documento descreve as variáveis de ambiente utilizadas pelo módulo de integração.

## 🔑 Autenticação

### JWT

```bash
# Chave secreta para assinatura dos tokens
JWT_SECRET_KEY=your-secret-key

# Algoritmo de assinatura
JWT_ALGORITHM=HS256

# Tempo de expiração do token de acesso (em segundos)
JWT_ACCESS_TOKEN_EXPIRE=3600

# Tempo de expiração do token de atualização (em segundos)
JWT_REFRESH_TOKEN_EXPIRE=604800
```

### OAuth2

```bash
# URL do provedor OAuth2
OAUTH2_PROVIDER_URL=https://oauth2.example.com

# ID do cliente
OAUTH2_CLIENT_ID=your-client-id

# Segredo do cliente
OAUTH2_CLIENT_SECRET=your-client-secret

# Escopo padrão
OAUTH2_DEFAULT_SCOPE=read write
```

## 🔄 Mensageria

### Redis

```bash
# Host do Redis
REDIS_HOST=localhost

# Porta do Redis
REDIS_PORT=6379

# Senha do Redis
REDIS_PASSWORD=your-password

# Banco de dados
REDIS_DB=0

# Prefixo para chaves
REDIS_KEY_PREFIX=integracao:
```

### Kafka

```bash
# Servidores bootstrap
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# ID do grupo de consumidores
KAFKA_CONSUMER_GROUP_ID=integracao-group

# Tópicos
KAFKA_TOPIC_MESSAGES=messages
KAFKA_TOPIC_EVENTS=events
KAFKA_TOPIC_NOTIFICATIONS=notifications

# Configurações do produtor
KAFKA_PRODUCER_ACKS=all
KAFKA_PRODUCER_RETRIES=3
```

## 📊 Monitoramento

### Prometheus

```bash
# Porta do servidor de métricas
PROMETHEUS_PORT=9090

# Prefixo das métricas
PROMETHEUS_METRICS_PREFIX=integracao_

# Intervalo de coleta (em segundos)
PROMETHEUS_COLLECT_INTERVAL=15
```

### Logging

```bash
# Nível de log
LOG_LEVEL=INFO

# Formato do log
LOG_FORMAT=json

# Arquivo de log
LOG_FILE=logs/integracao.log

# Rotação de logs
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
```

## 🔒 Segurança

### CORS

```bash
# Origens permitidas
CORS_ALLOWED_ORIGINS=https://example.com,https://api.example.com

# Métodos permitidos
CORS_ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS

# Headers permitidos
CORS_ALLOWED_HEADERS=Authorization,Content-Type

# Credenciais
CORS_ALLOW_CREDENTIALS=true
```

### Rate Limiting

```bash
# Limite de requisições por IP
RATE_LIMIT_IP=100

# Limite de requisições por usuário
RATE_LIMIT_USER=1000

# Janela de tempo (em segundos)
RATE_LIMIT_WINDOW=60
```

## 🗄️ Banco de Dados

### PostgreSQL

```bash
# Host do banco de dados
DB_HOST=localhost

# Porta do banco de dados
DB_PORT=5432

# Nome do banco de dados
DB_NAME=integracao

# Usuário do banco de dados
DB_USER=postgres

# Senha do banco de dados
DB_PASSWORD=your-password

# Pool de conexões
DB_POOL_MIN=5
DB_POOL_MAX=20
```

## 🔄 Cache

### Redis Cache

```bash
# Host do Redis
CACHE_REDIS_HOST=localhost

# Porta do Redis
CACHE_REDIS_PORT=6379

# Senha do Redis
CACHE_REDIS_PASSWORD=your-password

# Banco de dados
CACHE_REDIS_DB=1

# TTL padrão (em segundos)
CACHE_DEFAULT_TTL=3600
```

## 📡 API

### Servidor

```bash
# Host do servidor
API_HOST=0.0.0.0

# Porta do servidor
API_PORT=8000

# Workers
API_WORKERS=4

# Timeout
API_TIMEOUT=60

# Limite de requisições
API_MAX_REQUESTS=10000
```

### WebSocket

```bash
# Host do WebSocket
WS_HOST=0.0.0.0

# Porta do WebSocket
WS_PORT=8001

# Ping interval (em segundos)
WS_PING_INTERVAL=20

# Ping timeout (em segundos)
WS_PING_TIMEOUT=60
```

## 🔍 Tracing

### OpenTelemetry

```bash
# Endpoint do coletor
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317

# Nome do serviço
OTEL_SERVICE_NAME=integracao

# Ambiente
OTEL_ENVIRONMENT=development

# Amostragem
OTEL_SAMPLER_RATIO=1.0
```

## 📝 Exemplo de Arquivo .env

```bash
# Autenticação
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE=3600
JWT_REFRESH_TOKEN_EXPIRE=604800

# Mensageria
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-password
REDIS_DB=0
REDIS_KEY_PREFIX=integracao:

KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CONSUMER_GROUP_ID=integracao-group
KAFKA_TOPIC_MESSAGES=messages
KAFKA_TOPIC_EVENTS=events
KAFKA_TOPIC_NOTIFICATIONS=notifications

# Monitoramento
PROMETHEUS_PORT=9090
PROMETHEUS_METRICS_PREFIX=integracao_
PROMETHEUS_COLLECT_INTERVAL=15

LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/integracao.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Segurança
CORS_ALLOWED_ORIGINS=https://example.com,https://api.example.com
CORS_ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOWED_HEADERS=Authorization,Content-Type
CORS_ALLOW_CREDENTIALS=true

RATE_LIMIT_IP=100
RATE_LIMIT_USER=1000
RATE_LIMIT_WINDOW=60

# Banco de Dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=integracao
DB_USER=postgres
DB_PASSWORD=your-password
DB_POOL_MIN=5
DB_POOL_MAX=20

# Cache
CACHE_REDIS_HOST=localhost
CACHE_REDIS_PORT=6379
CACHE_REDIS_PASSWORD=your-password
CACHE_REDIS_DB=1
CACHE_DEFAULT_TTL=3600

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_TIMEOUT=60
API_MAX_REQUESTS=10000

# WebSocket
WS_HOST=0.0.0.0
WS_PORT=8001
WS_PING_INTERVAL=20
WS_PING_TIMEOUT=60

# Tracing
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=integracao
OTEL_ENVIRONMENT=development
OTEL_SAMPLER_RATIO=1.0
```

## 📚 Referências

- [Python-dotenv](https://github.com/theskumar/python-dotenv)
- [FastAPI Settings](https://fastapi.tiangolo.com/advanced/settings/)
- [Redis Configuration](https://redis.io/topics/config)
- [Kafka Configuration](https://kafka.apache.org/documentation/#configuration)
- [OpenTelemetry Configuration](https://opentelemetry.io/docs/concepts/sdk-configuration/) 