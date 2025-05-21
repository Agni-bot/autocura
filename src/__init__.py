"""
Pacote principal do sistema de autocura.
Este módulo contém os componentes principais do sistema.
"""

from .monitoramento import MonitoramentoMultidimensional, MetricasSistema
from .diagnostico import Diagnostico, RedeNeuralDiagnostico, DiagnosticoSistema
from .gerador import GeradorAcoes

__version__ = "0.1.0"
__author__ = "Equipe de Desenvolvimento"

__all__ = [
    'MonitoramentoMultidimensional',
    'MetricasSistema',
    'Diagnostico',
    'RedeNeuralDiagnostico',
    'DiagnosticoSistema',
    'GeradorAcoes'
] 