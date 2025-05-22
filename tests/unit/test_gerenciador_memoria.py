import pytest
import tempfile
import os
from datetime import datetime
from prometheus_client import CollectorRegistry
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def test_config():
    """Fixture que fornece configuração para testes."""
    return {
        "memoria_path": os.path.join(tempfile.gettempdir(), "memoria_test.json"),
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "prometheus_port": 9091,
        "grafana_port": 3001,
        "loki_port": 3101
    }

@pytest.fixture
def prometheus_registry():
    """Fixture que fornece um registro Prometheus limpo para testes."""
    return CollectorRegistry()

@pytest.fixture
def gerenciador_memoria(test_config, prometheus_registry):
    """Fixture que cria uma instância do GerenciadorMemoria para testes."""
    return GerenciadorMemoria(
        config=test_config,
        registry=prometheus_registry
    )

@pytest.mark.asyncio
async def test_inicializacao_basica(gerenciador_memoria):
    """Testa a inicialização básica do GerenciadorMemoria."""
    assert gerenciador_memoria is not None
    assert "memoria_operacional" in gerenciador_memoria.memoria
    assert "memoria_etica" in gerenciador_memoria.memoria

@pytest.mark.asyncio
async def test_inicializacao_com_config(gerenciador_memoria, test_config):
    """Testa a inicialização com configuração personalizada."""
    assert gerenciador_memoria.caminho_memoria == test_config["memoria_path"]
    assert gerenciador_memoria.redis_host == test_config["redis_host"]
    assert gerenciador_memoria.redis_port == test_config["redis_port"]

@pytest.mark.asyncio
async def test_criar_entidade(gerenciador_memoria):
    """Testa a criação de uma entidade na memória."""
    dados = {"teste": "valor"}
    entidade = await gerenciador_memoria.criar_entidade("conhecimento", dados, ["teste"])
    
    assert entidade is not None
    assert entidade.tipo == "conhecimento"
    assert entidade.dados == dados
    assert "teste" in entidade.tags

@pytest.mark.asyncio
async def test_obter_entidade(gerenciador_memoria):
    """Testa a recuperação de uma entidade da memória."""
    dados = {"teste": "valor"}
    entidade = await gerenciador_memoria.criar_entidade("conhecimento", dados, ["teste"])
    
    entidade_recuperada = await gerenciador_memoria.obter_entidade(entidade.id)
    assert entidade_recuperada is not None
    assert entidade_recuperada.id == entidade.id
    assert entidade_recuperada.dados == dados

@pytest.mark.asyncio
async def test_atualizar_entidade(gerenciador_memoria):
    """Testa a atualização de uma entidade na memória."""
    dados_iniciais = {"teste": "valor"}
    entidade = await gerenciador_memoria.criar_entidade("conhecimento", dados_iniciais, ["teste"])
    
    dados_atualizados = {"teste": "novo_valor"}
    sucesso = await gerenciador_memoria.atualizar_entidade(entidade.id, dados_atualizados)
    assert sucesso is True
    
    entidade_atualizada = await gerenciador_memoria.obter_entidade(entidade.id)
    assert entidade_atualizada.dados["teste"] == "novo_valor"

@pytest.mark.asyncio
async def test_metricas_prometheus(gerenciador_memoria):
    """Testa se as métricas do Prometheus estão sendo registradas corretamente."""
    # Cria algumas entidades
    dados = {"teste": "valor"}
    await gerenciador_memoria.criar_entidade("conhecimento", dados, ["teste"])
    await gerenciador_memoria.criar_entidade("evento", dados, ["teste"])
    
    # Verifica se as métricas foram incrementadas
    metricas = gerenciador_memoria.metricas
    assert metricas["entidades_criadas"].labels(tipo="conhecimento")._value.get() == 1
    assert metricas["entidades_criadas"].labels(tipo="evento")._value.get() == 1

@pytest.mark.asyncio
async def test_limpar_memoria_antiga(gerenciador_memoria):
    """Testa a limpeza de memória antiga."""
    # Cria algumas entidades
    dados = {"teste": "valor"}
    await gerenciador_memoria.criar_entidade("conhecimento", dados, ["teste"])
    
    # Limpa memória
    gerenciador_memoria.limpar_memoria_antiga(dias=0)  # Força limpeza imediata
    
    # Verifica se as entidades foram removidas
    stats = await gerenciador_memoria.obter_estatisticas()
    assert stats["total_entidades"] == 0

@pytest.mark.asyncio
async def test_obter_estatisticas(gerenciador_memoria):
    """Testa a obtenção de estatísticas da memória."""
    # Cria algumas entidades
    dados = {"teste": "valor"}
    await gerenciador_memoria.criar_entidade("conhecimento", dados, ["teste"])
    await gerenciador_memoria.criar_entidade("evento", dados, ["teste"])
    
    # Obtém estatísticas
    stats = await gerenciador_memoria.obter_estatisticas()
    
    assert "total_entidades" in stats
    assert "entidades_por_tipo" in stats
    assert stats["total_entidades"] == 2
    assert stats["entidades_por_tipo"]["conhecimento"] == 1
    assert stats["entidades_por_tipo"]["evento"] == 1 