#!/usr/bin/env python3
import os
import sys
import logging
from datetime import datetime

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Função principal para executar testes de desempenho.
    """
    try:
        # Adiciona diretório raiz ao path
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.append(root_dir)
        
        # Importa e executa testes
        from tests.performance.test_desempenho import test_performance
        
        logger.info("Iniciando testes de desempenho...")
        start_time = datetime.now()
        
        test_performance()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Testes de desempenho concluídos em {duration:.2f} segundos")
        
    except Exception as e:
        logger.error(f"Erro ao executar testes de desempenho: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 