import pytest
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria
from src.anomalias.detector_anomalias import DetectorAnomalias

@pytest.fixture
def detector_anomalias():
    return DetectorAnomalias()

@pytest.fixture
def gerenciador(detector_anomalias):
    return GerenciadorMemoria(detector_anomalias=detector_anomalias)

def test_deteccao_anomalia(gerenciador, detector_anomalias):
    """Testa a detecção de anomalias com integração."""
    dados = {
        "estado_sistema": {
            "nivel_autonomia": 1,
            "status": "normal"
        },
        "metricas": {
            "cpu_uso": 95,
            "memoria_uso": 90
        }
    }
    anomalia = detector_anomalias.detectar_anomalia(dados)
    assert anomalia is not None
    assert anomalia["tipo"] == "alta_carga"
    assert anomalia["severidade"] == "alta"

def test_registro_anomalia(gerenciador, detector_anomalias):
    """Testa o registro de anomalias com integração."""
    dados = {
        "estado_sistema": {
            "nivel_autonomia": 1,
            "status": "normal"
        },
        "metricas": {
            "cpu_uso": 95,
            "memoria_uso": 90
        }
    }
    anomalia = detector_anomalias.detectar_anomalia(dados)
    gerenciador.registrar_anomalia(anomalia)
    memoria = gerenciador.carregar_memoria()
    assert len(memoria["anomalias"]) == 1
    assert memoria["anomalias"][0]["tipo"] == "alta_carga"
    assert memoria["anomalias"][0]["severidade"] == "alta" 