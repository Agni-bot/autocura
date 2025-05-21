"""
Testes unitários para o módulo de ações de correção.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from typing import Dict, Any

from src.core.acoes_correcao import (
    AcaoCorrecao,
    GerenciadorAcoes,
    TipoAcao,
    StatusAcao
)

@pytest.fixture
def gerenciador():
    """Fixture que fornece uma instância do GerenciadorAcoes com mocks configurados"""
    memoria = AsyncMock()
    gerenciador = GerenciadorAcoes(memoria=memoria)
    return gerenciador

@pytest.fixture
def acao_exemplo():
    """Fixture que fornece um exemplo de ação para testes"""
    return {
        "tipo": TipoAcao.CORRECAO,
        "descricao": "Corrigir falha no sistema",
        "parametros": {
            "componente": "api",
            "severidade": "alta"
        }
    }

@pytest.mark.asyncio
async def test_criar_acao(gerenciador, acao_exemplo):
    """Testa a criação de uma ação de correção."""
    # Configura o mock para retornar um ID
    gerenciador.memoria.criar_entidade.return_value = "123"
    
    # Cria ação
    acao = await gerenciador.criar_acao(
        tipo=acao_exemplo["tipo"],
        descricao=acao_exemplo["descricao"],
        parametros=acao_exemplo["parametros"]
    )
    
    assert acao is not None
    assert acao.tipo == acao_exemplo["tipo"]
    assert acao.descricao == acao_exemplo["descricao"]
    assert acao.parametros == acao_exemplo["parametros"]
    
    # Verifica se o mock foi chamado corretamente
    gerenciador.memoria.criar_entidade.assert_called_once()

@pytest.mark.asyncio
async def test_executar_acao(gerenciador, acao_exemplo):
    """Testa a execução de uma ação de correção."""
    # Configura os mocks
    acao_id = "123"
    acao_dados = {
        "id": acao_id,
        "tipo": acao_exemplo["tipo"].value,
        "descricao": acao_exemplo["descricao"],
        "parametros": acao_exemplo["parametros"],
        "status": StatusAcao.PENDENTE.value,
        "data_criacao": None,
        "data_inicio": None,
        "data_fim": None,
        "sucesso": None,
        "validada": False,
        "data_validacao": None
    }
    
    gerenciador.memoria.criar_entidade.return_value = acao_id
    gerenciador.memoria.obter_entidade.return_value = acao_dados
    gerenciador.memoria.atualizar_entidade = AsyncMock()
    
    # Cria e executa ação
    acao = await gerenciador.criar_acao(
        tipo=acao_exemplo["tipo"],
        descricao=acao_exemplo["descricao"],
        parametros=acao_exemplo["parametros"]
    )
    
    resultado = await gerenciador.executar_acao(acao.id)
    
    assert resultado is True
    gerenciador.memoria.atualizar_entidade.assert_called_once()

@pytest.mark.asyncio
async def test_finalizar_acao(gerenciador, acao_exemplo):
    """Testa a finalização de uma ação de correção."""
    # Configura os mocks
    acao_id = "123"
    acao_dados = {
        "id": acao_id,
        "tipo": acao_exemplo["tipo"].value,
        "descricao": acao_exemplo["descricao"],
        "parametros": acao_exemplo["parametros"],
        "status": StatusAcao.EM_EXECUCAO.value,
        "data_criacao": None,
        "data_inicio": None,
        "data_fim": None,
        "sucesso": None,
        "validada": False,
        "data_validacao": None
    }
    
    gerenciador.memoria.criar_entidade.return_value = acao_id
    gerenciador.memoria.obter_entidade.return_value = acao_dados
    gerenciador.memoria.atualizar_entidade = AsyncMock()
    
    # Cria, executa e finaliza ação
    acao = await gerenciador.criar_acao(
        tipo=acao_exemplo["tipo"],
        descricao=acao_exemplo["descricao"],
        parametros=acao_exemplo["parametros"]
    )
    
    await gerenciador.executar_acao(acao.id)
    resultado = await gerenciador.finalizar_acao(acao.id, sucesso=True)
    
    assert resultado is True
    assert gerenciador.memoria.atualizar_entidade.call_count == 2

@pytest.mark.asyncio
async def test_obter_acao(gerenciador, acao_exemplo):
    """Testa a obtenção de uma ação de correção."""
    # Configura os mocks
    acao_id = "123"
    acao_dados = {
        "id": acao_id,
        "tipo": acao_exemplo["tipo"].value,
        "descricao": acao_exemplo["descricao"],
        "parametros": acao_exemplo["parametros"],
        "status": StatusAcao.PENDENTE.value,
        "data_criacao": None,
        "data_inicio": None,
        "data_fim": None,
        "sucesso": None,
        "validada": False,
        "data_validacao": None
    }
    gerenciador.memoria.criar_entidade.return_value = acao_id
    gerenciador.memoria.obter_entidade.return_value = acao_dados
    
    # Cria ação com id fixo
    acao = await gerenciador.criar_acao(
        tipo=acao_exemplo["tipo"],
        descricao=acao_exemplo["descricao"],
        parametros=acao_exemplo["parametros"]
    )
    acao.id = acao_id  # Força o id para garantir alinhamento
    
    # Obtém ação
    acao_obtida = await gerenciador.obter_acao(acao.id)
    
    assert acao_obtida is not None
    assert acao_obtida.id == acao_id
    assert acao_obtida.tipo == acao.tipo
    assert acao_obtida.descricao == acao.descricao
    assert acao_obtida.parametros == acao.parametros
    
    gerenciador.memoria.obter_entidade.assert_called_once_with("acoes", acao_id)

@pytest.mark.asyncio
async def test_listar_acoes(gerenciador, acao_exemplo):
    """Testa a listagem de ações de correção."""
    # Mock do método de memória
    gerenciador.memoria.buscar_entidades = AsyncMock()
    acoes_mock = []
    for i in range(3):
        acoes_mock.append({
            "id": str(i),
            "tipo": acao_exemplo["tipo"].value,
            "descricao": f"{acao_exemplo['descricao']} {i}",
            "parametros": acao_exemplo["parametros"],
            "status": StatusAcao.PENDENTE.value,
            "data_criacao": None,
            "data_inicio": None,
            "data_fim": None,
            "sucesso": None,
            "validada": False,
            "data_validacao": None
        })
    gerenciador.memoria.buscar_entidades.return_value = acoes_mock
    
    # Lista ações
    acoes = await gerenciador.listar_acoes()
    
    assert len(acoes) == 3
    assert all(isinstance(acao, AcaoCorrecao) for acao in acoes)

@pytest.mark.asyncio
async def test_validar_acao(gerenciador, acao_exemplo):
    """Testa a validação de uma ação de correção."""
    # Configura os mocks
    acao_id = "123"
    acao_dados = {
        "id": acao_id,
        "tipo": acao_exemplo["tipo"].value,
        "descricao": acao_exemplo["descricao"],
        "parametros": acao_exemplo["parametros"],
        "status": StatusAcao.PENDENTE.value,
        "data_criacao": None,
        "data_inicio": None,
        "data_fim": None,
        "sucesso": None,
        "validada": False,
        "data_validacao": None
    }
    gerenciador.memoria.obter_entidade.return_value = acao_dados
    gerenciador.memoria.atualizar_entidade = AsyncMock()
    
    # Valida ação
    resultado = await gerenciador.validar_acao(acao_id)
    
    assert resultado is True
    gerenciador.memoria.atualizar_entidade.assert_called_once()

@pytest.mark.asyncio
async def test_acao_inexistente(gerenciador):
    """Testa operações com ação inexistente."""
    # Configura o mock para retornar None
    gerenciador.memoria.obter_entidade.return_value = None
    
    # Tenta obter ação inexistente
    acao = await gerenciador.obter_acao("id_inexistente")
    assert acao is None
    
    # Tenta executar ação inexistente
    resultado = await gerenciador.executar_acao("id_inexistente")
    assert resultado is False
    
    # Tenta finalizar ação inexistente
    resultado = await gerenciador.finalizar_acao("id_inexistente", True)
    assert resultado is False

@pytest.mark.asyncio
async def test_acao_invalida(gerenciador):
    """Testa a criação de ação com parâmetros inválidos."""
    # Tenta criar ação sem tipo
    acao = await gerenciador.criar_acao(
        tipo=None,
        descricao="Teste",
        parametros={}
    )
    assert acao is None
    
    # Tenta criar ação sem descrição
    acao = await gerenciador.criar_acao(
        tipo=TipoAcao.CORRECAO,
        descricao="",
        parametros={}
    )
    assert acao is None 