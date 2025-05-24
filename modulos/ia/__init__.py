"""Módulo de IA do Sistema AutoCura"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

try:
    from .src.agents.adaptive_agent import AdaptiveAgent
    from .src.evolution.evolution_engine import EvolutionEngine
except ImportError as e:
    logger.warning(f"Importação parcial do módulo IA: {e}")
    AdaptiveAgent = None
    EvolutionEngine = None

__all__ = ["AdaptiveAgent", "EvolutionEngine"]