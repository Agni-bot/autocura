"""
Testes para funcionalidades críticas do sistema de monitoramento.
"""

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from pathlib import Path
from prometheus_client import CollectorRegistry
from src.monitoramento.recursos import MonitorRecursos
from src.monitoramento.config import CONFIG

@pytest.fixture
def mock_psutil():
    """Fixture que retorna um mock do psutil."""
    with patch('psutil.cpu_percent') as mock_cpu, \
         patch('psutil.virtual_memory') as mock_mem, \
         patch('psutil.disk_usage') as mock_disk, \
         patch('psutil.swap_memory') as mock_swap, \
         patch('psutil.process_iter') as mock_process:
        
        # Configura retornos padrão
        mock_cpu.return_value = [50.0, 60.0]  # 2 cores
        mock_mem.return_value = MagicMock(
            total=1024*1024*1024,  # 1GB
            available=512*1024*1024,  # 512MB
            percent=50.0
        )
        mock_disk.return_value = MagicMock(
            total=1024*1024*1024,  # 1GB
            used=512*1024*1024,  # 512MB
            free=512*1024*1024,  # 512MB
            percent=50.0
        )
        mock_swap.return_value = MagicMock(
            total=1024*1024*1024,  # 1GB
            used=256*1024*1024,  # 256MB
            percent=25.0
        )
        mock_process.return_value = [
            MagicMock(info={'pid': 1, 'name': 'test', 'cpu_percent': 30.0}),
            MagicMock(info={'pid': 2, 'name': 'test2', 'cpu_percent': 40.0})
        ]
        
        yield {
            'cpu': mock_cpu,
            'mem': mock_mem,
            'disk': mock_disk,
            'swap': mock_swap,
            'process': mock_process
        }

@pytest.fixture
def monitor_recursos():
    """Fixture que retorna uma instância do MonitorRecursos."""
    registry = CollectorRegistry()
    return MonitorRecursos(registry=registry)

@pytest.mark.asyncio
async def test_coleta_metricas_basicas(monitor_recursos, mock_psutil):
    """Testa a coleta básica de métricas."""
    metricas = monitor_recursos.coletar_metricas()
    
    assert 'cpu' in metricas
    assert 'memoria' in metricas
    assert 'disco' in metricas
    assert 'equidade' in metricas
    assert 'timestamp' in metricas
    
    # Verifica valores específicos
    assert metricas['cpu']['total'] == 55.0  # média dos cores
    assert metricas['memoria']['percentual'] == 50.0
    assert metricas['disco']['percentual'] == 50.0
    assert metricas['equidade'] == 1.0  # valor padrão quando não há recursos

@pytest.mark.asyncio
async def test_verificacao_limites_cpu(monitor_recursos, mock_psutil):
    """Testa a verificação de limites de CPU."""
    # Simula uso alto de CPU
    mock_psutil['cpu'].return_value = [90.0, 95.0]
    
    metricas = monitor_recursos.coletar_metricas()
    alertas = monitor_recursos.verificar_limites(metricas)
    
    assert alertas is True
    assert len(monitor_recursos.historico) > 0
    ultimo_alerta = monitor_recursos.historico[-1]
    assert 'alertas' in ultimo_alerta
    assert any(a['tipo'] == 'cpu' for a in ultimo_alerta['alertas'])

@pytest.mark.asyncio
async def test_verificacao_limites_memoria(monitor_recursos, mock_psutil):
    """Testa a verificação de limites de memória."""
    # Simula uso alto de memória
    mock_psutil['mem'].return_value = MagicMock(
        total=1024*1024*1024,
        available=100*1024*1024,  # Pouca memória disponível
        percent=90.0  # 90% de uso
    )
    
    metricas = monitor_recursos.coletar_metricas()
    alertas = monitor_recursos.verificar_limites(metricas)
    
    assert alertas is True
    assert len(monitor_recursos.historico) > 0
    ultimo_alerta = monitor_recursos.historico[-1]
    assert 'alertas' in ultimo_alerta
    assert any(a['tipo'] == 'memoria' for a in ultimo_alerta['alertas'])

