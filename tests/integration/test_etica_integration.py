import pytest
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria
from src.services.etica.validacao_etica import ValidacaoEtica

@pytest.fixture
def validacao_etica():
    return ValidacaoEtica()

@pytest.fixture
def gerenciador(validacao_etica):
    return GerenciadorMemoria(validacao_etica=validacao_etica)

def test_validacao_etica_decisao(gerenciador, validacao_etica):
    """Testa a validação ética de decisões com integração."""
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    assert gerenciador.validar_decisao_etica(decisao) == True
    assert validacao_etica.validar_decisao(decisao) == True

def test_validacao_etica_acao(gerenciador, validacao_etica):
    """Testa a validação ética de ações com integração."""
    acao = {
        "id": "test_1",
        "tipo": "hotfix",
        "impacto": "baixo",
        "risco": "baixo",
        "beneficio": "alto"
    }
    assert gerenciador.validar_acao_etica(acao) == True
    assert validacao_etica.validar_acao(acao) == True 