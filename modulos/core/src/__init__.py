"""Módulo core do sistema de autocura."""

from .interfaces import (
    ModuleInterface, EventInterface, StorageInterface,
    LoggingInterface, MetricsInterface, SecurityInterface,
    HealthStatus, Message, Response
)

from .base import (
    BaseModule, BaseEventSystem, BaseStorage,
    BaseLogger, BaseMetrics, BaseSecurity
)

from .config.config import config
from .logging import logger
from .metrics import metrics
from .events import events
from .storage import storage
from .security import security

__version__ = "0.1.0"
__author__ = "Sistema de Autocura"
__description__ = "Módulo core do sistema de autocura"

# Exporta interfaces
__all__ = [
    "ModuleInterface",
    "EventInterface",
    "StorageInterface",
    "LoggingInterface",
    "MetricsInterface",
    "SecurityInterface",
    "HealthStatus",
    "Message",
    "Response",
    "BaseModule",
    "BaseEventSystem",
    "BaseStorage",
    "BaseLogger",
    "BaseMetrics",
    "BaseSecurity",
    "config",
    "logger",
    "metrics",
    "events",
    "storage",
    "security"
] 