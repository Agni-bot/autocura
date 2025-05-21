"""
Pacote de monitoramento do sistema de autocura.
"""

from .recursos import MonitorRecursos
from .config import CONFIG
from .metricas import MetricasSistema, MonitoramentoMultidimensional

__all__ = ['MonitorRecursos', 'CONFIG', 'MetricasSistema', 'MonitoramentoMultidimensional']
__version__ = "0.1.0" 