"""
Sistema de feedback para evolução contínua
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class FeedbackSystem:
    """Sistema de feedback para evolução contínua"""
    
    def __init__(self, feedback_path: Optional[Path] = None):
        self.feedback_path = feedback_path or Path("feedback_history.json")
        self.feedback_history = self._load_feedback_history()
        logger.info("FeedbackSystem inicializado com sucesso")
    
    def _load_feedback_history(self) -> List[Dict]:
        """Carrega histórico de feedback"""
        try:
            if self.feedback_path.exists():
                with open(self.feedback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar histórico de feedback: {e}")
            return []
    
    def save(self) -> None:
        """Salva histórico de feedback"""
        try:
            with open(self.feedback_path, 'w', encoding='utf-8') as f:
                json.dump(self.feedback_history, f, indent=4, ensure_ascii=False)
            logger.info("Histórico de feedback salvo")
        except Exception as e:
            logger.error(f"Erro ao salvar histórico de feedback: {e}")
    
    def register(self, feedback_data: Dict) -> None:
        """Registra novo feedback"""
        try:
            feedback_entry = {
                "timestamp": datetime.now().isoformat(),
                "data": feedback_data,
                "processed": False
            }
            self.feedback_history.append(feedback_entry)
            self.save()
            logger.info("Feedback registrado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao registrar feedback: {e}")
    
    def analyze(self) -> Dict:
        """Analisa feedback acumulado"""
        try:
            # Agrupa feedback por tipo
            feedback_by_type = {}
            for entry in self.feedback_history:
                feedback_type = entry["data"].get("tipo", "geral")
                if feedback_type not in feedback_by_type:
                    feedback_by_type[feedback_type] = []
                feedback_by_type[feedback_type].append(entry)
            
            # Analisa cada tipo de feedback
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "total_feedback": len(self.feedback_history),
                "por_tipo": {},
                "tendencias": self._identify_trends(feedback_by_type),
                "acoes_recomendadas": self._generate_recommendations(feedback_by_type)
            }
            
            # Marca feedback como processado
            for entry in self.feedback_history:
                entry["processed"] = True
            self.save()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao analisar feedback: {e}")
            return {}
    
    def _identify_trends(self, feedback_by_type: Dict) -> List[Dict]:
        """Identifica tendências no feedback"""
        trends = []
        try:
            for feedback_type, entries in feedback_by_type.items():
                # Analisa frequência
                frequency = len(entries)
                
                # Analisa sentimento (se disponível)
                sentiment = self._analyze_sentiment(entries)
                
                # Analisa padrões temporais
                temporal_patterns = self._analyze_temporal_patterns(entries)
                
                trends.append({
                    "tipo": feedback_type,
                    "frequencia": frequency,
                    "sentimento": sentiment,
                    "padroes_temporais": temporal_patterns
                })
        except Exception as e:
            logger.error(f"Erro ao identificar tendências: {e}")
        
        return trends
    
    def _analyze_sentiment(self, entries: List[Dict]) -> Dict:
        """Analisa sentimento do feedback"""
        try:
            # TODO: Implementar análise de sentimento mais sofisticada
            positive = 0
            negative = 0
            neutral = 0
            
            for entry in entries:
                sentiment = entry["data"].get("sentimento", "neutral")
                if sentiment == "positive":
                    positive += 1
                elif sentiment == "negative":
                    negative += 1
                else:
                    neutral += 1
            
            total = len(entries)
            return {
                "positive": positive / total if total > 0 else 0,
                "negative": negative / total if total > 0 else 0,
                "neutral": neutral / total if total > 0 else 0
            }
        except Exception as e:
            logger.error(f"Erro ao analisar sentimento: {e}")
            return {}
    
    def _analyze_temporal_patterns(self, entries: List[Dict]) -> Dict:
        """Analisa padrões temporais no feedback"""
        try:
            # TODO: Implementar análise temporal mais sofisticada
            return {
                "frequencia_media": len(entries) / 24 if entries else 0,  # por hora
                "ultima_atualizacao": entries[-1]["timestamp"] if entries else None
            }
        except Exception as e:
            logger.error(f"Erro ao analisar padrões temporais: {e}")
            return {}
    
    def _generate_recommendations(self, feedback_by_type: Dict) -> List[Dict]:
        """Gera recomendações baseadas no feedback"""
        recommendations = []
        try:
            for feedback_type, entries in feedback_by_type.items():
                # Analisa problemas mais frequentes
                common_issues = self._identify_common_issues(entries)
                
                # Gera recomendações específicas
                for issue in common_issues:
                    recommendations.append({
                        "tipo": feedback_type,
                        "problema": issue["descricao"],
                        "prioridade": issue["frequencia"],
                        "acao_recomendada": self._suggest_action(issue)
                    })
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {e}")
        
        return recommendations
    
    def _identify_common_issues(self, entries: List[Dict]) -> List[Dict]:
        """Identifica problemas comuns no feedback"""
        issues = {}
        try:
            for entry in entries:
                if "problema" in entry["data"]:
                    problem = entry["data"]["problema"]
                    if problem not in issues:
                        issues[problem] = {
                            "descricao": problem,
                            "frequencia": 0,
                            "exemplos": []
                        }
                    issues[problem]["frequencia"] += 1
                    issues[problem]["exemplos"].append(entry["data"])
        except Exception as e:
            logger.error(f"Erro ao identificar problemas comuns: {e}")
        
        return sorted(
            issues.values(),
            key=lambda x: x["frequencia"],
            reverse=True
        )
    
    def _suggest_action(self, issue: Dict) -> str:
        """Sugere ação para resolver problema"""
        try:
            # TODO: Implementar lógica mais sofisticada de sugestão
            return f"Revisar e ajustar {issue['descricao']}"
        except Exception as e:
            logger.error(f"Erro ao sugerir ação: {e}")
            return "Revisar feedback para sugestão específica" 