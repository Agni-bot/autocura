"""
Módulo Core - Componentes Fundamentais
=====================================

Contém as interfaces, gerenciadores e funcionalidades core do sistema.
"""

from .memoria.gerenciador_memoria import GerenciadorMemoria
from .memoria.registrador_contexto import RegistradorContexto
from .messaging.universal_bus import UniversalEventBus
from .serialization.adaptive_serializer import AdaptiveSerializer

__all__ = [
    "GerenciadorMemoria",
    "RegistradorContexto", 
    "UniversalEventBus",
    "AdaptiveSerializer"
]
