"""
Módulo de memória do sistema de autocura.
Responsável pelo gerenciamento e persistência de dados do sistema.
"""

from .gerenciador_memoria import GerenciadorMemoria
from .gerenciador import GerenciadorMemoria as GerenciadorMemoriaLegacy

__version__ = "0.1.0"
__all__ = ["GerenciadorMemoria", "GerenciadorMemoriaLegacy"] 