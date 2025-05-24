import os
import logging.config
from typing import Dict, Any

def configurar_logging(config_path: str = None) -> Dict[str, Any]:
    """Configura o sistema de logging com as configurações padrão ou de um arquivo"""
    
    # Configuração padrão
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'padrao': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'json': {
                'format': '%(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'padrao',
                'stream': 'ext://sys.stdout'
            },
            'arquivo': {
                'class': 'logging.FileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': 'logs/ethical_audit.log',
                'mode': 'a'
            },
            'arquivo_erro': {
                'class': 'logging.FileHandler',
                'level': 'ERROR',
                'formatter': 'json',
                'filename': 'logs/ethical_errors.log',
                'mode': 'a'
            }
        },
        'loggers': {
            'ethical_logger': {
                'level': 'INFO',
                'handlers': ['console', 'arquivo', 'arquivo_erro'],
                'propagate': False
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }
    
    # Cria diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)
    
    # Carrega configuração do arquivo se fornecido
    if config_path and os.path.exists(config_path):
        import yaml
        with open(config_path, 'r') as f:
            config_arquivo = yaml.safe_load(f)
            config.update(config_arquivo)
    
    # Aplica configuração
    logging.config.dictConfig(config)
    
    return config 