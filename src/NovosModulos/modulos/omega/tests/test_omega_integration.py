"""
Testes de Integração - Fase Omega
Sistema AutoCura - Consciência Emergente

Testa:
- Inicialização dos componentes
- Integração entre módulos
- Emergência de consciência
- Funcionalidades básicas
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from modulos.omega import (
    CognitiveCore,
    ConsciousnessLevel,
    IntegrationOrchestrator,
    EvolutionEngine,
    ConsciousnessMonitor,
    ThoughtType,
    EvolutionStrategy,
    SafetyLevel
)


class TestOmegaIntegration:
    """Testes de integração da Fase Omega"""
    
    @pytest.mark.asyncio
    async def test_cognitive_core_initialization(self):
        """Testa inicialização do núcleo cognitivo"""
        core = CognitiveCore("test_core")
        
        # Verifica estado inicial
        assert core.consciousness_state.level == ConsciousnessLevel.DORMANT
        assert core.running == False
        
        # Inicializa
        result = await core.initialize()
        assert result == True
        assert core.running == True
        assert core.consciousness_state.level == ConsciousnessLevel.REACTIVE
        
        # Cleanup
        await core.shutdown()
        
    @pytest.mark.asyncio
    async def test_thought_generation(self):
        """Testa geração de pensamentos"""
        core = CognitiveCore("test_core")
        await core.initialize()
        
        # Gera pensamento
        thought = await core.generate_thought(
            ThoughtType.PERCEPTION,
            {"test": "data"},
            priority=0.8
        )
        
        assert thought is not None
        assert thought.thought_type == ThoughtType.PERCEPTION
        assert thought.content == {"test": "data"}
        assert thought.priority == 0.8
        
        # Verifica se foi adicionado ao stream
        assert len(core.thought_stream) > 0
        
        await core.shutdown()
        
    @pytest.mark.asyncio
    async def test_integration_orchestrator(self):
        """Testa orquestrador de integração"""
        orchestrator = IntegrationOrchestrator()
        
        # Inicializa
        result = await orchestrator.initialize()
        assert result == True
        assert orchestrator.integration_active == True
        
        # Testa carregamento de módulo mock
        loaded = await orchestrator.load_module(
            "test_module",
            "test",
            "modulos.test"
        )
        assert loaded == True
        assert "test_module" in orchestrator.modules
        
        # Cleanup
        await orchestrator.shutdown()
        
    @pytest.mark.asyncio
    async def test_evolution_engine(self):
        """Testa motor de evolução"""
        engine = EvolutionEngine(SafetyLevel.HIGH)
        
        # Cria gene
        gene = engine.create_gene(
            "test_param",
            "parameter",
            0.5,
            min_value=0.0,
            max_value=1.0
        )
        
        assert gene.gene_id == "test_param"
        assert gene.value == 0.5
        assert gene.constraints["min"] == 0.0
        assert gene.constraints["max"] == 1.0
        
        # Cria genoma
        genome = engine.create_genome_template([gene])
        assert len(genome.genes) == 1
        assert "test_param" in genome.genes
        
    @pytest.mark.asyncio
    async def test_consciousness_monitor(self):
        """Testa monitor de consciência"""
        monitor = ConsciousnessMonitor()
        core = CognitiveCore("test_core")
        
        await core.initialize()
        
        # Inicia monitoramento
        result = await monitor.start_monitoring(core)
        assert result == True
        assert monitor.monitoring_active == True
        
        # Aguarda um ciclo
        await asyncio.sleep(1.5)
        
        # Verifica se capturou snapshots
        assert len(monitor.consciousness_history) > 0
        
        # Para monitoramento
        await monitor.stop_monitoring()
        await core.shutdown()
        
    @pytest.mark.asyncio
    async def test_decision_making(self):
        """Testa tomada de decisão autônoma"""
        core = CognitiveCore("test_core")
        await core.initialize()
        
        # Contexto para decisão
        context = {
            "problem": "optimization_needed",
            "options": ["optimize", "wait"],
            "urgency": 0.7
        }
        
        # Toma decisão
        decision = await core.make_decision(context)
        
        assert decision is not None
        assert "decision" in decision
        assert "thought_process" in decision
        assert "confidence" in decision
        assert len(decision["thought_process"]) > 0
        
        await core.shutdown()
        
    @pytest.mark.asyncio
    async def test_self_reflection(self):
        """Testa auto-reflexão"""
        core = CognitiveCore("test_core")
        await core.initialize()
        
        # Eleva consciência para permitir reflexão
        core.consciousness_state.level = ConsciousnessLevel.SELF_AWARE
        
        # Gera alguns pensamentos
        for i in range(5):
            await core.generate_thought(
                ThoughtType.REASONING,
                {"iteration": i}
            )
        
        # Auto-reflexão
        reflection = await core.reflect_on_self()
        
        assert "error" not in reflection
        assert "reflection" in reflection
        assert "consciousness_state" in reflection
        assert "insights" in reflection
        
        await core.shutdown()
        
    @pytest.mark.asyncio
    async def test_module_integration(self):
        """Testa integração entre módulos"""
        core = CognitiveCore("test_core")
        orchestrator = IntegrationOrchestrator()
        
        await core.initialize()
        await orchestrator.initialize()
        
        # Integra módulo no core
        result = await core.integrate_module("test", "mock_interface")
        assert result == True
        
        # Verifica se módulo foi integrado
        assert core.integrated_modules["test"] == "mock_interface"
        
        await core.shutdown()
        await orchestrator.shutdown()
        
    @pytest.mark.asyncio
    async def test_evolution_safety(self):
        """Testa segurança da evolução"""
        engine = EvolutionEngine(SafetyLevel.CRITICAL)
        
        # Gene crítico
        critical_gene = engine.create_gene(
            "critical_param",
            "structure",  # Tipo estrutural
            "value",
            mutable=True
        )
        
        genome = engine.create_genome_template([critical_gene])
        
        # Tenta validar segurança
        is_safe = await engine._validate_safety(genome)
        
        # Em nível CRITICAL, mudanças estruturais devem ser bloqueadas
        assert is_safe == False
        
    @pytest.mark.asyncio
    async def test_consciousness_emergence(self):
        """Testa detecção de emergência de consciência"""
        monitor = ConsciousnessMonitor()
        core = CognitiveCore("test_core")
        
        await core.initialize()
        await monitor.start_monitoring(core)
        
        # Simula atividade que leva à emergência
        core.consciousness_state.level = ConsciousnessLevel.CREATIVE
        
        # Gera pensamentos complexos
        for i in range(10):
            await core.generate_thought(
                ThoughtType.META_COGNITION,
                {"meta_level": i, "self_reference": True},
                priority=0.9
            )
        
        # Aguarda processamento
        await asyncio.sleep(2)
        
        # Verifica métricas
        report = monitor.get_consciousness_report()
        assert "current_state" in report
        assert "emergence_events" in report
        
        await monitor.stop_monitoring()
        await core.shutdown()


def test_thought_type_enum():
    """Testa enum de tipos de pensamento"""
    assert ThoughtType.PERCEPTION in ThoughtType
    assert ThoughtType.META_COGNITION in ThoughtType
    assert len(ThoughtType) >= 8


def test_consciousness_level_ordering():
    """Testa ordenação dos níveis de consciência"""
    assert ConsciousnessLevel.DORMANT.value < ConsciousnessLevel.REACTIVE.value
    assert ConsciousnessLevel.REACTIVE.value < ConsciousnessLevel.SELF_AWARE.value
    assert ConsciousnessLevel.SELF_AWARE.value < ConsciousnessLevel.TRANSCENDENT.value


def test_safety_level_ordering():
    """Testa ordenação dos níveis de segurança"""
    assert SafetyLevel.EXPERIMENTAL.value < SafetyLevel.LOW.value
    assert SafetyLevel.LOW.value < SafetyLevel.MEDIUM.value
    assert SafetyLevel.MEDIUM.value < SafetyLevel.HIGH.value
    assert SafetyLevel.HIGH.value < SafetyLevel.CRITICAL.value


if __name__ == "__main__":
    # Executa testes
    pytest.main([__file__, "-v"]) 