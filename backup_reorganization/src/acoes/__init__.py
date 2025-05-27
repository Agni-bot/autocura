"""
Módulo de ações do sistema de autocura.
Responsável pela geração e execução de ações corretivas.
"""

from .gerador_acoes import (
    GeradorAcoes,
    Acao,
    PlanoAcao,
    TipoAcao,
    PrioridadeAcao
)

__all__ = [
    'GeradorAcoes',
    'Acao',
    'PlanoAcao',
    'TipoAcao',
    'PrioridadeAcao'
]
__version__ = "0.1.0" 