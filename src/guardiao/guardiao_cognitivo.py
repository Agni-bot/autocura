# Módulo Guardião Cognitivo

import logging
import time
import json
import threading
import os
from typing import Dict, List, Any, Tuple, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import numpy as np
import requests
import flask
from kubernetes import client, config # Adicionado para interagir com Kubernetes
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
from prometheus_client import Counter, Gauge, Histogram

from ..memoria.gerenciador_memoria import GerenciadorMemoria

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("GuardiãoCognitivo")

# --- Definições de Estruturas de Dados ---
@dataclass
class DiagnosticoInfo:
    id: str
    timestamp: float
    anomalias_detectadas: List[Tuple[str, float]]
    causa_raiz_identificada: Optional[str] = None
    confianca_geral: float = 0.0
    contexto: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DiagnosticoInfo":
        return cls(
            id=data.get("id", "unknown_id"),
            timestamp=data.get("timestamp", time.time()),
            anomalias_detectadas=data.get("anomalias_detectadas", []),
            causa_raiz_identificada=data.get("causa_raiz_identificada"),
            confianca_geral=data.get("confianca_geral", 0.0),
            contexto=data.get("contexto", {})
        )

@dataclass
class PlanoAcaoInfo:
    id: str
    diagnostico_id: str
    acoes_ids: List[str]
    timestamp_geracao: float
    status_execucao: str
    timestamp_conclusao: Optional[float] = None
    resultado_eficacia: Optional[Dict[str, float]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlanoAcaoInfo":
        return cls(
            id=data.get("id", "unknown_id"),
            diagnostico_id=data.get("diagnostico_id", "unknown_diag_id"),
            acoes_ids=data.get("acoes_ids", []),
            timestamp_geracao=data.get("timestamp_geracao", time.time()),
            status_execucao=data.get("status_execucao", "criado"),
            timestamp_conclusao=data.get("timestamp_conclusao"),
            resultado_eficacia=data.get("resultado_eficacia")
        )

@dataclass
class EventoCognitivo:
    """Representa um evento cognitivo do sistema."""
    tipo: str
    timestamp: datetime
    severidade: float
    contexto: Dict[str, Any]
    impacto: float
    resolvido: bool = False

# --- Configurações do Guardião ---
CONFIG_GUARDIAN = {
    "api_monitoramento_url": os.getenv("MONITORAMENTO_SERVICE_URL", "http://monitoramento:8080/api"),
    "api_diagnostico_url": os.getenv("DIAGNOSTICO_SERVICE_URL", "http://diagnostico:8080/api"),
    "api_gerador_acoes_url": os.getenv("ACAO_SERVICE_URL", "http://gerador-acoes:8080/api"),
    "intervalo_verificacao_segundos": int(os.getenv("GUARDIAN_INTERVALO_VERIFICACAO_SEGUNDOS", "60")),
    "historico_diagnosticos_max_tamanho": int(os.getenv("GUARDIAN_HISTORICO_DIAGNOSTICOS_MAX", "1000")),
    "historico_planos_acao_max_tamanho": int(os.getenv("GUARDIAN_HISTORICO_PLANOS_ACAO_MAX", "500")),
    "limiar_incoerencia_diagnostico": float(os.getenv("GUARDIAN_LIMIAR_INCOERENCIA", "0.7")),
    "limiar_baixa_eficacia_acao": float(os.getenv("GUARDIAN_LIMIAR_BAIXA_EFICACIA", "0.3")),
    "janela_estabilidade_decisoes_segundos": int(os.getenv("GUARDIAN_JANELA_ESTABILIDADE_SEGUNDOS", "3600")),
    "max_oscilacoes_decisao_permitidas": int(os.getenv("GUARDIAN_MAX_OSCILACOES_DECISAO", "5")),
    "emergency_target_namespace": os.getenv("EMERGENCY_TARGET_NAMESPACE", "autocura"),
    "emergency_target_deployments": os.getenv("EMERGENCY_TARGET_DEPLOYMENTS", "diagnostico,gerador-acoes,monitoramento,observabilidade"), # Lista separada por vírgula
    "alert_webhook_url": os.getenv("ALERT_WEBHOOK_URL") # URL para enviar alertas (ex: Slack, Teams)
}

class GuardiaoCognitivo:
    """Guardião Cognitivo - Responsável pelo monitoramento de saúde e salvaguardas do sistema"""
    
    def __init__(self, gerenciador_memoria: GerenciadorMemoria):
        self.gerenciador_memoria = gerenciador_memoria
        self.alertas_ativos = []
        self.incidentes = []
        self.historico_diagnosticos = deque(maxlen=CONFIG_GUARDIAN["historico_diagnosticos_max_tamanho"])
        self.historico_planos_acao = deque(maxlen=CONFIG_GUARDIAN["historico_planos_acao_max_tamanho"])
        self.lock = threading.Lock()
        self.rodando = False
        self.thread_monitoramento = None
        self.kube_api_client = None
        self._inicializar_kube_client()
        logger.info("Guardião Cognitivo inicializado com config: %s", CONFIG_GUARDIAN)

        # Métricas Prometheus
        self.metricas = {
            "eventos_cognitivos": Counter(
                "eventos_cognitivos_total",
                "Total de eventos cognitivos",
                ["tipo", "severidade"]
            ),
            "saude_cognitiva": Gauge(
                "saude_cognitiva",
                "Saúde cognitiva do sistema",
                ["dimensao"]
            ),
            "tempo_resposta": Histogram(
                "tempo_resposta_guardiao",
                "Tempo de resposta do guardião",
                ["acao"]
            )
        }
        
        # Histórico de eventos
        self.historico_eventos: List[EventoCognitivo] = []
        
        # Limites de alerta
        self.limites = {
            "cpu": 80.0,
            "memoria": 80.0,
            "latencia": 1000.0,
            "erros": 5.0,
            "anomalias": 3.0
        }
        
        # Ações protetivas
        self.acoes_protetivas = {
            "alta_cpu": self._acao_alta_cpu,
            "alta_memoria": self._acao_alta_memoria,
            "alta_latencia": self._acao_alta_latencia,
            "alta_taxa_erros": self._acao_alta_taxa_erros,
            "anomalia_detectada": self._acao_anomalia_detectada
        }
        
        # Cache de métricas
        self.cache_metricas = {}
        self.cache_timeout = timedelta(minutes=5)
        
        self.logger.info("Guardião Cognitivo inicializado")

    def _inicializar_kube_client(self):
        try:
            config.load_incluster_config() # Para rodar dentro do cluster Kubernetes
            self.kube_api_client = client.AppsV1Api()
            logger.info("Configuração Kubernetes In-Cluster carregada com sucesso.")
        except config.ConfigException as e1:
            logger.warning(f"Não foi possível carregar configuração in-cluster: {e1}. Tentando kube_config local...")
            try:
                config.load_kube_config() # Para rodar localmente com um kubeconfig
                self.kube_api_client = client.AppsV1Api()
                logger.info("Configuração Kubernetes Local (kube_config) carregada com sucesso.")
            except config.ConfigException as e2:
                logger.error(f"Não foi possível carregar nenhuma configuração Kubernetes: {e2}. Funcionalidades de intervenção no cluster estarão desabilitadas.")
                self.kube_api_client = None

    def _enviar_alerta(self, mensagem: str, detalhes: Dict[str, Any]):
        logger.critical(f"ALERTA: {mensagem} - Detalhes: {json.dumps(detalhes)}")
        if CONFIG_GUARDIAN["alert_webhook_url"]:
            try:
                payload = {
                    "text": f"🚨 *Alerta do Guardião Cognitivo* 🚨\n*Tipo*: {mensagem}\n*Detalhes*: ```{json.dumps(detalhes, indent=2)}```"
                }
                response = requests.post(CONFIG_GUARDIAN["alert_webhook_url"], json=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"Alerta enviado com sucesso para o webhook.")
            except requests.exceptions.RequestException as e:
                logger.error(f"Falha ao enviar alerta para o webhook: {e}")
        else:
            logger.warning("Nenhuma URL de webhook para alertas configurada (ALERT_WEBHOOK_URL).")

    def _acionar_protocolo_emergencia(self, tipo_emergencia: str, detalhes: Dict[str, Any]):
        self._enviar_alerta(f"PROTOCOLO DE EMERGÊNCIA: {tipo_emergencia}", detalhes)

        if not self.kube_api_client:
            logger.error("API Kubernetes não está disponível. Não é possível escalar deployments.")
            return

        target_namespace = CONFIG_GUARDIAN["emergency_target_namespace"]
        target_deployments_str = CONFIG_GUARDIAN["emergency_target_deployments"]
        deployments_to_scale = [d.strip() for d in target_deployments_str.split(",") if d.strip()]

        if not deployments_to_scale:
            logger.warning("Nenhum deployment alvo configurado para escalonamento de emergência.")
            return

        logger.info(f"Iniciando escalonamento de emergência para 0 réplicas dos deployments: {deployments_to_scale} no namespace {target_namespace}")
        for dep_name in deployments_to_scale:
            try:
                logger.info(f"Escalando deployment \t{dep_name}\t para 0 réplicas...")
                scale_body = {"spec": {"replicas": 0}}
                self.kube_api_client.patch_namespaced_deployment_scale(
                    name=dep_name,
                    namespace=target_namespace,
                    body=scale_body
                )
                logger.info(f"Deployment \t{dep_name}\t escalado para 0 réplicas com sucesso.")
            except client.exceptions.ApiException as e:
                logger.error(f"Erro da API Kubernetes ao escalar deployment \t{dep_name}\t: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado ao escalar deployment \t{dep_name}\t: {e}")
        
        logger.critical("Ações de intervenção de emergência (escalonamento de deployments) concluídas.")

    def _obter_diagnosticos_recentes(self, limite: int = 100) -> List[DiagnosticoInfo]:
        diagnostico_url = CONFIG_GUARDIAN['api_diagnostico_url']
        url = f"{diagnostico_url}/diagnosticos/recentes?limite={limite}"
        logger.debug(f"Obtendo diagnósticos recentes de: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            diagnosticos_data = response.json()
            return [DiagnosticoInfo.from_dict(d) for d in diagnosticos_data]
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter diagnósticos recentes do serviço de Diagnóstico: {e}")
            with self.lock:
                return list(self.historico_diagnosticos)[-limite:]
        except Exception as e:
            logger.error(f"Erro inesperado ao processar diagnósticos recentes: {e}")
            return []

    def _obter_planos_acao_concluidos_recentes(self, limite: int = 50) -> List[PlanoAcaoInfo]:
        gerador_acoes_url = CONFIG_GUARDIAN['api_gerador_acoes_url']
        url = f"{gerador_acoes_url}/planos/concluidos/recentes?limite={limite}"
        logger.debug(f"Obtendo planos de ação concluídos recentes de: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            planos_data = response.json()
            return [PlanoAcaoInfo.from_dict(p) for p in planos_data]
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter planos de ação recentes do serviço Gerador de Ações: {e}")
            with self.lock:
                concluidos = [p for p in self.historico_planos_acao if p.status_execucao in ["concluido", "falhou"]]
                return concluidos[-limite:]
        except Exception as e:
            logger.error(f"Erro inesperado ao processar planos de ação recentes: {e}")
            return []

    def verificar_coerencia_diagnosticos(self):
        logger.info("Verificando coerência de diagnósticos...")
        diagnosticos = self._obter_diagnosticos_recentes(limite=50)
        if len(diagnosticos) < 10:
            logger.info("Dados insuficientes para análise de coerência de diagnósticos.")
            return

        baixa_confianca_count = sum(1 for d in diagnosticos if d.confianca_geral < 0.5)
        if len(diagnosticos) > 0 and (baixa_confianca_count / len(diagnosticos)) > CONFIG_GUARDIAN["limiar_incoerencia_diagnostico"]:
            self._acionar_protocolo_emergencia(
                "Incoerência de Diagnósticos: Baixa Confiança Generalizada",
                {"total_diagnosticos": len(diagnosticos), "baixa_confianca_count": baixa_confianca_count}
            )
            return
        logger.info("Coerência de diagnósticos parece estável.")

    def verificar_eficacia_acoes(self):
        logger.info("Verificando eficácia de ações corretivas...")
        planos_concluidos = self._obter_planos_acao_concluidos_recentes(limite=20)
        if len(planos_concluidos) < 5:
            logger.info("Dados insuficientes para análise de eficácia de ações.")
            return

        eficacias_gerais = []
        for plano in planos_concluidos:
            if plano.resultado_eficacia and plano.status_execucao == "concluido":
                valores_eficacia = [v for v in plano.resultado_eficacia.values() if isinstance(v, (int, float))]
                if valores_eficacia:
                    media_eficacia_plano = np.mean(valores_eficacia)
                    eficacias_gerais.append(media_eficacia_plano)
        
        if not eficacias_gerais:
            logger.warning("Nenhum plano concluído com sucesso com dados de eficácia para análise.")
            return

        media_total_eficacia = np.mean(eficacias_gerais)
        if media_total_eficacia < CONFIG_GUARDIAN["limiar_baixa_eficacia_acao"]:
            self._acionar_protocolo_emergencia(
                "Baixa Eficácia de Ações Corretivas",
                {"media_eficacia_recente": float(media_total_eficacia), "num_planos_analisados": len(eficacias_gerais)}
            )
            return
        logger.info(f"Eficácia média das ações: {media_total_eficacia:.2f}. Parece estável.")

    def verificar_estabilidade_decisoes(self):
        logger.info("Verificando estabilidade de decisões...")
        planos_recentes = list(self.historico_planos_acao)[-50:]
        if len(planos_recentes) < 10:
            logger.info("Dados insuficientes para análise de estabilidade de decisões.")
            return

        num_cancelados_recentemente = sum(1 for p in planos_recentes if p.status_execucao == "cancelado" and (time.time() - p.timestamp_geracao) < CONFIG_GUARDIAN["janela_estabilidade_decisoes_segundos"])
        if num_cancelados_recentemente > CONFIG_GUARDIAN["max_oscilacoes_decisao_permitidas"]:
             self._acionar_protocolo_emergencia(
                "Instabilidade de Decisões: Alta Taxa de Cancelamento de Planos",
                {"num_cancelados_recentemente": num_cancelados_recentemente, "periodo_segundos": CONFIG_GUARDIAN["janela_estabilidade_decisoes_segundos"]}
            )
             return
        logger.info("Estabilidade de decisões parece adequada.")

    def _loop_monitoramento(self):
        logger.info("Loop de monitoramento do Guardião iniciado.")
        while self.rodando:
            try:
                self.verificar_coerência_diagnosticos()
                time.sleep(2)
                self.verificar_eficacia_acoes()
                time.sleep(2)
                self.verificar_estabilidade_decisoes()
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento do Guardião: {e}", exc_info=True)
            
            intervalo_atual = CONFIG_GUARDIAN["intervalo_verificacao_segundos"]
            for _ in range(max(1, intervalo_atual // 5)):
                if not self.rodando:
                    break
                time.sleep(min(5, intervalo_atual))
        logger.info("Loop de monitoramento do Guardião finalizado.")

    def iniciar(self):
        if self.rodando:
            logger.warning("Guardião Cognitivo já está rodando.")
            return
        self.rodando = True
        self.thread_monitoramento = threading.Thread(target=self._loop_monitoramento, daemon=True)
        self.thread_monitoramento.start()
        logger.info("Guardião Cognitivo iniciado.")

    def parar(self):
        if not self.rodando:
            logger.warning("Guardião Cognitivo não está rodando.")
            return
        self.rodando = False
        if self.thread_monitoramento and self.thread_monitoramento.is_alive():
            self.thread_monitoramento.join(timeout=10)
        logger.info("Guardião Cognitivo parado.")

    def registrar_novo_diagnostico(self, diagnostico: DiagnosticoInfo):
        with self.lock:
            self.historico_diagnosticos.append(diagnostico)
        logger.debug(f"Novo diagnóstico registrado no Guardião: {diagnostico.id}")

    def registrar_novo_plano_acao(self, plano: PlanoAcaoInfo):
        with self.lock:
            for i, p_existente in enumerate(self.historico_planos_acao):
                if p_existente.id == plano.id:
                    self.historico_planos_acao[i] = plano
                    logger.debug(f"Plano de ação atualizado no Guardião: {plano.id}, Status: {plano.status_execucao}")
                    return
            self.historico_planos_acao.append(plano)
        logger.debug(f"Novo plano de ação registrado no Guardião: {plano.id}")

    def monitorar_saude_sistema(self) -> Dict[str, Any]:
        """Monitora a saúde geral do sistema"""
        estado = self.gerenciador_memoria.obter_estado_sistema()
        metricas = estado.get("metricas_desempenho", {})
        
        # Análise de métricas críticas
        alertas = []
        if metricas.get("cpu_uso", 0) > 90:
            alertas.append({
                "tipo": "critico",
                "componente": "cpu",
                "mensagem": "Uso de CPU acima do limite",
                "valor": metricas["cpu_uso"]
            })
        
        if metricas.get("memoria_uso", 0) > 85:
            alertas.append({
                "tipo": "critico",
                "componente": "memoria",
                "mensagem": "Uso de memória acima do limite",
                "valor": metricas["memoria_uso"]
            })
        
        if metricas.get("latencia", 0) > 1000:
            alertas.append({
                "tipo": "critico",
                "componente": "latencia",
                "mensagem": "Latência acima do limite",
                "valor": metricas["latencia"]
            })
        
        # Atualizar estado do sistema
        if alertas:
            self.gerenciador_memoria.atualizar_estado_sistema({
                "alertas_ativos": alertas,
                "status": "alerta"
            })
        
        return {
            "status": "alerta" if alertas else "normal",
            "alertas": alertas,
            "metricas": metricas
        }
    
    def verificar_integridade_etica(self) -> Dict[str, Any]:
        """Verifica a integridade ética do sistema"""
        validacoes = self.gerenciador_memoria.obter_validacoes_eticas()
        violacoes = []
        
        for validacao in validacoes:
            if not validacao.get("aprovada", False):
                violacoes.append({
                    "tipo": "violacao_etica",
                    "componente": validacao.get("componente"),
                    "mensagem": validacao.get("mensagem"),
                    "timestamp": validacao.get("timestamp")
                })
        
        if violacoes:
            self.gerenciador_memoria.atualizar_estado_sistema({
                "status": "violacao_etica",
                "incidentes": violacoes
            })
        
        return {
            "status": "violacao" if violacoes else "normal",
            "violacoes": violacoes
        }
    
    def verificar_autonomia(self) -> Dict[str, Any]:
        """Verifica o estado atual de autonomia do sistema"""
        estado = self.gerenciador_memoria.obter_estado_sistema()
        nivel_atual = estado.get("nivel_autonomia", 1)
        transicoes = self.gerenciador_memoria.obter_transicoes_autonomia()
        
        # Verificar se há transições pendentes
        transicoes_pendentes = [
            t for t in transicoes
            if t.get("estado") == "pendente"
        ]
        
        if transicoes_pendentes:
            self.gerenciador_memoria.atualizar_estado_sistema({
                "status": "transicao_pendente",
                "transicao_atual": transicoes_pendentes[0]
            })
        
        return {
            "nivel_atual": nivel_atual,
            "transicoes_pendentes": transicoes_pendentes
        }
    
    def aplicar_salvaguardas(self, incidente: Dict[str, Any]) -> None:
        """Aplica salvaguardas baseadas no tipo de incidente"""
        tipo_incidente = incidente.get("tipo")
        
        if tipo_incidente == "critico":
            # Reduzir autonomia para nível mínimo
            self.gerenciador_memoria.atualizar_estado_sistema({
                "nivel_autonomia": 1,
                "status": "emergencia"
            })
            logger.warning("Autonomia reduzida para nível mínimo devido a incidente crítico")
        
        elif tipo_incidente == "violacao_etica":
            # Suspender operações autônomas
            self.gerenciador_memoria.atualizar_estado_sistema({
                "status": "suspenso",
                "motivo": "violacao_etica"
            })
            logger.warning("Operações suspensas devido a violação ética")
        
        # Registrar incidente
        self.gerenciador_memoria.registrar_acao({
            "tipo": "salvaguarda",
            "incidente": incidente,
            "acao": "aplicada",
            "timestamp": datetime.now().isoformat()
        })
    
    def verificar_aprendizado(self) -> Dict[str, Any]:
        """Verifica o estado do aprendizado do sistema"""
        aprendizados = self.gerenciador_memoria.obter_aprendizados_recentes()
        
        # Análise de padrões de aprendizado
        padroes = []
        for aprendizado in aprendizados:
            if aprendizado.get("tipo") == "padrao":
                padroes.append(aprendizado)
        
        return {
            "total_aprendizados": len(aprendizados),
            "padroes_detectados": len(padroes),
            "ultimo_aprendizado": aprendizados[-1] if aprendizados else None
        }
    
    def executar_ciclo_monitoramento(self) -> Dict[str, Any]:
        """Executa um ciclo completo de monitoramento"""
        resultados = {
            "saude": self.monitorar_saude_sistema(),
            "etica": self.verificar_integridade_etica(),
            "autonomia": self.verificar_autonomia(),
            "aprendizado": self.verificar_aprendizado()
        }
        
        # Verificar necessidade de salvaguardas
        if resultados["saude"]["status"] == "alerta":
            for alerta in resultados["saude"]["alertas"]:
                self.aplicar_salvaguardas(alerta)
        
        if resultados["etica"]["status"] == "violacao":
            for violacao in resultados["etica"]["violacoes"]:
                self.aplicar_salvaguardas(violacao)
        
        return resultados

    async def registrar_evento(self, tipo: str, severidade: float, contexto: Dict[str, Any], impacto: float) -> None:
        """Registra um evento cognitivo.
        
        Args:
            tipo: Tipo do evento
            severidade: Severidade do evento (0-1)
            contexto: Contexto do evento
            impacto: Impacto do evento (0-1)
        """
        evento = EventoCognitivo(
            tipo=tipo,
            timestamp=datetime.now(),
            severidade=severidade,
            contexto=contexto,
            impacto=impacto
        )
        
        self.historico_eventos.append(evento)
        
        # Atualiza métricas
        self.metricas["eventos_cognitivos"].labels(
            tipo=tipo,
            severidade=f"{severidade:.1f}"
        ).inc()
        
        self.logger.info(f"Evento cognitivo registrado: {tipo} (severidade: {severidade}, impacto: {impacto})")
    
    async def avaliar_saude_cognitiva(self) -> Dict[str, Any]:
        """Avalia a saúde cognitiva do sistema.
        
        Returns:
            Dicionário com avaliação da saúde
        """
        saude = {
            "timestamp": datetime.now(),
            "score_geral": 1.0,
            "dimensoes": {},
            "alertas": []
        }
        
        # Avalia cada dimensão
        for dimensao, limite in self.limites.items():
            valor = self.cache_metricas.get(dimensao, 0)
            score = 1.0 - (valor / limite) if valor < limite else 0.0
            
            saude["dimensoes"][dimensao] = {
                "valor": valor,
                "limite": limite,
                "score": score
            }
            
            # Atualiza métrica
            self.metricas["saude_cognitiva"].labels(dimensao=dimensao).set(score)
            
            # Verifica alertas
            if valor > limite:
                saude["alertas"].append({
                    "dimensao": dimensao,
                    "valor": valor,
                    "limite": limite,
                    "severidade": (valor - limite) / limite
                })
        
        # Calcula score geral
        scores = [d["score"] for d in saude["dimensoes"].values()]
        saude["score_geral"] = np.mean(scores)
        
        return saude
    
    async def verificar_limites(self, metricas: Dict[str, float]) -> List[Dict[str, Any]]:
        """Verifica se as métricas ultrapassam os limites.
        
        Args:
            metricas: Dicionário com métricas
            
        Returns:
            Lista de violações de limites
        """
        violacoes = []
        
        for nome, valor in metricas.items():
            if nome in self.limites and valor > self.limites[nome]:
                violacoes.append({
                    "metrica": nome,
                    "valor": valor,
                    "limite": self.limites[nome],
                    "severidade": (valor - self.limites[nome]) / self.limites[nome]
                })
        
        return violacoes
    
    async def executar_acao_protetiva(self, tipo: str, contexto: Dict[str, Any]) -> bool:
        """Executa uma ação protetiva.
        
        Args:
            tipo: Tipo da ação
            contexto: Contexto da ação
            
        Returns:
            True se a ação foi executada com sucesso
        """
        if tipo not in self.acoes_protetivas:
            self.logger.error(f"Ação protetiva desconhecida: {tipo}")
            return False
        
        try:
            with self.metricas["tempo_resposta"].labels(acao=tipo).time():
                sucesso = await self.acoes_protetivas[tipo](contexto)
            
            if sucesso:
                self.logger.info(f"Ação protetiva {tipo} executada com sucesso")
            else:
                self.logger.warning(f"Ação protetiva {tipo} falhou")
            
            return sucesso
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ação protetiva {tipo}: {e}")
            return False
    
    async def _acao_alta_cpu(self, contexto: Dict[str, Any]) -> bool:
        """Ação protetiva para alta CPU."""
        try:
            # Implementar lógica de ação
            await asyncio.sleep(1)  # Simulação
            return True
        except Exception as e:
            self.logger.error(f"Erro na ação de alta CPU: {e}")
            return False
    
    async def _acao_alta_memoria(self, contexto: Dict[str, Any]) -> bool:
        """Ação protetiva para alta memória."""
        try:
            # Implementar lógica de ação
            await asyncio.sleep(1)  # Simulação
            return True
        except Exception as e:
            self.logger.error(f"Erro na ação de alta memória: {e}")
            return False
    
    async def _acao_alta_latencia(self, contexto: Dict[str, Any]) -> bool:
        """Ação protetiva para alta latência."""
        try:
            # Implementar lógica de ação
            await asyncio.sleep(1)  # Simulação
            return True
        except Exception as e:
            self.logger.error(f"Erro na ação de alta latência: {e}")
            return False
    
    async def _acao_alta_taxa_erros(self, contexto: Dict[str, Any]) -> bool:
        """Ação protetiva para alta taxa de erros."""
        try:
            # Implementar lógica de ação
            await asyncio.sleep(1)  # Simulação
            return True
        except Exception as e:
            self.logger.error(f"Erro na ação de alta taxa de erros: {e}")
            return False
    
    async def _acao_anomalia_detectada(self, contexto: Dict[str, Any]) -> bool:
        """Ação protetiva para anomalia detectada."""
        try:
            # Implementar lógica de ação
            await asyncio.sleep(1)  # Simulação
            return True
        except Exception as e:
            self.logger.error(f"Erro na ação de anomalia: {e}")
            return False
    
    async def atualizar_metricas(self, metricas: Dict[str, float]) -> None:
        """Atualiza as métricas do sistema.
        
        Args:
            metricas: Dicionário com métricas
        """
        self.cache_metricas = metricas
        self.cache_metricas["timestamp"] = datetime.now()
    
    async def obter_historico_eventos(self, periodo: Optional[timedelta] = None) -> List[EventoCognitivo]:
        """Obtém o histórico de eventos.
        
        Args:
            periodo: Período de tempo (opcional)
            
        Returns:
            Lista de eventos
        """
        if not periodo:
            return self.historico_eventos
        
        inicio = datetime.now() - periodo
        return [
            evento for evento in self.historico_eventos
            if evento.timestamp >= inicio
        ]
    
    async def limpar_historico(self, periodo: timedelta) -> None:
        """Limpa o histórico de eventos antigos.
        
        Args:
            periodo: Período de tempo para manter
        """
        inicio = datetime.now() - periodo
        self.historico_eventos = [
            evento for evento in self.historico_eventos
            if evento.timestamp >= inicio
        ]
        
        self.logger.info(f"Histórico de eventos limpo (período: {periodo})")
    
    async def gerar_relatorio(self, periodo: Optional[timedelta] = None) -> Dict[str, Any]:
        """Gera um relatório do guardião.
        
        Args:
            periodo: Período de tempo (opcional)
            
        Returns:
            Dicionário com relatório
        """
        eventos = await self.obter_historico_eventos(periodo)
        saude = await self.avaliar_saude_cognitiva()
        
        relatorio = {
            "timestamp": datetime.now(),
            "saude": saude,
            "eventos": [
                {
                    "tipo": e.tipo,
                    "timestamp": e.timestamp,
                    "severidade": e.severidade,
                    "impacto": e.impacto,
                    "resolvido": e.resolvido
                }
                for e in eventos
            ],
            "metricas": self.cache_metricas
        }
        
        return relatorio

# Criar instância do gerenciador de memória
gerenciador_memoria = GerenciadorMemoria()
gerenciador_memoria.initialize()

# Criar instância do guardião
guardiao_singleton = GuardiaoCognitivo(gerenciador_memoria)

# Inicializar Flask app
app = flask.Flask(__name__)

@app.route("/health", methods=["GET"])
def health_check():
    is_healthy = guardiao_singleton.rodando
    if guardiao_singleton.thread_monitoramento and not guardiao_singleton.thread_monitoramento.is_alive():
        is_healthy = False
        logger.error("Health check falhou: Thread de monitoramento não está ativa!")
    return flask.jsonify({
        "status": "healthy" if is_healthy else "unhealthy", 
        "timestamp": time.time(), 
        "guardian_running": guardiao_singleton.rodando,
        "monitoring_thread_active": guardiao_singleton.thread_monitoramento.is_alive() if guardiao_singleton.thread_monitoramento else False,
        "kube_api_available": guardiao_singleton.kube_api_client is not None
    })

@app.route("/api/guardian/start", methods=["POST"])
def start_guardian():
    guardiao_singleton.iniciar()
    return flask.jsonify({"message": "Guardião Cognitivo iniciando..."})

@app.route("/api/guardian/stop", methods=["POST"])
def stop_guardian():
    guardiao_singleton.parar()
    return flask.jsonify({"message": "Guardião Cognitivo parando..."})

@app.route("/api/guardian/status", methods=["GET"])
def guardian_status():
    return flask.jsonify({
        "running": guardiao_singleton.rodando,
        "diagnostics_history_size": len(guardiao_singleton.historico_diagnosticos),
        "action_plans_history_size": len(guardiao_singleton.historico_planos_acao),
        "config": CONFIG_GUARDIAN
    })

@app.route("/event/new_diagnosis", methods=["POST"])
def new_diagnosis_event():
    data = flask.request.json
    try:
        diag_info = DiagnosticoInfo.from_dict(data)
        guardiao_singleton.registrar_novo_diagnostico(diag_info)
        return flask.jsonify({"message": "Diagnóstico recebido"}), 201
    except KeyError as e:
        logger.error(f"Campo ausente ao processar evento de novo diagnóstico: {e}")
        return flask.jsonify({"error": f"Campo ausente: {e}"}), 400
    except Exception as e:
        logger.error(f"Erro ao processar evento de novo diagnóstico: {e}", exc_info=True)
        return flask.jsonify({"error": str(e)}), 500

@app.route("/event/new_action_plan", methods=["POST"])
def new_action_plan_event():
    data = flask.request.json
    try:
        plan_info = PlanoAcaoInfo.from_dict(data)
        guardiao_singleton.registrar_novo_plano_acao(plan_info)
        return flask.jsonify({"message": "Plano de ação recebido"}), 201
    except KeyError as e:
        logger.error(f"Campo ausente ao processar evento de novo plano de ação: {e}")
        return flask.jsonify({"error": f"Campo ausente: {e}"}), 400
    except Exception as e:
        logger.error(f"Erro ao processar evento de novo plano de ação: {e}", exc_info=True)
        return flask.jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("Iniciando serviço Guardião Cognitivo autonomamente com API Flask.")
    if not CONFIG_GUARDIAN['api_diagnostico_url'].startswith("http") or not CONFIG_GUARDIAN['api_gerador_acoes_url'].startswith("http"):
        logger.warning("URLs dos serviços de Diagnóstico ou Gerador de Ações não parecem estar configuradas corretamente via variáveis de ambiente. Usando defaults.")
    
    guardiao_singleton.iniciar()
    app.run(host="0.0.0.0", port=8081, debug=False)

