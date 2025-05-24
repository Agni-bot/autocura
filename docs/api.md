# Documentação das APIs - AutoCura

## 📡 Endpoints Disponíveis

### Monitor (Porta 9090)

#### GET /health
Verifica a saúde do serviço de monitoramento.

**Resposta:**
```json
{
    "status": "ok",
    "timestamp": "2025-05-24T02:33:15.025Z",
    "versao": "1.0.0"
}
```

#### GET /metrics
Retorna métricas do sistema em formato Prometheus.

**Resposta:**
```
# HELP validacoes_total Total de validações realizadas
# TYPE validacoes_total counter
validacoes_total 42

# HELP tempo_resposta_seconds Tempo de resposta das operações
# TYPE tempo_resposta_seconds histogram
tempo_resposta_seconds_bucket{le="0.1"} 10
tempo_resposta_seconds_bucket{le="0.5"} 30
tempo_resposta_seconds_bucket{le="1.0"} 42
```

### Observador (Porta 8080)

#### GET /health
Verifica a saúde do serviço de observabilidade.

**Resposta:**
```json
{
    "status": "ok",
    "timestamp": "2025-05-24T02:33:15.025Z",
    "versao": "1.0.0"
}
```

#### GET /logs
Retorna os logs mais recentes.

**Parâmetros:**
- `limit` (opcional): Número máximo de logs (padrão: 100)
- `level` (opcional): Nível do log (INFO, WARN, ERROR)

**Resposta:**
```json
{
    "logs": [
        {
            "timestamp": "2025-05-24T02:33:15.025Z",
            "level": "INFO",
            "mensagem": "Sistema iniciado",
            "modulo": "observador"
        }
    ]
}
```

### Validador (Porta 8080)

#### POST /validar
Valida uma requisição ou operação.

**Corpo da Requisição:**
```json
{
    "tipo": "requisicao",
    "conteudo": "Dados para validação",
    "metadados": {
        "origem": "sistema",
        "timestamp": "2025-05-24T02:33:15.025Z"
    }
}
```

**Resposta:**
```json
{
    "valido": true,
    "resultado": {
        "score": 0.95,
        "critérios": {
            "seguranca": "aprovado",
            "privacidade": "aprovado",
            "conformidade": "aprovado"
        }
    }
}
```

### Guardião (Porta 8080)

#### GET /status
Retorna o status atual do sistema de proteção.

**Resposta:**
```json
{
    "protecao_ativa": true,
    "nivel_protecao": "alto",
    "ultima_verificacao": "2025-05-24T02:33:15.025Z",
    "alertas_ativos": []
}
```

#### POST /configurar
Configura parâmetros de proteção.

**Corpo da Requisição:**
```json
{
    "nivel_protecao": "alto",
    "regras": {
        "bloqueio_automatico": true,
        "notificacoes": true
    }
}
```

**Resposta:**
```json
{
    "status": "configurado",
    "timestamp": "2025-05-24T02:33:15.025Z"
}
```

## 🔒 Segurança

- Todas as APIs requerem autenticação via token JWT
- Tokens devem ser enviados no header `Authorization: Bearer <token>`
- Rate limiting: 100 requisições por minuto por IP
- Todas as comunicações são via HTTPS

## 📊 Métricas Disponíveis

### Monitor
- `validacoes_total`: Total de validações realizadas
- `tempo_resposta_seconds`: Tempo de resposta das operações
- `erros_total`: Total de erros encontrados
- `requisicoes_total`: Total de requisições processadas

### Observador
- `logs_total`: Total de logs gerados
- `logs_por_nivel`: Distribuição de logs por nível
- `tempo_processamento_logs`: Tempo de processamento dos logs

### Validador
- `validacoes_por_tipo`: Distribuição de validações por tipo
- `score_medio`: Score médio das validações
- `tempo_validacao`: Tempo médio de validação

### Guardião
- `alertas_ativos`: Número de alertas ativos
- `bloqueios_realizados`: Total de bloqueios realizados
- `tempo_resposta_protecao`: Tempo de resposta do sistema de proteção

## 🔄 Fluxo de Dados

1. Requisição recebida pelo sistema
2. Validação inicial pelo Validador
3. Monitoramento contínuo pelo Monitor
4. Registro de logs pelo Observador
5. Proteção ativa pelo Guardião

## 🛠️ Exemplos de Uso

### Python
```python
import requests

# Configuração
BASE_URL = "http://localhost"
TOKEN = "seu-token-jwt"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Validar requisição
response = requests.post(
    f"{BASE_URL}:8080/validar",
    json={
        "tipo": "requisicao",
        "conteudo": "dados",
        "metadados": {"origem": "teste"}
    },
    headers=HEADERS
)

# Verificar métricas
metrics = requests.get(f"{BASE_URL}:9090/metrics", headers=HEADERS)
```

### Curl
```bash
# Verificar saúde do sistema
curl -H "Authorization: Bearer seu-token-jwt" http://localhost:9090/health

# Obter logs
curl -H "Authorization: Bearer seu-token-jwt" http://localhost:8080/logs?limit=10&level=INFO
``` 