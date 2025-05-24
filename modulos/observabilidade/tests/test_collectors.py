import pytest
from datetime import datetime
from modulos.observabilidade.src.collectors.multidim_collector import MultiDimensionalCollector

@pytest.fixture
def collector():
    return MultiDimensionalCollector()

def test_collect_classical_metrics(collector):
    """Testa coleta de métricas clássicas"""
    metrics = collector.collect_classical_metrics()
    
    # Verifica estrutura básica
    assert "timestamp" in metrics
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics
    
    # Verifica tipos de dados
    assert isinstance(metrics["cpu"]["percent"], float)
    assert isinstance(metrics["cpu"]["per_cpu"], list)
    assert isinstance(metrics["memory"]["total"], int)
    assert isinstance(metrics["disk"]["total"], int)
    
    # Verifica limites
    assert 0 <= metrics["cpu"]["percent"] <= 100
    assert 0 <= metrics["memory"]["percent"] <= 100
    assert 0 <= metrics["disk"]["percent"] <= 100

def test_metrics_history(collector):
    """Testa histórico de métricas"""
    # Coleta algumas métricas
    for _ in range(5):
        collector.collect_classical_metrics()
    
    # Verifica histórico
    history = collector.get_metrics_history(limit=3)
    assert len(history) == 3
    assert all("timestamp" in m for m in history)

def test_calculate_equity(collector):
    """Testa cálculo de equidade"""
    # Coleta métricas
    collector.collect_classical_metrics()
    
    # Calcula equidade
    equity = collector.calculate_equity()
    
    # Verifica resultado
    assert isinstance(equity, float)
    assert 0 <= equity <= 1

def test_prepare_quantum_metrics(collector):
    """Testa preparação para métricas quânticas"""
    collector.prepare_quantum_metrics()
    
    # Verifica estrutura
    assert hasattr(collector, "quantum_metrics")
    assert "coherence_time" in collector.quantum_metrics
    assert "entanglement_degree" in collector.quantum_metrics
    assert "quantum_volume" in collector.quantum_metrics
    assert "error_rate" in collector.quantum_metrics 