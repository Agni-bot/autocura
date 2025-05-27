"""
Sistema AutoCura - Módulo Principal
==================================

Sistema de autocura cognitiva com arquitetura modular e evolutiva.
"""

__version__ = "1.0.0-alpha"
__author__ = "Sistema Multiagente AutoCura"
__description__ = "Sistema de autocura cognitiva com IA evolutiva"

# Importações básicas apenas quando necessário
# Evita importações automáticas que podem causar problemas de dependências

# Removida a importação que causava erro
# from .monitoramento import MonitoramentoMultidimensional, MetricasSistema

from .services.diagnostico.rede_neural import Diagnostico, DiagnosticoSistema, RedeNeuralDiagnostico
from .services.gerador.gerador_acoes import GeradorAcoes

__all__ = [
    'Diagnostico',
    'RedeNeuralDiagnostico',
    'DiagnosticoSistema',
    'GeradorAcoes'
] 