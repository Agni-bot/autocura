"""
Testes do módulo core da Consciência Situacional.
"""

import pytest
from datetime import datetime
from typing import Dict, List, Any
from ..core import Situacao, Contexto, AnalisadorSituacional, GeradorContexto, ProjetorConsequencias

@pytest.fixture
def metricas():
    """Fixture com métricas de exemplo."""
    return {
        'cpu_usage': 0.75,
        'memory_usage': 0.60,
        'disk_usage': 0.45,
        'network_usage': 0.30
    }

@pytest.fixture
def logs():
    """Fixture com logs de exemplo."""
    return [
        'INFO: Serviço iniciado',
        'WARNING: Alta utilização de CPU',
        'ERROR: Falha na conexão com banco de dados'
    ]

@pytest.fixture
def eventos():
    """Fixture com eventos de exemplo."""
    return [
        {
            'tipo': 'alerta',
            'severidade': 'alta',
            'mensagem': 'CPU acima do limite',
            'timestamp': datetime.now().timestamp()
        },
        {
            'tipo': 'erro',
            'severidade': 'critica',
            'mensagem': 'Falha na conexão',
            'timestamp': datetime.now().timestamp()
        }
    ]

@pytest.fixture
def contexto():
    """Fixture com contexto de exemplo."""
    return {
        'servico': 'api',
        'ambiente': 'producao',
        'versao': '1.0.0'
    }

@pytest.fixture
def situacao(metricas, logs, eventos, contexto):
    """Fixture com situação de exemplo."""
    return Situacao(
        id='1',
        timestamp=datetime.now().timestamp(),
        metricas=metricas,
        logs=logs,
        eventos=eventos,
        contexto=contexto
    )

@pytest.fixture
def analisador():
    """Fixture com analisador."""
    return AnalisadorSituacional()

@pytest.fixture
def gerador():
    """Fixture com gerador de contexto."""
    return GeradorContexto()

@pytest.fixture
def projetor():
    """Fixture com projetor de consequências."""
    return ProjetorConsequencias()

def test_criar_situacao(situacao):
    """Testa criação de situação."""
    assert situacao.id == '1'
    assert isinstance(situacao.timestamp, float)
    assert isinstance(situacao.metricas, dict)
    assert isinstance(situacao.logs, list)
    assert isinstance(situacao.eventos, list)
    assert isinstance(situacao.contexto, dict)
    assert isinstance(situacao.score, float)

def test_analisar_situacao(analisador, metricas, logs, eventos, contexto):
    """Testa análise de situação."""
    situacao = analisador.analisar(metricas, logs, eventos, contexto)
    assert isinstance(situacao, Situacao)
    assert situacao.metricas == metricas
    assert situacao.logs == logs
    assert situacao.eventos == eventos
    assert situacao.contexto == contexto

def test_gerar_contexto(gerador, situacao):
    """Testa geração de contexto."""
    contexto = gerador.gerar_contexto(situacao)
    assert isinstance(contexto, Contexto)
    assert contexto.situacao == situacao
    assert isinstance(contexto.dependencias, dict)
    assert isinstance(contexto.impactos, dict)
    assert isinstance(contexto.prioridades, dict)
    assert isinstance(contexto.score, float)

def test_atualizar_contexto(gerador, situacao):
    """Testa atualização de contexto."""
    contexto = gerador.gerar_contexto(situacao)
    dados = {
        'dependencias': {'api': ['db', 'cache']},
        'impactos': {'api': 0.8},
        'prioridades': {'api': 1}
    }
    gerador.atualizar_contexto(dados)
    assert contexto.dependencias == dados['dependencias']
    assert contexto.impactos == dados['impactos']
    assert contexto.prioridades == dados['prioridades']

def test_projetar_consequencias(projetor, gerador, situacao):
    """Testa projeção de consequências."""
    contexto = gerador.gerar_contexto(situacao)
    projecao = projetor.projetar(contexto)
    assert isinstance(projecao, dict)
    assert 'tendencias' in projecao
    assert 'cenarios' in projecao
    assert 'probabilidades' in projecao
    assert 'timestamp' in projecao 