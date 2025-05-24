"""Analisador Híbrido para Diagnósticos do Sistema AutoCura"""

from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HybridAnalyzer:
    """Analisador híbrido que usa múltiplos paradigmas de diagnóstico"""
    
    def __init__(self):
        self.paradigms = ["classical", "statistical", "neural", "quantum-ready"]
        self.analysis_history = []
        self.diagnostic_rules = self._load_diagnostic_rules()
        logger.info("HybridAnalyzer inicializado com paradigmas: %s", self.paradigms)
    
    def _load_diagnostic_rules(self) -> Dict[str, Any]:
        """Carrega regras de diagnóstico"""
        return {
            "performance_thresholds": {
                "cpu_warning": 80.0,
                "cpu_critical": 95.0,
                "memory_warning": 85.0,
                "memory_critical": 95.0,
                "disk_warning": 90.0,
                "disk_critical": 98.0
            },
            "patterns": {
                "degradation": ["high_cpu_sustained", "memory_leak", "disk_full"],
                "anomalies": ["unexpected_spikes", "irregular_patterns", "system_errors"]
            }
        }
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa análise usando múltiplos paradigmas"""
        try:
            analysis_start = datetime.now()
            
            # Executa análises por paradigma
            classical_result = self._classical_analysis(data)
            statistical_result = self._statistical_analysis(data)
            neural_result = self._neural_analysis(data)
            
            # Consolida resultados
            consolidated_diagnostics = self._consolidate_results(
                classical_result, statistical_result, neural_result
            )
            
            analysis_time = (datetime.now() - analysis_start).total_seconds()
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "analysis_metadata": {
                    "paradigms_used": self.paradigms,
                    "data_size": len(str(data)),
                    "analysis_time": analysis_time,
                    "confidence_score": self._calculate_confidence(consolidated_diagnostics)
                },
                "consolidated_diagnostics": consolidated_diagnostics,
                "recommendations": self._generate_recommendations(consolidated_diagnostics)
            }
            
            self.analysis_history.append(result)
            
            # Mantém histórico limitado
            if len(self.analysis_history) > 100:
                self.analysis_history.pop(0)
            
            logger.info("Análise concluída em %.2f segundos", analysis_time)
            return result
            
        except Exception as e:
            logger.error("Erro na análise: %s", e)
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "analysis_metadata": {"failed": True},
                "consolidated_diagnostics": []
            }
    
    def _classical_analysis(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Análise clássica baseada em regras"""
        diagnostics = []
        
        # Análise de métricas do sistema
        if "system" in data:
            system_data = data["system"]
            
            # CPU Analysis
            cpu_percent = system_data.get("cpu_percent", 0)
            if cpu_percent > self.diagnostic_rules["performance_thresholds"]["cpu_critical"]:
                diagnostics.append({
                    "issue": "critical_cpu_usage",
                    "severity": "CRITICAL",
                    "confidence": 0.95,
                    "value": cpu_percent,
                    "threshold": self.diagnostic_rules["performance_thresholds"]["cpu_critical"]
                })
            elif cpu_percent > self.diagnostic_rules["performance_thresholds"]["cpu_warning"]:
                diagnostics.append({
                    "issue": "high_cpu_usage",
                    "severity": "WARNING",
                    "confidence": 0.85,
                    "value": cpu_percent,
                    "threshold": self.diagnostic_rules["performance_thresholds"]["cpu_warning"]
                })
            
            # Memory Analysis
            memory_percent = system_data.get("memory_percent", 0)
            if memory_percent > self.diagnostic_rules["performance_thresholds"]["memory_critical"]:
                diagnostics.append({
                    "issue": "critical_memory_usage",
                    "severity": "CRITICAL",
                    "confidence": 0.95,
                    "value": memory_percent,
                    "threshold": self.diagnostic_rules["performance_thresholds"]["memory_critical"]
                })
            elif memory_percent > self.diagnostic_rules["performance_thresholds"]["memory_warning"]:
                diagnostics.append({
                    "issue": "high_memory_usage",
                    "severity": "WARNING",
                    "confidence": 0.85,
                    "value": memory_percent,
                    "threshold": self.diagnostic_rules["performance_thresholds"]["memory_warning"]
                })
        
        return diagnostics
    
    def _statistical_analysis(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Análise estatística de tendências"""
        diagnostics = []
        
        # Análise de tendências baseada no histórico
        if len(self.analysis_history) >= 5:
            recent_analyses = self.analysis_history[-5:]
            
            # Simula detecção de tendência de degradação
            if "system" in data:
                diagnostics.append({
                    "issue": "performance_trend_analysis",
                    "severity": "INFO",
                    "confidence": 0.7,
                    "trend": "stable",  # Simulado
                    "prediction": "no_immediate_issues"
                })
        
        return diagnostics
    
    def _neural_analysis(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Análise usando redes neurais (simulada)"""
        diagnostics = []
        
        # Simulação de análise neural
        diagnostics.append({
            "issue": "neural_pattern_analysis",
            "severity": "INFO",
            "confidence": 0.6,
            "pattern_type": "normal_operation",
            "anomaly_score": 0.1  # Baixo = normal
        })
        
        return diagnostics
    
    def _consolidate_results(self, *analysis_results) -> List[Dict[str, Any]]:
        """Consolida resultados de múltiplas análises"""
        consolidated = []
        
        for result_set in analysis_results:
            consolidated.extend(result_set)
        
        # Remove duplicatas e ordena por severidade
        severity_order = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3}
        consolidated.sort(key=lambda x: severity_order.get(x.get("severity", "INFO"), 3))
        
        return consolidated
    
    def _calculate_confidence(self, diagnostics: List[Dict[str, Any]]) -> float:
        """Calcula confiança geral da análise"""
        if not diagnostics:
            return 1.0
        
        confidences = [d.get("confidence", 0.5) for d in diagnostics]
        return sum(confidences) / len(confidences)
    
    def _generate_recommendations(self, diagnostics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas nos diagnósticos"""
        recommendations = []
        
        for diag in diagnostics:
            issue = diag.get("issue", "")
            severity = diag.get("severity", "INFO")
            
            if "cpu" in issue.lower():
                recommendations.append({
                    "action": "optimize_cpu_usage",
                    "priority": 1 if severity == "CRITICAL" else 2,
                    "description": "Otimizar uso de CPU ou adicionar recursos"
                })
            
            elif "memory" in issue.lower():
                recommendations.append({
                    "action": "optimize_memory_usage", 
                    "priority": 1 if severity == "CRITICAL" else 2,
                    "description": "Limpar cache ou adicionar memória"
                })
            
            elif "disk" in issue.lower():
                recommendations.append({
                    "action": "cleanup_disk_space",
                    "priority": 1 if severity == "CRITICAL" else 3,
                    "description": "Limpar arquivos temporários ou expandir armazenamento"
                })
        
        return recommendations
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna histórico de análises"""
        return self.analysis_history[-limit:]
    
    def reset_history(self) -> bool:
        """Limpa histórico de análises"""
        try:
            self.analysis_history.clear()
            logger.info("Histórico de análises limpo")
            return True
        except Exception as e:
            logger.error("Erro ao limpar histórico: %s", e)
            return False 