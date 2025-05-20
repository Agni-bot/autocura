"""
Módulo core do sistema de autocura.
"""

from .base import BaseComponent, BaseService, BaseModel, BaseValidator
from .config import config, ConfiguracaoBase

__all__ = [
    "BaseComponent",
    "BaseService", 
    "BaseModel",
    "BaseValidator",
    "config",
    "ConfiguracaoBase"
]

__version__ = "0.1.0" 