#!/usr/bin/env python3
"""
Script para executar a reorganização do projeto e atualização da memória.
"""

import logging
import subprocess
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def executar_script(script_path: Path):
    """Executa um script Python."""
    try:
        logger.info(f"Executando script: {script_path}")
        resultado = subprocess.run(
            ['python', str(script_path)],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Script executado com sucesso: {script_path}")
        if resultado.stdout:
            logger.info(f"Saída do script:\n{resultado.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar script {script_path}:")
        logger.error(f"Saída de erro:\n{e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao executar script {script_path}: {str(e)}")
        raise

def main():
    """Função principal."""
    try:
        # Diretório base do projeto
        base_dir = Path(__file__).parent.parent
        
        # Scripts a serem executados
        scripts = [
            base_dir / 'scripts' / 'reorganizar.py',
            base_dir / 'src' / 'memoria' / 'atualizar_memoria.py'
        ]
        
        # Executa cada script
        for script in scripts:
            if script.exists():
                executar_script(script)
            else:
                logger.error(f"Script não encontrado: {script}")
                raise FileNotFoundError(f"Script não encontrado: {script}")
        
        logger.info("Atualização do projeto concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante a atualização do projeto: {str(e)}")
        raise

if __name__ == '__main__':
    main() 