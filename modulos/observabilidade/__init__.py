"""Módulo de Observabilidade do Sistema AutoCura"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

try:
    from .src.collectors.multidim_collector import MultiDimensionalCollector
    from .src.storage.hybrid_storage import HybridStorage
    from .src.auditoria.ethical_auditor import EthicalAuditor
except ImportError as e:
    logger.warning(f"Importação parcial do módulo observabilidade: {e}")
    MultiDimensionalCollector = None
    HybridStorage = None
    EthicalAuditor = None

__all__ = ["MultiDimensionalCollector", "HybridStorage", "EthicalAuditor"]