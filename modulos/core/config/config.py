"""Configurações do módulo core."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import timedelta

@dataclass
class CoreConfig:
    """Configurações do módulo core."""
    
    # Configurações gerais
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Configurações do core
    CORE_HOST: str = os.getenv("CORE_HOST", "localhost")
    CORE_PORT: int = int(os.getenv("CORE_PORT", "8000"))
    CORE_WORKERS: int = int(os.getenv("CORE_WORKERS", "4"))
    
    # Configurações de logging
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/core.log")
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Configurações de eventos
    EVENT_HISTORY_SIZE: int = int(os.getenv("EVENT_HISTORY_SIZE", "1000"))
    EVENT_PROCESSING_TIMEOUT: int = int(os.getenv("EVENT_PROCESSING_TIMEOUT", "30"))
    
    # Configurações de middleware
    MIDDLEWARE_TIMEOUT: int = int(os.getenv("MIDDLEWARE_TIMEOUT", "30"))
    MIDDLEWARE_RETRY_ATTEMPTS: int = int(os.getenv("MIDDLEWARE_RETRY_ATTEMPTS", "3"))
    MIDDLEWARE_RETRY_DELAY: int = int(os.getenv("MIDDLEWARE_RETRY_DELAY", "1"))
    
    # Configurações de segurança
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION: timedelta = timedelta(
        minutes=int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    )
    
    # Configurações de armazenamento
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "memory")  # memory, redis, postgres
    STORAGE_HOST: str = os.getenv("STORAGE_HOST", "localhost")
    STORAGE_PORT: int = int(os.getenv("STORAGE_PORT", "6379"))
    STORAGE_DB: int = int(os.getenv("STORAGE_DB", "0"))
    STORAGE_PASSWORD: Optional[str] = os.getenv("STORAGE_PASSWORD")
    
    # Configurações de métricas
    METRICS_ENABLED: bool = os.getenv("METRICS_ENABLED", "true").lower() == "true"
    METRICS_HOST: str = os.getenv("METRICS_HOST", "localhost")
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))
    
    # Configurações de cache
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutos
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # Configurações de monitoramento
    MONITORING_ENABLED: bool = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    MONITORING_INTERVAL: int = int(os.getenv("MONITORING_INTERVAL", "60"))
    MONITORING_METRICS: list = field(default_factory=lambda: [
        "cpu_usage",
        "memory_usage",
        "disk_usage",
        "network_io",
        "request_latency",
        "error_rate"
    ])
    
    # Configurações de autocura
    AUTOCURE_ENABLED: bool = os.getenv("AUTOCURE_ENABLED", "true").lower() == "true"
    AUTOCURE_INTERVAL: int = int(os.getenv("AUTOCURE_INTERVAL", "300"))
    AUTOCURE_THRESHOLDS: Dict[str, float] = field(default_factory=lambda: {
        "cpu_usage": 80.0,
        "memory_usage": 80.0,
        "disk_usage": 80.0,
        "error_rate": 5.0,
        "request_latency": 1000.0
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a configuração para um dicionário."""
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith("_")
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração."""
        return getattr(self, key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Define um valor de configuração."""
        setattr(self, key, value)
        
    def update(self, config_dict: Dict[str, Any]) -> None:
        """Atualiza configurações a partir de um dicionário."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
    def validate(self) -> bool:
        """Valida as configurações."""
        # Validações básicas
        if not self.CORE_HOST:
            return False
            
        if not 0 < self.CORE_PORT < 65536:
            return False
            
        if self.CORE_WORKERS < 1:
            return False
            
        if not self.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            return False
            
        # Validações de segurança
        if self.ENVIRONMENT == "production" and self.DEBUG:
            return False
            
        if self.ENVIRONMENT == "production" and self.JWT_SECRET == "your-secret-key":
            return False
            
        # Validações de armazenamento
        if self.STORAGE_TYPE not in ["memory", "redis", "postgres"]:
            return False
            
        if self.STORAGE_TYPE != "memory" and not self.STORAGE_HOST:
            return False
            
        # Validações de métricas
        if self.METRICS_ENABLED and not self.METRICS_HOST:
            return False
            
        return True

# Instância global de configuração
config = CoreConfig() 