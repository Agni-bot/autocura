# Serviços

Este documento descreve os serviços disponíveis no módulo de integração.

## 📨 Serviço de Mensagens

### MessageService

```python
from typing import List, Optional
from datetime import datetime
from .models import Mensagem, TipoMensagem, StatusMensagem

class MessageService:
    def __init__(self, redis_client, kafka_producer):
        self.redis = redis_client
        self.kafka = kafka_producer
        
    async def send(self, message: Mensagem) -> Mensagem:
        """
        Envia uma mensagem para processamento.
        
        Args:
            message: Mensagem a ser enviada
            
        Returns:
            Mensagem: Mensagem enviada com status atualizado
            
        Raises:
            Exception: Se houver erro no processamento
        """
        try:
            # Atualizar status
            message.status = StatusMensagem.PROCESSANDO
            
            # Salvar no Redis
            await self.redis.set(
                f"message:{message.id}",
                message.json(),
                ex=3600
            )
            
            # Publicar no Kafka
            await self.kafka.send_and_wait(
                topic=f"messages.{message.tipo}",
                value=message.json().encode()
            )
            
            # Atualizar status
            message.status = StatusMensagem.CONCLUIDA
            await self.redis.set(
                f"message:{message.id}",
                message.json(),
                ex=3600
            )
            
            return message
            
        except Exception as e:
            message.status = StatusMensagem.ERRO
            message.erro = str(e)
            await self.redis.set(
                f"message:{message.id}",
                message.json(),
                ex=3600
            )
            raise
            
    async def get(self, message_id: str) -> Optional[Mensagem]:
        """
        Obtém uma mensagem pelo ID.
        
        Args:
            message_id: ID da mensagem
            
        Returns:
            Optional[Mensagem]: Mensagem encontrada ou None
        """
        data = await self.redis.get(f"message:{message_id}")
        if data:
            return Mensagem.parse_raw(data)
        return None
        
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        tipo: Optional[TipoMensagem] = None,
        status: Optional[StatusMensagem] = None
    ) -> List[Mensagem]:
        """
        Lista mensagens com filtros opcionais.
        
        Args:
            skip: Número de mensagens para pular
            limit: Limite de mensagens por página
            tipo: Filtrar por tipo de mensagem
            status: Filtrar por status
            
        Returns:
            List[Mensagem]: Lista de mensagens
        """
        # Implementar lógica de listagem
        pass
```

## 📊 Serviço de Métricas

### MetricsService

```python
from typing import List, Optional
from datetime import datetime
from .models import Metrica

class MetricsService:
    def __init__(self, redis_client, prometheus_client):
        self.redis = redis_client
        self.prometheus = prometheus_client
        
    async def record_metric(self, metric: Metrica):
        """
        Registra uma métrica.
        
        Args:
            metric: Métrica a ser registrada
        """
        # Registrar no Prometheus
        self.prometheus.record_metric(
            name=metric.nome,
            value=metric.valor,
            labels=metric.labels
        )
        
        # Salvar no Redis
        await self.redis.zadd(
            f"metrics:{metric.nome}",
            {metric.json(): metric.timestamp.timestamp()}
        )
        
    async def get_metrics(
        self,
        nome: Optional[str] = None,
        tipo: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Metrica]:
        """
        Obtém métricas com filtros opcionais.
        
        Args:
            nome: Filtrar por nome da métrica
            tipo: Filtrar por tipo
            start_time: Data inicial
            end_time: Data final
            
        Returns:
            List[Metrica]: Lista de métricas
        """
        # Implementar lógica de consulta
        pass
```

## 🔔 Serviço de Alertas

### AlertService

