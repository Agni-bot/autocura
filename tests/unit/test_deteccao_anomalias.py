import pytest
from datetime import datetime, timedelta
import numpy as np
from src.seguranca.deteccao_anomalias import DetectorAnomalias, MetricasSeguranca

@pytest.fixture
def detector():
    """Fixture que fornece uma instância do detector de anomalias para os testes."""
    return DetectorAnomalias(
        contamination=0.1,
        window_size=10,
        threshold_score=-0.5
    )

def test_inicializacao(detector):
    """Testa a inicialização do detector de anomalias."""
    assert detector.contamination == 0.1
    assert detector.window_size == 10
    assert detector.threshold_score == -0.5
    assert len(detector.metricas_historico) == 0
    assert len(detector.anomalias_detectadas) == 0

def test_registrar_metricas(detector):
    """Testa o registro de métricas."""
    metricas = MetricasSeguranca(
        cpu_usage=50.0,
        memoria_usage=60.0,
        latencia=150.0,
        requests_por_segundo=100.0,
        erro_rate=0.01,
        auth_failures=0,
        timestamp=datetime.now()
    )
    
    detector.registrar_metricas(metricas)
    assert len(detector.metricas_historico) == 1
    assert detector.metricas_historico[0] == metricas

def test_janela_metricas(detector):
    """Testa o comportamento da janela de métricas."""
    # Registra mais métricas que o tamanho da janela
    for i in range(15):
        metricas = MetricasSeguranca(
            cpu_usage=50.0 + i,
            memoria_usage=60.0 + i,
            latencia=150.0 + i,
            requests_por_segundo=100.0 + i,
            erro_rate=0.01,
            auth_failures=0,
            timestamp=datetime.now()
        )
        detector.registrar_metricas(metricas)
    
    # Verifica se manteve apenas as últimas window_size métricas
    assert len(detector.metricas_historico) == detector.window_size
    assert detector.metricas_historico[-1].cpu_usage == 64.0  # 50 + 14

def test_treinar_modelo(detector):
    """Testa o treinamento do modelo."""
    # Registra métricas suficientes para treinar
    for i in range(10):
        metricas = MetricasSeguranca(
            cpu_usage=50.0 + i,
            memoria_usage=60.0 + i,
            latencia=150.0 + i,
            requests_por_segundo=100.0 + i,
            erro_rate=0.01,
            auth_failures=0,
            timestamp=datetime.now()
        )
        detector.registrar_metricas(metricas)
    
    # Treina o modelo
    detector.treinar_modelo()
    # Não há assert específico pois o treinamento é interno

def test_detectar_anomalias(detector):
    """Testa a detecção de anomalias."""
    # Registra métricas normais
    for i in range(9):
        metricas = MetricasSeguranca(
            cpu_usage=50.0,
            memoria_usage=60.0,
            latencia=150.0,
            requests_por_segundo=100.0,
            erro_rate=0.01,
            auth_failures=0,
            timestamp=datetime.now()
        )
        detector.registrar_metricas(metricas)
    
    # Registra uma métrica anômala
    metricas_anomala = MetricasSeguranca(
        cpu_usage=95.0,  # Valor muito alto
        memoria_usage=90.0,  # Valor muito alto
        latencia=500.0,  # Valor muito alto
        requests_por_segundo=1000.0,  # Valor muito alto
        erro_rate=0.5,  # Valor muito alto
        auth_failures=10,  # Valor muito alto
        timestamp=datetime.now()
    )
    detector.registrar_metricas(metricas_anomala)
    
    # Treina o modelo
    detector.treinar_modelo()
    
    # Detecta anomalias
    anomalias = detector.detectar_anomalias()
    assert len(anomalias) > 0  # Deve detectar pelo menos uma anomalia

def test_obter_estatisticas(detector):
    """Testa a obtenção de estatísticas."""
    # Registra algumas anomalias
    for i in range(3):
        metricas = MetricasSeguranca(
            cpu_usage=90.0,
            memoria_usage=85.0,
            latencia=400.0,
            requests_por_segundo=800.0,
            erro_rate=0.3,
            auth_failures=5,
            timestamp=datetime.now()
        )
        detector.registrar_metricas(metricas)
    
    # Treina e detecta
    detector.treinar_modelo()
    detector.detectar_anomalias()
    
    # Obtém estatísticas
    stats = detector.obter_estatisticas()
    assert stats["total_anomalias"] > 0
    assert stats["ultima_anomalia"] is not None
    assert "metricas_mais_afetadas" in stats

def test_limpar_historico(detector):
    """Testa a limpeza do histórico de anomalias."""
    # Registra anomalias antigas e recentes
    agora = datetime.now()
    
    # Anomalia antiga
    metricas_antiga = MetricasSeguranca(
        cpu_usage=90.0,
        memoria_usage=85.0,
        latencia=400.0,
        requests_por_segundo=800.0,
        erro_rate=0.3,
        auth_failures=5,
        timestamp=agora - timedelta(days=10)
    )
    detector.registrar_metricas(metricas_antiga)
    
    # Anomalia recente
    metricas_recente = MetricasSeguranca(
        cpu_usage=90.0,
        memoria_usage=85.0,
        latencia=400.0,
        requests_por_segundo=800.0,
        erro_rate=0.3,
        auth_failures=5,
        timestamp=agora
    )
    detector.registrar_metricas(metricas_recente)
    
    # Treina e detecta
    detector.treinar_modelo()
    detector.detectar_anomalias()
    
    # Limpa histórico
    detector.limpar_historico(dias=7)
    
    # Verifica se manteve apenas a anomalia recente
    assert len(detector.anomalias_detectadas) == 1
    assert datetime.fromisoformat(detector.anomalias_detectadas[0]["timestamp"]) > agora - timedelta(days=7) 