"""
Modelos Core do Sistema AutoCura
===============================

Exporta os modelos fundamentais usados em todo o sistema.
"""

from .metricas import (
    Metrica,
    MetricasSistema, 
    MetricasAplicacao,
    TipoMetrica,
    criar_metrica,
    validar_metricas_sistema,
    METRICAS_DEFAULT
)

__all__ = [
    "Metrica",
    "MetricasSistema",
    "MetricasAplicacao", 
    "TipoMetrica",
    "criar_metrica",
    "validar_metricas_sistema",
    "METRICAS_DEFAULT"
] 