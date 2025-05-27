"""
Fixtures compartilhadas para os testes do sistema de autocura.

Este módulo contém fixtures que podem ser utilizadas em todos os testes,
evitando duplicação de código e garantindo consistência.

Tipos de Testes:
- Unitários: Testes de componentes individuais
- Integração: Testes de interação entre componentes
- E2E: Testes end-to-end do sistema completo
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
import sys
import yaml

# Adiciona o diretório src ao PYTHONPATH
src_path = str(Path(__file__).parent.parent / "src")
sys.path.append(src_path)

# Configuração de logging para testes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_test_config() -> Dict[str, Any]:
    """Carrega configurações de teste do arquivo YAML."""
    config_path = Path(__file__).parent.parent / "config" / "test" / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def config_teste() -> Dict[str, Any]:
    """
    Fixture que fornece configurações de teste para toda a sessão.
    
    Returns:
        Dict[str, Any]: Configurações de teste carregadas do arquivo YAML
    """
    return load_test_config()

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
    from src.orchestration.monitoramento import MonitoramentoTestes
    
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
    """Fixture que retorna a configuração de teste."""
    config = load_test_config()
    return {
        "test_mode": True,
        "log_level": config["logging"]["level"],
        "memory_path": config["memory"]["path"],
        "api_url": f"http://{config['api']['host']}:{config['api']['port']}",
        "monitoring_enabled": config["monitoring"]["enabled"]
    }

@pytest.fixture(scope="session")
def test_memory():
    """Fixture que retorna um dicionário de memória de teste."""
    return {
        "last_update": "2024-03-20T00:00:00Z",
        "metrics": {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0
        },
        "alerts": [],
        "adjustments": []
    }

@pytest.fixture(scope="function")
def clean_test_env():
    """Fixture que limpa o ambiente de teste antes e depois de cada teste."""
    config = load_test_config()
    # Setup
    test_files = [
        config["memory"]["path"],
        config["logging"]["file"]
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
    
    yield
    
    # Teardown
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)

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