"""
Módulo guardião do sistema de autocura.
"""

from .guardiao_cognitivo import (
    GuardiaoCognitivo,
    DiagnosticoInfo,
    PlanoAcaoInfo,
    CONFIG_GUARDIAN
)
from .protocolos_emergencia import ProtocoloEmergencia
from .fluxo_emergencia import FluxoEmergencia

__all__ = [
    "GuardiaoCognitivo",
    "DiagnosticoInfo",
    "PlanoAcaoInfo",
    "CONFIG_GUARDIAN",
    "ProtocoloEmergencia",
    "FluxoEmergencia"
]

__version__ = "0.1.0" 