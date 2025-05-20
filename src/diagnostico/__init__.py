"""
Módulo de diagnóstico do sistema de autocura.

Este módulo é responsável por analisar métricas do sistema e gerar diagnósticos
baseados em anomalias detectadas.
"""

from .diagnostico import Diagnostico, RedeNeuralDiagnostico
from .diagnostico_sistema import DiagnosticoSistema
from .core import DiagnosticoCore, AnalisadorMetricas, GeradorDiagnosticos, obter_metricas_do_monitoramento
from .diagnostico import TipoDiagnostico, SeveridadeDiagnostico 

__version__ = '0.1.0'
__author__ = 'Sistema de Autocura'
__all__ = [
    "Diagnostico",
    "RedeNeuralDiagnostico",
    "DiagnosticoSistema",
    "DiagnosticoCore",
    "AnalisadorMetricas",
    "GeradorDiagnosticos",
    "obter_metricas_do_monitoramento"
] 