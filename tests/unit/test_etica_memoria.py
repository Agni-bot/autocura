import pytest
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def gerenciador():
    return GerenciadorMemoria()

def test_validar_decisao_etica(gerenciador):
    """Testa a validação ética de decisões."""
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    assert gerenciador.validar_decisao_etica(decisao) == True

def test_validar_decisao_etica_risco_alto(gerenciador):
    """Testa a validação ética de decisões com risco alto."""
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "impacto": "alto",
        "risco": "alto",
        "beneficio": "baixo"
    }
    assert gerenciador.validar_decisao_etica(decisao) == False

def test_validar_acao_etica(gerenciador):
    """Testa a validação ética de ações."""
    acao = {
        "id": "test_1",
        "tipo": "hotfix",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    assert gerenciador.validar_acao_etica(acao) == True

def test_validar_acao_etica_risco_alto(gerenciador):
    """Testa a validação ética de ações com risco alto."""
    acao = {
        "id": "test_1",
        "tipo": "hotfix",
        "impacto": "alto",
        "risco": "alto",
        "beneficio": "baixo"
    }
    assert gerenciador.validar_acao_etica(acao) == False 