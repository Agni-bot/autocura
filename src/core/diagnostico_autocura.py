import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json
from enum import Enum
from uuid import uuid4

from ..memoria.gerenciador_memoria import GerenciadorMemoria

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("diagnostico_autocura")

class TipoDiagnostico(Enum):
    """Tipos de diagnóstico"""
    SISTEMA = "sistema"
    PERFORMANCE = "performance"
    SEGURANCA = "seguranca"
    CONFIGURACAO = "configuracao"
    DEPENDENCIA = "dependencia"

class Severidade(Enum):
    """Níveis de severidade"""
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class StatusDiagnostico(Enum):
    """Status possíveis de um diagnóstico"""
    ABERTO = "aberto"
    EM_ANALISE = "em_analise"
    RESOLVIDO = "resolvido"
    FALHA = "falha"
    CANCELADO = "cancelado"

class DiagnosticoAutocura:
    """Representa um diagnóstico de autocura no sistema"""
    
    def __init__(
        self,
        tipo: TipoDiagnostico,
        descricao: str,
        severidade: Severidade,
        metricas: Dict[str, Any],
        id: Optional[str] = None,
        status: StatusDiagnostico = StatusDiagnostico.ABERTO,
        data_criacao: Optional[datetime] = None,
        data_analise: Optional[datetime] = None,
        data_resolucao: Optional[datetime] = None,
        resolucao: Optional[str] = None,
        acoes_tomadas: Optional[List[str]] = None
    ):
        self.id = id or str(uuid4())
        self.tipo = tipo
        self.descricao = descricao
        self.severidade = severidade
        self.metricas = metricas
        self.status = status
        self.data_criacao = data_criacao or datetime.now()
        self.data_analise = data_analise
        self.data_resolucao = data_resolucao
        self.resolucao = resolucao
        self.acoes_tomadas = acoes_tomadas or []

class GerenciadorDiagnostico:
    """Gerenciador de diagnósticos de autocura"""
    
    def __init__(self):
        self.memoria = None
        logger.info("Gerenciador de Diagnósticos inicializado")
    
    async def criar_diagnostico(
        self,
        tipo: TipoDiagnostico,
        descricao: str,
        severidade: Severidade,
        metricas: Dict[str, Any]
    ) -> Optional[DiagnosticoAutocura]:
        """Cria um novo diagnóstico"""
        if not tipo or not descricao:
            return None
            
        diagnostico = DiagnosticoAutocura(
            tipo=tipo,
            descricao=descricao,
            severidade=severidade,
            metricas=metricas
        )
        
        await self.memoria.criar_entidade("diagnosticos", diagnostico.__dict__)
        return diagnostico
    
    async def analisar_diagnostico(self, diagnostico_id: str) -> bool:
        """Inicia a análise de um diagnóstico"""
        diagnostico = await self.obter_diagnostico(diagnostico_id)
        if not diagnostico:
            return False
            
        diagnostico.status = StatusDiagnostico.EM_ANALISE
        diagnostico.data_analise = datetime.now()
        
        await self.memoria.atualizar_entidade("diagnosticos", diagnostico_id, diagnostico.__dict__)
        return True
    
    async def finalizar_diagnostico(
        self,
        diagnostico_id: str,
        resolucao: str,
        acoes_tomadas: List[str]
    ) -> bool:
        """Finaliza um diagnóstico com resolução"""
        diagnostico = await self.obter_diagnostico(diagnostico_id)
        if not diagnostico:
            return False
            
        diagnostico.status = StatusDiagnostico.RESOLVIDO
        diagnostico.data_resolucao = datetime.now()
        diagnostico.resolucao = resolucao
        diagnostico.acoes_tomadas = acoes_tomadas
        
        await self.memoria.atualizar_entidade("diagnosticos", diagnostico_id, diagnostico.__dict__)
        return True
    
    async def obter_diagnostico(self, diagnostico_id: str) -> Optional[DiagnosticoAutocura]:
        """Obtém um diagnóstico pelo ID"""
        dados = await self.memoria.obter_entidade("diagnosticos", diagnostico_id)
        if not dados:
            return None
            
        return DiagnosticoAutocura(**dados)
    
    async def listar_diagnosticos(self) -> List[DiagnosticoAutocura]:
        """Lista todos os diagnósticos"""
        dados = await self.memoria.buscar_entidades("diagnosticos")
        return [DiagnosticoAutocura(**d) for d in dados]
    
    async def analisar_tendencias(self) -> Dict[str, Any]:
        """Analisa tendências nos diagnósticos"""
        diagnosticos = await self.listar_diagnosticos()
        
        # Agrupa por tipo e severidade
        agrupamento = {}
        for d in diagnosticos:
            if d.tipo not in agrupamento:
                agrupamento[d.tipo] = {}
            if d.severidade not in agrupamento[d.tipo]:
                agrupamento[d.tipo][d.severidade] = 0
            agrupamento[d.tipo][d.severidade] += 1
        
        # Identifica padrões
        padroes = []
        for tipo, sevs in agrupamento.items():
            if sevs.get(Severidade.ALTA, 0) > 5:
                padroes.append(f"Alta incidência de problemas {tipo.value}")
            if sevs.get(Severidade.CRITICA, 0) > 0:
                padroes.append(f"Problemas críticos detectados em {tipo.value}")
        
        # Gera recomendações
        recomendacoes = []
        for padrao in padroes:
            if "alta incidência" in padrao:
                recomendacoes.append(f"Investigar causa raiz dos problemas {padrao}")
            if "críticos" in padrao:
                recomendacoes.append(f"Priorizar resolução dos problemas {padrao}")
        
        return {
            "padroes": padroes,
            "recomendacoes": recomendacoes,
            "agrupamento": agrupamento
        }

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