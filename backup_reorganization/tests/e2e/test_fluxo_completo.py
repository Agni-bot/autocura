"""
Testes end-to-end do fluxo completo do sistema.
"""

import pytest
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria
from src.services.etica.validacao_etica import ValidacaoEtica
from src.services.diagnostico.rede_neural import RedeNeuralAltaOrdem
from src.services.monitoramento.coletor_metricas import ColetorMetricas
from src.services.gerador.gerador_acoes import GeradorAcoes

@pytest.fixture
def validacao_etica():
    return ValidacaoEtica()

@pytest.fixture
def detector_anomalias():
    return RedeNeuralAltaOrdem()

@pytest.fixture
def gerenciador(validacao_etica, detector_anomalias):
    return GerenciadorMemoria(
        validacao_etica=validacao_etica,
        detector_anomalias=detector_anomalias
    )

def test_fluxo_completo(gerenciador):
    """Testa o fluxo completo do sistema."""
    # 1. Atualizar estado do sistema
    estado = {
        "nivel_autonomia": 1,
        "status": "normal"
    }
    gerenciador.atualizar_estado_sistema(estado)
    
    # 2. Registrar decisão
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    gerenciador.registrar_decisao(decisao)
    
    # 3. Registrar ação
    acao = {
        "id": "test_2",
        "tipo": "hotfix",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    gerenciador.registrar_acao(acao)
    
    # 4. Detectar anomalia
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
    anomalia = gerenciador.detector_anomalias.detectar_anomalia(dados)
    gerenciador.registrar_anomalia(anomalia)
    
    # 5. Verificar estado final
    memoria = gerenciador.carregar_memoria()
    assert memoria["estado_sistema"]["nivel_autonomia"] == 1
    assert len(memoria["decisoes"]) == 1
    assert len(memoria["acoes"]) == 1
    assert len(memoria["anomalias"]) == 1
    assert memoria["anomalias"][0]["tipo"] == "alta_carga" 