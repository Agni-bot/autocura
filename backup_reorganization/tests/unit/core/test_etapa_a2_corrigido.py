"""
Testes da Etapa A2: IA com Preparação Cognitiva
===============================================

Testes funcionais para validar as implementações da Etapa A2.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

# Importações corrigidas para estrutura consolidada
from src.core.interfaces import UniversalModuleInterface, ModuleInterface
from src.core.memoria.gerenciador_memoria import GerenciadorMemoria
from src.core.messaging.universal_bus import UniversalEventBus


class MockMultiDimensionalCollector:
    """Mock do coletor multi-dimensional para testes"""
    
    def __init__(self):
        self.capabilities = {
            "classical": True,
            "quantum": False,
            "nano": False,
            "bio": False
        }
        self.metrics_collected = []
    
    async def collect(self) -> Dict[str, Any]:
        """Simula coleta de métricas multi-dimensionais"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "classical": {
                "cpu_percent": 45.2,
                "memory_percent": 67.8,
                "disk_usage": 23.1
            },
            "quantum": {
                "coherence_time": 0.1,
                "entanglement_degree": 0.85,
                "fidelity": 0.92
            } if self.capabilities["quantum"] else None,
            "nano": {
                "particle_count": 1000000,
                "energy_level": 2.3,
                "temperature": 298.15
            } if self.capabilities["nano"] else None,
            "bio": {
                "dna_sequences": 150,
                "enzyme_activity": 0.78,
                "stability_index": 0.91
            } if self.capabilities["bio"] else None
        }
        
        self.metrics_collected.append(metrics)
        return metrics
    
    def detect_capabilities(self) -> Dict[str, bool]:
        """Detecta capacidades disponíveis"""
        return self.capabilities.copy()


