# Adaptadores

Este documento descreve os adaptadores disponíveis no módulo de integração.

## 📨 Adaptador de Mensagens

### MessageAdapter

```python
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from .models import Mensagem, TipoMensagem

class MessageAdapter(ABC):
    @abstractmethod
    async def send(self, message: Mensagem) -> None:
        """
        Envia uma mensagem.
        
        Args:
            message: Mensagem a ser enviada
        """
        pass
        
    @abstractmethod
    async def receive(self) -> Optional[Mensagem]:
        """
        Recebe uma mensagem.
        
        Returns:
            Optional[Mensagem]: Mensagem recebida ou None
        """
        pass
        
    @abstractmethod
    async def acknowledge(self, message_id: str) -> None:
        """
        Confirma o recebimento de uma mensagem.
        
        Args:
            message_id: ID da mensagem
        """
        pass
```

## 📧 Adaptador de Email

### EmailAdapter

```python
from typing import List, Optional
from .models import Mensagem
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAdapter(MessageAdapter):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        
    async def send(self, message: Mensagem) -> None:
        """
        Envia um email.
        
        Args:
            message: Mensagem contendo dados do email
        """
        # Criar mensagem
        email = MIMEMultipart()
        email["From"] = self.username
        email["To"] = message.destino
        email["Subject"] = message.metadata.get("subject", "")
        
        # Adicionar corpo
        email.attach(MIMEText(message.payload, "plain"))
        
        # Enviar email
        async with aiosmtplib.SMTP(
            hostname=self.host,
            port=self.port,
            use_tls=self.use_tls
        ) as smtp:
            await smtp.login(self.username, self.password)
            await smtp.send_message(email)
            
    async def receive(self) -> Optional[Mensagem]:
        """
        Recebe um email.
        
        Returns:
            Optional[Mensagem]: Email recebido ou None
        """
        # Implementar lógica de recebimento
        pass
        
    async def acknowledge(self, message_id: str) -> None:
        """
        Confirma o recebimento de um email.
        
        Args:
            message_id: ID do email
        """
        # Implementar lógica de confirmação
        pass
```

## 💬 Adaptador de Chat

### ChatAdapter

```python
from typing import List, Optional
from .models import Mensagem
import aiohttp
import json

class ChatAdapter(MessageAdapter):
    def __init__(
        self,
        api_url: str,
        api_key: str,
        channel: str
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.channel = channel
        
    async def send(self, message: Mensagem) -> None:
        """
        Envia uma mensagem de chat.
        
        Args:
            message: Mensagem a ser enviada
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/messages",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "channel": self.channel,
                    "text": message.payload,
                    "metadata": message.metadata
                }
            ) as response:
                if response.status != 200:
                    raise Exception("Erro ao enviar mensagem")
                    
    async def receive(self) -> Optional[Mensagem]:
        """
        Recebe uma mensagem de chat.
        
        Returns:
            Optional[Mensagem]: Mensagem recebida ou None
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/messages",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                },
                params={"channel": self.channel}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return Mensagem(
                            id=data["id"],
                            tipo=TipoMensagem.CHAT,
                            origem=data["user"],
                            destino=self.channel,
                            payload=data["text"],
                            metadata=data.get("metadata", {})
                        )
        return None
        
    async def acknowledge(self, message_id: str) -> None:
        """
        Confirma o recebimento de uma mensagem.
        
        Args:
            message_id: ID da mensagem
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/messages/{message_id}/ack",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                }
            ) as response:
                if response.status != 200:
                    raise Exception("Erro ao confirmar mensagem")
```

## 📱 Adaptador de SMS

### SMSAdapter

```python
from typing import Optional
from .models import Mensagem
import aiohttp
import json

class SMSAdapter(MessageAdapter):
    def __init__(
        self,
        api_url: str,
        api_key: str,
        from_number: str
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.from_number = from_number
        
    async def send(self, message: Mensagem) -> None:
        """
        Envia um SMS.
        
        Args:
            message: Mensagem a ser enviada
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/messages",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": self.from_number,
                    "to": message.destino,
                    "text": message.payload
                }
            ) as response:
                if response.status != 200:
                    raise Exception("Erro ao enviar SMS")
                    
    async def receive(self) -> Optional[Mensagem]:
        """
        Recebe um SMS.
        
        Returns:
            Optional[Mensagem]: SMS recebido ou None
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/messages",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return Mensagem(
                            id=data["id"],
                            tipo=TipoMensagem.SMS,
                            origem=data["from"],
                            destino=data["to"],
                            payload=data["text"]
                        )
        return None
        
    async def acknowledge(self, message_id: str) -> None:
        """
        Confirma o recebimento de um SMS.
        
        Args:
            message_id: ID do SMS
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/messages/{message_id}/ack",
                headers={
                    "Authorization": f"Bearer {self.api_key}"
                }
            ) as response:
                if response.status != 200:
                    raise Exception("Erro ao confirmar SMS")
```

## 📝 Exemplo de Uso

```python
from fastapi import FastAPI, Depends
from .adapters import (
    MessageAdapter,
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

# Dependências
def get_email_adapter():
    return email_adapter

def get_chat_adapter():
    return chat_adapter

def get_sms_adapter():
    return sms_adapter

# Rotas
@app.post("/email")
async def send_email(
    message: Mensagem,
    adapter: EmailAdapter = Depends(get_email_adapter)
):
    await adapter.send(message)
    return {"status": "success"}

@app.post("/chat")
async def send_chat(
    message: Mensagem,
    adapter: ChatAdapter = Depends(get_chat_adapter)
):
    await adapter.send(message)
    return {"status": "success"}

@app.post("/sms")
async def send_sms(
    message: Mensagem,
    adapter: SMSAdapter = Depends(get_sms_adapter)
):
    await adapter.send(message)
    return {"status": "success"}
```

## 📚 Referências

- [Python Async IO](https://docs.python.org/3/library/asyncio.html)
- [aiohttp](https://docs.aiohttp.org/)
- [aiosmtplib](https://aiosmtplib.readthedocs.io/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Python ABC](https://docs.python.org/3/library/abc.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html) 