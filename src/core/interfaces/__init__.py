"""Interfaces do sistema de autocura."""

from .universal_interface import (
    UniversalModuleInterface,
    TechnologyReadiness,
    ModuleCapabilities,
    QuantumReadyInterface,
    NanoInterface,
    BioInterface
)

from .base_interfaces import (
    ModuleInterface,
    EventInterface,
    StorageInterface,
    LoggingInterface,
    MetricsInterface,
    SecurityInterface,
    HealthStatus,
    Message,
    Response
)

__all__ = [
    # Universal interfaces
    'UniversalModuleInterface',
    'TechnologyReadiness',
    'ModuleCapabilities',
    'QuantumReadyInterface',
    'NanoInterface',
    'BioInterface',
    # Base interfaces
    'ModuleInterface',
    'EventInterface',
    'StorageInterface',
    'LoggingInterface',
    'MetricsInterface',
    'SecurityInterface',
    'HealthStatus',
    'Message',
    'Response'
] 