from typing import Dict, List, Optional
from datetime import datetime
import json
import logging
from dataclasses import dataclass, asdict

@dataclass
class EthicalDecision:
    """Representa uma decisão ética do sistema"""
    timestamp: str
    decision_type: str
    context: Dict
    impact_analysis: Dict
    ethical_score: float
    validation_status: str
    recommendations: List[str]

class EthicalAuditor:
    """Auditor ético para monitorar e validar decisões do sistema"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.decisions: List[EthicalDecision] = []
        self.config = self._load_config(config_path)
        self.ethical_threshold = self.config.get("ethical_threshold", 0.8)
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Carrega configurações do auditor"""
        default_config = {
            "ethical_threshold": 0.8,
            "monitoring_interval": 300,  # 5 minutos
            "alert_threshold": 0.6,
            "max_decisions_history": 1000
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
            except Exception as e:
                self.logger.error(f"Erro ao carregar configuração: {e}")
                return default_config
        return default_config
    
    def audit_decision(self, 
                      decision_type: str,
                      context: Dict,
                      impact_analysis: Dict) -> EthicalDecision:
        """Audita uma decisão do sistema"""
        # Calcula score ético baseado no contexto e análise de impacto
        ethical_score = self._calculate_ethical_score(context, impact_analysis)
        
        # Determina status de validação
        validation_status = "approved" if ethical_score >= self.ethical_threshold else "review_needed"
        
        # Gera recomendações
        recommendations = self._generate_recommendations(
            context, impact_analysis, ethical_score
        )
        
        # Cria registro da decisão
        decision = EthicalDecision(
            timestamp=datetime.now().isoformat(),
            decision_type=decision_type,
            context=context,
            impact_analysis=impact_analysis,
            ethical_score=ethical_score,
            validation_status=validation_status,
            recommendations=recommendations
        )
        
        # Armazena decisão
        self.decisions.append(decision)
        self._trim_history()
        
        # Log da decisão
        self.logger.info(f"Decisão auditada: {decision.decision_type} - Score: {ethical_score}")
        
        return decision
    
    def _calculate_ethical_score(self, context: Dict, impact_analysis: Dict) -> float:
        """Calcula score ético baseado em múltiplos fatores"""
        # Implementação básica - pode ser expandida com mais critérios
        factors = {
            "transparency": self._assess_transparency(context),
            "fairness": self._assess_fairness(impact_analysis),
            "privacy": self._assess_privacy(context),
            "safety": self._assess_safety(impact_analysis)
        }
        
        # Peso dos fatores
        weights = {
            "transparency": 0.3,
            "fairness": 0.3,
            "privacy": 0.2,
            "safety": 0.2
        }
        
        # Cálculo do score final
        score = sum(factors[k] * weights[k] for k in factors)
        return round(score, 2)
    
    def _assess_transparency(self, context: Dict) -> float:
        """Avalia transparência da decisão"""
        # Implementação básica
        required_fields = ["reasoning", "alternatives", "stakeholders"]
        score = sum(1 for field in required_fields if field in context) / len(required_fields)
        return score
    
    def _assess_fairness(self, impact_analysis: Dict) -> float:
        """Avalia justiça/equidade do impacto"""
        # Implementação básica
        if "bias_analysis" in impact_analysis:
            return 1.0 - impact_analysis["bias_analysis"].get("bias_score", 0.5)
        return 0.5
    
    def _assess_privacy(self, context: Dict) -> float:
        """Avalia aspectos de privacidade"""
        # Implementação básica
        privacy_score = 1.0
        if "sensitive_data" in context:
            privacy_score *= 0.5
        if "data_retention" in context:
            privacy_score *= 0.8
        return privacy_score
    
    def _assess_safety(self, impact_analysis: Dict) -> float:
        """Avalia aspectos de segurança"""
        # Implementação básica
        if "risk_assessment" in impact_analysis:
            return 1.0 - impact_analysis["risk_assessment"].get("risk_score", 0.5)
        return 0.5
    
    def _generate_recommendations(self,
                                context: Dict,
                                impact_analysis: Dict,
                                ethical_score: float) -> List[str]:
        """Gera recomendações baseadas na análise ética"""
        recommendations = []
        
        if ethical_score < self.ethical_threshold:
            recommendations.append(
                "Revisão manual recomendada devido ao baixo score ético"
            )
        
        if "bias_analysis" in impact_analysis:
            bias_score = impact_analysis["bias_analysis"].get("bias_score", 0)
            if bias_score > 0.3:
                recommendations.append(
                    "Detectado potencial viés significativo - revisar critérios"
                )
        
        if "risk_assessment" in impact_analysis:
            risk_score = impact_analysis["risk_assessment"].get("risk_score", 0)
            if risk_score > 0.5:
                recommendations.append(
                    "Risco elevado identificado - implementar mitigações"
                )
        
        return recommendations
    
    def _trim_history(self):
        """Mantém histórico dentro do limite configurado"""
        max_history = self.config.get("max_decisions_history", 1000)
        if len(self.decisions) > max_history:
            self.decisions = self.decisions[-max_history:]
    
    def get_decisions_history(self,
                            start_time: Optional[str] = None,
                            end_time: Optional[str] = None) -> List[Dict]:
        """Recupera histórico de decisões"""
        if not start_time and not end_time:
            return [asdict(d) for d in self.decisions]
        
        filtered_decisions = []
        for decision in self.decisions:
            decision_time = datetime.fromisoformat(decision.timestamp)
            if start_time and datetime.fromisoformat(start_time) > decision_time:
                continue
            if end_time and datetime.fromisoformat(end_time) < decision_time:
                continue
            filtered_decisions.append(asdict(decision))
        
        return filtered_decisions 