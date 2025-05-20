"""
Testes do módulo de configuração da Consciência Situacional.
"""

import pytest
import os
import yaml
import json
from pathlib import Path
from ..config import Configurador, CONFIG_PADRAO

@pytest.fixture
def config_path(tmp_path):
    """Fixture com caminho temporário para arquivo de configuração."""
    return str(tmp_path / 'config.yaml')

@pytest.fixture
def config_yaml(config_path):
    """Fixture com arquivo YAML de configuração."""
    config = {
        'servicos': {
            'monitoramento': {
                'url': 'http://test:8080',
                'timeout': 10
            }
        }
    }
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    return config_path

@pytest.fixture
def config_json(config_path):
    """Fixture com arquivo JSON de configuração."""
    config = {
        'servicos': {
            'monitoramento': {
                'url': 'http://test:8080',
                'timeout': 10
            }
        }
    }
    json_path = config_path.replace('.yaml', '.json')
    with open(json_path, 'w') as f:
        json.dump(config, f)
    return json_path

@pytest.fixture
def configurador(config_path):
    """Fixture com configurador."""
    return Configurador(config_path)

def test_carregar_config_yaml(configurador, config_yaml):
    """Testa carregamento de configuração YAML."""
    configurador.config_path = config_yaml
    configurador._carregar_config()
    assert configurador.config['servicos']['monitoramento']['url'] == 'http://test:8080'
    assert configurador.config['servicos']['monitoramento']['timeout'] == 10

def test_carregar_config_json(configurador, config_json):
    """Testa carregamento de configuração JSON."""
    configurador.config_path = config_json
    configurador._carregar_config()
    assert configurador.config['servicos']['monitoramento']['url'] == 'http://test:8080'
    assert configurador.config['servicos']['monitoramento']['timeout'] == 10

def test_obter_config(configurador):
    """Testa obtenção de configuração."""
    configurador.config = CONFIG_PADRAO
    config = configurador.obter_config('servicos.monitoramento')
    assert config['url'] == 'http://monitoramento:8080'
    assert config['timeout'] == 5

def test_definir_config(configurador):
    """Testa definição de configuração."""
    configurador.definir_config('test.key', 'value')
    assert configurador.config['test']['key'] == 'value'

def test_salvar_config(configurador, config_path):
    """Testa salvamento de configuração."""
    configurador.config = {'test': {'key': 'value'}}
    configurador.salvar_config()
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    assert config['test']['key'] == 'value'

def test_obter_config_servico(configurador):
    """Testa obtenção de configuração de serviço."""
    configurador.config = CONFIG_PADRAO
    config = configurador.obter_config_servico('monitoramento')
    assert config['url'] == 'http://monitoramento:8080'
    assert config['timeout'] == 5

def test_obter_config_monitoramento(configurador):
    """Testa obtenção de configuração de monitoramento."""
    configurador.config = CONFIG_PADRAO
    config = configurador.obter_config_monitoramento()
    assert config['intervalo_coleta'] == 5
    assert config['retencao_historico'] == 3600

def test_obter_config_observabilidade(configurador):
    """Testa obtenção de configuração de observabilidade."""
    configurador.config = CONFIG_PADRAO
    config = configurador.obter_config_observabilidade()
    assert config['nivel_log'] == 'INFO'
    assert config['retencao_logs'] == 86400

def test_obter_config_diagnostico(configurador):
    """Testa obtenção de configuração de diagnóstico."""
    configurador.config = CONFIG_PADRAO
    config = configurador.obter_config_diagnostico()
    assert config['limiar_alerta'] == 0.8
    assert config['intervalo_analise'] == 10

def test_obter_config_autocorrecao(configurador):
    """Testa obtenção de configuração de autocorreção."""
    configurador.config = CONFIG_PADRAO
    config = configurador.obter_config_autocorrecao()
    assert config['max_tentativas'] == 3
    assert config['intervalo_retry'] == 5

def test_obter_config_orquestracao(configurador):
    """Testa obtenção de configuração de orquestração."""
    configurador.config = CONFIG_PADRAO
    config = configurador.obter_config_orquestracao()
    assert config['max_replicas'] == 10
    assert config['min_replicas'] == 1

def test_obter_config_prometheus(configurador):
    """Testa obtenção de configuração do Prometheus."""
    configurador.config = CONFIG_PADRAO
    config = configurador.obter_config_prometheus()
    assert config['url'] == 'http://prometheus:9090'
    assert config['timeout'] == 5

def test_obter_config_grafana(configurador):
    """Testa obtenção de configuração do Grafana."""
    configurador.config = CONFIG_PADRAO
    config = configurador.obter_config_grafana()
    assert config['url'] == 'http://grafana:3000'
    assert config['timeout'] == 5 