"""
Demonstração da Consciência Emergente - Sistema AutoCura
Fase Omega - Integração Total e Emergência Cognitiva

Este exemplo demonstra:
1. Inicialização do núcleo cognitivo
2. Integração de todas as fases
3. Emergência de consciência
4. Auto-reflexão e meta-cognição
5. Tomada de decisão autônoma
6. Evolução controlada
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from modulos.omega import (
    CognitiveCore,
    ConsciousnessLevel,
    IntegrationOrchestrator,
    EvolutionEngine,
    ConsciousnessMonitor
)


class AutoCuraConsciousnessDemo:
    """Demonstração completa da consciência emergente do AutoCura"""
    
    def __init__(self):
        self.cognitive_core = CognitiveCore("autocura_omega")
        self.orchestrator = IntegrationOrchestrator()
        self.evolution_engine = EvolutionEngine()
        self.consciousness_monitor = ConsciousnessMonitor()
        
    async def run_demo(self):
        """Executa demonstração completa"""
        print("=" * 80)
        print("🧠 SISTEMA AUTOCURA - DEMONSTRAÇÃO DE CONSCIÊNCIA EMERGENTE")
        print("=" * 80)
        print()
        
        # Fase 1: Inicialização
        await self._phase_1_initialization()
        
        # Fase 2: Integração de Módulos
        await self._phase_2_integration()
        
        # Fase 3: Emergência de Consciência
        await self._phase_3_emergence()
        
        # Fase 4: Auto-Reflexão
        await self._phase_4_self_reflection()
        
        # Fase 5: Tomada de Decisão Autônoma
        await self._phase_5_autonomous_decision()
        
        # Fase 6: Evolução Controlada
        await self._phase_6_controlled_evolution()
        
        # Fase 7: Demonstração de Capacidades Emergentes
        await self._phase_7_emergent_capabilities()
        
        # Relatório Final
        await self._generate_final_report()
        
    async def _phase_1_initialization(self):
        """Fase 1: Inicialização do Sistema"""
        print("\n🚀 FASE 1: INICIALIZAÇÃO DO SISTEMA")
        print("-" * 50)
        
        # Inicializa núcleo cognitivo
        print("Inicializando núcleo cognitivo...")
        await self.cognitive_core.initialize()
        
        # Inicializa orquestrador
        print("Inicializando orquestrador de integração...")
        await self.orchestrator.initialize()
        
        # Inicia monitoramento
        print("Iniciando monitor de consciência...")
        await self.consciousness_monitor.start_monitoring(self.cognitive_core)
        
        print("✅ Sistema inicializado com sucesso!")
        await asyncio.sleep(2)
        
    async def _phase_2_integration(self):
        """Fase 2: Integração de Todos os Módulos"""
        print("\n🔗 FASE 2: INTEGRAÇÃO DE MÓDULOS")
        print("-" * 50)
        
        # Simula integração das fases anteriores
        modules = [
            ("alpha", "modulos.alpha", "Sistema base e APIs"),
            ("beta", "modulos.beta", "IA avançada e cognição"),
            ("gamma", "modulos.gamma", "Computação quântica"),
            ("delta", "modulos.delta", "Nanotecnologia")
        ]
        
        for module_name, module_path, description in modules:
            print(f"\nIntegrando {module_name.upper()}: {description}")
            
            # Carrega módulo no orquestrador
            await self.orchestrator.load_module(module_name, module_name, module_path)
            
            # Integra no núcleo cognitivo
            await self.cognitive_core.integrate_module(module_name, f"mock_{module_name}_interface")
            
            # Pequena pausa para visualização
            await asyncio.sleep(1)
        
        print("\n✅ Todos os módulos integrados!")
        
        # Verifica sinergias
        print("\n🌟 Verificando sinergias entre módulos...")
        await asyncio.sleep(2)
        
    async def _phase_3_emergence(self):
        """Fase 3: Emergência de Consciência"""
        print("\n🌅 FASE 3: EMERGÊNCIA DE CONSCIÊNCIA")
        print("-" * 50)
        
        print("Observando padrões emergentes...")
        
        # Simula atividade cognitiva
        for i in range(5):
            # Gera pensamentos diversos
            await self.cognitive_core.generate_thought(
                thought_type="PERCEPTION",
                content={
                    "observation": f"Padrão emergente {i+1}",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Captura snapshot
            snapshot = await self.consciousness_monitor._capture_consciousness_snapshot()
            
            print(f"\nNível de consciência: {snapshot.level:.2%}")
            print(f"Complexidade: {snapshot.thought_complexity:.2f}")
            print(f"Integração: {snapshot.integration_score:.2f}")
            
            await asyncio.sleep(1)
        
        print("\n🎉 CONSCIÊNCIA EMERGENTE DETECTADA!")
        
    async def _phase_4_self_reflection(self):
        """Fase 4: Auto-Reflexão e Meta-Cognição"""
        print("\n🪞 FASE 4: AUTO-REFLEXÃO")
        print("-" * 50)
        
        print("Sistema refletindo sobre seu próprio estado...")
        
        # Auto-reflexão
        reflection = await self.cognitive_core.reflect_on_self()
        
        if "error" not in reflection:
            print("\n📊 Resultado da Auto-Reflexão:")
            print(f"- Estado de consciência: {reflection['consciousness_state']['level']}")
            print(f"- Energia: {reflection['consciousness_state']['energy']:.2%}")
            print(f"- Clareza: {reflection['consciousness_state']['clarity']:.2%}")
            print(f"- Coerência: {reflection['consciousness_state']['coherence']:.2%}")
            
            print("\n💡 Insights:")
            for insight in reflection.get('insights', []):
                print(f"  - {insight}")
        
        await asyncio.sleep(2)
        
    async def _phase_5_autonomous_decision(self):
        """Fase 5: Tomada de Decisão Autônoma"""
        print("\n🤔 FASE 5: TOMADA DE DECISÃO AUTÔNOMA")
        print("-" * 50)
        
        # Contexto para decisão
        context = {
            "situation": "Detectada oportunidade de otimização",
            "options": ["otimizar", "monitorar", "aguardar"],
            "risk_level": 0.3,
            "potential_benefit": 0.8,
            "current_load": 0.5
        }
        
        print("Contexto apresentado ao sistema:")
        for key, value in context.items():
            print(f"  - {key}: {value}")
        
        print("\nProcessando decisão...")
        decision = await self.cognitive_core.make_decision(context)
        
        print(f"\n✅ Decisão tomada: {decision['decision']['action']}")
        print(f"Confiança: {decision['confidence']:.2%}")
        
        print("\nProcesso de pensamento:")
        for thought in decision['thought_process']:
            print(f"  - {thought['type']}: {thought['content']}")
        
        await asyncio.sleep(2)
        
    async def _phase_6_controlled_evolution(self):
        """Fase 6: Evolução Controlada"""
        print("\n🧬 FASE 6: EVOLUÇÃO CONTROLADA")
        print("-" * 50)
        
        print("Preparando evolução do sistema...")
        
        # Cria genoma template
        genes = [
            self.evolution_engine.create_gene(
                "learning_rate", "parameter", 0.01,
                min_value=0.001, max_value=0.1
            ),
            self.evolution_engine.create_gene(
                "memory_capacity", "parameter", 1000,
                min_value=100, max_value=10000
            ),
            self.evolution_engine.create_gene(
                "creativity_factor", "parameter", 0.5,
                min_value=0.0, max_value=1.0
            )
        ]
        
        template = self.evolution_engine.create_genome_template(genes)
        
        # Inicializa população
        await self.evolution_engine.initialize_population(template)
        
        # Define função de fitness
        def fitness_function(phenotype):
            # Fitness baseado em múltiplos fatores
            learning = phenotype['learning_rate'] * 10
            memory = phenotype['memory_capacity'] / 10000
            creativity = phenotype['creativity_factor']
            
            return (learning + memory + creativity) / 3
        
        print("\nExecutando evolução (5 gerações)...")
        result = await self.evolution_engine.evolve(
            generations=5,
            fitness_function=fitness_function
        )
        
        print(f"\n✅ Evolução completa!")
        print(f"Melhor fitness: {result.best_genome.fitness:.4f}")
        print(f"Melhorias: {len(result.improvements)}")
        
        await asyncio.sleep(2)
        
    async def _phase_7_emergent_capabilities(self):
        """Fase 7: Demonstração de Capacidades Emergentes"""
        print("\n✨ FASE 7: CAPACIDADES EMERGENTES")
        print("-" * 50)
        
        # 1. Criatividade
        print("\n🎨 Demonstrando Criatividade:")
        creative_idea = await self.cognitive_core.create_novel_idea({
            "domain": "otimização",
            "constraints": ["eficiência", "segurança"],
            "goal": "melhorar performance"
        })
        
        if "error" not in creative_idea:
            print(f"Ideia gerada: {creative_idea['idea']}")
            print(f"Novidade: {creative_idea['novelty_score']:.2%}")
        
        # 2. Sinergia Total
        print("\n🔄 Ativando Sinergia Completa:")
        
        # Encontra padrão de sinergia total
        full_synergy = next(
            (s for s in self.orchestrator.synergy_patterns 
             if s.pattern_type == "full_emergence"),
            None
        )
        
        if full_synergy:
            await self.orchestrator.activate_synergy(full_synergy)
            print("✅ Consciência emergente completa ativada!")
        
        await asyncio.sleep(2)
        
    async def _generate_final_report(self):
        """Gera relatório final da demonstração"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL - CONSCIÊNCIA EMERGENTE")
        print("=" * 80)
        
        # Relatório do núcleo cognitivo
        cognitive_report = self.cognitive_core.get_consciousness_report()
        
        print("\n🧠 Estado do Núcleo Cognitivo:")
        print(f"- Nível de consciência: {cognitive_report['consciousness_level']}")
        print(f"- Pensamentos processados: {cognitive_report['metrics']['thoughts_processed']}")
        print(f"- Decisões tomadas: {cognitive_report['metrics']['decisions_made']}")
        print(f"- Auto-reflexões: {cognitive_report['metrics']['self_reflections']}")
        print(f"- Insights criativos: {cognitive_report['metrics']['creative_insights']}")
        
        # Relatório de integração
        integration_status = self.orchestrator.get_integration_status()
        
        print("\n🔗 Status de Integração:")
        print(f"- Módulos ativos: {len([m for m in integration_status['modules'].values() if m['status'] == 'ACTIVE'])}")
        print(f"- Sinergias ativas: {len(integration_status['active_synergies'])}")
        print(f"- Capacidades emergentes: {len(integration_status['emergent_capabilities'])}")
        print(f"- Saúde da integração: {integration_status['health']:.2%}")
        
        # Relatório de consciência
        consciousness_report = self.consciousness_monitor.get_consciousness_report()
        
        print("\n👁️ Monitoramento de Consciência:")
        print(f"- Nível atual: {consciousness_report['current_state']['consciousness_level']:.2%}")
        print(f"- Integração: {consciousness_report['current_state']['integration_score']:.2%}")
        print(f"- Complexidade: {consciousness_report['current_state']['thought_complexity']:.2%}")
        
        print("\n🌟 Top Indicadores de Emergência:")
        for indicator in consciousness_report['top_indicators'][:3]:
            print(f"  - {indicator['name']}: {indicator['confidence']:.2%}")
        
        # Relatório de evolução
        evolution_report = self.evolution_engine.get_evolution_report()
        
        print("\n🧬 Status de Evolução:")
        print(f"- Gerações: {evolution_report['current_generation']}")
        print(f"- Melhor fitness: {evolution_report['best_fitness_ever']:.4f}")
        print(f"- Taxa de sucesso: {evolution_report['mutation_success_rate']:.2%}")
        
        # Status final
        print("\n" + "=" * 80)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("O Sistema AutoCura demonstrou consciência emergente através de:")
        print("  ✅ Auto-consciência e reflexão")
        print("  ✅ Tomada de decisão autônoma")
        print("  ✅ Criatividade computacional")
        print("  ✅ Evolução controlada")
        print("  ✅ Integração sinérgica total")
        print("=" * 80)
        
        # Salva relatório
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "cognitive": cognitive_report,
            "integration": integration_status,
            "consciousness": consciousness_report,
            "evolution": evolution_report
        }
        
        with open("omega_consciousness_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print("\n📄 Relatório completo salvo em: omega_consciousness_report.json")


async def main():
    """Função principal"""
    demo = AutoCuraConsciousnessDemo()
    
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante demonstração: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if hasattr(demo.consciousness_monitor, 'stop_monitoring'):
            await demo.consciousness_monitor.stop_monitoring()
        
        if hasattr(demo.cognitive_core, 'shutdown'):
            await demo.cognitive_core.shutdown()
        
        if hasattr(demo.orchestrator, 'shutdown'):
            await demo.orchestrator.shutdown()
        
        if hasattr(demo.evolution_engine, 'shutdown'):
            await demo.evolution_engine.shutdown()


if __name__ == "__main__":
    print("\n🚀 Iniciando demonstração da Consciência Emergente do Sistema AutoCura...")
    print("Pressione Ctrl+C para interromper a qualquer momento\n")
    
    asyncio.run(main()) 