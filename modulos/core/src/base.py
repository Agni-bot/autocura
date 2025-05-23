"""Implementações base do sistema de autocura."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from .interfaces import (
    ModuleInterface, EventInterface, StorageInterface,
    LoggingInterface, MetricsInterface, SecurityInterface,
    HealthStatus, Message, Response
)

class BaseModule(ModuleInterface):
    """Implementação base de um módulo."""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self._initialized = False
        self._shutdown = False
        self._dependencies: Dict[str, ModuleInterface] = {}
        self._event_handlers: Dict[str, List[callable]] = {}
        
    async def initialize(self) -> None:
        """Inicializa o módulo."""
        if self._initialized:
            return
            
        self._initialized = True
        self._shutdown = False
        
        # Inicializa dependências
        for dep in self._dependencies.values():
            await dep.initialize()
            
    async def shutdown(self) -> None:
        """Desliga o módulo de forma segura."""
        if self._shutdown:
            return
            
        self._shutdown = True
        self._initialized = False
        
        # Desliga dependências
        for dep in self._dependencies.values():
            await dep.shutdown()
            
    async def health_check(self) -> HealthStatus:
        """Verifica a saúde do módulo."""
        return HealthStatus(
            status="healthy" if self._initialized and not self._shutdown else "unhealthy",
            details={
                "name": self.name,
                "version": self.version,
                "initialized": self._initialized,
                "shutdown": self._shutdown,
                "dependencies": {
                    name: await dep.health_check()
                    for name, dep in self._dependencies.items()
                }
            },
            timestamp=datetime.now(),
            version=self.version
        )
        
    async def process_message(self, message: Message) -> Response:
        """Processa uma mensagem recebida."""
        if not self._initialized or self._shutdown:
            return Response(
                success=False,
                data=None,
                error="Module not initialized or shutdown",
                timestamp=datetime.now(),
                metadata={}
            )
            
        try:
            handler = getattr(self, f"handle_{message.type}", None)
            if handler:
                result = await handler(message.payload)
                return Response(
                    success=True,
                    data=result,
                    error=None,
                    timestamp=datetime.now(),
                    metadata={}
                )
            else:
                return Response(
                    success=False,
                    data=None,
                    error=f"No handler for message type: {message.type}",
                    timestamp=datetime.now(),
                    metadata={}
                )
        except Exception as e:
            return Response(
                success=False,
                data=None,
                error=str(e),
                timestamp=datetime.now(),
                metadata={}
            )
            
    def add_dependency(self, name: str, module: ModuleInterface) -> None:
        """Adiciona uma dependência ao módulo."""
        self._dependencies[name] = module
        
    def remove_dependency(self, name: str) -> None:
        """Remove uma dependência do módulo."""
        self._dependencies.pop(name, None)

class BaseEventSystem(EventInterface):
    """Implementação base do sistema de eventos."""
    
    def __init__(self):
        self._handlers: Dict[str, List[callable]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        
    async def initialize(self) -> None:
        """Inicializa o sistema de eventos."""
        self._running = True
        asyncio.create_task(self._process_events())
        
    async def shutdown(self) -> None:
        """Desliga o sistema de eventos."""
        self._running = False
        
    async def publish(self, event_type: str, data: Any) -> None:
        """Publica um evento."""
        await self._queue.put((event_type, data))
        
    async def subscribe(self, event_type: str, handler: callable) -> None:
        """Inscreve um handler para um tipo de evento."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    async def unsubscribe(self, event_type: str, handler: callable) -> None:
        """Cancela a inscrição de um handler."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
            
    async def _process_events(self) -> None:
        """Processa eventos da fila."""
        while self._running:
            try:
                event_type, data = await self._queue.get()
                if event_type in self._handlers:
                    for handler in self._handlers[event_type]:
                        try:
                            await handler(data)
                        except Exception as e:
                            logging.error(f"Error processing event {event_type}: {e}")
            except Exception as e:
                logging.error(f"Error in event processing loop: {e}")

class BaseStorage(StorageInterface):
    """Implementação base do sistema de armazenamento."""
    
    def __init__(self):
        self._storage: Dict[str, Any] = {}
        
    async def store(self, key: str, value: Any) -> None:
        """Armazena um valor."""
        self._storage[key] = value
        
    async def retrieve(self, key: str) -> Any:
        """Recupera um valor."""
        return self._storage.get(key)
        
    async def delete(self, key: str) -> None:
        """Remove um valor."""
        self._storage.pop(key, None)
        
    async def list_keys(self, pattern: str) -> List[str]:
        """Lista chaves que correspondem a um padrão."""
        import re
        regex = re.compile(pattern)
        return [k for k in self._storage.keys() if regex.match(k)]

class BaseLogger(LoggingInterface):
    """Implementação base do sistema de logging."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._logs: List[Dict[str, Any]] = []
        
    async def log(self, level: str, message: str, **kwargs) -> None:
        """Registra uma mensagem de log."""
        log_entry = {
            "level": level,
            "message": message,
            "timestamp": datetime.now(),
            **kwargs
        }
        self._logs.append(log_entry)
        getattr(self.logger, level.lower())(message, extra=kwargs)
        
    async def get_logs(self, level: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Recupera logs com filtros opcionais."""
        filtered_logs = self._logs
        
        if level:
            filtered_logs = [log for log in filtered_logs if log["level"] == level]
            
        if start_time:
            filtered_logs = [log for log in filtered_logs 
                           if log["timestamp"] >= start_time]
            
        if end_time:
            filtered_logs = [log for log in filtered_logs 
                           if log["timestamp"] <= end_time]
            
        return filtered_logs

class BaseMetrics(MetricsInterface):
    """Implementação base do sistema de métricas."""
    
    def __init__(self):
        self._metrics: Dict[str, Dict[str, float]] = {}
        
    async def record_metric(self, name: str, value: float,
                          tags: Optional[Dict[str, str]] = None) -> None:
        """Registra uma métrica."""
        if name not in self._metrics:
            self._metrics[name] = {}
            
        tag_key = str(tags) if tags else "default"
        self._metrics[name][tag_key] = value
        
    async def get_metric(self, name: str,
                        tags: Optional[Dict[str, str]] = None) -> float:
        """Recupera o valor de uma métrica."""
        if name not in self._metrics:
            return 0.0
            
        tag_key = str(tags) if tags else "default"
        return self._metrics[name].get(tag_key, 0.0)
        
    async def list_metrics(self, pattern: str) -> List[str]:
        """Lista métricas que correspondem a um padrão."""
        import re
        regex = re.compile(pattern)
        return [k for k in self._metrics.keys() if regex.match(k)]

class BaseSecurity(SecurityInterface):
    """Implementação base do sistema de segurança."""
    
    def __init__(self):
        self._users: Dict[str, Dict[str, Any]] = {}
        self._permissions: Dict[str, Dict[str, List[str]]] = {}
        
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Autentica um usuário ou serviço."""
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not username or not password:
            return False
            
        user = self._users.get(username)
        if not user:
            return False
            
        return user.get("password") == password
        
    async def authorize(self, subject: str, action: str,
                       resource: str) -> bool:
        """Verifica se um sujeito tem permissão para uma ação."""
        if subject not in self._permissions:
            return False
            
        resource_perms = self._permissions[subject].get(resource, [])
        return action in resource_perms
        
    async def encrypt(self, data: Any) -> bytes:
        """Criptografa dados."""
        # Implementação básica - em produção usar biblioteca de criptografia
        return str(data).encode()
        
    async def decrypt(self, data: bytes) -> Any:
        """Descriptografa dados."""
        # Implementação básica - em produção usar biblioteca de criptografia
        return data.decode() 