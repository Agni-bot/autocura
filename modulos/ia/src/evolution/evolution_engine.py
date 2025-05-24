from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class EvolutionEngine:
    """Engine responsável pela evolução automática do sistema"""
    
    def __init__(self):
        self.evolution_cycles = 0
        self.last_evolution = datetime.now()
        self.evolution_threshold = 0.8  # Limiar para evolução automática
        self.metrics_history = []
        self.evolution_log = []
        logger.info("EvolutionEngine inicializado")
    
    def evaluate_evolution_need(self, metrics: Dict[str, Any]) -> bool:
        """Avalia se o sistema precisa evoluir"""
        self.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        })
        
        # Mantém histórico limitado
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)
        
        # Critérios simples para evolução
        if len(self.metrics_history) < 10:
            return False
        
        # Verifica tendências de performance
        recent_metrics = self.metrics_history[-10:]
        avg_performance = sum(
            m["metrics"].get("performance_score", 0.5) 
            for m in recent_metrics
        ) / len(recent_metrics)
        
        # Verifica se é hora de evoluir
        time_since_evolution = datetime.now() - self.last_evolution
        time_threshold = time_since_evolution > timedelta(hours=24)
        
        return avg_performance > self.evolution_threshold or time_threshold
    
    def evolve_capabilities(self) -> Dict[str, Any]:
        """Executa evolução das capacidades do sistema"""
        evolution_result = {
            "cycle": self.evolution_cycles + 1,
            "timestamp": datetime.now().isoformat(),
            "changes": [],
            "success": True
        }
        
        try:
            # Simula evolução baseada no ciclo atual
            if self.evolution_cycles == 0:
                evolution_result["changes"].append("Enabled quantum readiness")
            elif self.evolution_cycles == 1:
                evolution_result["changes"].append("Enhanced nano interfaces")
            elif self.evolution_cycles == 2:
                evolution_result["changes"].append("Activated bio-compatibility")
            else:
                evolution_result["changes"].append("Optimized existing capabilities")
            
            self.evolution_cycles += 1
            self.last_evolution = datetime.now()
            
            # Registra evolução
            self.evolution_log.append(evolution_result)
            
            logger.info(f"Evolução {self.evolution_cycles} executada com sucesso")
            
        except Exception as e:
            evolution_result["success"] = False
            evolution_result["error"] = str(e)
            logger.error(f"Erro na evolução: {e}")
        
        return evolution_result
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do engine de evolução"""
        return {
            "evolution_level": self.evolution_cycles,
            "last_evolution": self.last_evolution.isoformat(),
            "next_evolution": self._predict_next_evolution(),
            "evolution_threshold": self.evolution_threshold,
            "metrics_collected": len(self.metrics_history),
            "total_evolutions": len(self.evolution_log)
        }
    
    def _predict_next_evolution(self) -> str:
        """Prediz quando será a próxima evolução"""
        if len(self.metrics_history) < 5:
            return "Insufficient data"
        
        # Análise simples baseada em tendências
        if self.evolution_cycles < 3:
            return "Within 24 hours"
        else:
            return "Based on performance metrics"
    
    def get_evolution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna histórico de evoluções"""
        return self.evolution_log[-limit:]
    
    def reset_evolution_cycle(self) -> bool:
        """Reseta o ciclo de evolução (para testes ou manutenção)"""
        try:
            self.evolution_cycles = 0
            self.last_evolution = datetime.now()
            self.metrics_history.clear()
            self.evolution_log.clear()
            logger.info("Ciclo de evolução resetado")
            return True
        except Exception as e:
            logger.error(f"Erro ao resetar evolução: {e}")
            return False 