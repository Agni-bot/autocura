import pytest
from datetime import datetime
from ..core import AnalisadorMetricas, GeradorDiagnosticos

@pytest.fixture
def limites():
    return {
        'cpu_uso': 80.0,
        'memoria_uso': 85.0,
        'disco_uso': 90.0
    }

@pytest.fixture
def regras():
    return {
        'cpu_uso': [
            {
                'tipo': 'sobrecarga_cpu',
                'descricao': 'Alto uso de CPU detectado',
                'limite': 80.0,
                'acao': 'escalar'
            }
        ],
        'memoria_uso': [
            {
                'tipo': 'vazamento_memoria',
                'descricao': 'Possível vazamento de memória',
                'limite': 85.0,
                'acao': 'investigar'
            }
        ]
    }

def test_analisador_metricas_normal(limites):
    analisador = AnalisadorMetricas(limites)
    metricas = {
        'cpu_uso': 50.0,
        'memoria_uso': 60.0,
        'disco_uso': 70.0
    }
    
    resultado = analisador.analisar_metricas(metricas)
    
    assert resultado['status_geral'] == 'normal'
    assert len(resultado['anomalias']) == 0

def test_analisador_metricas_anomalia(limites):
    analisador = AnalisadorMetricas(limites)
    metricas = {
        'cpu_uso': 90.0,
        'memoria_uso': 60.0,
        'disco_uso': 70.0
    }
    
    resultado = analisador.analisar_metricas(metricas)
    
    assert resultado['status_geral'] == 'anomalia'
    assert len(resultado['anomalias']) == 1
    assert resultado['anomalias'][0]['metrica'] == 'cpu_uso'
    assert resultado['anomalias'][0]['severidade'] == 'critica'

def test_gerador_diagnosticos(regras):
    gerador = GeradorDiagnosticos(regras)
    anomalias = [
        {
            'metrica': 'cpu_uso',
            'valor': 90.0,
            'limite': 80.0,
            'severidade': 'critica'
        }
    ]
    
    diagnostico = gerador.gerar_diagnostico(anomalias)
    
    assert 'timestamp' in diagnostico
    assert len(diagnostico['problemas']) == 1
    assert len(diagnostico['recomendacoes']) == 1
    assert diagnostico['problemas'][0]['tipo'] == 'sobrecarga_cpu'
    assert diagnostico['recomendacoes'][0]['acao'] == 'monitorar'

def test_gerador_diagnosticos_sem_anomalias(regras):
    gerador = GeradorDiagnosticos(regras)
    anomalias = []
    
    diagnostico = gerador.gerar_diagnostico(anomalias)
    
    assert 'timestamp' in diagnostico
    assert len(diagnostico['problemas']) == 0
    assert len(diagnostico['recomendacoes']) == 0

def test_calcular_severidade(limites):
    analisador = AnalisadorMetricas(limites)
    
    # Teste severidade crítica
    assert analisador._calcular_severidade(120.0, 80.0) == 'critica'
    
    # Teste severidade alta
    assert analisador._calcular_severidade(100.0, 80.0) == 'alta'
    
    # Teste severidade média
    assert analisador._calcular_severidade(90.0, 80.0) == 'media' 