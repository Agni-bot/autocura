"""
Configuração da API de IA Avançada
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class IAConfig:
    """Configurações da API de IA."""
    
    # Configurações básicas
    API_KEY: str = os.getenv("AI_API_KEY", "")
    API_ENDPOINT: str = os.getenv("AI_API_ENDPOINT", "https://api.suaapi.com/v1")
    API_VERSION: str = os.getenv("AI_API_VERSION", "v1")
    API_ORGANIZATION: Optional[str] = os.getenv("AI_API_ORGANIZATION")
    
    # Rate Limiting
    RATE_LIMIT_CALLS: int = int(os.getenv("AI_API_RATE_LIMIT_CALLS", "100"))
    RATE_LIMIT_INTERVAL: int = int(os.getenv("AI_API_RATE_LIMIT_INTERVAL", "60"))
    
    # Timeout e Retry
    TIMEOUT: int = int(os.getenv("AI_API_TIMEOUT", "30"))
    MAX_RETRIES: int = int(os.getenv("AI_API_MAX_RETRIES", "3"))
    RETRY_INTERVAL: int = int(os.getenv("AI_API_RETRY_INTERVAL", "5"))
    
    # Cache
    CACHE_ENABLED: bool = os.getenv("AI_API_CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("AI_API_CACHE_TTL", "3600"))
    
    # Fallback
    FALLBACK_ENABLED: bool = os.getenv("AI_API_FALLBACK_ENABLED", "true").lower() == "true"
    FALLBACK_MODEL: str = os.getenv("AI_API_FALLBACK_MODEL", "local")
    
    # Logging
    LOG_LEVEL: str = os.getenv("AI_API_LOG_LEVEL", "INFO")
    LOG_REQUESTS: bool = os.getenv("AI_API_LOG_REQUESTS", "true").lower() == "true"
    
    # Métricas
    METRICS_ENABLED: bool = os.getenv("AI_API_METRICS_ENABLED", "true").lower() == "true"
    METRICS_PREFIX: str = os.getenv("AI_API_METRICS_PREFIX", "ia_avancada")
    
    # Validação Ética
    ETHICAL_VALIDATION_ENABLED: bool = os.getenv("AI_API_ETHICAL_VALIDATION_ENABLED", "true").lower() == "true"
    ETHICAL_MIN_CONFIDENCE: float = float(os.getenv("AI_API_ETHICAL_MIN_CONFIDENCE", "0.95"))
    ETHICAL_REVIEW_REQUIRED: bool = os.getenv("AI_API_ETHICAL_REVIEW_REQUIRED", "true").lower() == "true"
    
    # Contexto
    CONTEXT_WINDOW: int = int(os.getenv("AI_API_CONTEXT_WINDOW", "4096"))
    MAX_TOKENS: int = int(os.getenv("AI_API_MAX_TOKENS", "1024"))
    TEMPERATURE: float = float(os.getenv("AI_API_TEMPERATURE", "0.7"))
    
    # Modelos
    PRIMARY_MODEL: str = os.getenv("AI_API_PRIMARY_MODEL", "gpt-4")
    FALLBACK_MODEL: str = os.getenv("AI_API_FALLBACK_MODEL", "gpt-3.5-turbo")
    ETHICAL_MODEL: str = os.getenv("AI_API_ETHICAL_MODEL", "ethical-gpt")
    
    # Segurança
    SSL_VERIFY: bool = os.getenv("AI_API_SSL_VERIFY", "true").lower() == "true"
    ENCRYPT_PAYLOAD: bool = os.getenv("AI_API_ENCRYPT_PAYLOAD", "true").lower() == "true"

    def validate(self) -> bool:
        """Valida as configurações necessárias."""
        if not self.API_KEY:
            raise ValueError("AI_API_KEY não configurada")
        if not self.API_ENDPOINT:
            raise ValueError("AI_API_ENDPOINT não configurado")
        return True

# Instância global das configurações
ia_config = IAConfig() 