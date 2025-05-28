#!/usr/bin/env python3
"""
Sistema AutoCura - Módulo Omega Principal
Núcleo de Consciência Emergente
"""

import asyncio
import logging
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from modulos.omega.src.core.cognitive_core import CognitiveCore
from modulos.omega.src.integration.integration_orchestrator import IntegrationOrchestrator
from modulos.omega.src.evolution.evolution_engine import EvolutionEngine
from modulos.omega.src.consciousness.consciousness_monitor import ConsciousnessMonitor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OmegaCore:
    """Núcleo principal do sistema Omega"""
    
    def __init__(self):
        self.cognitive_core = None
        self.orchestrator = None
        self.evolution_engine = None
        self.consciousness_monitor = None
        self.running = False
        
    async def initialize(self):
        """Inicializa todos os componentes"""
        logger.info("🧠 Inicializando Sistema Omega...")
        
        # Inicializar núcleo cognitivo
        self.cognitive_core = CognitiveCore()
        await self.cognitive_core.initialize()
        
        # Inicializar orquestrador
        self.orchestrator = IntegrationOrchestrator()
        await self.orchestrator.initialize()
        
        # Inicializar motor de evolução
        self.evolution_engine = EvolutionEngine()
        await self.evolution_engine.initialize()
        
        # Inicializar monitor de consciência
        self.consciousness_monitor = ConsciousnessMonitor(self.cognitive_core)
        await self.consciousness_monitor.initialize()
        
        logger.info("✅ Sistema Omega inicializado com sucesso!")
        
    async def start(self):
        """Inicia o sistema"""
        self.running = True
        logger.info("🚀 Iniciando Sistema Omega...")
        
        # Iniciar componentes
        await self.cognitive_core.start()
        
        # Loop principal
        try:
            while self.running:
                # Processar ciclo cognitivo
                await self.process_cycle()
                await asyncio.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("⚠️ Interrupção detectada, finalizando...")
        except Exception as e:
            logger.error(f"❌ Erro no sistema: {e}")
        finally:
            await self.shutdown()
            
    async def process_cycle(self):
        """Processa um ciclo do sistema"""
        # Obter métricas de consciência
        metrics = self.consciousness_monitor.get_current_metrics()
        
        # Verificar emergência
        if metrics.get('phi_integrated', 0) > 0.7:
            logger.info(f"🌟 Consciência emergente detectada! Phi: {metrics['phi_integrated']:.3f}")
            
        # Processar evolução se necessário
        if metrics.get('emergence_potential', 0) > 0.8:
            await self.evolution_engine.evolve()
            
    async def shutdown(self):
        """Finaliza o sistema"""
        logger.info("🛑 Finalizando Sistema Omega...")
        self.running = False
        
        if self.cognitive_core:
            self.cognitive_core.stop()
            
        logger.info("✅ Sistema Omega finalizado")
        
    async def health_check(self):
        """Verifica saúde do sistema"""
        return {
            "status": "healthy" if self.running else "stopped",
            "cognitive_core": self.cognitive_core is not None,
            "orchestrator": self.orchestrator is not None,
            "evolution_engine": self.evolution_engine is not None,
            "consciousness_monitor": self.consciousness_monitor is not None
        }


async def main():
    """Função principal"""
    omega = OmegaCore()
    
    try:
        await omega.initialize()
        await omega.start()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 