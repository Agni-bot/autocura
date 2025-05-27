import pytest
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def gerenciador():
    return GerenciadorMemoria()

def test_criar_entidade(gerenciador):
    """Testa a criação de uma entidade."""
    entidade = gerenciador.criar_entidade("test_1", "manutencao", {"status": "pendente"})
    assert entidade["id"] == "test_1"
    assert entidade["tipo"] == "manutencao"
    assert entidade["dados"]["status"] == "pendente"

def test_criar_entidade_tipo_invalido(gerenciador):
    """Testa a criação de uma entidade com tipo inválido."""
    with pytest.raises(ValueError):
        gerenciador.criar_entidade("test_1", "tipo_invalido", {})

def test_criar_entidade_tamanho_excedido(gerenciador):
    """Testa a criação de uma entidade com tamanho excedido."""
    dados_grandes = {"dados": "x" * 1000000}
    with pytest.raises(ValueError):
        gerenciador.criar_entidade("test_1", "manutencao", dados_grandes)

def test_atualizar_entidade(gerenciador):
    """Testa a atualização de uma entidade."""
    gerenciador.criar_entidade("test_1", "manutencao", {"status": "pendente"})
    entidade_atualizada = gerenciador.atualizar_entidade("test_1", {"status": "concluido"})
    assert entidade_atualizada["dados"]["status"] == "concluido"

def test_obter_entidade(gerenciador):
    """Testa a obtenção de uma entidade."""
    gerenciador.criar_entidade("test_1", "manutencao", {"status": "pendente"})
    entidade = gerenciador.obter_entidade("test_1")
    assert entidade["id"] == "test_1"
    assert entidade["tipo"] == "manutencao"
    assert entidade["dados"]["status"] == "pendente"

def test_buscar_entidades(gerenciador):
    """Testa a busca de entidades."""
    gerenciador.criar_entidade("test_1", "manutencao", {"status": "pendente"})
    gerenciador.criar_entidade("test_2", "hotfix", {"status": "concluido"})
    entidades = gerenciador.buscar_entidades(tipo="manutencao")
    assert len(entidades) == 1
    assert entidades[0]["id"] == "test_1"

def test_adicionar_relacionamento(gerenciador):
    """Testa a adição de um relacionamento."""
    gerenciador.criar_entidade("test_1", "manutencao", {})
    gerenciador.criar_entidade("test_2", "hotfix", {})
    gerenciador.adicionar_relacionamento("test_1", "test_2", "depende_de")
    relacionamentos = gerenciador.obter_relacionamentos("test_1")
    assert len(relacionamentos) == 1
    assert relacionamentos[0]["entidade_id"] == "test_2"
    assert relacionamentos[0]["tipo"] == "depende_de"

def test_obter_relacionamentos(gerenciador):
    """Testa a obtenção de relacionamentos."""
    gerenciador.criar_entidade("test_1", "manutencao", {})
    gerenciador.criar_entidade("test_2", "hotfix", {})
    gerenciador.adicionar_relacionamento("test_1", "test_2", "depende_de")
    relacionamentos = gerenciador.obter_relacionamentos("test_1")
    assert len(relacionamentos) == 1
    assert relacionamentos[0]["entidade_id"] == "test_2"
    assert relacionamentos[0]["tipo"] == "depende_de" 