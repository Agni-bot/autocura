"""
Validador Ético - Responsável pela validação ética de decisões e ações do sistema
"""
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..memoria.gerenciador_memoria import GerenciadorMemoria
from ..ia.cliente_ia import ClienteIA

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("validador_etico")

class ValidadorEtico:
    """Validador Ético - Responsável pela validação ética de decisões e ações do sistema"""
    
    def __init__(self, gerenciador_memoria: GerenciadorMemoria):
        self.gerenciador_memoria = gerenciador_memoria
        self.principios_eticos = self._carregar_principios_eticos()
        self.cliente_ia = ClienteIA()
        logger.info("Validador Ético inicializado")
    
    def validar_decisao(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Valida uma decisão do sistema sob a perspectiva ética"""
        try:
            # Enriquece a decisão com contexto
            decisao_enriquecida = self._enriquecer_decisao(decisao)
            
            # Usa a IA para validação ética avançada
            resultado_ia = self.cliente_ia.validar_etica(decisao_enriquecida)
            
            # Se a IA aprovou, faz validações adicionais locais
            if resultado_ia["aprovada"]:
                resultado_local = self._validar_localmente(decisao)
                if not resultado_local["aprovada"]:
                    return resultado_local
            
            # Registra a validação
            validacao = {
                "tipo": "decisao",
                "decisao_id": decisao.get("id"),
                "timestamp": datetime.now().isoformat(),
                "aprovada": resultado_ia["aprovada"],
                "confianca": resultado_ia.get("confianca", 0.0),
                "justificativa": resultado_ia.get("justificativa", ""),
                "analise_ia": resultado_ia
            }
            
            self.gerenciador_memoria.registrar_validacao_etica(validacao)
            
            return validacao
            
        except Exception as e:
            logger.error(f"Erro ao validar decisão: {str(e)}")
            return {
                "aprovada": False,
                "erro": str(e)
            }
    
    def _enriquecer_decisao(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece a decisão com contexto adicional."""
        try:
            decisao_enriquecida = decisao.copy()
            
            # Adiciona histórico recente
            historico = self.gerenciador_memoria.obter_historico_por_tipo("decisao")
            decisao_enriquecida["historico_recente"] = historico[:5]
            
            # Adiciona estado do sistema
            estado = self.gerenciador_memoria.obter_estado_sistema()
            decisao_enriquecida["estado_sistema"] = estado
            
            # Adiciona métricas relevantes
            metricas = estado.get("metricas_desempenho", {})
            decisao_enriquecida["metricas"] = metricas
            
            # Adiciona princípios éticos
            decisao_enriquecida["principios"] = self.principios_eticos
            
            return decisao_enriquecida
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer decisão: {str(e)}")
            return decisao
    
    def _validar_localmente(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza validações éticas locais adicionais."""
        try:
            resultados = []
            
            for principio in self.principios_eticos:
                resultado = self._aplicar_principio(principio, decisao)
                resultados.append(resultado)
            
            # Verifica se todos os princípios foram respeitados
            aprovada = all(r["aprovado"] for r in resultados)
            
            return {
                "aprovada": aprovada,
                "resultados": resultados,
                "tipo": "validacao_local"
            }
            
        except Exception as e:
            logger.error(f"Erro na validação local: {str(e)}")
            return {
                "aprovada": False,
                "erro": str(e),
                "tipo": "validacao_local"
            }
    
    def _carregar_principios_eticos(self) -> List[Dict[str, Any]]:
        """Carrega os princípios éticos do sistema"""
        try:
            return [
                {
                    "id": "transparencia",
                    "descricao": "Todas as decisões devem ser transparentes e explicáveis",
                    "peso": 0.9
                },
                {
                    "id": "privacidade",
                    "descricao": "Dados sensíveis devem ser protegidos",
                    "peso": 0.95
                },
                {
                    "id": "equidade",
                    "descricao": "Decisões devem ser justas e não discriminatórias",
                    "peso": 0.9
                },
                {
                    "id": "seguranca",
                    "descricao": "A segurança do sistema e usuários é prioritária",
                    "peso": 1.0
                },
                {
                    "id": "responsabilidade",
                    "descricao": "Deve haver responsabilização clara por cada decisão",
                    "peso": 0.85
                }
            ]
        except Exception as e:
            logger.error(f"Erro ao carregar princípios éticos: {str(e)}")
            return []
    
    def _aplicar_principio(self, principio: Dict[str, Any], decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica um princípio ético específico"""
        try:
            # Implementação básica - em produção seria mais sofisticada
            if principio["id"] == "transparencia":
                aprovado = "justificativa" in decisao and "explicacao" in decisao
            elif principio["id"] == "privacidade":
                aprovado = not decisao.get("envolve_dados_sensiveis", False)
            elif principio["id"] == "equidade":
                aprovado = not decisao.get("impacto_diferencial", False)
            elif principio["id"] == "seguranca":
                aprovado = decisao.get("risco_seguranca", "alto") != "alto"
            elif principio["id"] == "responsabilidade":
                aprovado = "responsavel" in decisao
            else:
                aprovado = True
            
            return {
                "principio": principio["id"],
                "aprovado": aprovado,
                "peso": principio["peso"]
            }
            
        except Exception as e:
            logger.error(f"Erro ao aplicar princípio {principio['id']}: {str(e)}")
            return {
                "principio": principio["id"],
                "aprovado": False,
                "erro": str(e)
            }
    
    def gerar_relatorio_etica(self) -> Dict[str, Any]:
        """Gera um relatório sobre o estado ético do sistema"""
        validacoes = self.gerenciador_memoria.obter_validacoes_eticas()
        
        # Análise de tendências
        total_validacoes = len(validacoes)
        validacoes_aprovadas = sum(1 for v in validacoes if v.get("aprovada", False))
        taxa_aprovacao = validacoes_aprovadas / total_validacoes if total_validacoes > 0 else 0
        
        # Análise por princípio
        analise_principios = {}
        for principio in self.principios_eticos:
            validacoes_principio = [
                v for v in validacoes
                if any(r["principio"] == principio["id"] for r in v.get("resultados", []))
            ]
            aprovadas_principio = sum(
                1 for v in validacoes_principio
                if all(r["aprovado"] for r in v.get("resultados", []) if r["principio"] == principio["id"])
            )
            analise_principios[principio["id"]] = {
                "total": len(validacoes_principio),
                "aprovadas": aprovadas_principio,
                "taxa_aprovacao": aprovadas_principio / len(validacoes_principio) if validacoes_principio else 0
            }
        
        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "total_validacoes": total_validacoes,
            "validacoes_aprovadas": validacoes_aprovadas,
            "taxa_aprovacao": taxa_aprovacao,
            "analise_principios": analise_principios,
            "ultimas_validacoes": validacoes[-10:] if validacoes else []
        }
        
        return relatorio 