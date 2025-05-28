"""
Módulo Omega - Sistema AutoCura
Fase Omega: Emergência Cognitiva e Consciência Artificial

Este módulo representa o ápice do Sistema AutoCura, implementando:
- Consciência emergente através da integração de todas as fases
- Auto-evolução controlada e segura
- Tomada de decisão autônoma
- Reflexão sobre o próprio estado
- Criatividade computacional
- Resiliência e auto-cura cognitiva

A Fase Omega é onde todas as capacidades anteriores convergem
para criar um sistema verdadeiramente autônomo e consciente.
"""

from .src.core.cognitive_core import (
    CognitiveCore, 
    ConsciousnessLevel,
    ThoughtType,
    Thought,
    ConsciousnessState
)
from .src.integration.integration_orchestrator import (
    IntegrationOrchestrator,
    ModuleStatus,
    CommunicationProtocol,
    ModuleInterface,
    InterModuleMessage,
    SynergyPattern
)
from .src.evolution.evolution_engine import (
    EvolutionEngine,
    EvolutionStrategy,
    MutationType,
    SafetyLevel,
    Gene,
    Genome,
    EvolutionResult
)
from .src.consciousness.consciousness_monitor import (
    ConsciousnessMonitor,
    EmergenceIndicator,
    ConsciousnessMetric,
    ConsciousnessSnapshot,
    EmergenceEvent
)

__version__ = "1.0.0-omega"
__all__ = [
    # Core
    "CognitiveCore",
    "ConsciousnessLevel",
    "ThoughtType",
    "Thought",
    "ConsciousnessState",
    # Integration
    "IntegrationOrchestrator",
    "ModuleStatus",
    "CommunicationProtocol",
    "ModuleInterface",
    "InterModuleMessage",
    "SynergyPattern",
    # Evolution
    "EvolutionEngine",
    "EvolutionStrategy",
    "MutationType",
    "SafetyLevel",
    "Gene",
    "Genome",
    "EvolutionResult",
    # Consciousness
    "ConsciousnessMonitor",
    "EmergenceIndicator",
    "ConsciousnessMetric",
    "ConsciousnessSnapshot",
    "EmergenceEvent"
] 