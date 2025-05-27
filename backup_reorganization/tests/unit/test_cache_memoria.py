import pytest
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def gerenciador():
    return GerenciadorMemoria()

def test_limpar_cache(gerenciador):
    """Testa a limpeza do cache."""
    gerenciador.criar_entidade("test_1", "manutencao", {"status": "pendente"})
    gerenciador.obter_entidade("test_1")  # Adiciona ao cache
    gerenciador.limpar_cache()
    assert gerenciador._cache == {}

def test_obter_estatisticas(gerenciador):
    """Testa a obtenção de estatísticas."""
    gerenciador.criar_entidade("test_1", "manutencao", {"status": "pendente"})
    gerenciador.criar_entidade("test_2", "hotfix", {"status": "concluido"})
    gerenciador.obter_entidade("test_1")  # Adiciona ao cache
    estatisticas = gerenciador.obter_estatisticas()
    assert estatisticas["total_entidades"] == 2
    assert estatisticas["entidades_por_tipo"]["manutencao"] == 1
    assert estatisticas["entidades_por_tipo"]["hotfix"] == 1
    assert estatisticas["cache"]["tamanho"] == 1
    assert estatisticas["cache"]["hit_rate"] == 0.5 