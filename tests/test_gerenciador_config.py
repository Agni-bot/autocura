import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import json
import yaml
import os
from src.config.gerenciador_config import GerenciadorConfig, Configuracao

@pytest.fixture
def config():
    """Configuração básica para os testes."""
    return {
        "base_dir": "test_config"
    }

@pytest.fixture
def gerenciador(config):
    """Instância do gerenciador de configuração."""
    return GerenciadorConfig(config)

@pytest.fixture
def configuracao_exemplo():
    """Configuração de exemplo para testes."""
    return {
        "nome": "teste",
        "valor": {"chave": "valor"},
        "tipo": "sistema",
        "ambiente": "teste",
        "tags": ["teste"],
        "descricao": "Configuração de teste"
    }

@pytest.mark.asyncio
async def test_inicializacao(gerenciador, config):
    """Testa a inicialização do gerenciador."""
    assert gerenciador.config == config
    assert gerenciador.base_dir == Path(config["base_dir"])
    assert isinstance(gerenciador.configuracoes, dict)
    assert isinstance(gerenciador.historico, dict)
    assert "configuracoes_criadas" in gerenciador.metricas
    assert "configuracoes_atualizadas" in gerenciador.metricas
    assert "configuracoes_carregadas" in gerenciador.metricas
    assert "tempo_operacao" in gerenciador.metricas
    assert "sistema" in gerenciador.tipos_config
    assert "aplicacao" in gerenciador.tipos_config
    assert "ambiente" in gerenciador.tipos_config
    assert "secreto" in gerenciador.tipos_config

@pytest.mark.asyncio
async def test_criar_configuracao(gerenciador, configuracao_exemplo):
    """Testa a criação de configuração."""
    config = await gerenciador.criar_configuracao(**configuracao_exemplo)
    
    assert config is not None
    assert config.id == f"{configuracao_exemplo['tipo']}_{configuracao_exemplo['nome']}"
    assert config.nome == configuracao_exemplo["nome"]
    assert config.valor == configuracao_exemplo["valor"]
    assert config.tipo == configuracao_exemplo["tipo"]
    assert config.ambiente == configuracao_exemplo["ambiente"]
    assert config.tags == configuracao_exemplo["tags"]
    assert config.descricao == configuracao_exemplo["descricao"]
    assert config.versao == "1.0"
    
    # Verifica arquivo
    arquivo = gerenciador.base_dir / configuracao_exemplo["tipo"] / f"{configuracao_exemplo['nome']}.json"
    assert arquivo.exists()
    
    with open(arquivo, "r") as f:
        dados = json.load(f)
        assert dados == configuracao_exemplo["valor"]
    
    # Verifica cache
    assert config.id in gerenciador.configuracoes
    assert gerenciador.configuracoes[config.id] == config
    
    # Verifica histórico
    assert config.id in gerenciador.historico
    assert len(gerenciador.historico[config.id]) == 1
    assert gerenciador.historico[config.id][0] == config

@pytest.mark.asyncio
async def test_criar_configuracao_tipo_invalido(gerenciador, configuracao_exemplo):
    """Testa criação de configuração com tipo inválido."""
    configuracao_exemplo["tipo"] = "invalido"
    config = await gerenciador.criar_configuracao(**configuracao_exemplo)
    assert config is None

@pytest.mark.asyncio
async def test_atualizar_configuracao(gerenciador, configuracao_exemplo):
    """Testa a atualização de configuração."""
    # Cria configuração
    config = await gerenciador.criar_configuracao(**configuracao_exemplo)
    assert config is not None
    
    # Atualiza valor
    novo_valor = {"nova_chave": "novo_valor"}
    sucesso = await gerenciador.atualizar_configuracao(config.id, novo_valor)
    assert sucesso
    
    # Verifica arquivo
    arquivo = gerenciador.base_dir / configuracao_exemplo["tipo"] / f"{configuracao_exemplo['nome']}.json"
    assert arquivo.exists()
    
    with open(arquivo, "r") as f:
        dados = json.load(f)
        assert dados == novo_valor
    
    # Verifica cache
    config_atualizada = gerenciador.configuracoes[config.id]
    assert config_atualizada.valor == novo_valor
    assert config_atualizada.versao == "1.1"
    
    # Verifica histórico
    assert len(gerenciador.historico[config.id]) == 2
    assert gerenciador.historico[config.id][-1] == config_atualizada

@pytest.mark.asyncio
async def test_atualizar_configuracao_inexistente(gerenciador):
    """Testa atualização de configuração inexistente."""
    sucesso = await gerenciador.atualizar_configuracao("inexistente", {"valor": "teste"})
    assert not sucesso

@pytest.mark.asyncio
async def test_obter_configuracao(gerenciador, configuracao_exemplo):
    """Testa a obtenção de configuração."""
    # Cria configuração
    config = await gerenciador.criar_configuracao(**configuracao_exemplo)
    assert config is not None
    
    # Obtém configuração
    config_obtida = await gerenciador.obter_configuracao(config.id)
    assert config_obtida == config
    
    # Testa configuração inexistente
    config_inexistente = await gerenciador.obter_configuracao("inexistente")
    assert config_inexistente is None

