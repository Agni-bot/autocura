"""
Testes para o módulo de métricas do sistema.
"""

import pytest
from datetime import datetime
from src.monitoramento.metricas import MetricasSistema, MonitoramentoMultidimensional

@pytest.fixture
def metricas_sistema():
    """Fixture que retorna uma instância de MetricasSistema."""
    return MetricasSistema(
        throughput=500.0,
        taxa_erro=2.5,
        latencia=50.0,
        uso_recursos={
            "cpu": 45.0,
            "memoria": 60.0,
            "disco": 30.0
        }
    )

@pytest.fixture
def monitoramento():
    """Fixture que retorna uma instância de MonitoramentoMultidimensional."""
    return MonitoramentoMultidimensional()

def test_metricas_sistema_inicializacao(metricas_sistema):
    """Testa a inicialização correta de MetricasSistema."""
    assert metricas_sistema.throughput == 500.0
    assert metricas_sistema.taxa_erro == 2.5
    assert metricas_sistema.latencia == 50.0
    assert metricas_sistema.uso_recursos["cpu"] == 45.0
    assert metricas_sistema.uso_recursos["memoria"] == 60.0
    assert metricas_sistema.uso_recursos["disco"] == 30.0
    assert isinstance(metricas_sistema.timestamp, datetime)

def test_metricas_sistema_validacao():
    """Testa a validação de valores em MetricasSistema."""
    # Teste com valores válidos
    metricas = MetricasSistema(
        throughput=100.0,
        taxa_erro=5.0,
        latencia=30.0,
        uso_recursos={"cpu": 50.0}
    )
    assert metricas.throughput == 100.0
    
    # Teste com throughput negativo
    with pytest.raises(ValueError, match="Throughput não pode ser negativo"):
        MetricasSistema(
            throughput=-100.0,
            taxa_erro=5.0,
            latencia=30.0,
            uso_recursos={"cpu": 50.0}
        )
    
    # Teste com taxa de erro inválida
    with pytest.raises(ValueError, match="Taxa de erro deve estar entre 0 e 100"):
        MetricasSistema(
            throughput=100.0,
            taxa_erro=150.0,
            latencia=30.0,
            uso_recursos={"cpu": 50.0}
        )
    
    # Teste com latência negativa
    with pytest.raises(ValueError, match="Latência não pode ser negativa"):
        MetricasSistema(
            throughput=100.0,
            taxa_erro=5.0,
            latencia=-30.0,
            uso_recursos={"cpu": 50.0}
        )
    
    # Teste com uso de recursos inválido
    with pytest.raises(ValueError, match="Uso de cpu deve estar entre 0 e 100"):
        MetricasSistema(
            throughput=100.0,
            taxa_erro=5.0,
            latencia=30.0,
            uso_recursos={"cpu": 150.0}
        )

def test_monitoramento_multidimensional_coleta(monitoramento):
    """Testa a coleta de métricas no MonitoramentoMultidimensional."""
    metricas = monitoramento.coletar_metricas()
    assert isinstance(metricas, MetricasSistema)
    assert 0 <= metricas.throughput <= 1000
    assert 0 <= metricas.taxa_erro <= 100
    assert 0 <= metricas.latencia <= 1000
    assert all(0 <= uso <= 100 for uso in metricas.uso_recursos.values())

def test_monitoramento_multidimensional_registro(monitoramento):
    """Testa o registro de métricas no MonitoramentoMultidimensional."""
    metricas = MetricasSistema(
        throughput=100.0,
        taxa_erro=5.0,
        latencia=30.0,
        uso_recursos={"cpu": 50.0}
    )
    
    monitoramento.registrar_metricas(metricas)
    assert len(monitoramento._historico) == 1
    assert monitoramento._historico[0] == metricas

def test_monitoramento_multidimensional_historico(monitoramento):
    """Testa a obtenção do histórico de métricas."""
    # Registra algumas métricas
    for i in range(5):
        metricas = MetricasSistema(
            throughput=100.0 + i,
            taxa_erro=5.0,
            latencia=30.0,
            uso_recursos={"cpu": 50.0}
        )
        monitoramento.registrar_metricas(metricas)
    
    # Testa obtenção de todo o histórico
    historico_completo = monitoramento.obter_historico()
    assert len(historico_completo) == 5
    
    # Testa obtenção de parte do histórico
    historico_parcial = monitoramento.obter_historico(limite=3)
    assert len(historico_parcial) == 3
    assert historico_parcial[-1].throughput == 104.0

def test_monitoramento_multidimensional_limpeza(monitoramento):
    """Testa a limpeza do histórico de métricas."""
    # Registra algumas métricas
    for i in range(5):
        metricas = MetricasSistema(
            throughput=100.0 + i,
            taxa_erro=5.0,
            latencia=30.0,
            uso_recursos={"cpu": 50.0}
        )
        monitoramento.registrar_metricas(metricas)
    
    # Limpa o histórico
    monitoramento.limpar_historico()
    assert len(monitoramento._historico) == 0 