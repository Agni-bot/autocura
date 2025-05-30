"""
Módulo de configuração base do sistema de autocura.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from redis import Redis, ConnectionPool

def _get_default_endpoints() -> Dict[str, str]:
    """Retorna os endpoints padrão do sistema."""
    return {
        "monitoramento": os.getenv("ENDPOINT_MONITORAMENTO", "http://localhost:8000/monitoramento"),
        "diagnostico": os.getenv("ENDPOINT_DIAGNOSTICO", "http://localhost:8000/diagnostico"),
        "acoes": os.getenv("ENDPOINT_ACOES", "http://localhost:8000/acoes"),
        "guardiao": os.getenv("ENDPOINT_GUARDIAO", "http://localhost:8000/guardiao")
    }

# Configuração do Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'autocura-redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Configuração do connection pool
redis_pool = ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True
)

# Cliente Redis
redis_client = Redis(connection_pool=redis_pool)

@dataclass
class ConfiguracaoBase:
    """Configuração base do sistema."""
    
    # Configurações gerais
    AMBIENTE: str = os.getenv("AMBIENTE", "desenvolvimento")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Configurações de memória
    MEMORIA_MAXIMA: int = int(os.getenv("MEMORIA_MAXIMA", "1000"))
    MEMORIA_TTL: int = int(os.getenv("MEMORIA_TTL", "3600"))
    
    # Configurações de monitoramento
    INTERVALO_MONITORAMENTO: int = int(os.getenv("INTERVALO_MONITORAMENTO", "60"))
    THRESHOLD_ALERTA: float = float(os.getenv("THRESHOLD_ALERTA", "0.8"))
    
    # Configurações de diagnóstico
    MODELO_DIAGNOSTICO: str = os.getenv("MODELO_DIAGNOSTICO", "padrao")
    CONFIANCA_MINIMA: float = float(os.getenv("CONFIANCA_MINIMA", "0.7"))
    
    # Configurações de ações
    ACAO_AUTOMATICA: bool = os.getenv("ACAO_AUTOMATICA", "False").lower() == "true"
    MAX_TENTATIVAS: int = int(os.getenv("MAX_TENTATIVAS", "3"))
    
    # Configurações de segurança
    CHAVE_API: Optional[str] = os.getenv("CHAVE_API")
    TOKEN_JWT: Optional[str] = os.getenv("TOKEN_JWT")
    
    # Configurações de integração
    ENDPOINTS: Dict[str, str] = field(default_factory=_get_default_endpoints)
    
    # Configurações de Kubernetes
    KUBERNETES_NAMESPACE: str = os.getenv("KUBERNETES_NAMESPACE", "default")
    KUBERNETES_CONFIG: Optional[str] = os.getenv("KUBERNETES_CONFIG")
    
    # Configurações de notificação
    NOTIFICACOES_ATIVAS: bool = os.getenv("NOTIFICACOES_ATIVAS", "True").lower() == "true"
    CANAIS_NOTIFICACAO: List[str] = field(default_factory=lambda: os.getenv("CANAIS_NOTIFICACAO", "telegram,slack").split(","))
    
    def __post_init__(self):
        """Validação pós-inicialização."""
        if self.AMBIENTE not in ["desenvolvimento", "homologacao", "producao"]:
            raise ValueError("Ambiente inválido")
            
        if self.LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError("Nível de log inválido")
            
        if self.MEMORIA_MAXIMA <= 0:
            raise ValueError("Memória máxima deve ser positiva")
            
        if self.INTERVALO_MONITORAMENTO <= 0:
            raise ValueError("Intervalo de monitoramento deve ser positivo")
            
        if not 0 <= self.THRESHOLD_ALERTA <= 1:
            raise ValueError("Threshold de alerta deve estar entre 0 e 1")
            
        if not 0 <= self.CONFIANCA_MINIMA <= 1:
            raise ValueError("Confiança mínima deve estar entre 0 e 1")
            
        if self.MAX_TENTATIVAS <= 0:
            raise ValueError("Número máximo de tentativas deve ser positivo")

# Instância global de configuração
config = ConfiguracaoBase()

__all__ = ["config", "ConfiguracaoBase"] 