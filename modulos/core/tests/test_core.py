"""Testes do módulo core."""

import pytest
import asyncio
from datetime import datetime, timedelta

from ..src import (
    ModuleInterface, EventInterface, StorageInterface,
    LoggingInterface, MetricsInterface, SecurityInterface,
    BaseModule, BaseEventSystem, BaseStorage,
    BaseLogger, BaseMetrics, BaseSecurity,
    config, logger, metrics, events, storage, security
)

class TestModule(BaseModule):
    """Módulo de teste."""
    
    def __init__(self):
        super().__init__("test", "0.1.0")
        
    async def handle_test(self, data: dict) -> dict:
        """Handler de teste."""
        return {"received": data}

@pytest.fixture
async def test_module():
    """Fixture para módulo de teste."""
    module = TestModule()
    await module.initialize()
    yield module
    await module.shutdown()

@pytest.mark.asyncio
async def test_module_lifecycle():
    """Testa ciclo de vida do módulo."""
    module = TestModule()
    
    # Inicialização
    assert not module._initialized
    await module.initialize()
    assert module._initialized
    
    # Health check
    health = await module.health_check()
    assert health.status == "healthy"
    assert health.version == "0.1.0"
    
    # Processamento de mensagem
    message = {
        "source": "test",
        "target": "test",
        "type": "test",
        "payload": {"data": "test"},
        "timestamp": datetime.now(),
        "metadata": {}
    }
    response = await module.process_message(message)
    assert response.success
    assert response.data == {"received": {"data": "test"}}
    
    # Shutdown
    await module.shutdown()
    assert not module._initialized

@pytest.mark.asyncio
async def test_event_system():
    """Testa sistema de eventos."""
    # Inicialização
    await events.initialize()
    
    # Publicação e subscrição
    received_events = []
    
    async def handler(data):
        received_events.append(data)
        
    await events.subscribe("test", handler)
    await events.publish("test", {"data": "test"})
    
    # Aguarda processamento
    await asyncio.sleep(0.1)
    assert len(received_events) == 1
    assert received_events[0] == {"data": "test"}
    
    # Histórico
    history = await events.get_event_history("test")
    assert len(history) == 1
    
    # Limpeza
    await events.clear_history()
    history = await events.get_event_history()
    assert len(history) == 0
    
    # Shutdown
    await events.shutdown()

@pytest.mark.asyncio
async def test_storage():
    """Testa sistema de armazenamento."""
    # Inicialização
    await storage.initialize()
    
    # Armazenamento
    await storage.store("test", {"data": "test"})
    value = await storage.retrieve("test")
    assert value == {"data": "test"}
    
    # Listagem
    keys = await storage.list_keys("test.*")
    assert "test" in keys
    
    # Remoção
    await storage.delete("test")
    value = await storage.retrieve("test")
    assert value is None
    
    # Shutdown
    await storage.shutdown()

@pytest.mark.asyncio
async def test_logging():
    """Testa sistema de logging."""
    # Logging
    await logger.log("INFO", "Test message", extra={"test": True})
    
    # Recuperação
    logs = await logger.get_logs(level="INFO")
    assert len(logs) > 0
    assert logs[0]["message"] == "Test message"
    assert logs[0]["test"] is True
    
    # Limpeza
    await logger.clear_logs()
    logs = await logger.get_logs()
    assert len(logs) == 0

@pytest.mark.asyncio
async def test_metrics():
    """Testa sistema de métricas."""
    # Registro
    await metrics.record_metric("test", 1.0, {"tag": "test"})
    value = await metrics.get_metric("test", {"tag": "test"})
    assert value == 1.0
    
    # Histórico
    history = await metrics.get_metric_history("test")
    assert len(history) > 0
    
    # Estatísticas
    stats = await metrics.get_metric_stats("test")
    assert stats["min"] == 1.0
    assert stats["max"] == 1.0
    assert stats["avg"] == 1.0
    assert stats["count"] == 1
    
    # Timer
    async with metrics.Timer(metrics, "test_timer"):
        await asyncio.sleep(0.1)
    
    value = await metrics.get_metric("test_timer_duration")
    assert value > 0

@pytest.mark.asyncio
async def test_security():
    """Testa sistema de segurança."""
    # Inicialização
    await security.initialize()
    
    # Criação de usuário
    await security.create_user("test", "password", {
        "resource": ["read", "write"]
    })
    
    # Autenticação
    auth = await security.authenticate({
        "username": "test",
        "password": "password"
    })
    assert auth is True
    
    # Autorização
    auth = await security.authorize("test", "read", "resource")
    assert auth is True
    
    # Token
    token = await security.generate_token("test")
    assert token != ""
    
    # Validação de token
    valid = await security.validate_token(token)
    assert valid is True
    
    # Atualização de permissões
    await security.update_permissions("test", {
        "resource": ["read"]
    })
    auth = await security.authorize("test", "write", "resource")
    assert auth is False
    
    # Remoção de usuário
    await security.delete_user("test")
    auth = await security.authenticate({
        "username": "test",
        "password": "password"
    })
    assert auth is False
    
    # Shutdown
    await security.shutdown()

@pytest.mark.asyncio
async def test_config():
    """Testa configurações."""
    # Validação
    assert config.validate() is True
    
    # Atualização
    config.update({
        "DEBUG": False,
        "LOG_LEVEL": "ERROR"
    })
    assert config.DEBUG is False
    assert config.LOG_LEVEL == "ERROR"
    
    # Conversão para dicionário
    config_dict = config.to_dict()
    assert "DEBUG" in config_dict
    assert "LOG_LEVEL" in config_dict 