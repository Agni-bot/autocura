"""
Módulo de monitoramento do sistema de autocura.
Responsável pela coleta e análise de métricas do sistema.
"""

from .metricas import MetricasSistema, MonitoramentoMultidimensional

__all__ = ['MetricasSistema', 'MonitoramentoMultidimensional']
__version__ = "0.1.0" 