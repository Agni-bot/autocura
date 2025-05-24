# Documentação da API

## Visão Geral

A API do sistema AutoCura fornece endpoints para interação com os diferentes módulos do sistema. A API é RESTful e utiliza JSON como formato de dados.

## Autenticação

Todas as requisições devem incluir um token de autenticação no header:

```
Authorization: Bearer <seu-token>
```

## Endpoints

### Monitoramento

#### GET /api/v1/metricas
Retorna métricas do sistema.

**Parâmetros:**
- `tipo` (opcional): Filtro por tipo de métrica
- `periodo` (opcional): Período de tempo (ex: "1h", "24h", "7d")

**Resposta:**
```json
{
  "metricas": [
    {
      "id": "string",
      "tipo": "string",
      "valor": "number",
      "timestamp": "string",
      "metadata": {}
    }
  ]
}
```

#### POST /api/v1/metricas
Registra nova métrica.

**Corpo:**
```json
{
  "tipo": "string",
  "valor": "number",
  "metadata": {}
}
```

### Ética

#### POST /api/v1/etica/validar
Valida decisão ética.

**Corpo:**
```json
{
  "contexto": "string",
  "acao": "string",
  "parametros": {}
}
```

**Resposta:**
```json
{
  "valido": "boolean",
  "explicacao": "string",
  "recomendacoes": []
}
```

### Diagnóstico

#### GET /api/v1/diagnostico/status
Retorna status do diagnóstico.

**Resposta:**
```json
{
  "status": "string",
  "ultima_verificacao": "string",
  "problemas": []
}
```

#### POST /api/v1/diagnostico/analisar
Inicia nova análise.

**Corpo:**
```json
{
  "tipo": "string",
  "parametros": {}
}
```

## Códigos de Erro

- `400`: Requisição inválida
- `401`: Não autorizado
- `403`: Proibido
- `404`: Não encontrado
- `500`: Erro interno

## Exemplos

### Python
```python
import requests

headers = {
    'Authorization': 'Bearer seu-token'
}

# Obter métricas
response = requests.get(
    'http://api.autocura.dev/api/v1/metricas',
    headers=headers,
    params={'periodo': '24h'}
)

# Validar decisão ética
response = requests.post(
    'http://api.autocura.dev/api/v1/etica/validar',
    headers=headers,
    json={
        'contexto': 'decisao_autonoma',
        'acao': 'ajuste_parametros',
        'parametros': {'limite': 0.8}
    }
)
```

### JavaScript
```javascript
const axios = require('axios');

const api = axios.create({
    baseURL: 'http://api.autocura.dev',
    headers: {
        'Authorization': 'Bearer seu-token'
    }
});

// Obter métricas
const getMetricas = async () => {
    const response = await api.get('/api/v1/metricas', {
        params: { periodo: '24h' }
    });
    return response.data;
};

// Validar decisão ética
const validarDecisao = async (contexto, acao, parametros) => {
    const response = await api.post('/api/v1/etica/validar', {
        contexto,
        acao,
        parametros
    });
    return response.data;
};
```

## WebSocket

### Conexão
```
ws://api.autocura.dev/ws
```

### Eventos

#### metricas
Recebe atualizações de métricas em tempo real.

```json
{
  "tipo": "metricas",
  "dados": {
    "id": "string",
    "tipo": "string",
    "valor": "number",
    "timestamp": "string"
  }
}
```

#### alertas
Recebe alertas do sistema.

```json
{
  "tipo": "alertas",
  "dados": {
    "nivel": "string",
    "mensagem": "string",
    "timestamp": "string"
  }
}
```

## Rate Limiting

- 100 requisições por minuto por IP
- 1000 requisições por hora por token

## Versões

- v1 (atual)
- v0 (deprecated)

## Changelog

### v1.0.0
- Implementação inicial da API
- Endpoints básicos de monitoramento
- Validação ética
- Diagnóstico

### v1.1.0
- Adição de WebSocket
- Novos endpoints de métricas
- Melhorias na validação ética 