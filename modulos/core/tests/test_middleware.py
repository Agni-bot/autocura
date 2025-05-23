"""Testes do middleware de comunicação."""

import asyncio
import pytest
from ..src.events import EventBus
from ..src.middleware import Message, Middleware
from ..src.interfaces import ModuleInterface

class MockModule(ModuleInterface):
    """Módulo mock para testes."""
    
    def __init__(self, module_id: str):
        self.module_id = module_id
        self.received_messages = []
    
    async def initialize(self) -> None:
        pass
    
    async def shutdown(self) -> None:
        pass
    
    async def health_check(self) -> dict:
        return {"status": "ok"}

@pytest.fixture
def event_bus():
    """Fixture que retorna uma instância do EventBus."""
    return EventBus()

@pytest.fixture
def middleware(event_bus):
    """Fixture que retorna uma instância do Middleware."""
    return Middleware(event_bus)

@pytest.fixture
def mock_module():
    """Fixture que retorna um módulo mock."""
    return MockModule("test_module")

@pytest.mark.asyncio
async def test_register_module(middleware, mock_module):
    """Testa registro de módulo."""
    # Registra o módulo
    await middleware.register_module("test_module", mock_module)
    
    # Verifica se está registrado
    assert middleware.is_module_registered("test_module")
    assert "test_module" in middleware.get_registered_modules()

@pytest.mark.asyncio
async def test_unregister_module(middleware, mock_module):
    """Testa remoção de registro de módulo."""
    # Registra o módulo
    await middleware.register_module("test_module", mock_module)
    
    # Remove registro
    await middleware.unregister_module("test_module")
    
    # Verifica se foi removido
    assert not middleware.is_module_registered("test_module")
    assert "test_module" not in middleware.get_registered_modules()

@pytest.mark.asyncio
async def test_send_message(middleware, mock_module):
    """Testa envio de mensagem entre módulos."""
    # Registra o módulo
    await middleware.register_module("test_module", mock_module)
    
    # Envia mensagem
    test_content = {"test": "data"}
    await middleware.send_message(
        source="sender",
        target="test_module",
        content=test_content,
        message_type="test"
    )
    
    # Aguarda processamento assíncrono
    await asyncio.sleep(0.1)
    
    # Verifica se a mensagem foi recebida
    assert len(mock_module.received_messages) == 1
    assert mock_module.received_messages[0].content == test_content

@pytest.mark.asyncio
async def test_broadcast(middleware):
    """Testa broadcast de mensagem."""
    # Cria e registra múltiplos módulos
    modules = {
        "module1": MockModule("module1"),
        "module2": MockModule("module2"),
        "module3": MockModule("module3")
    }
    
    for module_id, module in modules.items():
        await middleware.register_module(module_id, module)
    
    # Faz broadcast de uma mensagem
    test_content = {"test": "broadcast"}
    await middleware.broadcast(
        source="sender",
        content=test_content,
        message_type="broadcast"
    )
    
    # Aguarda processamento assíncrono
    await asyncio.sleep(0.1)
    
    # Verifica se todos os módulos receberam
    for module in modules.values():
        assert len(module.received_messages) == 1
        assert module.received_messages[0].content == test_content

@pytest.mark.asyncio
async def test_message_handler(middleware):
    """Testa registro e execução de handlers de mensagem."""
    received_messages = []
    
    async def message_handler(message: Message):
        received_messages.append(message)
    
    # Registra o handler
    await middleware.register_message_handler("test_type", message_handler)
    
    # Envia mensagem do tipo testado
    test_content = {"test": "handler"}
    await middleware.send_message(
        source="sender",
        target="test_module",
        content=test_content,
        message_type="test_type"
    )
    
    # Aguarda processamento assíncrono
    await asyncio.sleep(0.1)
    
    # Verifica se o handler foi executado
    assert len(received_messages) == 1
    assert received_messages[0].content == test_content

@pytest.mark.asyncio
async def test_error_handling(middleware, mock_module):
    """Testa tratamento de erros no middleware."""
    error_messages = []
    
    async def error_handler(message: Message):
        raise Exception("Test error")
    
    async def error_logger(message: Message):
        error_messages.append(message)
    
    # Registra handlers
    await middleware.register_message_handler("error_type", error_handler)
    await middleware.register_message_handler("error_type", error_logger)
    
    # Envia mensagem que causará erro
    await middleware.send_message(
        source="sender",
        target="test_module",
        content={"test": "error"},
        message_type="error_type"
    )
    
    # Aguarda processamento assíncrono
    await asyncio.sleep(0.1)
    
    # Verifica se o segundo handler ainda foi executado
    assert len(error_messages) == 1 