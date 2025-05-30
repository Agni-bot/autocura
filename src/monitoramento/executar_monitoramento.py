#!/usr/bin/env python3
"""
Script para executar o monitoramento do sistema.
"""

import os
import sys
import logging
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from src.monitoramento import MonitorSistema
from src.monitoramento.config import CONFIG

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('monitoramento.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Função principal."""
    try:
        # Inicializa o monitor
        monitor = MonitorSistema()
        
        # Inicia o monitoramento
        monitor.iniciar()
        
        # Mantém o script rodando
        while True:
            try:
                # Aguarda input do usuário
                comando = input("Digite 'q' para sair: ")
                if comando.lower() == 'q':
                    break
            except KeyboardInterrupt:
                break
                
        # Para o monitoramento
        monitor.parar()
        
    except Exception as e:
        logger.error(f"Erro ao executar monitoramento: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 