"""
Fixtures compartilhadas para os testes do sistema de autocura.

Este módulo contém fixtures que podem ser utilizadas em todos os testes,
evitando duplicação de código e garantindo consistência.
"""

import os
import pytest
import logging
from typing import Dict, Any, Generator
from datetime import datetime
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
from prometheus_client import CollectorRegistry

# Configuração de logging para testes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def config_teste() -> Dict[str, Any]:
    """
    Fixture que fornece configurações de teste para toda a sessão.
    
    Returns:
        Dict[str, Any]: Configurações de teste
    """
    return {
        "ambiente": "teste",
        "timeout": 30,
        "retry_count": 3,
        "api_url": os.getenv("TEST_API_URL", "http://localhost:8000"),
        "db_url": os.getenv("TEST_DB_URL", "postgresql://test:test@localhost:5432/test_db"),
        "redis_url": os.getenv("TEST_REDIS_URL", "redis://localhost:6379/0")
    }

@pytest.fixture(scope="function")
def mock_api() -> Generator[Mock, None, None]:
    """
    Fixture que fornece um mock da API para cada teste.
    
    Yields:
        Mock: Mock da API
    """
    with patch("requests.Session") as mock:
        yield mock

@pytest.fixture(scope="function")
def mock_db() -> Generator[Mock, None, None]:
    """
    Fixture que fornece um mock do banco de dados para cada teste.
    
    Yields:
        Mock: Mock do banco de dados
    """
    with patch("sqlalchemy.create_engine") as mock:
        yield mock

@pytest.fixture(scope="function")
def mock_redis() -> Generator[Mock, None, None]:
    """
    Fixture que fornece um mock do Redis para cada teste.
    
    Yields:
        Mock: Mock do Redis
    """
    with patch("redis.Redis") as mock:
        yield mock

@pytest.fixture(scope="function")
def dados_teste() -> Dict[str, Any]:
    """
    Fixture que fornece dados de teste para cada teste.
    
    Returns:
        Dict[str, Any]: Dados de teste
    """
    return {
        "id": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "nome": "Teste",
        "data": datetime.now().isoformat(),
        "status": "ativo",
        "metadados": {
            "versao": "1.0.0",
            "ambiente": "teste"
        }
    }

@pytest.fixture(scope="session")
def monitoramento() -> Generator[Any, None, None]:
    """
    Fixture que fornece uma instância do monitoramento para toda a sessão.
    
    Yields:
        MonitoramentoTestes: Instância do monitoramento
    """
    from src.orquestrador.monitoramento import MonitoramentoTestes
    
    monitor = MonitoramentoTestes()
    yield monitor
    
    # Limpa recursos após os testes
    monitor.verificar_alertas()

@pytest.fixture(scope="function")
def temp_dir(tmp_path: Path) -> Path:
    """
    Fixture que fornece um diretório temporário para cada teste.
    
    Args:
        tmp_path: Fixture do pytest que fornece um diretório temporário
        
    Returns:
        Path: Caminho do diretório temporário
    """
    return tmp_path

@pytest.fixture(scope="function")
def log_captura(caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
    """
    Fixture que captura logs durante a execução do teste.
    
    Args:
        caplog: Fixture do pytest para captura de logs
        
    Returns:
        pytest.LogCaptureFixture: Fixture de captura de logs
    """
    caplog.set_level(logging.INFO)
    return caplog

@pytest.fixture(scope="function")
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Fixture que configura variáveis de ambiente para o teste.
    
    Args:
        monkeypatch: Fixture do pytest para modificar variáveis de ambiente
    """
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ENVIRONMENT", "test")

@pytest.fixture(scope="function")
def mock_time(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Fixture que mocka o tempo para testes que dependem de timestamps.
    
    Args:
        monkeypatch: Fixture do pytest para modificar variáveis de ambiente
    """
    class MockDatetime:
        @classmethod
        def now(cls):
            return datetime(2024, 1, 1, 12, 0, 0)
            
    monkeypatch.setattr("datetime.datetime", MockDatetime)

@pytest.fixture(scope="session")
def test_config():
    """Configuração global para testes."""
    return {
        "memoria_path": os.path.join(tempfile.gettempdir(), "memoria_test.json"),
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 1,  # DB 1 para testes
        "prometheus_port": 9091,
        "grafana_port": 3001,
        "loki_port": 3101
    }

@pytest.fixture(scope="session")
def prometheus_registry():
    """Registry do Prometheus para testes."""
    return CollectorRegistry()

@pytest.fixture(scope="session")
def temp_dir():
    """Diretório temporário para testes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup e teardown automático para cada teste."""
    # Setup
    yield
    # Teardown
    # Limpa arquivos temporários se necessário 