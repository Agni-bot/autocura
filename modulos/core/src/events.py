"""Sistema de eventos do core."""

import asyncio
from typing import Any, Dict, List, Optional, Set
from .interfaces import EventInterface

class Event:
    """Representa um evento no sistema."""
    
    def __init__(self, type: str, data: Dict[str, Any], 
                 timestamp: Optional[float] = None):
        self.type = type
        self.data = data
        self.timestamp = timestamp or asyncio.get_event_loop().time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o evento para dicionário."""
        return {
            'type': self.type,
            'data': self.data,
            'timestamp': self.timestamp
        }

class EventBus(EventInterface):
    """Implementação do sistema de eventos."""
    
    def __init__(self):
        self._subscribers: Dict[str, Set[callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = 1000
    
    async def publish(self, event: Dict[str, Any], topic: str) -> None:
        """Publica um evento em um tópico."""
        event_obj = Event(type=topic, data=event)
        self._event_history.append(event_obj)
        
        # Limita o tamanho do histórico
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]
        
        # Notifica os subscribers
        if topic in self._subscribers:
            for handler in self._subscribers[topic]:
                try:
                    await handler(event_obj)
                except Exception as e:
                    # Log do erro mas não interrompe a execução
                    print(f"Erro ao processar evento {topic}: {str(e)}")
    
    async def subscribe(self, topic: str, handler: callable) -> None:
        """Inscreve um handler para um tópico."""
        if topic not in self._subscribers:
            self._subscribers[topic] = set()
        self._subscribers[topic].add(handler)
    
    async def unsubscribe(self, topic: str, handler: callable) -> None:
        """Remove a inscrição de um handler."""
        if topic in self._subscribers and handler in self._subscribers[topic]:
            self._subscribers[topic].remove(handler)
    
    def get_event_history(self, topic: Optional[str] = None, 
                         limit: int = 100) -> List[Event]:
        """Recupera o histórico de eventos."""
        if topic:
            events = [e for e in self._event_history if e.type == topic]
        else:
            events = self._event_history
        return events[-limit:]
    
    def clear_history(self) -> None:
        """Limpa o histórico de eventos."""
        self._event_history.clear() 