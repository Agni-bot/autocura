"""
Script para execução automática dos testes do sistema de autocura.
"""

import os
import sys
import yaml
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .automatizador_testes import AutomatizadorTestes

def carregar_configuracao() -> Dict[str, Any]:
    """
    Carrega as configurações do arquivo YAML.
    
    Returns:
        Dict[str, Any]: Configurações carregadas
    """
    config_path = Path(__file__).parent / "config_testes.yaml"
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Erro ao carregar configurações: {str(e)}")
        sys.exit(1)

def configurar_logging(config: Dict[str, Any]) -> None:
    """
    Configura o sistema de logging.
    
    Args:
        config: Configurações carregadas
    """
    log_config = config.get("logging", {})
    log_path = Path(log_config.get("arquivo", "logs/testes.log"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_config.get("level", "INFO")),
        format=log_config.get("formato", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )

def configurar_ambiente(config: Dict[str, Any]) -> None:
    """
    Configura as variáveis de ambiente para os testes.
    
    Args:
        config: Configurações carregadas
    """
    variaveis = config.get("ambiente", {}).get("variaveis", {})
    for nome, valor in variaveis.items():
        os.environ[nome] = valor

def main():
    """Função principal de execução."""
    # Carrega configurações
    config = carregar_configuracao()
    
    # Configura logging
    configurar_logging(config)
    logger = logging.getLogger(__name__)
    
    # Configura ambiente
    configurar_ambiente(config)
    
    logger.info("Iniciando execução automática dos testes...")
    
    try:
        # Inicializa e executa o automatizador
        automatizador = AutomatizadorTestes(config)
        sucesso = automatizador.executar_todos_testes()
        
        if sucesso:
            logger.info("✅ Todos os testes passaram com sucesso!")
            sys.exit(0)
        else:
            logger.error("❌ Alguns testes falharam!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Erro durante a execução dos testes: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 