@pytest.mark.asyncio
async def test_buscar_configuracoes(gerenciador, configuracao_exemplo):
    """Testa a busca de configurações."""
    # Cria configurações
    config1 = await gerenciador.criar_configuracao(**configuracao_exemplo)
    assert config1 is not None
    
    config2 = await gerenciador.criar_configuracao(
        nome="teste2",
        valor={"chave2": "valor2"},
        tipo="aplicacao",
        ambiente="teste",
        tags=["teste"],
        descricao="Configuração de teste 2"
    )
    assert config2 is not None
    
    # Busca por tipo
    configs_tipo = await gerenciador.buscar_configuracoes(tipo="sistema")
    assert len(configs_tipo) == 1
    assert configs_tipo[0] == config1
    
    # Busca por ambiente
    configs_ambiente = await gerenciador.buscar_configuracoes(ambiente="teste")
    assert len(configs_ambiente) == 2
    
    # Busca por tags
    configs_tags = await gerenciador.buscar_configuracoes(tags=["teste"])
    assert len(configs_tags) == 2
    
    # Busca combinada
    configs_combinada = await gerenciador.buscar_configuracoes(
        tipo="aplicacao",
        ambiente="teste",
        tags=["teste"]
    )
    assert len(configs_combinada) == 1
    assert configs_combinada[0] == config2

@pytest.mark.asyncio
async def test_obter_historico(gerenciador, configuracao_exemplo):
    """Testa a obtenção do histórico de configuração."""
    # Cria configuração
    config = await gerenciador.criar_configuracao(**configuracao_exemplo)
    assert config is not None
    
    # Atualiza algumas vezes
    for i in range(3):
        novo_valor = {"versao": f"1.{i+1}"}
        sucesso = await gerenciador.atualizar_configuracao(config.id, novo_valor)
        assert sucesso
    
    # Obtém histórico
    historico = await gerenciador.obter_historico(config.id)
    assert len(historico) == 4  # Versão inicial + 3 atualizações
    
    # Verifica versões
    for i, versao in enumerate(historico):
        assert versao.versao == f"1.{i}"
    
    # Testa histórico inexistente
    historico_inexistente = await gerenciador.obter_historico("inexistente")
    assert historico_inexistente == []

@pytest.mark.asyncio
async def test_obter_estatisticas(gerenciador, configuracao_exemplo):
    """Testa a obtenção de estatísticas."""
    # Cria algumas configurações
    config1 = await gerenciador.criar_configuracao(**configuracao_exemplo)
    assert config1 is not None
    
    config2 = await gerenciador.criar_configuracao(
        nome="teste2",
        valor={"chave2": "valor2"},
        tipo="aplicacao",
        ambiente="teste",
        tags=["teste", "app"],
        descricao="Configuração de teste 2"
    )
    assert config2 is not None
    
    # Atualiza algumas vezes
    for i in range(2):
        novo_valor = {"versao": f"1.{i+1}"}
        sucesso = await gerenciador.atualizar_configuracao(config1.id, novo_valor)
        assert sucesso
    
    # Obtém estatísticas
    stats = await gerenciador.obter_estatisticas()
    
    assert stats["total_configuracoes"] == 2
    assert stats["por_tipo"]["sistema"] == 1
    assert stats["por_tipo"]["aplicacao"] == 1
    assert stats["por_ambiente"]["teste"] == 2
    assert stats["por_tag"]["teste"] == 2
    assert stats["por_tag"]["app"] == 1
    assert stats["total_versoes"] == 4  # 2 configurações + 2 atualizações

@pytest.mark.asyncio
async def test_carregar_configuracoes(gerenciador, configuracao_exemplo):
    """Testa o carregamento de configurações."""
    # Cria algumas configurações
    config1 = await gerenciador.criar_configuracao(**configuracao_exemplo)
    assert config1 is not None
    
    config2 = await gerenciador.criar_configuracao(
        nome="teste2",
        valor={"chave2": "valor2"},
        tipo="aplicacao",
        ambiente="teste",
        tags=["teste"],
        descricao="Configuração de teste 2"
    )
    assert config2 is not None
    
    # Limpa cache
    gerenciador.configuracoes.clear()
    gerenciador.historico.clear()
    
    # Carrega configurações
    await gerenciador.carregar_configuracoes()
    
    # Verifica cache
    assert len(gerenciador.configuracoes) == 2
    assert config1.id in gerenciador.configuracoes
    assert config2.id in gerenciador.configuracoes
    
    # Verifica histórico
    assert len(gerenciador.historico) == 2
    assert config1.id in gerenciador.historico
    assert config2.id in gerenciador.historico

@pytest.mark.asyncio
async def test_limpeza(gerenciador):
    """Testa a limpeza dos arquivos de teste."""
    # Remove diretório de teste
    if gerenciador.base_dir.exists():
        for arquivo in gerenciador.base_dir.glob("**/*"):
            if arquivo.is_file():
                arquivo.unlink()
        gerenciador.base_dir.rmdir() 