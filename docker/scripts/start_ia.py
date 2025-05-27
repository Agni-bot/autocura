#!/usr/bin/env python3
"""
Script de inicialização do módulo IA Evolutiva - Fase Alpha
"""

import asyncio
import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any

# Adiciona src ao path
sys.path.insert(0, '/app/src')

try:
    from core.memoria.gerenciador_memoria import GerenciadorMemoria
    from core.memoria.registrador_contexto import RegistradorContexto
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('autocura-ia')

class IAEvolutivaService:
    """Serviço de IA Evolutiva para Fase Alpha"""
    
    def __init__(self):
        self.memory_manager = GerenciadorMemoria()
        self.context_recorder = RegistradorContexto()
        self.cognitive_level = os.getenv('NIVEL_COGNITIVO_INICIAL', 'REACTIVE')
        self.api_url = os.getenv('API_URL', 'http://autocura-api:8000')
        self.running = False
        
        # Módulos cognitivos
        self.cognitive_modules = {
            "perception": True,
            "reasoning": True,
            "learning": False,
            "planning": False,
            "reflection": False,
            "quantum_reasoning": False,
            "self_modification": False
        }
        
        self.experiences = []
        
    async def initialize(self):
        """Inicializa o serviço de IA"""
        logger.info("Inicializando IA Evolutiva - Fase Alpha")
        
        # Registra inicialização
        self.context_recorder.registrar_evento(
            "ia_evolutiva_iniciada",
            f"IA Evolutiva iniciada com nível cognitivo: {self.cognitive_level}"
        )
        
        self.running = True
        logger.info(f"IA Evolutiva inicializada - Nível: {self.cognitive_level}")
        
    async def evolve_cognitive_level(self):
        """Evolui o nível cognitivo"""
        levels = ["REACTIVE", "DELIBERATIVE", "REFLECTIVE", "ADAPTIVE", "AUTONOMOUS"]
        current_index = levels.index(self.cognitive_level)
        
        if current_index < len(levels) - 1:
            old_level = self.cognitive_level
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
            
            # Registra evolução
            self.context_recorder.registrar_evento(
                "evolucao_cognitiva",
                f"IA evoluiu de {old_level} para {self.cognitive_level}"
            )
            
            logger.info(f"IA evoluiu: {old_level} → {self.cognitive_level}")
            return True
        return False
    
    async def analyze_system_state(self) -> Dict[str, Any]:
        """Analisa o estado atual do sistema"""
        try:
            # Simula análise cognitiva
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "cognitive_level": self.cognitive_level,
                "modules_active": [k for k, v in self.cognitive_modules.items() if v],
                "insights": [
                    {"type": "pattern", "description": "Padrão de comportamento detectado"},
                    {"type": "optimization", "description": "Oportunidade de otimização identificada"},
                    {"type": "anomaly", "description": "Anomalia leve no sistema"}
                ],
                "reasoning": {
                    "classical": "Análise baseada em regras lógicas",
                    "quantum": "Análise de superposição paralela" if self.cognitive_modules["quantum_reasoning"] else None
                },
                "recommendations": [
                    "Continuar monitoramento",
                    "Considerar evolução cognitiva",
                    "Otimizar coleta de métricas"
                ]
            }
            
            # Registra experiência
            self.experiences.append({
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis,
                "cognitive_level": self.cognitive_level
            })
            
            # Mantém apenas últimas 100 experiências
            if len(self.experiences) > 100:
                self.experiences = self.experiences[-100:]
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return {"error": str(e)}
    
    async def run_cognitive_cycle(self):
        """Executa ciclo cognitivo principal"""
        while self.running:
            try:
                # Análise do sistema
                analysis = await self.analyze_system_state()
                
                # Considera evolução (a cada 10 ciclos)
                if len(self.experiences) % 10 == 0:
                    evolved = await self.evolve_cognitive_level()
                    if evolved:
                        logger.info("IA evoluiu para próximo nível cognitivo")
                
                # Registra atividade
                self.context_recorder.registrar_evento(
                    "ciclo_cognitivo",
                    f"Ciclo executado - Nível: {self.cognitive_level}, Insights: {len(analysis.get('insights', []))}"
                )
                
                # Aguarda próximo ciclo (60 segundos)
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Erro no ciclo cognitivo: {e}")
                await asyncio.sleep(30)
    
    async def shutdown(self):
        """Finaliza o serviço"""
        logger.info("Finalizando IA Evolutiva")
        self.running = False
        
        self.context_recorder.registrar_evento(
            "ia_evolutiva_finalizada",
            f"IA Evolutiva finalizada - Nível final: {self.cognitive_level}"
        )

async def main():
    """Função principal"""
    ia_service = IAEvolutivaService()
    
    try:
        await ia_service.initialize()
        await ia_service.run_cognitive_cycle()
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
    finally:
        await ia_service.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 