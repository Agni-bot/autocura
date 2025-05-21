"""
Testes para funcionalidades críticas do módulo de ações.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.acoes.gerador_acoes import (
    GeradorAcoes,
    Acao,
    PlanoAcao,
    TipoAcao,
    PrioridadeAcao
)

@pytest.fixture
def mock_diagnostico():
    """Fixture que retorna um diagnóstico simulado para testes."""
    return {
        'tipo': 'CRITICO',
        'severidade': 'ALTA',
        'metricas_afetadas': ['cpu', 'memoria'],
        'causas_provaveis': [
            {'tipo': 'cpu', 'probabilidade': 0.9},
            {'tipo': 'memoria', 'probabilidade': 0.8}
        ],
        'timestamp': datetime.now().isoformat()
    }

@pytest.fixture
def gerador_acoes():
    """Fixture que retorna uma instância do GeradorAcoes."""
    return GeradorAcoes()

@pytest.mark.asyncio
async def test_geracao_acao_critica(gerador_acoes, mock_diagnostico):
    """Testa a geração de ações para diagnóstico crítico."""
    acoes = await gerador_acoes.gerar_acoes(mock_diagnostico)
    
    assert len(acoes) > 0
    assert all(isinstance(acao, Acao) for acao in acoes)
    assert any(acao.tipo == TipoAcao.CRITICA for acao in acoes)
    assert any(acao.prioridade == PrioridadeAcao.ALTA for acao in acoes)

@pytest.mark.asyncio
async def test_plano_acao_completo(gerador_acoes, mock_diagnostico):
    """Testa a geração de um plano de ação completo."""
    plano = await gerador_acoes.gerar_plano_acao(mock_diagnostico)
    
    assert isinstance(plano, PlanoAcao)
    assert len(plano.acoes) > 0
    assert plano.acoes_ordenadas
    assert plano.tempo_estimado > 0
    assert plano.probabilidade_sucesso > 0

@pytest.mark.asyncio
async def test_priorizacao_acoes(gerador_acoes, mock_diagnostico):
    """Testa a priorização correta das ações."""
    plano = await gerador_acoes.gerar_plano_acao(mock_diagnostico)
    
    # Verifica se as ações estão ordenadas por prioridade
    prioridades = [acao.prioridade for acao in plano.acoes]
    assert [p.value for p in prioridades] == sorted([p.value for p in prioridades], reverse=True)
    
    # Verifica se ações críticas têm prioridade alta
    acoes_criticas = [acao for acao in plano.acoes if acao.tipo == TipoAcao.CRITICA]
    assert all(acao.prioridade == PrioridadeAcao.ALTA for acao in acoes_criticas)

@pytest.mark.asyncio
async def test_dependencias_acoes(gerador_acoes, mock_diagnostico):
    """Testa o tratamento de dependências entre ações."""
    plano = await gerador_acoes.gerar_plano_acao(mock_diagnostico)
    
    # Verifica se as dependências são respeitadas na ordem
    for i, acao in enumerate(plano.acoes):
        for dependencia in acao.dependencias:
            # Encontra a ação dependente
            idx_dep = next(j for j, a in enumerate(plano.acoes) if a.id == dependencia)
            assert idx_dep < i  # Ação dependente deve vir antes

@pytest.mark.asyncio
async def test_validacao_acoes(gerador_acoes, mock_diagnostico):
    """Testa a validação de ações geradas."""
    plano = await gerador_acoes.gerar_plano_acao(mock_diagnostico)
    
    for acao in plano.acoes:
        assert acao.id is not None
        assert acao.descricao
        assert acao.tipo in TipoAcao
        assert acao.prioridade in PrioridadeAcao
        assert acao.tempo_estimado > 0
        assert 0 <= acao.probabilidade_sucesso <= 1

@pytest.mark.asyncio
async def test_evolucao_plano_acao(gerador_acoes, mock_diagnostico):
    """Testa a evolução do plano de ação com feedback."""
    # Gera plano inicial
    plano1 = await gerador_acoes.gerar_plano_acao(mock_diagnostico)
    
    # Simula feedback de execução
    feedback = {
        'acao_id': plano1.acoes[0].id,
        'sucesso': False,
        'erro': 'Falha na execução',
        'metricas_pos': {
            'cpu': {'total': 95.0},
            'memoria': {'percentual': 95.0}
        }
    }
    
    # Gera novo plano com feedback
    plano2 = await gerador_acoes.gerar_plano_acao(mock_diagnostico, feedback)
    
    # Verifica adaptação do plano
    assert plano2.id != plano1.id
    assert len(plano2.acoes) >= len(plano1.acoes)
    assert any(acao.descricao != plano1.acoes[0].descricao for acao in plano2.acoes) 