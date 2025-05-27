# Guia de Monitoramento

Este documento descreve as práticas de monitoramento implementadas no módulo de integração.

## 📊 Métricas

### Prometheus

#### Contadores

```python
from prometheus_client import Counter

MESSAGES_PROCESSED = Counter(
    'messages_processed_total',
    'Total de mensagens processadas',
    ['protocol', 'status']
)

ERRORS_TOTAL = Counter(
    'errors_total',
    'Total de erros',
    ['type', 'source']
)

AUTH_ATTEMPTS = Counter(
    'auth_attempts_total',
    'Total de tentativas de autenticação',
    ['success']
)
```

#### Gauges

```python
from prometheus_client import Gauge

QUEUE_SIZE = Gauge(
    'queue_size',
    'Tamanho atual da fila de mensagens'
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Número de conexões ativas',
    ['protocol']
)

MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Uso de memória em bytes'
)
```

#### Histogramas

```python
from prometheus_client import Histogram

PROCESSING_TIME = Histogram(
    'message_processing_seconds',
    'Tempo de processamento das mensagens',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

LATENCY = Histogram(
    'request_latency_seconds',
    'Latência das requisições',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)
```

#### Sumários

```python
from prometheus_client import Summary

REQUEST_SIZE = Summary(
    'request_size_bytes',
    'Tamanho das requisições'
)

RESPONSE_SIZE = Summary(
    'response_size_bytes',
    'Tamanho das respostas'
)
```

### Grafana

#### Dashboards

1. **Visão Geral**
   - Total de mensagens
   - Taxa de erros
   - Latência média
   - Uso de recursos

2. **Mensagens**
   - Processadas por protocolo
   - Status de processamento
   - Tamanho das mensagens
   - Tempo de processamento

3. **Conexões**
   - Conexões ativas
   - Novas conexões
   - Conexões fechadas
   - Erros de conexão

4. **Recursos**
   - CPU
   - Memória
   - Disco
   - Rede

5. **Segurança**
   - Tentativas de autenticação
   - Acessos negados
   - Erros de segurança
   - Tokens expirados

### Alertas

#### Regras

```yaml
groups:
- name: integracao
  rules:
  - alert: HighErrorRate
    expr: rate(errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Alta taxa de erros"
      description: "Taxa de erros acima de 10% nos últimos 5 minutos"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(request_latency_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Alta latência"
      description: "95% das requisições com latência acima de 1s"

  - alert: QueueSize
    expr: queue_size > 1000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Fila grande"
      description: "Fila de mensagens com mais de 1000 itens"
```

#### Notificações

- Email
- Slack
- PagerDuty
- Webhook

## 🔍 Logs

### Estrutura

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "integracao",
  "component": "message_processor",
  "message": "Mensagem processada",
  "details": {
    "message_id": "msg_123",
    "protocol": "http",
    "status": "success",
    "processing_time_ms": 50
  },
  "context": {
    "request_id": "req_123",
    "user_id": "user_123",
    "ip": "127.0.0.1"
  }
}
```

### Níveis

- DEBUG: Informações detalhadas
- INFO: Informações gerais
- WARNING: Avisos
- ERROR: Erros
- CRITICAL: Erros críticos

### Rotação

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/integracao.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
```

## 📈 Health Checks

### Endpoints

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "redis": check_redis(),
            "kafka": check_kafka(),
            "database": check_database()
        }
    }
```

### Verificações

1. **Redis**
   - Conexão
   - Ping
   - Memória
   - Clientes

2. **Kafka**
   - Conexão
   - Tópicos
   - Consumidores
   - Produtores

3. **Database**
   - Conexão
   - Queries
   - Transações
   - Índices

## 🔄 Tracing

### OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

def setup_tracing():
    trace.set_tracer_provider(TracerProvider())
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
```

### Spans

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def process_message(message):
    with tracer.start_as_current_span("process_message") as span:
        span.set_attribute("message_id", message.id)
        span.set_attribute("protocol", message.protocol)
        
        # Processamento
        span.add_event("message_processed")
```

## 📊 Dashboards

### Grafana

1. **Visão Geral**
   - Total de mensagens
   - Taxa de erros
   - Latência média
   - Uso de recursos

2. **Mensagens**
   - Processadas por protocolo
   - Status de processamento
   - Tamanho das mensagens
   - Tempo de processamento

3. **Conexões**
   - Conexões ativas
   - Novas conexões
   - Conexões fechadas
   - Erros de conexão

4. **Recursos**
   - CPU
   - Memória
   - Disco
   - Rede

5. **Segurança**
   - Tentativas de autenticação
   - Acessos negados
   - Erros de segurança
   - Tokens expirados

### Jaeger

1. **Traces**
   - Duração
   - Erros
   - Tags
   - Logs

2. **Services**
   - Dependências
   - Latência
   - Erros
   - Throughput

## 🚨 Alertas

### Regras

```yaml
groups:
- name: integracao
  rules:
  - alert: HighErrorRate
    expr: rate(errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Alta taxa de erros"
      description: "Taxa de erros acima de 10% nos últimos 5 minutos"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(request_latency_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Alta latência"
      description: "95% das requisições com latência acima de 1s"

  - alert: QueueSize
    expr: queue_size > 1000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Fila grande"
      description: "Fila de mensagens com mais de 1000 itens"
```

### Notificações

- Email
- Slack
- PagerDuty
- Webhook

## 📝 Relatórios

### Diários

- Total de mensagens
- Taxa de erros
- Latência média
- Uso de recursos

### Semanais

- Tendências
- Anomalias
- Capacidade
- Performance

### Mensais

- Crescimento
- Estabilidade
- Custos
- Planejamento

## 🔄 Manutenção

### Backup

- Logs
- Métricas
- Configurações
- Dados

### Limpeza

- Logs antigos
- Métricas antigas
- Dados temporários
- Cache

### Atualização

- Dependências
- Configurações
- Certificados
- Documentação

## 📚 Referências

- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)
- [OpenTelemetry](https://opentelemetry.io/docs/)
- [Jaeger](https://www.jaegertracing.io/docs/)
- [ELK Stack](https://www.elastic.co/guide/index.html) 