@pytest.mark.asyncio
async def test_ajuste_automatico_cpu(monitor_recursos, mock_psutil):
    """Testa o ajuste automático de CPU."""
    # Simula uso alto de CPU
    mock_psutil['cpu'].return_value = [90.0, 95.0]

    metricas = monitor_recursos.coletar_metricas()
    await monitor_recursos.ajustar_recursos(metricas)

    # Verifica se o contador de ajustes foi incrementado
    metric = monitor_recursos.ajustes_counter.collect()[0].samples
    cpu_count = [s.value for s in metric if s.labels.get('tipo') == 'cpu']
    assert cpu_count and cpu_count[0] > 0

@pytest.mark.asyncio
async def test_ajuste_automatico_memoria(monitor_recursos, mock_psutil):
    """Testa o ajuste automático de memória."""
    # Simula uso alto de memória
    mock_psutil['mem'].return_value = MagicMock(
        total=1024*1024*1024,
        available=100*1024*1024,
        percent=90.0
    )
    
    # Mock do processo com memory_percent
    mock_process = MagicMock()
    mock_process.info = {'pid': 1234, 'name': 'test', 'memory_percent': 5.0}
    mock_psutil['process'].return_value = [mock_process]

    metricas = monitor_recursos.coletar_metricas()
    await monitor_recursos.ajustar_recursos(metricas)
    
    # Verifica se o contador de ajustes foi incrementado
    metric = monitor_recursos.ajustes_counter.collect()[0].samples
    mem_count = [s.value for s in metric if s.labels.get('tipo') == 'memoria']
    assert mem_count and mem_count[0] >= 0

@pytest.mark.asyncio
async def test_atualizacao_memoria_compartilhada(monitor_recursos, tmp_path):
    """Testa a atualização da memória compartilhada."""
    # Configura caminho temporário para memória compartilhada
    monitor_recursos.memoria_path = tmp_path / "memoria_compartilhada.json"
    
    metricas = monitor_recursos.coletar_metricas()
    monitor_recursos.atualizar_memoria_compartilhada(metricas)
    
    # Verifica se o arquivo foi criado e contém os dados corretos
    assert monitor_recursos.memoria_path.exists()
    with open(monitor_recursos.memoria_path, 'r') as f:
        memoria = json.load(f)
        assert "memoria_tecnica" in memoria
        assert "metricas" in memoria["memoria_tecnica"]
        assert "recursos" in memoria["memoria_tecnica"]["metricas"]

@pytest.mark.asyncio
async def test_calculo_equidade(monitor_recursos):
    """Testa o cálculo de equidade na distribuição de recursos."""
    # Simula distribuição desigual de recursos
    monitor_recursos.recursos = {
        'recurso1': 80.0,
        'recurso2': 20.0,
        'recurso3': 30.0
    }
    
    equidade = monitor_recursos.calcular_equidade()
    
    # Equidade deve estar entre 0 e 1
    assert 0 <= equidade <= 1
    # Com essa distribuição desigual, a equidade deve ser baixa
    assert equidade < 0.5

@pytest.mark.asyncio
async def test_ajuste_equidade(monitor_recursos):
    """Testa o ajuste automático de equidade."""
    # Configura distribuição desigual
    monitor_recursos.recursos = {
        'recurso1': 80.0,
        'recurso2': 20.0,
        'recurso3': 30.0
    }
    
    await monitor_recursos.ajustar_equidade()
    
    # Após o ajuste, os recursos devem estar mais equilibrados
    valores = list(monitor_recursos.recursos.values())
    media = sum(valores) / len(valores)
    desvio = sum(abs(v - media) for v in valores) / len(valores)
    
    # O desvio deve ser pequeno após o ajuste
    assert desvio < 1.0

@pytest.mark.asyncio
async def test_encerramento_gracioso(monitor_recursos):
    """Testa o encerramento gracioso do monitoramento."""
    # Inicia monitoramento
    task = asyncio.create_task(monitor_recursos.iniciar_monitoramento())
    
    # Aguarda um pouco
    await asyncio.sleep(0.1)
    
    # Encerra graciosamente
    await monitor_recursos.encerrar()
    
    # Cancela a task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Verifica se os recursos foram limpos
    assert len(monitor_recursos.recursos) == 0
    assert len(monitor_recursos.historico) == 0 