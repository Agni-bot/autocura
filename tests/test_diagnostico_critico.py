"""
Testes para funcionalidades críticas do módulo de diagnóstico.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.diagnostico.diagnostico import (
    Diagnostico,
    TipoDiagnostico,
    SeveridadeDiagnostico,
    RedeNeuralDiagnostico
)
from src.diagnostico.diagnostico_sistema import DiagnosticoSistema
from src.diagnostico.core import AnalisadorMetricas, GeradorDiagnosticos

@pytest.fixture
def mock_metricas():
    """Fixture que retorna métricas simuladas para testes."""
    return {
        'cpu': {
            'total': 85.0,
            'por_core': [90.0, 80.0],
            'frequencia': 2100.0
        },
        'memoria': {
            'total': 1024 * 1024 * 1024,  # 1GB
            'disponivel': 100 * 1024 * 1024,  # 100MB
            'percentual': 90.0
        },
        'disco': {
            'total': 1024 * 1024 * 1024,  # 1GB
            'livre': 100 * 1024 * 1024,  # 100MB
            'percentual': 90.0
        },
        'timestamp': datetime.now().isoformat()
    }

@pytest.fixture
def analisador_metricas():
    """Fixture que retorna uma instância do AnalisadorMetricas."""
    return AnalisadorMetricas()

@pytest.fixture
def gerador_diagnosticos():
    """Fixture que retorna uma instância do GeradorDiagnosticos."""
    return GeradorDiagnosticos()

@pytest.mark.asyncio
async def test_analise_metricas_criticas(analisador_metricas, mock_metricas):
    """Testa a análise de métricas críticas."""
    anomalias = await analisador_metricas.analisar_metricas(mock_metricas)
    
    assert len(anomalias) > 0
    assert any(a['tipo'] == 'cpu' for a in anomalias)
    assert any(a['tipo'] == 'memoria' for a in anomalias)
    assert any(a['tipo'] == 'disco' for a in anomalias)

@pytest.mark.asyncio
async def test_geracao_diagnostico(gerador_diagnosticos, mock_metricas):
    """Testa a geração de diagnóstico a partir de métricas."""
    diagnostico = await gerador_diagnosticos.gerar_diagnostico(mock_metricas)
    
    assert isinstance(diagnostico, Diagnostico)
    assert diagnostico.tipo in [TipoDiagnostico.CRITICO, TipoDiagnostico.ALERTA]
    assert diagnostico.severidade in [SeveridadeDiagnostico.ALTA, SeveridadeDiagnostico.MEDIA]
    assert len(diagnostico.metricas_afetadas) > 0

@pytest.mark.asyncio
async def test_rede_neural_diagnostico(mock_metricas):
    """Testa o diagnóstico usando rede neural."""
    rede = RedeNeuralDiagnostico()
    resultado = await rede.analisar(mock_metricas)
    
    assert 'probabilidade_anomalia' in resultado
    assert 'causas_provaveis' in resultado
    assert len(resultado['causas_provaveis']) > 0
    assert 0 <= resultado['probabilidade_anomalia'] <= 1

@pytest.mark.asyncio
async def test_diagnostico_sistema_completo(mock_metricas):
    """Testa o fluxo completo de diagnóstico do sistema."""
    sistema = DiagnosticoSistema()
    
    # Executa diagnóstico
    resultado = await sistema.executar_diagnostico(mock_metricas)
    
    assert 'diagnostico' in resultado
    assert 'acoes_recomendadas' in resultado
    assert 'metricas_afetadas' in resultado
    assert len(resultado['acoes_recomendadas']) > 0

@pytest.mark.asyncio
async def test_evolucao_diagnostico(gerador_diagnosticos, mock_metricas):
    """Testa a evolução do diagnóstico ao longo do tempo."""
    # Primeiro diagnóstico
    diagnostico1 = await gerador_diagnosticos.gerar_diagnostico(mock_metricas)
    
    # Simula piora nas métricas
    mock_metricas['cpu']['total'] = 95.0
    mock_metricas['memoria']['percentual'] = 95.0
    
    # Segundo diagnóstico
    diagnostico2 = await gerador_diagnosticos.gerar_diagnostico(mock_metricas)
    
    # Verifica evolução
    assert diagnostico2.severidade >= diagnostico1.severidade
    assert len(diagnostico2.metricas_afetadas) >= len(diagnostico1.metricas_afetadas)

@pytest.mark.asyncio
async def test_correlacao_metricas(analisador_metricas, mock_metricas):
    """Testa a correlação entre diferentes métricas."""
    correlacoes = await analisador_metricas.analisar_correlacoes(mock_metricas)
    
    assert 'correlacoes' in correlacoes
    assert len(correlacoes['correlacoes']) > 0
    assert all('forca' in c for c in correlacoes['correlacoes'])
    assert all('tipo' in c for c in correlacoes['correlacoes']) 