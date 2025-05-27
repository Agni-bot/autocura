#!/usr/bin/env python3
"""
Script principal para executar o monitoramento de recursos do sistema.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import asyncio
import logging
import signal
from pathlib import Path
from prometheus_client import start_http_server
from src.monitoramento.recursos import MonitorRecursos

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitoramento.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Variáveis globais
monitor = None
prometheus_port = 9090

def signal_handler(signum, frame):
    """Manipulador de sinais para encerramento gracioso"""
    logger.info(f"Recebido sinal {signum}. Encerrando monitoramento...")
    if monitor:
        asyncio.create_task(monitor.encerrar())
    sys.exit(0)

async def main(MonitorClass=None, prometheus_registry=None):
    """Função principal que executa o monitoramento"""
    global monitor
    MonitorClass = MonitorClass or MonitorRecursos
    try:
        # Configura handlers de sinal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Cria diretório de logs se não existir
        Path('logs').mkdir(exist_ok=True)
        
        # Inicia servidor Prometheus
        start_http_server(prometheus_port)
        logger.info(f"Servidor Prometheus iniciado na porta {prometheus_port}")
        
        # Inicializa e inicia monitoramento
        logger.info("Iniciando sistema de monitoramento de recursos")
        monitor = MonitorClass(registry=prometheus_registry)
        await monitor.iniciar_monitoramento()
        
    except KeyboardInterrupt:
        logger.info("Monitoramento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal no monitoramento: {e}")
        if monitor:
            await monitor.encerrar()
    finally:
        if monitor:
            await monitor.encerrar()

if __name__ == '__main__':
    asyncio.run(main()) 