import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path
import threading
import time
import smtplib
import requests
import telegram
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..core.logger import Logger
from ..core.cache import Cache

class Notificador:
    """Sistema de notificações"""
    
    def __init__(self, logger: Logger, cache: Cache, config_path: str = "config/notificacoes.json"):
        self.logger = logger
        self.cache = cache
        self.config = self._carregar_config(config_path)
        self.lock = threading.Lock()
        self.thread_notificacao = None
        self.running = False
        self.logger.registrar_evento("notificador", "INFO", "Sistema de Notificações inicializado")
    
    def _carregar_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega a configuração do notificador"""
        try:
            caminho_config = Path(config_path)
            if caminho_config.exists():
                with open(caminho_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.registrar_evento("notificador", "WARNING", "Arquivo de configuração não encontrado. Usando configuração padrão.")
                return self._criar_config_padrao()
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao carregar configuração", e)
            return self._criar_config_padrao()
    
    def _criar_config_padrao(self) -> Dict[str, Any]:
        """Cria configuração padrão do notificador"""
        return {
            "configuracoes": {
                "intervalo_verificacao": 60,
                "max_notificacoes": 100,
                "cooldown": 300
            },
            "canais": {
                "email": {
                    "habilitado": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "usuario": "",
                    "senha": "",
                    "remetente": "",
                    "destinatarios": []
                },
                "slack": {
                    "habilitado": False,
                    "webhook_url": "",
                    "canal": "#alertas"
                },
                "telegram": {
                    "habilitado": False,
                    "token": "",
                    "chat_id": ""
                }
            },
            "niveis": {
                "info": {
                    "canais": ["email"],
                    "template": "INFO: {mensagem}"
                },
                "warning": {
                    "canais": ["email", "slack"],
                    "template": "⚠️ WARNING: {mensagem}"
                },
                "error": {
                    "canais": ["email", "slack", "telegram"],
                    "template": "🚨 ERROR: {mensagem}"
                }
            }
        }
    
    def iniciar(self) -> None:
        """Inicia o sistema de notificações"""
        try:
            if self.running:
                self.logger.registrar_evento("notificador", "WARNING", "Notificador já está em execução")
                return
            
            self.running = True
            self.thread_notificacao = threading.Thread(target=self._executar_notificacoes)
            self.thread_notificacao.start()
            
            self.logger.registrar_evento("notificador", "INFO", "Notificador iniciado com sucesso")
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao iniciar notificador", e)
            self.running = False
    
    def parar(self) -> None:
        """Para o sistema de notificações"""
        try:
            if not self.running:
                self.logger.registrar_evento("notificador", "WARNING", "Notificador não está em execução")
                return
            
            self.running = False
            if self.thread_notificacao:
                self.thread_notificacao.join()
            
            self.logger.registrar_evento("notificador", "INFO", "Notificador parado com sucesso")
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao parar notificador", e)
    
    def _executar_notificacoes(self) -> None:
        """Executa o processo de notificações"""
        try:
            while self.running:
                # Obtém alertas
                alertas = self.cache.obter("metricas", "ultimas").get("alertas", [])
                
                # Processa alertas
                for alerta in alertas:
                    self._processar_alerta(alerta)
                
                # Aguarda próximo ciclo
                time.sleep(self.config["configuracoes"]["intervalo_verificacao"])
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro no processo de notificações", e)
            self.running = False
    
    def _processar_alerta(self, alerta: Dict[str, Any]) -> None:
        """Processa um alerta e envia notificações"""
        try:
            # Verifica cooldown
            ultima_notificacao = self.cache.obter("notificacoes", f"ultima_{alerta['tipo']}")
            if ultima_notificacao:
                tempo_decorrido = (datetime.now() - datetime.fromisoformat(ultima_notificacao["timestamp"])).total_seconds()
                if tempo_decorrido < self.config["configuracoes"]["cooldown"]:
                    return
            
            # Determina nível
            nivel = self._determinar_nivel(alerta)
            
            # Obtém canais
            canais = self.config["niveis"][nivel]["canais"]
            
            # Prepara mensagem
            mensagem = self.config["niveis"][nivel]["template"].format(
                mensagem=alerta["mensagem"]
            )
            
            # Envia notificações
            for canal in canais:
                self._enviar_notificacao(canal, mensagem, alerta)
            
            # Registra notificação
            self._registrar_notificacao(alerta, nivel, mensagem)
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao processar alerta", e)
    
    def _determinar_nivel(self, alerta: Dict[str, Any]) -> str:
        """Determina o nível de um alerta"""
        try:
            # Obtém valor e limite
            valor = alerta["valor"]
            limite = alerta["limite"]
            
            # Calcula percentual
            percentual = (valor / limite) * 100
            
            # Determina nível
            if percentual >= 90:
                return "error"
            elif percentual >= 80:
                return "warning"
            else:
                return "info"
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao determinar nível", e)
            return "info"
    
    def _enviar_notificacao(self, canal: str, mensagem: str, alerta: Dict[str, Any]) -> None:
        """Envia notificação por um canal específico"""
        try:
            if canal == "email":
                self._enviar_email(mensagem, alerta)
            elif canal == "slack":
                self._enviar_slack(mensagem, alerta)
            elif canal == "telegram":
                self._enviar_telegram(mensagem, alerta)
            
        except Exception as e:
            self.logger.registrar_erro("notificador", f"Erro ao enviar notificação por {canal}", e)
    
    def _enviar_email(self, mensagem: str, alerta: Dict[str, Any]) -> None:
        """Envia notificação por email"""
        try:
            config = self.config["canais"]["email"]
            if not config["habilitado"]:
                return
            
            # Prepara email
            msg = MIMEMultipart()
            msg["From"] = config["remetente"]
            msg["To"] = ", ".join(config["destinatarios"])
            msg["Subject"] = f"Alerta: {alerta['tipo']}"
            
            # Adiciona corpo
            corpo = f"""
            {mensagem}
            
            Detalhes:
            - Tipo: {alerta['tipo']}
            - Métrica: {alerta['metrica']}
            - Valor: {alerta['valor']}
            - Limite: {alerta['limite']}
            - Timestamp: {datetime.now().isoformat()}
            """
            msg.attach(MIMEText(corpo, "plain"))
            
            # Envia email
            with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
                server.starttls()
                server.login(config["usuario"], config["senha"])
                server.send_message(msg)
            
            self.logger.registrar_evento("notificador", "INFO", f"Email enviado para {config['destinatarios']}")
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao enviar email", e)
    
    def _enviar_slack(self, mensagem: str, alerta: Dict[str, Any]) -> None:
        """Envia notificação para Slack"""
        try:
            config = self.config["canais"]["slack"]
            if not config["habilitado"]:
                return
            
            # Prepara payload
            payload = {
                "channel": config["canal"],
                "text": mensagem,
                "attachments": [{
                    "color": "danger" if alerta["valor"] > alerta["limite"] else "warning",
                    "fields": [
                        {
                            "title": "Tipo",
                            "value": alerta["tipo"],
                            "short": True
                        },
                        {
                            "title": "Métrica",
                            "value": alerta["metrica"],
                            "short": True
                        },
                        {
                            "title": "Valor",
                            "value": str(alerta["valor"]),
                            "short": True
                        },
                        {
                            "title": "Limite",
                            "value": str(alerta["limite"]),
                            "short": True
                        }
                    ],
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            # Envia mensagem
            response = requests.post(config["webhook_url"], json=payload)
            response.raise_for_status()
            
            self.logger.registrar_evento("notificador", "INFO", f"Mensagem enviada para Slack {config['canal']}")
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao enviar mensagem para Slack", e)
    
    def _enviar_telegram(self, mensagem: str, alerta: Dict[str, Any]) -> None:
        """Envia notificação para Telegram"""
        try:
            config = self.config["canais"]["telegram"]
            if not config["habilitado"]:
                return
            
            # Prepara bot
            bot = telegram.Bot(token=config["token"])
            
            # Prepara mensagem
            texto = f"""
            {mensagem}
            
            Detalhes:
            - Tipo: {alerta['tipo']}
            - Métrica: {alerta['metrica']}
            - Valor: {alerta['valor']}
            - Limite: {alerta['limite']}
            - Timestamp: {datetime.now().isoformat()}
            """
            
            # Envia mensagem
            bot.send_message(chat_id=config["chat_id"], text=texto)
            
            self.logger.registrar_evento("notificador", "INFO", f"Mensagem enviada para Telegram {config['chat_id']}")
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao enviar mensagem para Telegram", e)
    
    def _registrar_notificacao(self, alerta: Dict[str, Any], nivel: str, mensagem: str) -> None:
        """Registra uma notificação enviada"""
        try:
            # Prepara dados
            dados = {
                "timestamp": datetime.now().isoformat(),
                "alerta": alerta,
                "nivel": nivel,
                "mensagem": mensagem
            }
            
            # Registra no cache
            self.cache.definir("notificacoes", f"ultima_{alerta['tipo']}", dados)
            
            # Registra no log
            self.logger.registrar_evento("notificador", "INFO", f"Notificação registrada: {mensagem}")
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao registrar notificação", e)
    
    def obter_notificacoes(self, tipo: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtém notificações registradas"""
        try:
            notificacoes = []
            
            # Obtém todas as notificações do cache
            for chave in self.cache.obter("notificacoes", "chaves") or []:
                if tipo and not chave.startswith(f"ultima_{tipo}"):
                    continue
                
                notificacao = self.cache.obter("notificacoes", chave)
                if notificacao:
                    notificacoes.append(notificacao)
            
            # Ordena por timestamp
            notificacoes.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return notificacoes
            
        except Exception as e:
            self.logger.registrar_erro("notificador", "Erro ao obter notificações", e)
            return [] 