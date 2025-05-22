import pytest
from datetime import datetime
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def gerenciador():
    return GerenciadorMemoria()

def test_atualizar_estado_sistema(gerenciador):
    """Testa a atualização do estado do sistema."""
    estado = {
        "nivel_autonomia": 1,
        "status": "normal"
    }
    gerenciador.atualizar_estado_sistema(estado)
    memoria = gerenciador.carregar_memoria()
    assert memoria["estado_sistema"]["nivel_autonomia"] == 1
    assert memoria["estado_sistema"]["status"] == "normal"

def test_registrar_decisao(gerenciador):
    """Testa o registro de uma decisão."""
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    gerenciador.registrar_decisao(decisao)
    memoria = gerenciador.carregar_memoria()
    assert len(memoria["decisoes"]) == 1
    assert memoria["decisoes"][0]["id"] == "test_1"
    assert memoria["decisoes"][0]["tipo"] == "manutencao"

def test_registrar_acao(gerenciador):
    """Testa o registro de uma ação."""
    acao = {
        "id": "test_1",
        "tipo": "hotfix",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    gerenciador.registrar_acao(acao)
    memoria = gerenciador.carregar_memoria()
    assert len(memoria["acoes"]) == 1
    assert memoria["acoes"][0]["id"] == "test_1"
    assert memoria["acoes"][0]["tipo"] == "hotfix"

def test_obter_historico(gerenciador):
    """Testa a obtenção do histórico."""
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    acao = {
        "id": "test_2",
        "tipo": "hotfix",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    gerenciador.registrar_decisao(decisao)
    gerenciador.registrar_acao(acao)
    historico = gerenciador.obter_historico()
    assert len(historico["decisoes"]) == 1
    assert len(historico["acoes"]) == 1
    assert historico["decisoes"][0]["id"] == "test_1"
    assert historico["acoes"][0]["id"] == "test_2" 