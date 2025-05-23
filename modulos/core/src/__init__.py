"""Módulo Core do Sistema de Autocura."""

from .interfaces import (
    ModuleInterface,
    EventInterface,
    StorageInterface,
    LoggingInterface,
    MetricsInterface,
    SecurityInterface
)

from .events import Event, EventBus
from .middleware import Message, Middleware
from .logging import StructuredLogger, JsonFormatter

__version__ = "0.1.0"
__author__ = "Sistema Autocura"
__description__ = "Módulo Core do Sistema de Autocura"

__all__ = [
    'ModuleInterface',
    'EventInterface',
    'StorageInterface',
    'LoggingInterface',
    'MetricsInterface',
    'SecurityInterface',
    'Event',
    'EventBus',
    'Message',
    'Middleware',
    'StructuredLogger',
    'JsonFormatter'
] 