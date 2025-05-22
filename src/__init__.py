"""
Pacote principal do sistema de autocura.
"""

# Removida a importação que causava erro
# from .monitoramento import MonitoramentoMultidimensional, MetricasSistema

from .services.diagnostico.rede_neural import Diagnostico, DiagnosticoSistema, RedeNeuralDiagnostico
from .services.gerador.gerador_acoes import GeradorAcoes

__version__ = "0.1.0"
__author__ = "Equipe de Desenvolvimento"

__all__ = [
    'Diagnostico',
    'RedeNeuralDiagnostico',
    'DiagnosticoSistema',
    'GeradorAcoes'
] 