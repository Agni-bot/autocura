# Handlers

Este documento descreve os handlers disponíveis no módulo de integração.

## 📨 Handler de Mensagens

### MessageHandler

```python
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from .models import Mensagem, TipoMensagem

class MessageHandler(ABC):
    @abstractmethod
    async def handle(self, message: Mensagem) -> None:
        """
        Processa uma mensagem.
        
        Args:
            message: Mensagem a ser processada
        """
        pass
```

## 📧 Handler de Email

### EmailHandler

```python
from typing import Optional
from .models import Mensagem, TipoMensagem
from .adapters import EmailAdapter

class EmailHandler(MessageHandler):
    def __init__(self, adapter: EmailAdapter):
        self.adapter = adapter
        
    async def handle(self, message: Mensagem) -> None:
        """
        Processa um email.
        
        Args:
            message: Email a ser processado
        """
        # Validar mensagem
        if message.tipo != TipoMensagem.EMAIL:
            raise ValueError("Tipo de mensagem inválido")
            
        # Processar email
        await self.adapter.send(message)
```

## 💬 Handler de Chat

### ChatHandler

```python
from typing import Optional
from .models import Mensagem, TipoMensagem
from .adapters import ChatAdapter

class ChatHandler(MessageHandler):
    def __init__(self, adapter: ChatAdapter):
        self.adapter = adapter
        
    async def handle(self, message: Mensagem) -> None:
        """
        Processa uma mensagem de chat.
        
        Args:
            message: Mensagem a ser processada
        """
        # Validar mensagem
        if message.tipo != TipoMensagem.CHAT:
            raise ValueError("Tipo de mensagem inválido")
            
        # Processar mensagem
        await self.adapter.send(message)
```

## 📱 Handler de SMS

### SMSHandler

```python
from typing import Optional
from .models import Mensagem, TipoMensagem
from .adapters import SMSAdapter

class SMSHandler(MessageHandler):
    def __init__(self, adapter: SMSAdapter):
        self.adapter = adapter
        
    async def handle(self, message: Mensagem) -> None:
        """
        Processa um SMS.
        
        Args:
            message: SMS a ser processado
        """
        # Validar mensagem
        if message.tipo != TipoMensagem.SMS:
            raise ValueError("Tipo de mensagem inválido")
            
        # Processar SMS
        await self.adapter.send(message)
```

## 🔄 Handler de Eventos

### EventHandler

```python
from typing import Dict, Type
from .models import Mensagem, TipoMensagem
from .handlers import MessageHandler

class EventHandler:
    def __init__(self):
        self.handlers: Dict[TipoMensagem, MessageHandler] = {}
        
    def register(self, tipo: TipoMensagem, handler: MessageHandler) -> None:
        """
        Registra um handler para um tipo de mensagem.
        
        Args:
            tipo: Tipo de mensagem
            handler: Handler a ser registrado
        """
        self.handlers[tipo] = handler
        
    async def handle(self, message: Mensagem) -> None:
        """
        Processa uma mensagem usando o handler apropriado.
        
        Args:
            message: Mensagem a ser processada
            
        Raises:
            ValueError: Se não houver handler registrado para o tipo
        """
        handler = self.handlers.get(message.tipo)
        if not handler:
            raise ValueError(f"Handler não encontrado para tipo {message.tipo}")
            
        await handler.handle(message)
```

## 📝 Exemplo de Uso

```python
from fastapi import FastAPI, Depends
from .handlers import (
    MessageHandler,
    EmailHandler,
    ChatHandler,
    SMSHandler,
    EventHandler
)
from .adapters import (
    EmailAdapter,
    ChatAdapter,
    SMSAdapter
)

# Configuração
app = FastAPI()

# Adaptadores
email_adapter = EmailAdapter(
    host="smtp.gmail.com",
    port=587,
    username="seu_email@gmail.com",
    password="sua_senha"
)

chat_adapter = ChatAdapter(
    api_url="https://api.chat.com",
    api_key="sua_api_key",
    channel="geral"
)

sms_adapter = SMSAdapter(
    api_url="https://api.sms.com",
    api_key="sua_api_key",
    from_number="+5511999999999"
)

# Handlers
email_handler = EmailHandler(email_adapter)
chat_handler = ChatHandler(chat_adapter)
sms_handler = SMSHandler(sms_adapter)

# Event Handler
event_handler = EventHandler()
event_handler.register(TipoMensagem.EMAIL, email_handler)
event_handler.register(TipoMensagem.CHAT, chat_handler)
event_handler.register(TipoMensagem.SMS, sms_handler)

# Dependências
def get_event_handler():
    return event_handler

# Rotas
@app.post("/messages")
async def process_message(
    message: Mensagem,
    handler: EventHandler = Depends(get_event_handler)
):
    await handler.handle(message)
    return {"status": "success"}
```

## 📚 Referências

- [Python ABC](https://docs.python.org/3/library/abc.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Python Design Patterns](https://python-patterns.guide/)
- [Python Async IO](https://docs.python.org/3/library/asyncio.html)
- [Python Exceptions](https://docs.python.org/3/tutorial/errors.html) 