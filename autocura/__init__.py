"""
Sistema AutoCura - Pacote Principal
==================================

Sistema de autocura cognitiva com arquitetura evolutiva modular.
"""

__version__ = "1.0.0-alpha"
__author__ = "Sistema AutoCura"

from .core import *
from .services import *

__all__ = ["core", "services", "monitoring", "security", "evolution", "utils", "api"]
