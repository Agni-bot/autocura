"""Middleware de comunicação entre módulos."""

import asyncio
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from .interfaces import ModuleInterface, EventInterface

T = TypeVar('T')

class Message(Generic[T]):
    """Representa uma mensagem entre módulos."""
    
    def __init__(self, source: str, target: str, content: T,
                 message_type: str = "default"):
        self.source = source
        self.target = target
        self.content = content
        self.type = message_type
        self.timestamp = asyncio.get_event_loop().time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a mensagem para dicionário."""
        return {
            'source': self.source,
            'target': self.target,
            'content': self.content,
            'type': self.type,
            'timestamp': self.timestamp
        }

class Middleware:
    """Middleware para comunicação entre módulos."""
    
    def __init__(self, event_bus: EventInterface):
        self._event_bus = event_bus
        self._modules: Dict[str, ModuleInterface] = {}
        self._message_handlers: Dict[str, List[Callable]] = {}
    
    async def register_module(self, module_id: str, 
                            module: ModuleInterface) -> None:
        """Registra um módulo no middleware."""
        self._modules[module_id] = module
        await self._event_bus.subscribe(f"message.{module_id}", 
                                      self._handle_message)
    
    async def unregister_module(self, module_id: str) -> None:
        """Remove o registro de um módulo."""
        if module_id in self._modules:
            del self._modules[module_id]
            await self._event_bus.unsubscribe(f"message.{module_id}", 
                                            self._handle_message)
    
    async def send_message(self, source: str, target: str, 
                          content: Any, message_type: str = "default") -> None:
        """Envia uma mensagem entre módulos."""
        message = Message(source=source, target=target, 
                         content=content, message_type=message_type)
        await self._event_bus.publish(message.to_dict(), 
                                    f"message.{target}")
    
    async def register_message_handler(self, message_type: str, 
                                     handler: Callable) -> None:
        """Registra um handler para um tipo de mensagem."""
        if message_type not in self._message_handlers:
            self._message_handlers[message_type] = []
        self._message_handlers[message_type].append(handler)
    
    async def _handle_message(self, event: Any) -> None:
        """Processa uma mensagem recebida."""
        message = Message(**event.data)
        
        # Executa handlers específicos do tipo de mensagem
        if message.type in self._message_handlers:
            for handler in self._message_handlers[message.type]:
                try:
                    await handler(message)
                except Exception as e:
                    print(f"Erro ao processar mensagem {message.type}: {str(e)}")
    
    async def broadcast(self, source: str, content: Any, 
                       message_type: str = "default") -> None:
        """Envia uma mensagem para todos os módulos."""
        for module_id in self._modules:
            if module_id != source:
                await self.send_message(source, module_id, 
                                      content, message_type)
    
    def get_registered_modules(self) -> List[str]:
        """Retorna a lista de módulos registrados."""
        return list(self._modules.keys())
    
    def is_module_registered(self, module_id: str) -> bool:
        """Verifica se um módulo está registrado."""
        return module_id in self._modules 