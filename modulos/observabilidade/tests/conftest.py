import pytest
import redis
from datetime import datetime
from modulos.observabilidade.src.storage.hybrid_storage import HybridStorage

@pytest.fixture(scope="function")
def redis_client():
    """Fixture para cliente Redis limpo antes de cada teste"""
    client = redis.Redis(host='localhost', port=6379, db=0)
    yield client
    # Limpa todas as chaves após o teste
    client.flushdb()

@pytest.fixture(scope="function")
def storage(redis_client):
    """Fixture para HybridStorage com Redis limpo"""
    storage = HybridStorage(redis_url="redis://localhost:6379/0")
    storage.clear_metrics()  # Limpa métricas Prometheus
    yield storage
    # Limpeza adicional após o teste
    storage.clear_metrics()

@pytest.fixture(scope="function")
def sample_metrics():
    """Fixture para métricas de exemplo"""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "percent": 45.5,
            "per_cpu": [30.0, 40.0, 50.0, 60.0],
            "frequency": {"current": 2000, "min": 1000, "max": 3000}
        },
        "memory": {
            "total": 16000000000,
            "available": 8000000000,
            "percent": 50.0,
            "used": 8000000000,
            "free": 8000000000
        },
        "disk": {
            "total": 1000000000000,
            "used": 500000000000,
            "free": 500000000000,
            "percent": 50.0
        }
    } 