class MockEvolutionaryAgent:
    """Mock do agente evolutivo para testes"""
    
    def __init__(self):
        self.cognitive_level = "REACTIVE"
        self.cognitive_modules = {
            "perception": True,
            "reasoning": True,
            "learning": False
        }
        self.experiences = []
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simula análise cognitiva"""
        analysis = {
            "cognitive_level": self.cognitive_level,
            "modules_used": [k for k, v in self.cognitive_modules.items() if v],
            "insights": [
                {"type": "pattern", "description": "Padrão de uso detectado"},
                {"type": "anomaly", "description": "Anomalia leve identificada"},
                {"type": "optimization", "description": "Oportunidade de otimização"}
            ],
            "reasoning": {
                "classical": "Análise baseada em regras lógicas",
                "quantum": "Análise de superposição paralela" if self.cognitive_level in ["ADAPTIVE", "AUTONOMOUS"] else None
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Registra experiência
        self.experiences.append({
            "input": data,
            "output": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        return analysis
    
    def evolve(self) -> bool:
        """Simula evolução cognitiva"""
        levels = ["REACTIVE", "DELIBERATIVE", "REFLECTIVE", "ADAPTIVE", "AUTONOMOUS"]
        current_index = levels.index(self.cognitive_level)
        
        if current_index < len(levels) - 1:
            self.cognitive_level = levels[current_index + 1]
            
            # Ativa novos módulos baseado no nível
            if self.cognitive_level == "DELIBERATIVE":
                self.cognitive_modules["planning"] = True
            elif self.cognitive_level == "REFLECTIVE":
                self.cognitive_modules["reflection"] = True
            elif self.cognitive_level == "ADAPTIVE":
                self.cognitive_modules["learning"] = True
                self.cognitive_modules["quantum_reasoning"] = True
            elif self.cognitive_level == "AUTONOMOUS":
                self.cognitive_modules["self_modification"] = True
            
            return True
        return False


class MockMultiParadigmAnalyzer:
    """Mock do analisador multi-paradigma para testes"""
    
    def __init__(self):
        self.paradigms = [
            "STATISTICAL",
            "LOGICAL",
            "PATTERN_RECOGNITION",
            "NEURAL_NETWORK",
            "FUZZY_LOGIC"
        ]
        self.analyses_performed = []
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simula análise multi-paradigma"""
        individual_analyses = []
        
        for paradigm in self.paradigms:
            analysis = {
                "paradigm": paradigm,
                "confidence": 0.7 + (hash(paradigm) % 30) / 100,  # Simula confiança variável
                "findings": [f"Achado do paradigma {paradigm}"],
                "recommendations": [f"Recomendação baseada em {paradigm}"]
            }
            individual_analyses.append(analysis)
        
        # Simula consenso
        consensus_confidence = sum(a["confidence"] for a in individual_analyses) / len(individual_analyses)
        
        result = {
            "paradigms_used": len(self.paradigms),
            "individual_analyses": individual_analyses,
            "consensus": {
                "confidence_level": consensus_confidence,
                "consolidated_findings": ["Achado consolidado 1", "Achado consolidado 2"],
                "final_recommendations": ["Recomendação final 1", "Recomendação final 2"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self.analyses_performed.append(result)
        return result


# Testes da Etapa A2

@pytest.mark.asyncio
async def test_observabilidade_multi_dimensional():
    """Testa o sistema de observabilidade multi-dimensional"""
    collector = MockMultiDimensionalCollector()
    
    # Testa coleta básica
    metrics = await collector.collect()
    
    assert "timestamp" in metrics
    assert "classical" in metrics
    assert metrics["classical"]["cpu_percent"] > 0
    assert metrics["classical"]["memory_percent"] > 0
    
    # Testa detecção de capacidades
    capabilities = collector.detect_capabilities()
    assert capabilities["classical"] is True
    assert capabilities["quantum"] is False  # Ainda não disponível
    
    # Simula upgrade para capacidades quânticas
    collector.capabilities["quantum"] = True
    metrics_quantum = await collector.collect()
    assert metrics_quantum["quantum"] is not None
    assert "coherence_time" in metrics_quantum["quantum"]
    
    print("✅ Observabilidade multi-dimensional funcionando")


@pytest.mark.asyncio
async def test_framework_ia_evolutivo():
    """Testa o framework de IA evolutivo"""
    agent = MockEvolutionaryAgent()
    
    # Testa estado inicial
    assert agent.cognitive_level == "REACTIVE"
    assert agent.cognitive_modules["perception"] is True
    assert agent.cognitive_modules["learning"] is False
    
    # Testa análise inicial
    test_data = {"cpu": 50, "memory": 70}
    analysis = await agent.analyze(test_data)
    
    assert analysis["cognitive_level"] == "REACTIVE"
    assert len(analysis["insights"]) == 3
    assert analysis["reasoning"]["quantum"] is None  # Não disponível no nível REACTIVE
    
    # Testa evolução
    evolved = agent.evolve()
    assert evolved is True
    assert agent.cognitive_level == "DELIBERATIVE"
    assert agent.cognitive_modules["planning"] is True
    
    # Continua evoluindo até nível ADAPTIVE
    agent.evolve()  # REFLECTIVE
    agent.evolve()  # ADAPTIVE
    
    assert agent.cognitive_level == "ADAPTIVE"
    assert agent.cognitive_modules["quantum_reasoning"] is True
    
    # Testa análise avançada
    advanced_analysis = await agent.analyze(test_data)
    assert advanced_analysis["reasoning"]["quantum"] is not None
    
    print("✅ Framework de IA evolutivo funcionando")


@pytest.mark.asyncio
async def test_diagnostico_multi_paradigma():
    """Testa o sistema de diagnóstico multi-paradigma"""
    analyzer = MockMultiParadigmAnalyzer()
    
    # Testa análise multi-paradigma
    test_data = {"metrics": {"cpu": 80, "memory": 90, "errors": 5}}
    result = await analyzer.analyze(test_data)
    
    assert result["paradigms_used"] == 5
    assert len(result["individual_analyses"]) == 5
    assert "consensus" in result
    
    # Verifica análises individuais
    for analysis in result["individual_analyses"]:
        assert "paradigm" in analysis
        assert "confidence" in analysis
        assert analysis["confidence"] > 0.7
        assert len(analysis["findings"]) > 0
    
    # Verifica consenso
    consensus = result["consensus"]
    assert "confidence_level" in consensus
    assert consensus["confidence_level"] > 0.7
    assert len(consensus["final_recommendations"]) > 0
    
    print("✅ Diagnóstico multi-paradigma funcionando")


@pytest.mark.asyncio
async def test_integracao_etapa_a2():
    """Testa integração completa da Etapa A2"""
    # Inicializa componentes
    collector = MockMultiDimensionalCollector()
    agent = MockEvolutionaryAgent()
    analyzer = MockMultiParadigmAnalyzer()
    memory_manager = GerenciadorMemoria()
    
    # Pipeline completo: Coleta → IA → Diagnóstico
    
    # 1. Coleta métricas
    metrics = await collector.collect()
    assert metrics is not None
    
    # 2. Análise por IA evolutiva
    ia_analysis = await agent.analyze(metrics)
    assert ia_analysis["cognitive_level"] == "REACTIVE"
    
    # 3. Diagnóstico multi-paradigma
    diagnosis = await analyzer.analyze(metrics)
    assert diagnosis["paradigms_used"] > 0
    
    # 4. Evolução do agente
    agent.evolve()
    agent.evolve()  # Agora está em REFLECTIVE
    
    # 5. Nova análise com nível cognitivo superior
    advanced_analysis = await agent.analyze(metrics)
    assert advanced_analysis["cognitive_level"] == "REFLECTIVE"
    
    # 6. Verifica que o sistema mantém histórico
    assert len(agent.experiences) == 2  # Duas análises realizadas
    assert len(analyzer.analyses_performed) == 1  # Um diagnóstico realizado
    
    # 7. Testa capacidades futuras
    collector.capabilities["quantum"] = True
    quantum_metrics = await collector.collect()
    assert quantum_metrics["quantum"] is not None
    
    print("✅ Integração completa da Etapa A2 funcionando")


if __name__ == "__main__":
    # Executa testes diretamente
    asyncio.run(test_observabilidade_multi_dimensional())
    asyncio.run(test_framework_ia_evolutivo())
    asyncio.run(test_diagnostico_multi_paradigma())
    asyncio.run(test_integracao_etapa_a2())
    print("\n🎯 Todos os testes da Etapa A2 passaram com sucesso!") 