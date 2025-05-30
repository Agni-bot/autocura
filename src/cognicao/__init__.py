"""
Módulo de Cognição - Fase Beta
=============================

Sistema de cognição emergente do AutoCura com capacidades de:
- Coordenação multi-agente com consenso
- Detecção e reforço de padrões emergentes
- Auto-modificação controlada e segura
- Sandbox de evolução isolado

Componentes principais:
- SwarmCoordinator: Coordenação de múltiplos agentes
- BehaviorEmergence: Motor de emergência comportamental
- SafeCodeGenerator: Geração segura de código
- EvolutionSandbox: Ambiente de testes isolado
"""

from .swarm.swarm_coordinator import (
    SwarmCoordinator,
    ConsensusType,
    AgentRole,
    AgentDecision,
    SwarmDecision
)

from .emergence.behavior_emergence import (
    BehaviorEmergence,
    PatternType,
    EmergenceLevel,
    EmergentPattern,
    BehaviorEvent
)

from .self_modify.safe_code_generator import (
    SafeCodeGenerator,
    CodeType,
    SecurityLevel,
    ValidationResult,
    CodeGenerationRequest,
    GeneratedCode,
    SecurityViolation
)

from .sandbox.evolution_sandbox import (
    EvolutionSandbox,
    SandboxType,
    TestStatus,
    IsolationLevel,
    SandboxConfig,
    EvolutionTest,
    SandboxMetrics
)

__version__ = "1.0.0-beta"
__author__ = "Sistema AutoCura"

# Exportar classes principais
__all__ = [
    # Swarm Intelligence
    "SwarmCoordinator",
    "ConsensusType", 
    "AgentRole",
    "AgentDecision",
    "SwarmDecision",
    
    # Behavior Emergence
    "BehaviorEmergence",
    "PatternType",
    "EmergenceLevel", 
    "EmergentPattern",
    "BehaviorEvent",
    
    # Safe Code Generation
    "SafeCodeGenerator",
    "CodeType",
    "SecurityLevel",
    "ValidationResult",
    "CodeGenerationRequest",
    "GeneratedCode", 
    "SecurityViolation",
    
    # Evolution Sandbox
    "EvolutionSandbox",
    "SandboxType",
    "TestStatus",
    "IsolationLevel",
    "SandboxConfig",
    "EvolutionTest",
    "SandboxMetrics"
]

# Configurações padrão do módulo
DEFAULT_CONFIG = {
    "swarm": {
        "consensus_mechanism": ConsensusType.BYZANTINE_FAULT_TOLERANT,
        "min_agents": 4,
        "max_agents": 20
    },
    "emergence": {
        "observation_window": 1000,
        "pattern_threshold": 0.7,
        "min_confidence": 0.6
    },
    "code_generation": {
        "max_code_size": 10000,
        "max_complexity": 10,
        "security_level": SecurityLevel.SAFE
    },
    "sandbox": {
        "default_type": SandboxType.PROCESS,
        "default_isolation": IsolationLevel.HIGH,
        "max_sandboxes": 10
    }
}

def create_cognitive_system(config=None):
    """
    Cria um sistema cognitivo completo com todos os componentes
    
    Args:
        config: Configuração customizada (opcional)
        
    Returns:
        dict: Sistema cognitivo com todos os componentes
    """
    if config is None:
        config = DEFAULT_CONFIG
    
    # Inicializar componentes
    swarm_coordinator = SwarmCoordinator(
        consensus_mechanism=config["swarm"]["consensus_mechanism"]
    )
    
    behavior_emergence = BehaviorEmergence(
        observation_window=config["emergence"]["observation_window"],
        pattern_threshold=config["emergence"]["pattern_threshold"]
    )
    
    code_generator = SafeCodeGenerator()
    
    evolution_sandbox = EvolutionSandbox()
    
    return {
        "swarm_coordinator": swarm_coordinator,
        "behavior_emergence": behavior_emergence,
        "code_generator": code_generator,
        "evolution_sandbox": evolution_sandbox,
        "config": config
    }

def get_system_status():
    """
    Retorna status geral do sistema de cognição
    
    Returns:
        dict: Status do sistema
    """
    return {
        "module": "cognition",
        "version": __version__,
        "phase": "BETA",
        "status": "ACTIVE",
        "components": {
            "swarm_intelligence": "OPERATIONAL",
            "behavior_emergence": "OPERATIONAL", 
            "safe_code_generation": "OPERATIONAL",
            "evolution_sandbox": "OPERATIONAL"
        },
        "capabilities": [
            "Multi-agent coordination",
            "Byzantine fault tolerance",
            "Pattern emergence detection",
            "Behavior reinforcement",
            "Safe code generation",
            "Isolated evolution testing"
        ]
    } 