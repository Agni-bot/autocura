import pytest
import asyncio
import psutil
from datetime import datetime
from src.monitoramento.recursos import MonitorRecursos
from src.monitoramento.config import CONFIG

@pytest.fixture
def monitor():
    return MonitorRecursos()

@pytest.mark.asyncio
async def test_coleta_metricas(monitor):
    """Testa coleta de métricas do sistema"""
    metricas = monitor.coletar_metricas()
    
    # Verifica estrutura das métricas
    assert 'cpu' in metricas
    assert 'memoria' in metricas
    assert 'disco' in metricas
    assert 'equidade' in metricas
    assert 'timestamp' in metricas
    
    # Verifica tipos e valores
    assert isinstance(metricas['cpu']['total'], float)
    assert isinstance(metricas['cpu']['por_core'], list)
    assert isinstance(metricas['memoria']['percentual'], float)
    assert isinstance(metricas['disco']['percentual'], float)
    assert isinstance(metricas['equidade'], float)
    assert isinstance(metricas['timestamp'], str)
    
    # Verifica limites
    assert 0 <= metricas['cpu']['total'] <= 100
    assert 0 <= metricas['memoria']['percentual'] <= 100
    assert 0 <= metricas['disco']['percentual'] <= 100
    assert 0 <= metricas['equidade'] <= 1

@pytest.mark.asyncio
async def test_calculo_equidade(monitor):
    """Testa cálculo de equidade na distribuição de recursos"""
    # Teste com distribuição igual
    monitor.recursos = {
        'recurso1': 1.0,
        'recurso2': 1.0,
        'recurso3': 1.0
    }
    assert monitor.calcular_equidade() == 1.0
    
    # Teste com distribuição desigual
    monitor.recursos = {
        'recurso1': 0.8,
        'recurso2': 0.9,
        'recurso3': 0.7
    }
    equidade = monitor.calcular_equidade()
    assert 0 < equidade < 1.0
    
    # Teste sem recursos
    monitor.recursos = {}
    assert monitor.calcular_equidade() == 1.0

@pytest.mark.asyncio
async def test_verificacao_limites(monitor):
    """Testa verificação de limites de recursos"""
    # Teste com métricas normais
    metricas_normais = {
        'cpu': {
            'total': 50.0,
            'por_core': [50.0, 50.0],
            'frequencia': 2000.0
        },
        'memoria': {
            'percentual': 50.0,
            'swap': {'percentual': 50.0}
        },
        'disco': {
            'percentual': 50.0,
            'livre': 2 * 1024 * 1024 * 1024  # 2GB
        },
        'equidade': 0.9
    }
    assert not monitor.verificar_limites(metricas_normais)
    
    # Teste com CPU alta
    metricas_cpu_alta = metricas_normais.copy()
    metricas_cpu_alta['cpu']['total'] = 90.0
    assert monitor.verificar_limites(metricas_cpu_alta)
    
    # Teste com memória alta
    metricas_memoria_alta = metricas_normais.copy()
    metricas_memoria_alta['memoria']['percentual'] = 90.0
    assert monitor.verificar_limites(metricas_memoria_alta)
    
    # Teste com disco alto
    metricas_disco_alto = metricas_normais.copy()
    metricas_disco_alto['disco']['percentual'] = 95.0
    assert monitor.verificar_limites(metricas_disco_alto)
    
    # Teste com equidade baixa
    metricas_equidade_baixa = metricas_normais.copy()
    metricas_equidade_baixa['equidade'] = 0.5
    assert monitor.verificar_limites(metricas_equidade_baixa)

@pytest.mark.asyncio
async def test_ajuste_recursos(monitor):
    """Testa ajuste automático de recursos"""
    # Configura recursos iniciais
    monitor.recursos = {
        'recurso1': 0.9,
        'recurso2': 0.1
    }
    
    # Simula métricas que acionam ajuste
    metricas = {
        'cpu': {
            'total': 90.0,
            'por_core': [90.0, 90.0],
            'frequencia': 2000.0
        },
        'memoria': {
            'percentual': 90.0,
            'swap': {'percentual': 90.0}
        },
        'disco': {
            'percentual': 95.0,
            'livre': 512 * 1024 * 1024  # 512MB
        },
        'equidade': 0.5
    }
    
    # Executa ajuste
    await monitor.ajustar_recursos(metricas)
    
    # Verifica se equidade foi ajustada
    assert monitor.calcular_equidade() > 0.8
    
    # Verifica se histórico foi atualizado
    assert len(monitor.historico) > 0
    ultima_metrica = monitor.historico[-1]
    assert 'timestamp' in ultima_metrica
    assert 'metricas' in ultima_metrica

@pytest.mark.asyncio
async def test_monitoramento_continuo(monitor):
    """Testa monitoramento contínuo por 5 segundos"""
    # Inicia monitoramento em background
    monitor_task = asyncio.create_task(monitor.iniciar_monitoramento())
    
    # Aguarda 5 segundos
    await asyncio.sleep(5)
    
    # Cancela monitoramento
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass
        
    # Verifica histórico
    assert len(monitor.historico) > 0
    ultimas_metricas = monitor.historico[-1]
    assert 'cpu' in ultimas_metricas
    assert 'memoria' in ultimas_metricas
    assert 'disco' in ultimas_metricas
    assert 'equidade' in ultimas_metricas 