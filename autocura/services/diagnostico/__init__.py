"""
Módulo Services - Diagnóstico
============================

Serviços de diagnóstico e análise do sistema.
"""

try:
    from .diagnostico import DiagnosticoSistema
except ImportError:
    DiagnosticoSistema = None

try:
    from .real_suggestions import RealSuggestionsDetector
except ImportError:
    RealSuggestionsDetector = None

try:
    from .analisador_multiparadigma import AnalisadorMultiParadigma
except ImportError:
    AnalisadorMultiParadigma = None

__all__ = ["DiagnosticoSistema", "RealSuggestionsDetector", "AnalisadorMultiParadigma"]
