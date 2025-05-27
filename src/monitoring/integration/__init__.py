"""
Módulo de Integração do Dashboard de Monitoramento
=================================================

Este módulo fornece integração entre o dashboard HTML simples
e o módulo de monitoramento avançado do AutoCura.
"""

from .dashboard_bridge import DashboardBridge, dashboard_bridge, router

__all__ = ['DashboardBridge', 'dashboard_bridge', 'router'] 