```python
from typing import List, Optional
from datetime import datetime
from .models import Alerta

class AlertService:
    def __init__(self, redis_client, kafka_producer):
        self.redis = redis_client
        self.kafka = kafka_producer
        
    async def create_alert(self, alert: Alerta):
        """
        Cria um novo alerta.
        
        Args:
            alert: Alerta a ser criado
        """
        # Salvar no Redis
        await self.redis.set(
            f"alert:{alert.id}",
            alert.json(),
            ex=3600
        )
        
        # Publicar no Kafka
        await self.kafka.send_and_wait(
            topic="alerts",
            value=alert.json().encode()
        )
        
    async def resolve_alert(self, alert_id: str):
        """
        Resolve um alerta.
        
        Args:
            alert_id: ID do alerta
        """
        alert = await self.get_alert(alert_id)
        if alert:
            alert.resolvido = True
            alert.resolvido_em = datetime.utcnow()
            await self.redis.set(
                f"alert:{alert.id}",
                alert.json(),
                ex=3600
            )
            
    async def get_alert(self, alert_id: str) -> Optional[Alerta]:
        """
        Obtém um alerta pelo ID.
        
        Args:
            alert_id: ID do alerta
            
        Returns:
            Optional[Alerta]: Alerta encontrado ou None
        """
        data = await self.redis.get(f"alert:{alert_id}")
        if data:
            return Alerta.parse_raw(data)
        return None
        
    async def get_alerts(
        self,
        severidade: Optional[str] = None,
        resolvido: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Alerta]:
        """
        Obtém alertas com filtros opcionais.
        
        Args:
            severidade: Filtrar por severidade
            resolvido: Filtrar por status de resolução
            start_time: Data inicial
            end_time: Data final
            
        Returns:
            List[Alerta]: Lista de alertas
        """
        # Implementar lógica de consulta
        pass
```

## 🔄 Serviço WebSocket

### WebSocketService

```python
from typing import Set
from fastapi import WebSocket
from .models import Usuario

class WebSocketService:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        """
        Estabelece uma conexão WebSocket.
        
        Args:
            websocket: Conexão WebSocket
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        
    async def disconnect(self, websocket: WebSocket):
        """
        Fecha uma conexão WebSocket.
        
        Args:
            websocket: Conexão WebSocket
        """
        self.active_connections.remove(websocket)
        
    async def broadcast(self, message: str):
        """
        Envia uma mensagem para todas as conexões ativas.
        
        Args:
            message: Mensagem a ser enviada
        """
        for connection in self.active_connections:
            await connection.send_text(message)
            
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Envia uma mensagem para uma conexão específica.
        
        Args:
            message: Mensagem a ser enviada
            websocket: Conexão WebSocket
        """
        await websocket.send_text(message)
```

## 📝 Exemplo de Uso

```python
from fastapi import FastAPI, Depends
from redis import Redis
from aiokafka import AIOKafkaProducer
from prometheus_client import CollectorRegistry

# Configuração
app = FastAPI()
redis_client = Redis()
kafka_producer = AIOKafkaProducer()
prometheus_client = CollectorRegistry()

# Serviços
message_service = MessageService(redis_client, kafka_producer)
metrics_service = MetricsService(redis_client, prometheus_client)
alert_service = AlertService(redis_client, kafka_producer)
ws_service = WebSocketService()

# Dependências
def get_message_service():
    return message_service

def get_metrics_service():
    return metrics_service

def get_alert_service():
    return alert_service

def get_ws_service():
    return ws_service

# Rotas
@app.post("/messages")
async def send_message(
    message: Mensagem,
    service: MessageService = Depends(get_message_service)
):
    return await service.send(message)

@app.get("/metrics")
async def get_metrics(
    service: MetricsService = Depends(get_metrics_service)
):
    return await service.get_metrics()

@app.get("/alerts")
async def get_alerts(
    service: AlertService = Depends(get_alert_service)
):
    return await service.get_alerts()

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    service: WebSocketService = Depends(get_ws_service)
):
    await service.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await service.broadcast(data)
    except WebSocketDisconnect:
        await service.disconnect(websocket)
```

## 📚 Referências

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [Python Async IO](https://docs.python.org/3/library/asyncio.html) 