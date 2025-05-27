"""
Módulo de Autocura - Sistema de evolução contínua e adaptativa
"""

from .core import AutocuraEngine
from .memory import MemoryManager
from .feedback import FeedbackSystem
from .monitoring import AutocuraMonitor

__version__ = "0.1.0"
__all__ = ["AutocuraEngine", "MemoryManager", "FeedbackSystem", "AutocuraMonitor"] 