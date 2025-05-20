# Modelos

Este documento descreve os modelos de dados utilizados pelo módulo de integração.

## 📦 Modelos Base

### Mensagem

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TipoMensagem(str, Enum):
    EVENTO = "evento"
    COMANDO = "comando"
    RESPOSTA = "resposta"
    NOTIFICACAO = "notificacao"

class StatusMensagem(str, Enum):
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONCLUIDA = "concluida"
    ERRO = "erro"

class Mensagem(BaseModel):
    id: str = Field(..., description="Identificador único da mensagem")
    tipo: TipoMensagem = Field(..., description="Tipo da mensagem")
    origem: str = Field(..., description="Origem da mensagem")
    destino: str = Field(..., description="Destino da mensagem")
    payload: Dict[str, Any] = Field(..., description="Conteúdo da mensagem")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadados da mensagem")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora da mensagem")
    status: StatusMensagem = Field(default=StatusMensagem.PENDENTE, description="Status da mensagem")
    erro: Optional[str] = Field(default=None, description="Mensagem de erro, se houver")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Evento

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Evento(BaseModel):
    id: str = Field(..., description="Identificador único do evento")
    tipo: str = Field(..., description="Tipo do evento")
    origem: str = Field(..., description="Origem do evento")
    payload: Dict[str, Any] = Field(..., description="Conteúdo do evento")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadados do evento")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora do evento")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Comando

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Comando(BaseModel):
    id: str = Field(..., description="Identificador único do comando")
    tipo: str = Field(..., description="Tipo do comando")
    origem: str = Field(..., description="Origem do comando")
    destino: str = Field(..., description="Destino do comando")
    payload: Dict[str, Any] = Field(..., description="Conteúdo do comando")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadados do comando")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora do comando")
    timeout: Optional[int] = Field(default=None, description="Timeout em segundos")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## 🔄 Modelos de Resposta

### Resposta

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Resposta(BaseModel):
    id: str = Field(..., description="Identificador único da resposta")
    comando_id: str = Field(..., description="ID do comando relacionado")
    origem: str = Field(..., description="Origem da resposta")
    destino: str = Field(..., description="Destino da resposta")
    payload: Dict[str, Any] = Field(..., description="Conteúdo da resposta")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadados da resposta")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora da resposta")
    sucesso: bool = Field(..., description="Indica se a resposta foi bem-sucedida")
    erro: Optional[str] = Field(default=None, description="Mensagem de erro, se houver")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Notificação

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Notificacao(BaseModel):
    id: str = Field(..., description="Identificador único da notificação")
    tipo: str = Field(..., description="Tipo da notificação")
    origem: str = Field(..., description="Origem da notificação")
    destino: str = Field(..., description="Destino da notificação")
    payload: Dict[str, Any] = Field(..., description="Conteúdo da notificação")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadados da notificação")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora da notificação")
    prioridade: int = Field(default=0, description="Prioridade da notificação")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## 🔐 Modelos de Autenticação

### Usuário

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class Usuario(BaseModel):
    id: str = Field(..., description="Identificador único do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    nome: str = Field(..., description="Nome do usuário")
    ativo: bool = Field(default=True, description="Indica se o usuário está ativo")
    roles: List[str] = Field(default_factory=list, description="Papéis do usuário")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criação")
    updated_at: Optional[datetime] = Field(default=None, description="Data de atualização")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Token

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str = Field(..., description="Token de acesso")
    token_type: str = Field(default="bearer", description="Tipo do token")
    expires_at: datetime = Field(..., description="Data de expiração")
    refresh_token: Optional[str] = Field(default=None, description="Token de atualização")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## 📊 Modelos de Monitoramento

### Métrica

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Metrica(BaseModel):
    nome: str = Field(..., description="Nome da métrica")
    valor: float = Field(..., description="Valor da métrica")
    tipo: str = Field(..., description="Tipo da métrica")
    labels: Dict[str, str] = Field(default_factory=dict, description="Labels da métrica")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora da métrica")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Alerta

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Alerta(BaseModel):
    id: str = Field(..., description="Identificador único do alerta")
    nome: str = Field(..., description="Nome do alerta")
    descricao: str = Field(..., description="Descrição do alerta")
    severidade: str = Field(..., description="Severidade do alerta")
    origem: str = Field(..., description="Origem do alerta")
    payload: Dict[str, Any] = Field(..., description="Conteúdo do alerta")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data e hora do alerta")
    resolvido: bool = Field(default=False, description="Indica se o alerta foi resolvido")
    resolvido_em: Optional[datetime] = Field(default=None, description="Data de resolução")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

## 📝 Exemplo de Uso

```python
from datetime import datetime
from uuid import uuid4
from .models import Mensagem, TipoMensagem, StatusMensagem

# Criar uma mensagem
mensagem = Mensagem(
    id=str(uuid4()),
    tipo=TipoMensagem.EVENTO,
    origem="monitoramento",
    destino="diagnostico",
    payload={
        "cpu_usage": 85.5,
        "memory_usage": 70.2
    },
    metadata={
        "host": "server-01",
        "region": "us-east-1"
    }
)

# Atualizar status
mensagem.status = StatusMensagem.PROCESSANDO

# Registrar erro
mensagem.status = StatusMensagem.ERRO
mensagem.erro = "Falha ao processar métricas"

# Serializar para JSON
mensagem_json = mensagem.json()

# Deserializar de JSON
mensagem_deserializada = Mensagem.parse_raw(mensagem_json)
```

## 📚 Referências

- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [FastAPI Models](https://fastapi.tiangolo.com/tutorial/body/)
- [Python Enums](https://docs.python.org/3/library/enum.html)
- [Python Datetime](https://docs.python.org/3/library/datetime.html)
- [Python UUID](https://docs.python.org/3/library/uuid.html) 