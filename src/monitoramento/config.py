from typing import Dict, Any

"""
Configurações do sistema de monitoramento de recursos.
"""

# Configurações gerais
CONFIG: Dict[str, Any] = {
    # Intervalos de monitoramento (em segundos)
    'intervalo_monitoramento': 30,
    'intervalo_ajuste': 60,
    
    # Limites de recursos
    'limites': {
        'cpu': {
            'total': 80,  # percentual
            'por_core': 90,  # percentual
            'frequencia_minima': 1000  # MHz
        },
        'memoria': {
            'percentual': 80,  # percentual
            'swap_percentual': 70  # percentual
        },
        'disco': {
            'percentual': 85,  # percentual
            'espaco_livre_minimo': 1024 * 1024 * 1024  # 1GB em bytes
        },
        'equidade': 0.85  # índice de equidade mínimo
    },
    
    # Diretórios para limpeza
    'diretorios_temp': [
        '/tmp',
        './temp',
        './cache',
        './logs/temp'
    ],
    
    # Configurações de logging
    'logging': {
        'nivel': 'INFO',
        'arquivo': 'logs/monitoramento.log',
        'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'max_bytes': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    },
    
    # Configurações de memória compartilhada
    'memoria': {
        'max_historico': 1000,
        'arquivo': 'memoria/monitoramento.json'
    },
    
    # Configurações de ajuste automático
    'ajuste': {
        'cpu': {
            'percentual_ajuste': 70,  # percentual
            'prioridade_minima': 10  # nice value
        },
        'memoria': {
            'limite_cache': 1024 * 1024 * 1024,  # 1GB em bytes
            'percentual_swap': 50  # percentual
        },
        'disco': {
            'limite_logs': 1024 * 1024 * 1024,  # 1GB em bytes
            'dias_retencao': 7
        }
    },
    
    'alertas': {
        'email': {
            'smtp': {
                'servidor': 'smtp.gmail.com',
                'porta': 587,
                'usuario': 'seu-email@gmail.com',
                'senha': 'sua-senha'
            },
            'destinatarios': ['admin@exemplo.com']
        },
        'slack': {
            'webhook_url': 'https://hooks.slack.com/services/...',
            'canal': '#monitoramento',
            'icones': {
                'info': ':information_source:',
                'warning': ':warning:',
                'error': ':x:',
                'critical': ':rotating_light:'
            }
        }
    }
} 