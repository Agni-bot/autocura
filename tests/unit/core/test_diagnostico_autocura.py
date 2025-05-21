"""
Testes unitários para o módulo de diagnóstico de autocura.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any, List

from src.core.diagnostico_autocura import (
    DiagnosticoAutocura,
    GerenciadorDiagnostico,
    TipoDiagnostico,
    Severidade,
    StatusDiagnostico
)

@pytest.fixture
def diagnostico_exemplo() -> Dict[str, Any]:
    """Fornece um diagnóstico de exemplo para testes."""
    return {
        "tipo": TipoDiagnostico.SISTEMA,
        "descricao": "Falha no sistema de autocura",
        "severidade": Severidade.ALTA,
        "metricas": {
            "cpu": 95.0,
            "memoria": 85.0,
            "latencia": 500
        }
    }

@pytest.fixture
def gerenciador():
    """Fornece uma instância do gerenciador de diagnóstico para testes."""
    with patch("src.core.diagnostico_autocura.GerenciadorMemoria") as mock_memoria:
        gerenciador = GerenciadorDiagnostico()
        gerenciador.memoria = mock_memoria
        yield gerenciador

@pytest.mark.asyncio
async def test_criar_diagnostico(gerenciador, diagnostico_exemplo):
    """Testa a criação de um diagnóstico."""
    # Mock do método de memória
    gerenciador.memoria.criar_entidade = AsyncMock()
    
    # Cria diagnóstico
    diagnostico = await gerenciador.criar_diagnostico(
        tipo=diagnostico_exemplo["tipo"],
        descricao=diagnostico_exemplo["descricao"],
        severidade=diagnostico_exemplo["severidade"],
        metricas=diagnostico_exemplo["metricas"]
    )
    
    assert diagnostico is not None
    assert diagnostico.tipo == diagnostico_exemplo["tipo"]
    assert diagnostico.descricao == diagnostico_exemplo["descricao"]
    assert diagnostico.severidade == diagnostico_exemplo["severidade"]
    assert diagnostico.metricas == diagnostico_exemplo["metricas"]
    assert diagnostico.status == StatusDiagnostico.ABERTO
    assert diagnostico.data_criacao is not None
    
    # Verifica se foi salvo na memória
    gerenciador.memoria.criar_entidade.assert_called_once()

@pytest.mark.asyncio
async def test_analisar_diagnostico(gerenciador, diagnostico_exemplo):
    """Testa a análise de um diagnóstico."""
    # Mock do método de memória
    gerenciador.memoria.atualizar_entidade = AsyncMock()
    
    # Cria e analisa diagnóstico
    diagnostico = await gerenciador.criar_diagnostico(
        tipo=diagnostico_exemplo["tipo"],
        descricao=diagnostico_exemplo["descricao"],
        severidade=diagnostico_exemplo["severidade"],
        metricas=diagnostico_exemplo["metricas"]
    )
    
    resultado = await gerenciador.analisar_diagnostico(diagnostico.id)
    
    assert resultado is True
    assert diagnostico.status == StatusDiagnostico.EM_ANALISE
    assert diagnostico.data_analise is not None
    
    # Verifica se foi atualizado na memória
    gerenciador.memoria.atualizar_entidade.assert_called()

@pytest.mark.asyncio
async def test_finalizar_diagnostico(gerenciador, diagnostico_exemplo):
    """Testa a finalização de um diagnóstico."""
    # Mock do método de memória
    gerenciador.memoria.atualizar_entidade = AsyncMock()
    
    # Cria, analisa e finaliza diagnóstico
    diagnostico = await gerenciador.criar_diagnostico(
        tipo=diagnostico_exemplo["tipo"],
        descricao=diagnostico_exemplo["descricao"],
        severidade=diagnostico_exemplo["severidade"],
        metricas=diagnostico_exemplo["metricas"]
    )
    
    await gerenciador.analisar_diagnostico(diagnostico.id)
    resultado = await gerenciador.finalizar_diagnostico(
        diagnostico.id,
        resolucao="Problema resolvido",
        acoes_tomadas=["Reiniciou serviço", "Ajustou configuração"]
    )
    
    assert resultado is True
    assert diagnostico.status == StatusDiagnostico.RESOLVIDO
    assert diagnostico.data_resolucao is not None
    assert diagnostico.resolucao == "Problema resolvido"
    assert len(diagnostico.acoes_tomadas) == 2
    
    # Verifica se foi atualizado na memória
    gerenciador.memoria.atualizar_entidade.assert_called()

@pytest.mark.asyncio
async def test_obter_diagnostico(gerenciador, diagnostico_exemplo):
    """Testa a obtenção de um diagnóstico."""
    # Mock do método de memória
    gerenciador.memoria.obter_entidade = AsyncMock()
    
    # Cria diagnóstico
    diagnostico = await gerenciador.criar_diagnostico(
        tipo=diagnostico_exemplo["tipo"],
        descricao=diagnostico_exemplo["descricao"],
        severidade=diagnostico_exemplo["severidade"],
        metricas=diagnostico_exemplo["metricas"]
    )
    
    # Obtém diagnóstico
    diagnostico_obtido = await gerenciador.obter_diagnostico(diagnostico.id)
    
    assert diagnostico_obtido is not None
    assert diagnostico_obtido.id == diagnostico.id
    assert diagnostico_obtido.tipo == diagnostico.tipo
    assert diagnostico_obtido.descricao == diagnostico.descricao

@pytest.mark.asyncio
async def test_listar_diagnosticos(gerenciador, diagnostico_exemplo):
    """Testa a listagem de diagnósticos."""
    # Mock do método de memória
    gerenciador.memoria.buscar_entidades = AsyncMock()
    
    # Cria alguns diagnósticos
    for i in range(3):
        await gerenciador.criar_diagnostico(
            tipo=diagnostico_exemplo["tipo"],
            descricao=f"{diagnostico_exemplo['descricao']} {i}",
            severidade=diagnostico_exemplo["severidade"],
            metricas=diagnostico_exemplo["metricas"]
        )
    
    # Lista diagnósticos
    diagnosticos = await gerenciador.listar_diagnosticos()
    
    assert len(diagnosticos) == 3
    assert all(isinstance(d, DiagnosticoAutocura) for d in diagnosticos)

@pytest.mark.asyncio
async def test_analisar_tendencias(gerenciador, diagnostico_exemplo):
    """Testa a análise de tendências de diagnósticos."""
    # Cria alguns diagnósticos similares
    for i in range(3):
        await gerenciador.criar_diagnostico(
            tipo=diagnostico_exemplo["tipo"],
            descricao=f"{diagnostico_exemplo['descricao']} {i}",
            severidade=diagnostico_exemplo["severidade"],
            metricas=diagnostico_exemplo["metricas"]
        )
    
    # Analisa tendências
    tendencias = await gerenciador.analisar_tendencias()
    
    assert tendencias is not None
    assert "padroes" in tendencias
    assert "recomendacoes" in tendencias

@pytest.mark.asyncio
async def test_diagnostico_inexistente(gerenciador):
    """Testa operações com diagnóstico inexistente."""
    # Tenta obter diagnóstico inexistente
    diagnostico = await gerenciador.obter_diagnostico("id_inexistente")
    assert diagnostico is None
    
    # Tenta analisar diagnóstico inexistente
    resultado = await gerenciador.analisar_diagnostico("id_inexistente")
    assert resultado is False
    
    # Tenta finalizar diagnóstico inexistente
    resultado = await gerenciador.finalizar_diagnostico("id_inexistente")
    assert resultado is False

@pytest.mark.asyncio
async def test_diagnostico_invalido(gerenciador):
    """Testa a criação de diagnóstico com parâmetros inválidos."""
    # Tenta criar diagnóstico sem tipo
    diagnostico = await gerenciador.criar_diagnostico(
        tipo=None,
        descricao="Teste",
        severidade=Severidade.BAIXA,
        metricas={}
    )
    assert diagnostico is None
    
    # Tenta criar diagnóstico sem descrição
    diagnostico = await gerenciador.criar_diagnostico(
        tipo=TipoDiagnostico.SISTEMA,
        descricao="",
        severidade=Severidade.BAIXA,
        metricas={}
    )
    assert diagnostico is None
    
    # Tenta criar diagnóstico sem severidade
    diagnostico = await gerenciador.criar_diagnostico(
        tipo=TipoDiagnostico.SISTEMA,
        descricao="Teste",
        severidade=None,
        metricas={}
    )
    assert diagnostico is None 