"""Testes do módulo principal."""

import pytest
from fastapi.testclient import TestClient
from ..src.main import CoreModule
import asyncio

@pytest.fixture
def core_module():
    """Fixture que retorna uma instância do CoreModule."""
    return CoreModule()

@pytest.fixture
def client(core_module):
    """Fixture que retorna um cliente de teste."""
    return TestClient(core_module.app)

def test_health_check(client):
    """Testa o endpoint de verificação de saúde."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_config(client):
    """Testa o endpoint de configurações."""
    response = client.get("/config")
    assert response.status_code == 200
    config = response.json()
    
    # Verifica campos obrigatórios
    assert "ENVIRONMENT" in config
    assert "DEBUG" in config
    assert "LOG_LEVEL" in config
    assert "CORE_HOST" in config
    assert "CORE_PORT" in config
    assert "CORE_WORKERS" in config

def test_get_modules(client, core_module):
    """Testa o endpoint de módulos registrados."""
    # Registra um módulo mock
    class MockModule:
        async def initialize(self): pass
        async def shutdown(self): pass
        async def health_check(self): return {"status": "ok"}
    
    # Registra o módulo mock
    asyncio.run(core_module.middleware.register_module("test_module", MockModule()))
    
    # Testa o endpoint
    response = client.get("/modules")
    assert response.status_code == 200
    data = response.json()
    
    assert "modules" in data
    assert "test_module" in data["modules"]

@pytest.mark.asyncio
async def test_module_lifecycle(core_module):
    """Testa o ciclo de vida do módulo."""
    # Inicia o módulo
    start_task = asyncio.create_task(core_module.start())
    
    # Aguarda um pouco
    await asyncio.sleep(0.1)
    
    # Desliga o módulo
    await core_module.shutdown()
    
    # Cancela a tarefa de início
    start_task.cancel()
    try:
        await start_task
    except asyncio.CancelledError:
        pass

@pytest.mark.asyncio
async def test_error_handling(core_module):
    """Testa o tratamento de erros."""
    # Simula um erro
    core_module.event_bus = None
    
    # Tenta iniciar o módulo
    with pytest.raises(Exception):
        await core_module.start()
    
    # Verifica se o erro foi registrado
    logs = await core_module.logger.get_logs(level="error")
    assert len(logs) > 0
    assert "Erro ao iniciar o módulo core" in logs[0]["message"] 