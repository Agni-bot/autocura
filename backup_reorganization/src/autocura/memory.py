"""
Gerenciador de memória do sistema de autocura
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryManager:
    """Gerenciador de memória do sistema"""
    
    def __init__(self, memory_path: Optional[Path] = None):
        self.memory_path = memory_path or Path("memoria_compartilhada.json")
        self.memory = self._load_memory()
        logger.info("MemoryManager inicializado com sucesso")
    
    def _load_memory(self) -> Dict:
        """Carrega memória do arquivo"""
        try:
            if self.memory_path.exists():
                with open(self.memory_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self._create_initial_memory()
        except Exception as e:
            logger.error(f"Erro ao carregar memória: {e}")
            return self._create_initial_memory()
    
    def _create_initial_memory(self) -> Dict:
        """Cria estrutura inicial da memória"""
        return {
            "decisoes_recentes": [],
            "estado_sistema": {
                "versao": "0.1.0",
                "modulos_ativos": [],
                "ultima_atualizacao": datetime.now().isoformat(),
                "nivel_autonomia": 0,
                "status": "Inicialização",
                "metricas_desempenho": {
                    "cobertura_testes": "baseline",
                    "latencia_media": "baseline"
                },
                "alertas_ativos": [],
                "incidentes": []
            },
            "log_eventos": [],
            "parametros_gerais": {
                "modo_diagnostico": True,
                "limite_agentes": 10
            },
            "memoria_operacional": {
                "decisoes": [],
                "acoes": [],
                "validacoes": [],
                "auditorias": []
            },
            "memoria_etica": {
                "principios": [
                    "Privacidade por padrão",
                    "Transparência de decisões",
                    "Conformidade LGPD/GDPR"
                ],
                "violacoes": [],
                "ajustes": [],
                "relatorios": []
            },
            "memoria_tecnica": {
                "configuracoes": {},
                "dependencias": {},
                "logs": [],
                "metricas": {}
            },
            "memoria_cognitiva": {
                "aprendizados": [],
                "padroes": [],
                "heuristicas": [],
                "adaptacoes": []
            },
            "memoria_autonomia": {
                "transicoes": [],
                "niveis": {},
                "criterios": {},
                "validacoes": []
            }
        }
    
    def save(self) -> None:
        """Salva memória no arquivo"""
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=4, ensure_ascii=False)
            logger.info("Memória salva com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")
    
    def update_from_feedback(self, feedback_data: Dict) -> None:
        """Atualiza memória com base em feedback recebido"""
        try:
            # Registra feedback nos logs
            self.memory["log_eventos"].append({
                "data": datetime.now().isoformat(),
                "evento": "Feedback recebido",
                "detalhes": feedback_data
            })
            
            # Atualiza métricas se presentes
            if "metricas" in feedback_data:
                self.memory["estado_sistema"]["metricas_desempenho"].update(
                    feedback_data["metricas"]
                )
            
            # Registra aprendizado se presente
            if "aprendizado" in feedback_data:
                self.memory["memoria_cognitiva"]["aprendizados"].append(
                    feedback_data["aprendizado"]
                )
            
            self.save()
            logger.info("Memória atualizada com feedback")
        except Exception as e:
            logger.error(f"Erro ao atualizar memória com feedback: {e}")
    
    def record_evolution(self, evolution_record: Dict) -> None:
        """Registra ciclo de evolução na memória"""
        try:
            # Atualiza estado do sistema
            self.memory["estado_sistema"].update({
                "ultima_atualizacao": evolution_record["timestamp"],
                "metricas_desempenho": evolution_record["metrics"]
            })
            
            # Registra evolução nos logs
            self.memory["log_eventos"].append({
                "data": evolution_record["timestamp"],
                "evento": "Ciclo de evolução",
                "detalhes": evolution_record
            })
            
            # Registra melhorias aplicadas
            for improvement in evolution_record["improvements"]:
                self.memory["memoria_operacional"]["acoes"].append({
                    "tipo": "melhoria",
                    "detalhes": improvement,
                    "timestamp": evolution_record["timestamp"]
                })
            
            self.save()
            logger.info("Evolução registrada na memória")
        except Exception as e:
            logger.error(f"Erro ao registrar evolução: {e}")
    
    def get_system_state(self) -> Dict:
        """Retorna estado atual do sistema"""
        return self.memory["estado_sistema"]
    
    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Retorna decisões recentes"""
        return self.memory["decisoes_recentes"][-limit:]
    
    def get_active_alerts(self) -> List[Dict]:
        """Retorna alertas ativos"""
        return self.memory["estado_sistema"]["alertas_ativos"]
    
    def add_alert(self, alert: Dict) -> None:
        """Adiciona novo alerta"""
        try:
            self.memory["estado_sistema"]["alertas_ativos"].append({
                **alert,
                "timestamp": datetime.now().isoformat()
            })
            self.save()
            logger.info("Alerta adicionado")
        except Exception as e:
            logger.error(f"Erro ao adicionar alerta: {e}")
    
    def clear_alert(self, alert_id: str) -> None:
        """Remove alerta específico"""
        try:
            self.memory["estado_sistema"]["alertas_ativos"] = [
                alert for alert in self.memory["estado_sistema"]["alertas_ativos"]
                if alert.get("id") != alert_id
            ]
            self.save()
            logger.info(f"Alerta {alert_id} removido")
        except Exception as e:
            logger.error(f"Erro ao remover alerta: {e}") 