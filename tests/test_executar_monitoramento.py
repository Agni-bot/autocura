"""
Testes para o módulo de execução do monitoramento.
"""

import pytest
import asyncio
import signal
from unittest.mock import patch, MagicMock, AsyncMock
from prometheus_client import CollectorRegistry
from src.monitoramento.executar_monitoramento import main, signal_handler

@pytest.fixture
def mock_monitor():
    """Fixture que retorna um mock do MonitorRecursos."""
    mock = MagicMock()
    mock.iniciar_monitoramento = AsyncMock()
    mock.encerrar = AsyncMock()
    return mock

@pytest.fixture
def prometheus_registry():
    return CollectorRegistry()

@pytest.mark.asyncio
async def test_main_inicializacao(mock_monitor, prometheus_registry):
    """Testa a inicialização do monitoramento."""
    with patch('src.monitoramento.recursos.MonitorRecursos', return_value=mock_monitor) as MonitorClass:
        task = asyncio.create_task(main(MonitorClass=MonitorClass, prometheus_registry=prometheus_registry))
        await asyncio.sleep(0.2)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert mock_monitor.iniciar_monitoramento.called

@pytest.mark.asyncio
async def test_main_tratamento_erro(mock_monitor, prometheus_registry):
    """Testa o tratamento de erros no monitoramento."""
    mock_monitor.iniciar_monitoramento.side_effect = Exception("Erro de teste")
    with patch('src.monitoramento.recursos.MonitorRecursos', return_value=mock_monitor) as MonitorClass:
        task = asyncio.create_task(main(MonitorClass=MonitorClass, prometheus_registry=prometheus_registry))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        mock_monitor.iniciar_monitoramento.assert_called_once()
        mock_monitor.encerrar.assert_called()

def test_signal_handler(mock_monitor):
    """Testa o handler de sinais."""
    # Configura o mock global
    import src.monitoramento.executar_monitoramento
    src.monitoramento.executar_monitoramento.monitor = mock_monitor
    
    # Simula o recebimento de um sinal
    try:
        signal_handler(signal.SIGTERM, None)
    except RuntimeError:
        # Pode não haver event loop rodando, ignorar para teste
        pass
    
    # Verifica se o monitoramento foi encerrado
    mock_monitor.encerrar.assert_called()

@pytest.mark.asyncio
async def test_main_criacao_diretorios(prometheus_registry):
    """Testa a criação de diretórios necessários."""
    mock_monitor = MagicMock()
    mock_monitor.iniciar_monitoramento = AsyncMock()
    mock_monitor.encerrar = AsyncMock()
    with patch('pathlib.Path.mkdir') as mock_mkdir:
        with patch('src.monitoramento.recursos.MonitorRecursos', return_value=mock_monitor) as MonitorClass:
            task = asyncio.create_task(main(MonitorClass=MonitorClass, prometheus_registry=prometheus_registry))
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            mock_mkdir.assert_called_with(exist_ok=True)

@pytest.mark.asyncio
async def test_main_prometheus_server(prometheus_registry):
    """Testa a inicialização do servidor Prometheus."""
    mock_monitor = MagicMock()
    mock_monitor.iniciar_monitoramento = AsyncMock()
    mock_monitor.encerrar = AsyncMock()
    with patch('src.monitoramento.executar_monitoramento.start_http_server') as mock_start_server:
        with patch('src.monitoramento.recursos.MonitorRecursos', return_value=mock_monitor) as MonitorClass:
            task = asyncio.create_task(main(MonitorClass=MonitorClass, prometheus_registry=prometheus_registry))
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            mock_start_server.assert_called_once_with(9090) 