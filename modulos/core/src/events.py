"""Sistema de eventos do módulo core."""

import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

from .interfaces import EventInterface
from .config.config import config
from .logging import logger

class EventSystem(EventInterface):
    """Sistema de eventos assíncrono."""
    
    def __init__(self):
        """Inicializa o sistema de eventos."""
        self._handlers: Dict[str, List[Callable]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._history: List[Dict[str, Any]] = []
        self._max_history = config.EVENT_HISTORY_SIZE
        
    async def initialize(self) -> None:
        """Inicializa o sistema de eventos."""
        if self._running:
            return
            
        self._running = True
        asyncio.create_task(self._process_events())
        await logger.log("INFO", "Sistema de eventos inicializado")
        
    async def shutdown(self) -> None:
        """Desliga o sistema de eventos."""
        if not self._running:
            return
            
        self._running = False
        await logger.log("INFO", "Sistema de eventos desligado")
        
    async def publish(self, event_type: str, data: Any) -> None:
        """Publica um evento."""
        if not self._running:
            await logger.log("WARNING", "Tentativa de publicar evento com sistema desligado",
                           event_type=event_type)
            return
            
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now()
        }
        
        # Adiciona ao histórico
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
            
        # Envia para a fila
        await self._queue.put(event)
        await logger.log("DEBUG", f"Evento publicado: {event_type}")
        
    async def subscribe(self, event_type: str, handler: Callable) -> None:
        """Inscreve um handler para um tipo de evento."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
            
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            await logger.log("DEBUG", f"Handler inscrito para evento: {event_type}")
            
    async def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Cancela a inscrição de um handler."""
        if event_type in self._handlers:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                await logger.log("DEBUG", f"Handler removido do evento: {event_type}")
                
    async def _process_events(self) -> None:
        """Processa eventos da fila."""
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=config.EVENT_PROCESSING_TIMEOUT
                )
                
                event_type = event["type"]
                if event_type in self._handlers:
                    for handler in self._handlers[event_type]:
                        try:
                            await handler(event["data"])
                        except Exception as e:
                            await logger.log("ERROR", f"Erro ao processar evento {event_type}: {e}")
                            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                await logger.log("ERROR", f"Erro no processamento de eventos: {e}")
                
    async def get_event_history(self, event_type: Optional[str] = None,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Recupera histórico de eventos."""
        filtered_history = self._history
        
        if event_type:
            filtered_history = [e for e in filtered_history if e["type"] == event_type]
            
        if start_time:
            filtered_history = [e for e in filtered_history if e["timestamp"] >= start_time]
            
        if end_time:
            filtered_history = [e for e in filtered_history if e["timestamp"] <= end_time]
            
        return filtered_history
        
    async def clear_history(self) -> None:
        """Limpa o histórico de eventos."""
        self._history.clear()
        await logger.log("INFO", "Histórico de eventos limpo")
        
    def get_subscribers(self, event_type: str) -> List[Callable]:
        """Retorna lista de handlers inscritos em um tipo de evento."""
        return self._handlers.get(event_type, [])

# Instância global do sistema de eventos
events = EventSystem() 