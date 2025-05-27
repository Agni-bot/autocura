"""
Testes do módulo de integração da Consciência Situacional.
"""

import pytest
import requests
from unittest.mock import Mock, patch
from typing import Dict, List, Any
from ..integracao import IntegradorServicos, AdaptadorPrometheus, AdaptadorGrafana

@pytest.fixture
def config():
    """Fixture com configurações de exemplo."""
    return {
        'monitoramento_url': 'http://monitoramento:8080',
        'observabilidade_url': 'http://observabilidade:8080',
        'diagnostico_url': 'http://diagnostico:8080',
        'autocorrecao_url': 'http://autocorrecao:8080',
        'orquestracao_url': 'http://orquestracao:8080',
        'timeout': 5
    }

@pytest.fixture
def config_prometheus():
    """Fixture com configurações do Prometheus."""
    return {
        'url': 'http://prometheus:9090',
        'timeout': 5
    }

@pytest.fixture
def config_grafana():
    """Fixture com configurações do Grafana."""
    return {
        'url': 'http://grafana:3000',
        'api_key': 'test-key',
        'timeout': 5
    }

@pytest.fixture
def integrador(config):
    """Fixture com integrador."""
    return IntegradorServicos(config)

@pytest.fixture
def adaptador_prometheus(config_prometheus):
    """Fixture com adaptador do Prometheus."""
    return AdaptadorPrometheus(config_prometheus)

@pytest.fixture
def adaptador_grafana(config_grafana):
    """Fixture com adaptador do Grafana."""
    return AdaptadorGrafana(config_grafana)

@patch('requests.Session')
def test_obter_metricas(mock_session, integrador):
    """Testa obtenção de métricas."""
    mock_response = Mock()
    mock_response.json.return_value = {'cpu': 0.75, 'memory': 0.60}
    mock_session.return_value.get.return_value = mock_response
    
    metricas = integrador.obter_metricas()
    assert isinstance(metricas, dict)
    assert 'cpu' in metricas
    assert 'memory' in metricas

@patch('requests.Session')
def test_obter_logs(mock_session, integrador):
    """Testa obtenção de logs."""
    mock_response = Mock()
    mock_response.json.return_value = ['log1', 'log2']
    mock_session.return_value.get.return_value = mock_response
    
    logs = integrador.obter_logs()
    assert isinstance(logs, list)
    assert len(logs) == 2

@patch('requests.Session')
def test_obter_eventos(mock_session, integrador):
    """Testa obtenção de eventos."""
    mock_response = Mock()
    mock_response.json.return_value = [{'tipo': 'alerta'}, {'tipo': 'erro'}]
    mock_session.return_value.get.return_value = mock_response
    
    eventos = integrador.obter_eventos()
    assert isinstance(eventos, list)
    assert len(eventos) == 2

@patch('requests.Session')
def test_enviar_contexto(mock_session, integrador):
    """Testa envio de contexto."""
    mock_response = Mock()
    mock_session.return_value.post.return_value = mock_response
    
    contexto = {'servico': 'api', 'status': 'ok'}
    integrador.enviar_contexto(contexto)
    mock_session.return_value.post.assert_called_once()

@patch('requests.Session')
def test_enviar_projecao(mock_session, integrador):
    """Testa envio de projeção."""
    mock_response = Mock()
    mock_session.return_value.post.return_value = mock_response
    
    projecao = {'tendencias': [], 'cenarios': []}
    integrador.enviar_projecao(projecao)
    mock_session.return_value.post.assert_called_once()

@patch('requests.Session')
def test_consultar_metricas(mock_session, adaptador_prometheus):
    """Testa consulta de métricas no Prometheus."""
    mock_response = Mock()
    mock_response.json.return_value = {'status': 'success', 'data': {'result': []}}
    mock_session.return_value.get.return_value = mock_response
    
    resultado = adaptador_prometheus.consultar_metricas('up')
    assert isinstance(resultado, dict)
    assert 'status' in resultado
    assert 'data' in resultado

@patch('requests.Session')
def test_obter_dashboards(mock_session, adaptador_grafana):
    """Testa obtenção de dashboards do Grafana."""
    mock_response = Mock()
    mock_response.json.return_value = [{'title': 'Dashboard 1'}, {'title': 'Dashboard 2'}]
    mock_session.return_value.get.return_value = mock_response
    
    dashboards = adaptador_grafana.obter_dashboards()
    assert isinstance(dashboards, list)
    assert len(dashboards) == 2

@patch('requests.Session')
def test_obter_dashboard(mock_session, adaptador_grafana):
    """Testa obtenção de detalhes de dashboard."""
    mock_response = Mock()
    mock_response.json.return_value = {'dashboard': {'title': 'Dashboard 1'}}
    mock_session.return_value.get.return_value = mock_response
    
    dashboard = adaptador_grafana.obter_dashboard('test-uid')
    assert isinstance(dashboard, dict)
    assert 'dashboard' in dashboard

@patch('requests.Session')
def test_criar_dashboard(mock_session, adaptador_grafana):
    """Testa criação de dashboard."""
    mock_response = Mock()
    mock_session.return_value.post.return_value = mock_response
    
    dashboard = {'title': 'Novo Dashboard', 'panels': []}
    resultado = adaptador_grafana.criar_dashboard(dashboard)
    assert resultado is True
    mock_session.return_value.post.assert_called_once() 