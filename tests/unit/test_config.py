"""
Testes para o módulo de configuração do sistema.
"""

import pytest
from src.monitoramento.config import CONFIG

def test_config_estrutura():
    """Testa a estrutura básica da configuração."""
    assert isinstance(CONFIG, dict)
    assert 'intervalo_monitoramento' in CONFIG
    assert 'memoria' in CONFIG
    assert 'limites' in CONFIG
    assert 'ajuste' in CONFIG
    assert 'alertas' in CONFIG

def test_config_intervalo_monitoramento():
    """Testa o intervalo de monitoramento."""
    assert isinstance(CONFIG['intervalo_monitoramento'], int)
    assert CONFIG['intervalo_monitoramento'] > 0

def test_config_memoria():
    """Testa a configuração de memória."""
    memoria = CONFIG['memoria']
    assert isinstance(memoria, dict)
    assert 'max_historico' in memoria
    assert 'arquivo' in memoria
    assert isinstance(memoria['max_historico'], int)
    assert isinstance(memoria['arquivo'], str)

def test_config_limites():
    """Testa a configuração de limites."""
    limites = CONFIG['limites']
    assert isinstance(limites, dict)
    
    # Testa limites de CPU
    assert 'cpu' in limites
    assert 'total' in limites['cpu']
    assert 'por_core' in limites['cpu']
    assert 0 <= limites['cpu']['total'] <= 100
    assert 0 <= limites['cpu']['por_core'] <= 100
    
    # Testa limites de memória
    assert 'memoria' in limites
    assert 'percentual' in limites['memoria']
    assert 'swap_percentual' in limites['memoria']
    assert 0 <= limites['memoria']['percentual'] <= 100
    assert 0 <= limites['memoria']['swap_percentual'] <= 100
    
    # Testa limites de disco
    assert 'disco' in limites
    assert 'percentual' in limites['disco']
    assert 'espaco_livre_minimo' in limites['disco']
    assert 0 <= limites['disco']['percentual'] <= 100
    assert isinstance(limites['disco']['espaco_livre_minimo'], int)

def test_config_ajustes():
    """Testa a configuração de ajustes."""
    ajuste = CONFIG['ajuste']
    assert isinstance(ajuste, dict)
    
    # Testa ajustes de CPU
    assert 'cpu' in ajuste
    assert 'percentual_ajuste' in ajuste['cpu']
    assert 'prioridade_minima' in ajuste['cpu']
    assert 0 <= ajuste['cpu']['percentual_ajuste'] <= 100
    assert 0 <= ajuste['cpu']['prioridade_minima'] <= 100
    
    # Testa ajustes de memória
    assert 'memoria' in ajuste
    assert 'limite_cache' in ajuste['memoria']
    assert 'percentual_swap' in ajuste['memoria']
    assert isinstance(ajuste['memoria']['limite_cache'], int)
    assert 0 <= ajuste['memoria']['percentual_swap'] <= 100
    
    # Testa ajustes de disco
    assert 'disco' in ajuste
    assert 'dias_retencao' in ajuste['disco']
    assert 'limite_logs' in ajuste['disco']
    assert isinstance(ajuste['disco']['dias_retencao'], int)
    assert isinstance(ajuste['disco']['limite_logs'], int)

def test_config_alertas():
    """Testa a configuração de alertas."""
    alertas = CONFIG['alertas']
    assert isinstance(alertas, dict)
    
    # Testa configuração de email
    assert 'email' in alertas
    assert 'smtp' in alertas['email']
    smtp = alertas['email']['smtp']
    assert 'porta' in smtp
    assert 'servidor' in smtp
    assert 'usuario' in smtp
    assert 'senha' in smtp
    assert isinstance(smtp['porta'], int)
    assert isinstance(smtp['servidor'], str)
    assert isinstance(smtp['usuario'], str)
    assert isinstance(smtp['senha'], str)
    assert 'destinatarios' in alertas['email']
    assert isinstance(alertas['email']['destinatarios'], list)
    
    # Testa configuração de Slack
    assert 'slack' in alertas
    slack = alertas['slack']
    assert 'webhook_url' in slack
    assert 'canal' in slack
    assert 'icones' in slack
    assert isinstance(slack['webhook_url'], str)
    assert isinstance(slack['canal'], str)
    assert isinstance(slack['icones'], dict)
    for nivel in ['info', 'warning', 'error', 'critical']:
        assert nivel in slack['icones']
        assert isinstance(slack['icones'][nivel], str) 