import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import timedelta

"""
Configurações do sistema de monitoramento de recursos.
"""

@dataclass
class Config:
    # Configurações gerais
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 4
    
    # Configurações do Prometheus
    PROMETHEUS_PORT: int = 9090
    METRICS_INTERVAL: int = 15  # segundos
    
    # Configurações de métricas
    METRICS: Dict[str, Dict] = {
        "throughput": {
            "type": "gauge",
            "description": "Requisições por segundo",
            "labels": ["endpoint"]
        },
        "taxa_erro": {
            "type": "gauge",
            "description": "Taxa de erro em porcentagem",
            "labels": ["endpoint", "tipo_erro"]
        },
        "latencia": {
            "type": "histogram",
            "description": "Latência em milissegundos",
            "labels": ["endpoint"],
            "buckets": [0.1, 0.5, 1.0, 2.0, 5.0]
        },
        "uso_recursos": {
            "type": "gauge",
            "description": "Uso de recursos do sistema",
            "labels": ["recurso"]
        }
    }
    
    # Configurações de alertas
    ALERTAS: Dict[str, Dict] = {
        "threshold": {
            "throughput": {"min": 0, "max": 1000},
            "taxa_erro": {"min": 0, "max": 5},
            "latencia": {"min": 0, "max": 1000},
            "uso_recursos": {
                "cpu": {"min": 0, "max": 80},
                "memoria": {"min": 0, "max": 80},
                "disco": {"min": 0, "max": 80}
            }
        },
        "tendencia": {
            "janela": 3600,  # 1 hora
            "sensitivity": 0.1
        },
        "anomalia": {
            "janela": 86400,  # 24 horas
            "threshold": 3.0  # desvios padrão
        }
    }
    
    # Configurações de notificação
    NOTIFICACOES: Dict[str, Dict] = {
        "email": {
            "enabled": False,
            "smtp_server": "",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "from_addr": "",
            "to_addrs": []
        },
        "slack": {
            "enabled": False,
            "webhook_url": "",
            "channel": ""
        },
        "webhook": {
            "enabled": False,
            "url": "",
            "headers": {}
        }
    }
    
    # Configurações de visualização
    VIZUALIZACAO: Dict[str, Dict] = {
        "dashboard": {
            "refresh_interval": 30,  # segundos
            "max_points": 1000,
            "default_range": "1h"
        },
        "graficos": {
            "tendencias": {
                "type": "line",
                "smoothing": 0.3
            },
            "recursos": {
                "type": "pie",
                "show_legend": True
            }
        }
    }
    
    # Configurações adicionais
    MONITORAMENTO_INTERVALO: int = 60  # segundos
    MONITORAMENTO_TIMEOUT: int = 30  # segundos
    ALERTAS_THRESHOLD: Dict[str, float] = {
        "cpu": 80.0,  # porcentagem
        "memoria": 85.0,  # porcentagem
        "disco": 90.0,  # porcentagem
        "latencia": 1000.0,  # milissegundos
    }
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "monitoramento.log"
    NOTIFICACOES_CANAIS: List[str] = ["email", "slack"]
    NOTIFICACOES_EMAIL: Dict[str, str] = {}
    NOTIFICACOES_SLACK: Dict[str, str] = {}
    PROMETHEUS_URL: str = "http://localhost:9090"
    PROMETHEUS_TIMEOUT: int = 10  # segundos
    DIAGNOSTICO_INTERVALO: int = 300  # segundos
    DIAGNOSTICO_HISTORICO: int = 7  # dias
    VISUALIZACAO_PERIODO: timedelta = timedelta(days=7)  # dias
    VISUALIZACAO_INTERVALO: int = 60  # segundos
    VISUALIZACAO_ANOMALIA_THRESHOLD: float = 2.0  # desvios padrão
    VISUALIZACAO_CORRELACAO_THRESHOLD: float = 0.7  # coeficiente de correlação
    VISUALIZACAO_TENDENCIA_THRESHOLD: float = 0.1  # inclinação mínima
    VISUALIZACAO_DIMENSOES: Dict[str, Dict[str, Dict[str, str]]] = {
        "performance": {
            "descricao": "Métricas de performance do sistema",
            "unidade": "porcentagem",
            "limites": {"min": 0, "max": 100},
        },
        "saude": {
            "descricao": "Indicadores de saúde do sistema",
            "unidade": "porcentagem",
            "limites": {"min": 0, "max": 100},
        },
        "latencia": {
            "descricao": "Tempo de resposta do sistema",
            "unidade": "milissegundos",
            "limites": {"min": 0, "max": 1000},
        },
        "erros": {
            "descricao": "Taxa de erros do sistema",
            "unidade": "porcentagem",
            "limites": {"min": 0, "max": 100},
        },
    }
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Carrega configurações das variáveis de ambiente."""
        config = cls()
        
        # Configurações gerais
        config.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        config.HOST = os.getenv("HOST", config.HOST)
        config.PORT = int(os.getenv("PORT", config.PORT))
        config.WORKERS = int(os.getenv("WORKERS", config.WORKERS))
        
        # Configurações do Prometheus
        config.PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", config.PROMETHEUS_PORT))
        config.METRICS_INTERVAL = int(os.getenv("METRICS_INTERVAL", config.METRICS_INTERVAL))
        
        # Configurações de notificação
        if os.getenv("EMAIL_ENABLED", "false").lower() == "true":
            config.NOTIFICACOES["email"].update({
                "enabled": True,
                "smtp_server": os.getenv("SMTP_SERVER", ""),
                "smtp_port": int(os.getenv("SMTP_PORT", "587")),
                "username": os.getenv("SMTP_USERNAME", ""),
                "password": os.getenv("SMTP_PASSWORD", ""),
                "from_addr": os.getenv("EMAIL_FROM", ""),
                "to_addrs": os.getenv("EMAIL_TO", "").split(",")
            })
            
        if os.getenv("SLACK_ENABLED", "false").lower() == "true":
            config.NOTIFICACOES["slack"].update({
                "enabled": True,
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
                "channel": os.getenv("SLACK_CHANNEL", "")
            })
            
        if os.getenv("WEBHOOK_ENABLED", "false").lower() == "true":
            config.NOTIFICACOES["webhook"].update({
                "enabled": True,
                "url": os.getenv("WEBHOOK_URL", ""),
                "headers": {
                    "Authorization": os.getenv("WEBHOOK_AUTH", "")
                }
            })
            
        # Configurações adicionais
        config.MONITORAMENTO_INTERVALO = int(os.getenv("MONITORAMENTO_INTERVALO", config.MONITORAMENTO_INTERVALO))
        config.MONITORAMENTO_TIMEOUT = int(os.getenv("MONITORAMENTO_TIMEOUT", config.MONITORAMENTO_TIMEOUT))
        config.ALERTAS_THRESHOLD = {
            "cpu": float(os.getenv("ALERTAS_CPU_THRESHOLD", str(config.ALERTAS["threshold"]["uso_recursos"]["cpu"]["max"]))),
            "memoria": float(os.getenv("ALERTAS_MEMORIA_THRESHOLD", str(config.ALERTAS["threshold"]["uso_recursos"]["memoria"]["max"]))),
            "disco": float(os.getenv("ALERTAS_DISCO_THRESHOLD", str(config.ALERTAS["threshold"]["uso_recursos"]["disco"]["max"]))),
            "latencia": float(os.getenv("ALERTAS_LATENCIA_THRESHOLD", str(config.ALERTAS["threshold"]["latencia"]["max"]))),
        }
        config.LOG_LEVEL = os.getenv("LOG_LEVEL", config.LOG_LEVEL)
        config.LOG_FORMAT = os.getenv("LOG_FORMAT", config.LOG_FORMAT)
        config.LOG_FILE = os.getenv("LOG_FILE", config.LOG_FILE)
        config.NOTIFICACOES_CANAIS = os.getenv("NOTIFICACOES_CANAIS", ",".join(config.NOTIFICACOES_CANAIS)).split(",")
        config.NOTIFICACOES_EMAIL = {
            "smtp_server": os.getenv("NOTIFICACOES_EMAIL_SMTP", config.NOTIFICACOES["email"]["smtp_server"]),
            "smtp_port": int(os.getenv("NOTIFICACOES_EMAIL_PORT", str(config.NOTIFICACOES["email"]["smtp_port"]))),
            "username": os.getenv("NOTIFICACOES_EMAIL_USER", config.NOTIFICACOES["email"]["username"]),
            "password": os.getenv("NOTIFICACOES_EMAIL_PASS", config.NOTIFICACOES["email"]["password"]),
            "from_addr": os.getenv("NOTIFICACOES_EMAIL_FROM", config.NOTIFICACOES["email"]["from_addr"]),
            "to_addrs": os.getenv("NOTIFICACOES_EMAIL_TO", ",".join(config.NOTIFICACOES["email"]["to_addrs"])).split(","),
        }
        config.NOTIFICACOES_SLACK = {
            "webhook_url": os.getenv("NOTIFICACOES_SLACK_WEBHOOK", config.NOTIFICACOES["slack"]["webhook_url"]),
            "channel": os.getenv("NOTIFICACOES_SLACK_CHANNEL", config.NOTIFICACOES["slack"]["channel"]),
        }
        config.PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", config.PROMETHEUS_URL)
        config.PROMETHEUS_TIMEOUT = int(os.getenv("PROMETHEUS_TIMEOUT", config.PROMETHEUS_TIMEOUT))
        config.DIAGNOSTICO_INTERVALO = int(os.getenv("DIAGNOSTICO_INTERVALO", config.DIAGNOSTICO_INTERVALO))
        config.DIAGNOSTICO_HISTORICO = int(os.getenv("DIAGNOSTICO_HISTORICO", config.DIAGNOSTICO_HISTORICO))
        config.VISUALIZACAO_PERIODO = timedelta(days=int(os.getenv("VISUALIZACAO_PERIODO", str(config.VISUALIZACAO["dashboard"]["default_range"].split("h")[0]))))
        config.VISUALIZACAO_INTERVALO = int(os.getenv("VISUALIZACAO_INTERVALO", config.VISUALIZACAO_INTERVALO))
        config.VISUALIZACAO_ANOMALIA_THRESHOLD = float(os.getenv("VISUALIZACAO_ANOMALIA_THRESHOLD", config.VISUALIZACAO_ANOMALIA_THRESHOLD))
        config.VISUALIZACAO_CORRELACAO_THRESHOLD = float(os.getenv("VISUALIZACAO_CORRELACAO_THRESHOLD", config.VISUALIZACAO_CORRELACAO_THRESHOLD))
        config.VISUALIZACAO_TENDENCIA_THRESHOLD = float(os.getenv("VISUALIZACAO_TENDENCIA_THRESHOLD", config.VISUALIZACAO_TENDENCIA_THRESHOLD))
        config.VISUALIZACAO_DIMENSOES = {
            "performance": {
                "descricao": os.getenv("VISUALIZACAO_DIMENSOES_PERFORMANCE_DESC", config.VISUALIZACAO_DIMENSOES["performance"]["descricao"]),
                "unidade": os.getenv("VISUALIZACAO_DIMENSOES_PERFORMANCE_UN", config.VISUALIZACAO_DIMENSOES["performance"]["unidade"]),
                "limites": {
                    "min": int(os.getenv("VISUALIZACAO_DIMENSOES_PERFORMANCE_MIN", str(config.VISUALIZACAO_DIMENSOES["performance"]["limites"]["min"]))),
                    "max": int(os.getenv("VISUALIZACAO_DIMENSOES_PERFORMANCE_MAX", str(config.VISUALIZACAO_DIMENSOES["performance"]["limites"]["max"])))
                },
            },
            "saude": {
                "descricao": os.getenv("VISUALIZACAO_DIMENSOES_SAUDE_DESC", config.VISUALIZACAO_DIMENSOES["saude"]["descricao"]),
                "unidade": os.getenv("VISUALIZACAO_DIMENSOES_SAUDE_UN", config.VISUALIZACAO_DIMENSOES["saude"]["unidade"]),
                "limites": {
                    "min": int(os.getenv("VISUALIZACAO_DIMENSOES_SAUDE_MIN", str(config.VISUALIZACAO_DIMENSOES["saude"]["limites"]["min"]))),
                    "max": int(os.getenv("VISUALIZACAO_DIMENSOES_SAUDE_MAX", str(config.VISUALIZACAO_DIMENSOES["saude"]["limites"]["max"])))
                },
            },
            "latencia": {
                "descricao": os.getenv("VISUALIZACAO_DIMENSOES_LATENCIA_DESC", config.VISUALIZACAO_DIMENSOES["latencia"]["descricao"]),
                "unidade": os.getenv("VISUALIZACAO_DIMENSOES_LATENCIA_UN", config.VISUALIZACAO_DIMENSOES["latencia"]["unidade"]),
                "limites": {
                    "min": int(os.getenv("VISUALIZACAO_DIMENSOES_LATENCIA_MIN", str(config.VISUALIZACAO_DIMENSOES["latencia"]["limites"]["min"]))),
                    "max": int(os.getenv("VISUALIZACAO_DIMENSOES_LATENCIA_MAX", str(config.VISUALIZACAO_DIMENSOES["latencia"]["limites"]["max"])))
                },
            },
            "erros": {
                "descricao": os.getenv("VISUALIZACAO_DIMENSOES_ERROS_DESC", config.VISUALIZACAO_DIMENSOES["erros"]["descricao"]),
                "unidade": os.getenv("VISUALIZACAO_DIMENSOES_ERROS_UN", config.VISUALIZACAO_DIMENSOES["erros"]["unidade"]),
                "limites": {
                    "min": int(os.getenv("VISUALIZACAO_DIMENSOES_ERROS_MIN", str(config.VISUALIZACAO_DIMENSOES["erros"]["limites"]["min"]))),
                    "max": int(os.getenv("VISUALIZACAO_DIMENSOES_ERROS_MAX", str(config.VISUALIZACAO_DIMENSOES["erros"]["limites"]["max"])))
                },
            },
        }
        
        return config

# Instância global de configuração
CONFIG = Config.from_env() 