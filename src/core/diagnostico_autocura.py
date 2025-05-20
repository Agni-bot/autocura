import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from ..memoria.gerenciador_memoria import GerenciadorMemoria

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("diagnostico_autocura")

class SistemaDiagnosticoAutocura:
    """Sistema de diagnóstico e autocura do sistema"""
    
    def __init__(self, gerenciador_memoria: GerenciadorMemoria):
        self.gerenciador_memoria = gerenciador_memoria
        self.regras_diagnostico = self._carregar_regras_diagnostico()
        logger.info("Sistema de Diagnóstico e Autocura inicializado")
    
    def _carregar_regras_diagnostico(self) -> Dict[str, Any]:
        """Carrega as regras de diagnóstico do arquivo de configuração"""
        try:
            caminho_regras = Path("config/regras_diagnostico.json")
            if caminho_regras.exists():
                with open(caminho_regras, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Arquivo de regras não encontrado. Usando regras padrão.")
                return self._criar_regras_padrao()
        except Exception as e:
            logger.error(f"Erro ao carregar regras: {str(e)}")
            return self._criar_regras_padrao()
    
    def _criar_regras_padrao(self) -> Dict[str, Any]:
        """Cria regras padrão de diagnóstico"""
        return {
            "metricas_desempenho": {
                "latencia_maxima": 200,  # ms
                "cpu_maxima": 80,  # %
                "memoria_maxima": 80,  # %
                "erros_maximos": 5  # por minuto
            },
            "regras_anomalia": {
                "variacao_latencia": 50,  # ms
                "variacao_cpu": 20,  # %
                "variacao_memoria": 20,  # %
                "taxa_erro": 0.01  # 1%
            },
            "acoes_correcao": {
                "alta_latencia": ["otimizar_cache", "escalar_horizontal"],
                "alta_cpu": ["otimizar_processamento", "escalar_horizontal"],
                "alta_memoria": ["limpar_cache", "escalar_horizontal"],
                "alta_taxa_erro": ["revisar_logs", "reduzir_carga"]
            }
        }
    
    def executar_diagnostico(self) -> Dict[str, Any]:
        """Executa diagnóstico completo do sistema"""
        try:
            estado_sistema = self.gerenciador_memoria.obter_estado_sistema()
            metricas = estado_sistema.get("metricas_desempenho", {})
            
            diagnosticos = []
            anomalias = []
            
            # Verifica métricas de desempenho
            for metrica, valor in metricas.items():
                if metrica in self.regras_diagnostico["metricas_desempenho"]:
                    limite = self.regras_diagnostico["metricas_desempenho"][metrica]
                    if valor > limite:
                        diagnostico = {
                            "tipo": "metrica_excedida",
                            "metrica": metrica,
                            "valor": valor,
                            "limite": limite,
                            "severidade": "alta" if valor > limite * 1.5 else "media"
                        }
                        diagnosticos.append(diagnostico)
                        
                        # Registra anomalia
                        anomalia = {
                            "tipo": "anomalia_metrica",
                            "metrica": metrica,
                            "valor": valor,
                            "limite": limite,
                            "timestamp": datetime.now().isoformat()
                        }
                        anomalias.append(anomalia)
            
            # Registra diagnósticos e anomalias
            for diagnostico in diagnosticos:
                self.gerenciador_memoria.registrar_diagnostico(diagnostico)
            
            for anomalia in anomalias:
                self.gerenciador_memoria.registrar_anomalia(anomalia)
            
            return {
                "status": "completo",
                "diagnosticos": diagnosticos,
                "anomalias": anomalias,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar diagnóstico: {str(e)}")
            return {
                "status": "erro",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def executar_correcao(self, diagnostico: Dict[str, Any]) -> Dict[str, Any]:
        """Executa correção baseada no diagnóstico"""
        try:
            tipo_diagnostico = diagnostico.get("tipo")
            metrica = diagnostico.get("metrica")
            
            if tipo_diagnostico == "metrica_excedida" and metrica in self.regras_diagnostico["acoes_correcao"]:
                acoes = self.regras_diagnostico["acoes_correcao"][metrica]
                
                correcao = {
                    "tipo": "correcao_automatica",
                    "diagnostico": diagnostico,
                    "acoes": acoes,
                    "status": "iniciado",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Registra correção
                self.gerenciador_memoria.registrar_correcao(correcao)
                
                # Executa ações de correção
                for acao in acoes:
                    self._executar_acao_correcao(acao)
                
                correcao["status"] = "completo"
                self.gerenciador_memoria.registrar_correcao(correcao)
                
                return correcao
            
            return {
                "status": "sem_acao",
                "mensagem": "Nenhuma ação de correção disponível para o diagnóstico",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao executar correção: {str(e)}")
            return {
                "status": "erro",
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _executar_acao_correcao(self, acao: str) -> None:
        """Executa uma ação específica de correção"""
        try:
            if acao == "otimizar_cache":
                # Implementar lógica de otimização de cache
                pass
            elif acao == "escalar_horizontal":
                # Implementar lógica de escalonamento horizontal
                pass
            elif acao == "otimizar_processamento":
                # Implementar lógica de otimização de processamento
                pass
            elif acao == "limpar_cache":
                # Implementar lógica de limpeza de cache
                pass
            elif acao == "revisar_logs":
                # Implementar lógica de revisão de logs
                pass
            elif acao == "reduzir_carga":
                # Implementar lógica de redução de carga
                pass
            
            logger.info(f"Ação de correção executada: {acao}")
            
        except Exception as e:
            logger.error(f"Erro ao executar ação de correção {acao}: {str(e)}")
            raise 