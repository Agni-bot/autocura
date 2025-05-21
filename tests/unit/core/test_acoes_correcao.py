"""
Testes unitários para o módulo de ações de correção.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

from src.core.acoes_correcao import (
    AcaoCorrecao,
    GerenciadorAcoes,
    TipoAcao,
    StatusAcao
)

@pytest.fixture
def acao_exemplo() -> Dict[str, Any]:
    """Fornece uma ação de exemplo para testes."""
    return {
        "tipo": TipoAcao.CORRECAO,
        "descricao": "Corrigir falha no sistema",
        "parametros": {
            "componente": "api",
            "severidade": "alta"
        }
    }

@pytest.fixture
def gerenciador():
    """Fornece uma instância do gerenciador de ações para testes."""
    with patch("src.core.acoes_correcao.GerenciadorMemoria") as mock_memoria:
        gerenciador = GerenciadorAcoes()
        gerenciador.memoria = mock_memoria
        yield gerenciador

@pytest.mark.asyncio
async def test_criar_acao(gerenciador, acao_exemplo):
    """Testa a criação de uma ação de correção."""
    # Mock do método de memória
    gerenciador.memoria.criar_entidade = AsyncMock()
    
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
    assert acao.status == StatusAcao.PENDENTE
    assert acao.data_criacao is not None
    
    # Verifica se foi salvo na memória
    gerenciador.memoria.criar_entidade.assert_called_once()

@pytest.mark.asyncio
async def test_executar_acao(gerenciador, acao_exemplo):
    """Testa a execução de uma ação de correção."""
    # Mock do método de memória
    gerenciador.memoria.atualizar_entidade = AsyncMock()
    
    # Cria e executa ação
    acao = await gerenciador.criar_acao(
        tipo=acao_exemplo["tipo"],
        descricao=acao_exemplo["descricao"],
        parametros=acao_exemplo["parametros"]
    )
    
    resultado = await gerenciador.executar_acao(acao.id)
    
    assert resultado is True
    assert acao.status == StatusAcao.EM_EXECUCAO
    assert acao.data_inicio is not None
    
    # Verifica se foi atualizado na memória
    gerenciador.memoria.atualizar_entidade.assert_called()

@pytest.mark.asyncio
async def test_finalizar_acao(gerenciador, acao_exemplo):
    """Testa a finalização de uma ação de correção."""
    # Mock do método de memória
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
    assert acao.status == StatusAcao.CONCLUIDA
    assert acao.data_fim is not None
    assert acao.sucesso is True
    
    # Verifica se foi atualizado na memória
    gerenciador.memoria.atualizar_entidade.assert_called()

@pytest.mark.asyncio
async def test_obter_acao(gerenciador, acao_exemplo):
    """Testa a obtenção de uma ação de correção."""
    # Mock do método de memória
    gerenciador.memoria.obter_entidade = AsyncMock()
    
    # Cria ação
    acao = await gerenciador.criar_acao(
        tipo=acao_exemplo["tipo"],
        descricao=acao_exemplo["descricao"],
        parametros=acao_exemplo["parametros"]
    )
    
    # Obtém ação
    acao_obtida = await gerenciador.obter_acao(acao.id)
    
    assert acao_obtida is not None
    assert acao_obtida.id == acao.id
    assert acao_obtida.tipo == acao.tipo
    assert acao_obtida.descricao == acao.descricao

@pytest.mark.asyncio
async def test_listar_acoes(gerenciador, acao_exemplo):
    """Testa a listagem de ações de correção."""
    # Mock do método de memória
    gerenciador.memoria.buscar_entidades = AsyncMock()
    
    # Cria algumas ações
    for i in range(3):
        await gerenciador.criar_acao(
            tipo=acao_exemplo["tipo"],
            descricao=f"{acao_exemplo['descricao']} {i}",
            parametros=acao_exemplo["parametros"]
        )
    
    # Lista ações
    acoes = await gerenciador.listar_acoes()
    
    assert len(acoes) == 3
    assert all(isinstance(acao, AcaoCorrecao) for acao in acoes)

@pytest.mark.asyncio
async def test_validar_acao(gerenciador, acao_exemplo):
    """Testa a validação de uma ação de correção."""
    # Cria ação
    acao = await gerenciador.criar_acao(
        tipo=acao_exemplo["tipo"],
        descricao=acao_exemplo["descricao"],
        parametros=acao_exemplo["parametros"]
    )
    
    # Valida ação
    resultado = await gerenciador.validar_acao(acao.id)
    
    assert resultado is True
    assert acao.validada is True
    assert acao.data_validacao is not None

@pytest.mark.asyncio
async def test_acao_inexistente(gerenciador):
    """Testa operações com ação inexistente."""
    # Tenta obter ação inexistente
    acao = await gerenciador.obter_acao("id_inexistente")
    assert acao is None
    
    # Tenta executar ação inexistente
    resultado = await gerenciador.executar_acao("id_inexistente")
    assert resultado is False
    
    # Tenta finalizar ação inexistente
    resultado = await gerenciador.finalizar_acao("id_inexistente")
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