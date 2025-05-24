import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class Severidade(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Notificacao:
    titulo: str
    mensagem: str
    severidade: Severidade
    categoria: str
    metricas: Dict[str, float]
    timestamp: str

class NotificadorEtico:
    def __init__(self, config_path: str = "config/notificacoes.json"):
        self.logger = logging.getLogger("ethical_notifier")
        self.config = self._carregar_config(config_path)
        self._configurar_logging()
        
    def _carregar_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
            return self._config_padrao()
            
    def _config_padrao(self) -> Dict:
        return {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_emails": []
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",
                "channel": "#ethical-alerts"
            },
            "telegram": {
                "enabled": False,
                "bot_token": "",
                "chat_id": ""
            }
        }
        
    def _configurar_logging(self):
        handler = logging.FileHandler("logs/ethical_notifications.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
    def enviar_notificacao(self, notificacao: Notificacao) -> bool:
        """Envia notificação através de todos os canais configurados"""
        sucesso = True
        
        if self.config["email"]["enabled"]:
            sucesso &= self._enviar_email(notificacao)
            
        if self.config["slack"]["enabled"]:
            sucesso &= self._enviar_slack(notificacao)
            
        if self.config["telegram"]["enabled"]:
            sucesso &= self._enviar_telegram(notificacao)
            
        return sucesso
        
    def _enviar_email(self, notificacao: Notificacao) -> bool:
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]["from_email"]
            msg['To'] = ", ".join(self.config["email"]["to_emails"])
            msg['Subject'] = f"[{notificacao.severidade.value.upper()}] {notificacao.titulo}"
            
            corpo = f"""
            Categoria: {notificacao.categoria}
            Severidade: {notificacao.severidade.value}
            Timestamp: {notificacao.timestamp}
            
            {notificacao.mensagem}
            
            Métricas:
            {json.dumps(notificacao.metricas, indent=2)}
            """
            
            msg.attach(MIMEText(corpo, 'plain'))
            
            with smtplib.SMTP(self.config["email"]["smtp_server"], 
                            self.config["email"]["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["email"]["username"],
                           self.config["email"]["password"])
                server.send_message(msg)
                
            self.logger.info(f"Email enviado com sucesso: {notificacao.titulo}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {str(e)}")
            return False
            
    def _enviar_slack(self, notificacao: Notificacao) -> bool:
        try:
            payload = {
                "channel": self.config["slack"]["channel"],
                "text": f"*[{notificacao.severidade.value.upper()}] {notificacao.titulo}*\n"
                       f"*Categoria:* {notificacao.categoria}\n"
                       f"*Timestamp:* {notificacao.timestamp}\n\n"
                       f"{notificacao.mensagem}\n\n"
                       f"*Métricas:*\n```{json.dumps(notificacao.metricas, indent=2)}```"
            }
            
            response = requests.post(
                self.config["slack"]["webhook_url"],
                json=payload
            )
            
            if response.status_code == 200:
                self.logger.info(f"Slack enviado com sucesso: {notificacao.titulo}")
                return True
            else:
                self.logger.error(f"Erro ao enviar Slack: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao enviar Slack: {str(e)}")
            return False
            
    def _enviar_telegram(self, notificacao: Notificacao) -> bool:
        try:
            mensagem = (
                f"*[{notificacao.severidade.value.upper()}] {notificacao.titulo}*\n"
                f"*Categoria:* {notificacao.categoria}\n"
                f"*Timestamp:* {notificacao.timestamp}\n\n"
                f"{notificacao.mensagem}\n\n"
                f"*Métricas:*\n```{json.dumps(notificacao.metricas, indent=2)}```"
            )
            
            url = f"https://api.telegram.org/bot{self.config['telegram']['bot_token']}/sendMessage"
            payload = {
                "chat_id": self.config["telegram"]["chat_id"],
                "text": mensagem,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                self.logger.info(f"Telegram enviado com sucesso: {notificacao.titulo}")
                return True
            else:
                self.logger.error(f"Erro ao enviar Telegram: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao enviar Telegram: {str(e)}")
            return False
            
    def notificar_violacao_etica(self, categoria: str, mensagem: str, 
                                metricas: Dict[str, float], severidade: Severidade = Severidade.WARNING) -> bool:
        """Notifica sobre uma violação ética detectada"""
        notificacao = Notificacao(
            titulo="Violação Ética Detectada",
            mensagem=mensagem,
            severidade=severidade,
            categoria=categoria,
            metricas=metricas,
            timestamp=datetime.now().isoformat()
        )
        
        return self.enviar_notificacao(notificacao)
        
    def notificar_indice_baixo(self, categoria: str, indice: float, 
                              limite: float, metricas: Dict[str, float]) -> bool:
        """Notifica quando um índice ético está abaixo do limite"""
        notificacao = Notificacao(
            titulo=f"Índice {categoria} Abaixo do Limite",
            mensagem=f"O índice {categoria} está em {indice:.2f}, abaixo do limite de {limite:.2f}",
            severidade=Severidade.WARNING,
            categoria=categoria,
            metricas=metricas,
            timestamp=datetime.now().isoformat()
        )
        
        return self.enviar_notificacao(notificacao)
        
    def notificar_tempo_resposta(self, categoria: str, tempo: float, 
                                limite: float, metricas: Dict[str, float]) -> bool:
        """Notifica quando o tempo de resposta excede o limite"""
        notificacao = Notificacao(
            titulo="Tempo de Resposta Excedido",
            mensagem=f"O tempo de resposta para {categoria} está em {tempo:.2f}s, "
                    f"acima do limite de {limite:.2f}s",
            severidade=Severidade.WARNING,
            categoria=categoria,
            metricas=metricas,
            timestamp=datetime.now().isoformat()
        )
        
        return self.enviar_notificacao(notificacao)
        
    def notificar_dados_sensiveis(self, categoria: str, tamanho: int, 
                                 limite: int, metricas: Dict[str, float]) -> bool:
        """Notifica quando o volume de dados sensíveis excede o limite"""
        notificacao = Notificacao(
            titulo="Volume de Dados Sensíveis Excedido",
            mensagem=f"O volume de dados sensíveis para {categoria} está em {tamanho} bytes, "
                    f"acima do limite de {limite} bytes",
            severidade=Severidade.WARNING,
            categoria=categoria,
            metricas=metricas,
            timestamp=datetime.now().isoformat()
        )
        
        return self.enviar_notificacao(notificacao) 