import pytest
from datetime import datetime
import redis
from ..src.storage.hybrid_storage import HybridStorage

@pytest.fixture
def storage():
    return HybridStorage(redis_url="redis://localhost:6379/0")

@pytest.fixture
def sample_metrics():
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

def test_store_classical(storage, sample_metrics):
    """Testa armazenamento de métricas clássicas"""
    storage.store_classical(sample_metrics)
    
    # Verifica Redis
    metrics = storage.get_metrics()
    assert len(metrics) > 0
    latest = metrics[-1]
    assert "timestamp" in latest
    assert "data" in latest
    assert "cpu_percent" in latest["data"]
    assert "memory_percent" in latest["data"]
    assert "disk_percent" in latest["data"]

def test_get_metrics_time_range(storage, sample_metrics):
    """Testa recuperação de métricas por período"""
    # Armazena métricas
    storage.store_classical(sample_metrics)
    
    # Recupera últimas 24 horas
    start_time = datetime.now().timestamp() - 86400
    end_time = datetime.now().timestamp()
    
    metrics = storage.get_metrics(
        start_time=start_time,
        end_time=end_time
    )
    
    assert len(metrics) > 0
    assert all(start_time <= float(m["timestamp"]) <= end_time 
              for m in metrics)

def test_prepare_quantum_storage(storage):
    """Testa preparação para armazenamento quântico"""
    storage.prepare_quantum_storage()
    
    # Verifica estrutura
    assert hasattr(storage, "quantum_storage")
    assert "coherence_time" in storage.quantum_storage
    assert "entanglement_degree" in storage.quantum_storage
    assert "quantum_volume" in storage.quantum_storage
    assert "error_rate" in storage.quantum_storage

def test_prometheus_metrics(storage):
    """Testa configuração de métricas Prometheus"""
    metrics = storage.prometheus_metrics
    
    # Verifica métricas configuradas
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert "disk_percent" in metrics
    assert "equity_index" in metrics
    assert "metric_collections" in metrics 