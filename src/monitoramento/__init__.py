"""
Módulo de monitoramento do sistema AutoCura.

Este módulo é responsável por:
- Coletar métricas do sistema em tempo real
- Analisar tendências e anomalias
- Gerar alertas e notificações
- Visualizar dados em tempo real
- Integrar com Prometheus
- Diagnosticar problemas
- Visualização 4D do sistema
"""

__version__ = '1.0.0'

from .monitoramento import Monitoramento
from .metricas import MetricasSistema
from .monitor_recursos import MonitorRecursos
from .notificador import Notificador
from .diagnostico import SistemaDiagnostico, Problema, StatusDiagnostico, Severidade
from .visualizacao_4d import Visualizacao4D, Dimensao4D
from .config import CONFIG

__all__ = [
    'Monitoramento',
    'MetricasSistema',
    'MonitorRecursos',
    'Notificador',
    'SistemaDiagnostico',
    'Problema',
    'StatusDiagnostico',
    'Severidade',
    'Visualizacao4D',
    'Dimensao4D',
    'CONFIG'
] 