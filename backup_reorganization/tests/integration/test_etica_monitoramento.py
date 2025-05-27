import pytest
from modulos.etica import EticaManager
from modulos.monitoramento import MonitorManager

@pytest.mark.asyncio
async def test_etica_monitoramento():
    """Teste de integração entre os módulos de ética e monitoramento."""
    
    # Inicializa os managers
    etica = EticaManager()
    monitor = MonitorManager()
    
    # Coleta métricas
    metricas = await monitor.coletar_metricas()
    
    # Valida métricas com ética
    resultado = await etica.validar_metricas(metricas)
    
    # Verifica resultado
    assert resultado['valido'] == True
    assert 'explicacao' in resultado
    assert 'recomendacoes' in resultado

@pytest.mark.asyncio
async def test_etica_monitoramento_limites():
    """Teste de integração verificando limites éticos no monitoramento."""
    
    etica = EticaManager()
    monitor = MonitorManager()
    
    # Simula métricas acima do limite
    metricas = {
        'cpu_usage': 95,
        'memory_usage': 90,
        'disk_usage': 85
    }
    
    # Valida métricas
    resultado = await etica.validar_metricas(metricas)
    
    # Verifica que o sistema detectou o problema
    assert resultado['valido'] == False
    assert 'alerta' in resultado
    assert 'acao_corretiva' in resultado

@pytest.mark.asyncio
async def test_etica_monitoramento_ajuste():
    """Teste de integração verificando ajustes automáticos."""
    
    etica = EticaManager()
    monitor = MonitorManager()
    
    # Simula situação que requer ajuste
    metricas = {
        'cpu_usage': 80,
        'memory_usage': 75,
        'disk_usage': 70
    }
    
    # Obtém recomendação de ajuste
    ajuste = await etica.recomendar_ajuste(metricas)
    
    # Aplica ajuste
    resultado = await monitor.aplicar_ajuste(ajuste)
    
    # Verifica resultado
    assert resultado['sucesso'] == True
    assert 'novas_metricas' in resultado
    assert 'log_ajuste' in resultado 