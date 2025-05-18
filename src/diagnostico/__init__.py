"""
Módulo de diagnóstico do Sistema de Autocura.

Este módulo é responsável por analisar métricas do sistema e gerar diagnósticos
baseados em anomalias detectadas.
"""

from .core import AnalisadorMetricas, GeradorDiagnosticos, obter_metricas_do_monitoramento
from .diagnostico import Diagnostico, TipoDiagnostico, SeveridadeDiagnostico 

__version__ = '1.0.0'
__author__ = 'Sistema de Autocura'
__all__ = ['AnalisadorMetricas', 'GeradorDiagnosticos', 'obter_metricas_do_monitoramento'] 