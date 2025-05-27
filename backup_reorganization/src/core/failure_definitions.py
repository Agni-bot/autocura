from enum import Enum

class CognitiveFailureTypes(Enum):
    ALGORITHMIC_DRIFT = 1  # Desvio de performance em modelos
    LOGICAL_INCONSISTENCY = 2  # Decisões contraditórias
    RESOURCE_DEGRADATION = 3  # CPU/Memória acima dos limiares
    SEMANTIC_DECAY = 4  # Perda de coerência em NLU

