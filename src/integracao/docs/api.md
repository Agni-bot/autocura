# Documentação da API

Este documento descreve os endpoints e funcionalidades da API do módulo de integração.

## 🔑 Autenticação

### Obter Token

```http
POST /auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Resposta**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Atualizar Token

```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

**Resposta**

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 📨 Mensagens

### Enviar Mensagem

```http
POST /messages
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "protocol": "http",
  "content": "Hello World",
  "metadata": {
    "priority": "high",
    "tags": ["test", "api"]
  }
}
```

**Resposta**

```json
{
  "id": "msg_123",
  "status": "queued",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Obter Mensagem

```http
GET /messages/{message_id}
Authorization: Bearer <access_token>
```

**Resposta**

```json
{
  "id": "msg_123",
  "protocol": "http",
  "content": "Hello World",
  "status": "processed",
  "metadata": {
    "priority": "high",
    "tags": ["test", "api"]
  },
  "created_at": "2024-01-01T00:00:00Z",
  "processed_at": "2024-01-01T00:00:01Z"
}
```

### Listar Mensagens

```http
GET /messages
Authorization: Bearer <access_token>
Query Parameters:
  - status: string (optional)
  - protocol: string (optional)
  - from: datetime (optional)
  - to: datetime (optional)
  - page: integer (optional)
  - size: integer (optional)
```

**Resposta**

```json
{
  "items": [
    {
      "id": "msg_123",
      "protocol": "http",
      "status": "processed",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 10
}
```

## 🔄 Status

### Health Check

```http
GET /health
```

**Resposta**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z",
  "services": {
    "redis": "up",
    "kafka": "up",
    "database": "up"
  }
}
```

### Métricas

```http
GET /metrics
Authorization: Bearer <access_token>
```

**Resposta**

```json
{
  "messages": {
    "total": 1000,
    "processed": 950,
    "failed": 50,
    "queued": 0
  },
  "performance": {
    "latency_ms": 50,
    "throughput": 100
  },
  "resources": {
    "cpu_percent": 25,
    "memory_percent": 30
  }
}
```

## 🔒 Segurança

### CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
from fastapi import FastAPI, Request
from fastapi.middleware.throttling import ThrottlingMiddleware

app.add_middleware(
    ThrottlingMiddleware,
    rate_limit=100,
    time_window=60
)
```

## 📝 Schemas

### Message

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class Message(BaseModel):
    id: str = Field(..., description="ID único da mensagem")
    protocol: str = Field(..., description="Protocolo de comunicação")
    content: str = Field(..., description="Conteúdo da mensagem")
    status: str = Field(..., description="Status do processamento")
    metadata: Optional[Dict] = Field(default={}, description="Metadados adicionais")
    created_at: datetime = Field(..., description="Data de criação")
    processed_at: Optional[datetime] = Field(None, description="Data de processamento")
```

### Error

```python
class Error(BaseModel):
    code: str = Field(..., description="Código do erro")
    message: str = Field(..., description="Mensagem de erro")
    details: Optional[Dict] = Field(None, description="Detalhes adicionais")
```

## 🔄 Webhooks

### Configurar Webhook

```http
POST /webhooks
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "events": ["message.processed", "message.failed"],
  "secret": "webhook_secret"
}
```

**Resposta**

```json
{
  "id": "webhook_123",
  "url": "https://example.com/webhook",
  "events": ["message.processed", "message.failed"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Eventos

```json
{
  "event": "message.processed",
  "timestamp": "2024-01-01T00:00:00Z",
  "data": {
    "message_id": "msg_123",
    "status": "processed",
    "processing_time_ms": 50
  }
}
```

## 📚 Referências

- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAPI](https://swagger.io/specification/)
- [JWT](https://jwt.io/)
- [OAuth2](https://oauth.net/2/)
- [REST](https://restfulapi.net/) 