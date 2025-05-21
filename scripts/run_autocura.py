#!/usr/bin/env python
"""
Script para executar o sistema de autocura
"""

import os
import sys
import time
import logging
import yaml
from pathlib import Path
from datetime import datetime

# Adiciona diretório raiz ao PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from src.autocura import AutocuraEngine
from src.autocura.memory import MemoryManager
from src.autocura.feedback import FeedbackSystem
from src.autocura.monitoring import AutocuraMonitor

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/autocura.log')
    ]
)
logger = logging.getLogger(__name__)

def load_config() -> dict:
    """Carrega configurações do arquivo YAML"""
    try:
        config_path = ROOT_DIR / "config" / "autocura.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")
        sys.exit(1)

def setup_components(config: dict):
    """Configura componentes do sistema"""
    try:
        # Configura gerenciador de memória
        memory_manager = MemoryManager(
            memory_path=ROOT_DIR / config["memoria"]["caminho_arquivo"]
        )
        
        # Configura sistema de feedback
        feedback_system = FeedbackSystem(
            feedback_path=ROOT_DIR / config["feedback"]["caminho_arquivo"]
        )
        
        # Configura monitor
        monitor = AutocuraMonitor(
            metrics_path=ROOT_DIR / config["monitoramento"]["metricas"]["caminho_arquivo"],
            prometheus_port=config["monitoramento"]["prometheus"]["porta"]
        )
        
        # Configura motor de autocura
        engine = AutocuraEngine(
            config_path=ROOT_DIR / "config" / "autocura.yaml",
            memory_manager=memory_manager,
            feedback_system=feedback_system,
            monitor=monitor
        )
        
        return engine, memory_manager, feedback_system, monitor
        
    except Exception as e:
        logger.error(f"Erro ao configurar componentes: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    try:
        # Carrega configurações
        config = load_config()
        logger.info("Configurações carregadas com sucesso")
        
        # Configura componentes
        engine, memory, feedback, monitor = setup_components(config)
        logger.info("Componentes configurados com sucesso")
        
        # Loop principal
        while True:
            try:
                # Atualiza métricas do sistema
                monitor.update_system_metrics()
                
                # Executa ciclo de evolução
                evolution_record = engine.evolve()
                if evolution_record:
                    logger.info(f"Ciclo de evolução concluído: {evolution_record}")
                
                # Aguarda próximo ciclo
                time.sleep(config["geral"]["intervalo_evolucao"])
                
            except KeyboardInterrupt:
                logger.info("Encerrando sistema...")
                break
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente
        
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 