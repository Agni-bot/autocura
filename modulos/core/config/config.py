"""Configurações do módulo core."""

import os
from typing import Dict, Any

class Config:
    """Configurações do módulo core."""
    
    # Configurações gerais
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Configurações do core
    CORE_HOST = os.getenv("CORE_HOST", "localhost")
    CORE_PORT = int(os.getenv("CORE_PORT", "8000"))
    CORE_WORKERS = int(os.getenv("CORE_WORKERS", "4"))
    
    # Configurações de logging
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/app.log")
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "100"))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Configurações de eventos
    EVENT_HISTORY_SIZE = int(os.getenv("EVENT_HISTORY_SIZE", "1000"))
    EVENT_PROCESSING_TIMEOUT = float(os.getenv("EVENT_PROCESSING_TIMEOUT", "5.0"))
    
    # Configurações de middleware
    MIDDLEWARE_TIMEOUT = float(os.getenv("MIDDLEWARE_TIMEOUT", "10.0"))
    MIDDLEWARE_RETRY_ATTEMPTS = int(os.getenv("MIDDLEWARE_RETRY_ATTEMPTS", "3"))
    MIDDLEWARE_RETRY_DELAY = float(os.getenv("MIDDLEWARE_RETRY_DELAY", "1.0"))
    
    # Configurações de segurança
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", "3600"))
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Converte as configurações para dicionário."""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Obtém uma configuração específica."""
        return getattr(cls, key, default)
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """Define uma configuração específica."""
        setattr(cls, key, value)
    
    @classmethod
    def update(cls, config_dict: Dict[str, Any]) -> None:
        """Atualiza múltiplas configurações."""
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
    
    @classmethod
    def validate(cls) -> bool:
        """Valida as configurações."""
        try:
            # Validações básicas
            assert cls.CORE_PORT > 0
            assert cls.CORE_WORKERS > 0
            assert cls.LOG_MAX_SIZE > 0
            assert cls.LOG_BACKUP_COUNT > 0
            assert cls.EVENT_HISTORY_SIZE > 0
            assert cls.EVENT_PROCESSING_TIMEOUT > 0
            assert cls.MIDDLEWARE_TIMEOUT > 0
            assert cls.MIDDLEWARE_RETRY_ATTEMPTS > 0
            assert cls.MIDDLEWARE_RETRY_DELAY > 0
            assert cls.JWT_EXPIRATION > 0
            
            return True
        except AssertionError:
            return False 