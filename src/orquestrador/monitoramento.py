"""
Módulo de monitoramento para o sistema de testes.

Este módulo implementa a integração com ferramentas de monitoramento
como Prometheus, Grafana e ELK Stack.
"""

import os
import yaml
import logging
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from prometheus_client import start_http_server, Counter, Gauge, Histogram, CollectorRegistry
from elasticsearch import Elasticsearch
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitoramentoTestes:
    def __init__(self, config_path: Optional[str] = None, registry: Optional[CollectorRegistry] = None):
        """
        Inicializa o sistema de monitoramento.
        
        Args:
            config_path: Caminho para o arquivo de configuração
            registry: CollectorRegistry customizado para Prometheus (usado em testes)
        """
        self.config = self._carregar_configuracao(config_path)
        self._registry = registry
        self._inicializar_prometheus()
        self._inicializar_elasticsearch()
        self._inicializar_slack()
        
    def _carregar_configuracao(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Carrega as configurações do arquivo YAML.
        
        Args:
            config_path: Caminho para o arquivo de configuração
            
        Returns:
            Dict[str, Any]: Configurações carregadas
        """
        if config_path is None:
            config_path = Path(__file__).parent / "config_monitoramento.yaml"
            
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {str(e)}")
            return {}
            
    def _inicializar_prometheus(self) -> None:
        """Inicializa o servidor Prometheus."""
        if not self.config.get("prometheus", {}).get("habilitado", False):
            return
            
        prom_config = self.config["prometheus"]
        registry = self._registry
        
        # Inicializa métricas
        self.metricas = {
            "testes_executados": Counter(
                f"{prom_config['prefixo_metricas']}executados_total",
                "Total de testes executados",
                registry=registry
            ),
            "testes_falhas": Counter(
                f"{prom_config['prefixo_metricas']}falhas_total",
                "Total de falhas em testes",
                registry=registry
            ),
            "duracao_testes": Histogram(
                f"{prom_config['prefixo_metricas']}duracao_segundos",
                "Duração dos testes em segundos",
                registry=registry
            ),
            "cobertura_codigo": Gauge(
                f"{prom_config['prefixo_metricas']}cobertura_percentual",
                "Cobertura de código em percentual",
                registry=registry
            )
        }
        
        # Inicia servidor apenas se não for um registry customizado (evita conflito em testes)
        if registry is None:
            start_http_server(
                prom_config.get("porta", 9090),
                addr=prom_config.get("host", "localhost")
            )
        
    def _inicializar_elasticsearch(self) -> None:
        """Inicializa o cliente Elasticsearch."""
        if not self.config.get("elk", {}).get("habilitado", False):
            return
            
        elk_config = self.config["elk"]
        es_config = elk_config["elasticsearch"]
        
        self.es = Elasticsearch(
            f"http://{es_config['host']}:{es_config['porta']}"
        )
        
    def _inicializar_slack(self) -> None:
        """Inicializa o cliente Slack."""
        if not self.config.get("alertas", {}).get("slack", {}).get("webhook_url"):
            return
            
        self.slack = WebClient(
            token=os.getenv("SLACK_API_TOKEN", "")
        )
        
    def registrar_execucao_teste(self, nome: str, sucesso: bool, duracao: float) -> None:
        """
        Registra a execução de um teste.
        
        Args:
            nome: Nome do teste
            sucesso: Se o teste passou
            duracao: Duração em segundos
        """
        # Prometheus
        if hasattr(self, "metricas"):
            self.metricas["testes_executados"].inc()
            self.metricas["duracao_testes"].observe(duracao)
            
            if not sucesso:
                self.metricas["testes_falhas"].inc()
                
        # Elasticsearch
        if hasattr(self, "es"):
            doc = {
                "timestamp": datetime.now().isoformat(),
                "nome": nome,
                "sucesso": sucesso,
                "duracao": duracao
            }
            
            self.es.index(
                index=f"{self.config['elk']['elasticsearch']['indice_prefixo']}{datetime.now().strftime('%Y.%m.%d')}",
                document=doc
            )
            
    def atualizar_cobertura(self, percentual: float) -> None:
        """
        Atualiza a métrica de cobertura de código.
        
        Args:
            percentual: Percentual de cobertura
        """
        if hasattr(self, "metricas"):
            self.metricas["cobertura_codigo"].set(percentual)
            
    def enviar_alerta(self, tipo: str, mensagem: str, severidade: str = "info") -> None:
        """
        Envia alertas via email e Slack.
        
        Args:
            tipo: Tipo do alerta
            mensagem: Mensagem do alerta
            severidade: Severidade (info, warning, critical)
        """
        # Email
        if self.config.get("alertas", {}).get("email", {}).get("smtp", {}).get("servidor"):
            self._enviar_alerta_email(tipo, mensagem, severidade)
            
        # Slack
        if hasattr(self, "slack"):
            self._enviar_alerta_slack(tipo, mensagem, severidade)
            
    def _enviar_alerta_email(self, tipo: str, mensagem: str, severidade: str) -> None:
        """
        Envia alerta por email.
        
        Args:
            tipo: Tipo do alerta
            mensagem: Mensagem do alerta
            severidade: Severidade do alerta
        """
        email_config = self.config["alertas"]["email"]
        smtp_config = email_config["smtp"]
        
        msg = MIMEMultipart()
        msg["Subject"] = f"[{severidade.upper()}] {tipo}"
        msg["From"] = smtp_config["usuario"]
        msg["To"] = ", ".join(email_config["destinatarios"])
        
        msg.attach(MIMEText(mensagem, "plain"))
        
        try:
            with smtplib.SMTP(smtp_config["servidor"], smtp_config["porta"]) as server:
                server.starttls()
                server.login(smtp_config["usuario"], smtp_config["senha"])
                server.send_message(msg)
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            
    def _enviar_alerta_slack(self, tipo: str, mensagem: str, severidade: str) -> None:
        """
        Envia alerta via Slack.
        
        Args:
            tipo: Tipo do alerta
            mensagem: Mensagem do alerta
            severidade: Severidade do alerta
        """
        slack_config = self.config["alertas"]["slack"]
        icone = slack_config["icones"].get(severidade, ":information_source:")
        
        try:
            self.slack.chat_postMessage(
                channel=slack_config["canal"],
                text=f"{icone} *{tipo}*\n{mensagem}"
            )
        except SlackApiError as e:
            logger.error(f"Erro ao enviar mensagem Slack: {str(e)}")
            
    def verificar_alertas(self) -> None:
        """Verifica e dispara alertas baseados nas métricas."""
        if not hasattr(self, "metricas"):
            return
            
        # Verifica taxa de falhas
        falhas = self.metricas["testes_falhas"]._value.get()
        total = self.metricas["testes_executados"]._value.get()
        
        if total > 0 and falhas / total > 0.1:
            self.enviar_alerta(
                "Alta Taxa de Falhas",
                f"Taxa de falhas: {falhas/total:.1%}",
                "critical"
            )
            
        # Verifica cobertura
        cobertura = self.metricas["cobertura_codigo"]._value.get()
        if cobertura < 80:
            self.enviar_alerta(
                "Baixa Cobertura",
                f"Cobertura atual: {cobertura:.1f}%",
                "warning"
            ) 