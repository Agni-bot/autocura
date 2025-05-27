"""Interfaces base consolidadas do sistema de autocura."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class HealthStatus:
    """Status de saúde de um módulo."""
    status: str
    details: Dict[str, Any]
    timestamp: datetime
    version: str

@dataclass
class Message:
    """Mensagem para comunicação entre módulos."""
    source: str
    target: str
    type: str
    payload: Any
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class Response:
    """Resposta de um módulo."""
    success: bool
    data: Any
    error: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]

class ModuleInterface(ABC):
    """Interface base para todos os módulos do sistema."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Inicializa o módulo."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Desliga o módulo de forma segura."""
        pass
    
    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """Verifica a saúde do módulo."""
        pass
    
    @abstractmethod
    async def process_message(self, message: Message) -> Response:
        """Processa uma mensagem recebida."""
        pass

class EventInterface(ABC):
    """Interface para o sistema de eventos."""
    
    @abstractmethod
    async def publish(self, event_type: str, data: Any) -> None:
        """Publica um evento."""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: callable) -> None:
        """Inscreve um handler para um tipo de evento."""
        pass
    
    @abstractmethod
    async def unsubscribe(self, event_type: str, handler: callable) -> None:
        """Cancela a inscrição de um handler."""
        pass

class StorageInterface(ABC):
    """Interface para armazenamento de dados."""
    
    @abstractmethod
    async def store(self, key: str, value: Any) -> None:
        """Armazena um valor."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Any:
        """Recupera um valor."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove um valor."""
        pass
    
    @abstractmethod
    async def list_keys(self, pattern: str) -> List[str]:
        """Lista chaves que correspondem a um padrão."""
        pass

class LoggingInterface(ABC):
    """Interface para logging."""
    
    @abstractmethod
    async def log(self, level: str, message: str, **kwargs) -> None:
        """Registra uma mensagem de log."""
        pass
    
    @abstractmethod
    async def get_logs(self, level: Optional[str] = None, 
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Recupera logs com filtros opcionais."""
        pass

class MetricsInterface(ABC):
    """Interface para métricas."""
    
    @abstractmethod
    async def record_metric(self, name: str, value: float, 
                          tags: Optional[Dict[str, str]] = None) -> None:
        """Registra uma métrica."""
        pass
    
    @abstractmethod
    async def get_metric(self, name: str, 
                        tags: Optional[Dict[str, str]] = None) -> float:
        """Recupera o valor de uma métrica."""
        pass
    
    @abstractmethod
    async def list_metrics(self, pattern: str) -> List[str]:
        """Lista métricas que correspondem a um padrão."""
        pass

class SecurityInterface(ABC):
    """Interface para segurança."""
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Autentica um usuário ou serviço."""
        pass
    
    @abstractmethod
    async def authorize(self, subject: str, action: str, 
                       resource: str) -> bool:
        """Verifica se um sujeito tem permissão para uma ação."""
        pass
    
    @abstractmethod
    async def encrypt(self, data: Any) -> bytes:
        """Criptografa dados."""
        pass
    
    @abstractmethod
    async def decrypt(self, data: bytes) -> Any:
        """Descriptografa dados."""
        pass 