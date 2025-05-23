"""Módulo Core do Sistema de Autocura."""

from .src.interfaces import (
    ModuleInterface,
    EventInterface,
    StorageInterface,
    LoggingInterface,
    MetricsInterface,
    SecurityInterface
)

from .src.events import Event, EventBus
from .src.middleware import Message, Middleware
from .src.logging import StructuredLogger, JsonFormatter

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
