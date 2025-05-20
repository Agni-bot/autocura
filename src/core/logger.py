import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import threading
import time
import os
import sys

class Logger:
    """Sistema de logs"""
    
    def __init__(self, config_path: str = "config/logger.json"):
        self.config = self._carregar_config(config_path)
        self.loggers: Dict[str, logging.Logger] = {}
        self.lock = threading.Lock()
        self._configurar_logging()
        logger = logging.getLogger("logger")
        logger.info("Sistema de Logs inicializado")
    
    def _carregar_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega a configuração do logger"""
        try:
            caminho_config = Path(config_path)
            if caminho_config.exists():
                with open(caminho_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print("Arquivo de configuração não encontrado. Usando configuração padrão.")
                return self._criar_config_padrao()
        except Exception as e:
            print(f"Erro ao carregar configuração: {str(e)}")
            return self._criar_config_padrao()
    
    def _criar_config_padrao(self) -> Dict[str, Any]:
        """Cria configuração padrão do logger"""
        return {
            "configuracoes": {
                "nivel_padrao": "INFO",
                "formato": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "data_format": "%Y-%m-%d %H:%M:%S",
                "max_bytes": 10485760,
                "backup_count": 5
            },
            "handlers": {
                "console": {
                    "nivel": "INFO",
                    "formato": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "arquivo": {
                    "nivel": "DEBUG",
                    "formato": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "caminho": "logs",
                    "prefixo": "autocura"
                }
            },
            "loggers": {
                "sistema": {
                    "nivel": "INFO",
                    "handlers": ["console", "arquivo"]
                },
                "metricas": {
                    "nivel": "DEBUG",
                    "handlers": ["arquivo"]
                },
                "diagnostico": {
                    "nivel": "INFO",
                    "handlers": ["console", "arquivo"]
                },
                "cache": {
                    "nivel": "DEBUG",
                    "handlers": ["arquivo"]
                }
            }
        }
    
    def _configurar_logging(self) -> None:
        """Configura o sistema de logging"""
        try:
            # Cria diretório de logs se não existir
            caminho_logs = Path(self.config["handlers"]["arquivo"]["caminho"])
            caminho_logs.mkdir(parents=True, exist_ok=True)
            
            # Configura logging básico
            logging.basicConfig(
                level=getattr(logging, self.config["configuracoes"]["nivel_padrao"]),
                format=self.config["configuracoes"]["formato"],
                datefmt=self.config["configuracoes"]["data_format"]
            )
            
            # Configura handlers
            self._configurar_handlers()
            
            # Configura loggers
            self._configurar_loggers()
            
        except Exception as e:
            print(f"Erro ao configurar logging: {str(e)}")
            sys.exit(1)
    
    def _configurar_handlers(self) -> None:
        """Configura os handlers de logging"""
        try:
            # Handler Console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.config["handlers"]["console"]["nivel"]))
            console_handler.setFormatter(logging.Formatter(self.config["handlers"]["console"]["formato"]))
            
            # Handler Arquivo
            arquivo_handler = logging.handlers.RotatingFileHandler(
                filename=os.path.join(
                    self.config["handlers"]["arquivo"]["caminho"],
                    f"{self.config['handlers']['arquivo']['prefixo']}.log"
                ),
                maxBytes=self.config["configuracoes"]["max_bytes"],
                backupCount=self.config["configuracoes"]["backup_count"]
            )
            arquivo_handler.setLevel(getattr(logging, self.config["handlers"]["arquivo"]["nivel"]))
            arquivo_handler.setFormatter(logging.Formatter(self.config["handlers"]["arquivo"]["formato"]))
            
            # Registra handlers
            self.handlers = {
                "console": console_handler,
                "arquivo": arquivo_handler
            }
            
        except Exception as e:
            print(f"Erro ao configurar handlers: {str(e)}")
            raise
    
    def _configurar_loggers(self) -> None:
        """Configura os loggers específicos"""
        try:
            for nome, config in self.config["loggers"].items():
                # Cria logger
                logger = logging.getLogger(nome)
                logger.setLevel(getattr(logging, config["nivel"]))
                
                # Remove handlers existentes
                for handler in logger.handlers[:]:
                    logger.removeHandler(handler)
                
                # Adiciona handlers configurados
                for handler_name in config["handlers"]:
                    logger.addHandler(self.handlers[handler_name])
                
                # Desabilita propagação para root logger
                logger.propagate = False
                
                # Registra logger
                self.loggers[nome] = logger
            
        except Exception as e:
            print(f"Erro ao configurar loggers: {str(e)}")
            raise
    
    def obter_logger(self, nome: str) -> logging.Logger:
        """Obtém um logger específico"""
        try:
            if nome in self.loggers:
                return self.loggers[nome]
            else:
                # Cria novo logger com configuração padrão
                logger = logging.getLogger(nome)
                logger.setLevel(getattr(logging, self.config["configuracoes"]["nivel_padrao"]))
                
                # Adiciona handlers padrão
                for handler in self.handlers.values():
                    logger.addHandler(handler)
                
                # Desabilita propagação
                logger.propagate = False
                
                # Registra logger
                self.loggers[nome] = logger
                return logger
            
        except Exception as e:
            print(f"Erro ao obter logger: {str(e)}")
            return logging.getLogger(nome)
    
    def registrar_evento(self, nome: str, nivel: str, mensagem: str, **kwargs) -> None:
        """Registra um evento no log"""
        try:
            logger = self.obter_logger(nome)
            nivel_log = getattr(logging, nivel.upper())
            
            # Adiciona timestamp
            kwargs["timestamp"] = datetime.now().isoformat()
            
            # Formata mensagem com kwargs
            mensagem_formatada = mensagem.format(**kwargs)
            
            # Registra log
            logger.log(nivel_log, mensagem_formatada)
            
        except Exception as e:
            print(f"Erro ao registrar evento: {str(e)}")
    
    def registrar_erro(self, nome: str, mensagem: str, erro: Exception, **kwargs) -> None:
        """Registra um erro no log"""
        try:
            logger = self.obter_logger(nome)
            
            # Adiciona informações do erro
            kwargs["erro"] = str(erro)
            kwargs["tipo_erro"] = type(erro).__name__
            
            # Registra erro
            logger.error(mensagem, exc_info=True, extra=kwargs)
            
        except Exception as e:
            print(f"Erro ao registrar erro: {str(e)}")
    
    def registrar_metricas(self, nome: str, metricas: Dict[str, Any]) -> None:
        """Registra métricas no log"""
        try:
            logger = self.obter_logger("metricas")
            
            # Formata métricas
            mensagem = f"Métricas {nome}: {json.dumps(metricas, indent=2)}"
            
            # Registra métricas
            logger.debug(mensagem)
            
        except Exception as e:
            print(f"Erro ao registrar métricas: {str(e)}")
    
    def registrar_diagnostico(self, nome: str, diagnostico: Dict[str, Any]) -> None:
        """Registra diagnóstico no log"""
        try:
            logger = self.obter_logger("diagnostico")
            
            # Formata diagnóstico
            mensagem = f"Diagnóstico {nome}: {json.dumps(diagnostico, indent=2)}"
            
            # Registra diagnóstico
            logger.info(mensagem)
            
        except Exception as e:
            print(f"Erro ao registrar diagnóstico: {str(e)}")
    
    def registrar_cache(self, nome: str, operacao: str, dados: Dict[str, Any]) -> None:
        """Registra operação de cache no log"""
        try:
            logger = self.obter_logger("cache")
            
            # Formata operação
            mensagem = f"Cache {nome} - {operacao}: {json.dumps(dados, indent=2)}"
            
            # Registra operação
            logger.debug(mensagem)
            
        except Exception as e:
            print(f"Erro ao registrar cache: {str(e)}")
    
    def obter_logs(self, nome: str, nivel: Optional[str] = None, 
                  inicio: Optional[datetime] = None, fim: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Obtém logs filtrados"""
        try:
            logger = self.obter_logger(nome)
            
            # Obtém caminho do arquivo de log
            caminho_log = os.path.join(
                self.config["handlers"]["arquivo"]["caminho"],
                f"{self.config['handlers']['arquivo']['prefixo']}.log"
            )
            
            logs = []
            with open(caminho_log, 'r', encoding='utf-8') as f:
                for linha in f:
                    try:
                        # Parse log
                        log = self._parse_log(linha)
                        
                        # Aplica filtros
                        if self._aplicar_filtros(log, nome, nivel, inicio, fim):
                            logs.append(log)
                            
                    except Exception:
                        continue
            
            return logs
            
        except Exception as e:
            print(f"Erro ao obter logs: {str(e)}")
            return []
    
    def _parse_log(self, linha: str) -> Dict[str, Any]:
        """Parse uma linha de log"""
        try:
            # Extrai campos do log
            campos = linha.split(" - ")
            
            # Parse timestamp
            timestamp = datetime.strptime(campos[0], self.config["configuracoes"]["data_format"])
            
            # Parse logger
            logger = campos[1]
            
            # Parse nível
            nivel = campos[2]
            
            # Parse mensagem
            mensagem = " - ".join(campos[3:])
            
            return {
                "timestamp": timestamp.isoformat(),
                "logger": logger,
                "nivel": nivel,
                "mensagem": mensagem.strip()
            }
            
        except Exception as e:
            print(f"Erro ao parse log: {str(e)}")
            raise
    
    def _aplicar_filtros(self, log: Dict[str, Any], nome: Optional[str] = None,
                        nivel: Optional[str] = None, inicio: Optional[datetime] = None,
                        fim: Optional[datetime] = None) -> bool:
        """Aplica filtros no log"""
        try:
            # Filtra por nome
            if nome and log["logger"] != nome:
                return False
            
            # Filtra por nível
            if nivel and log["nivel"] != nivel.upper():
                return False
            
            # Filtra por período
            timestamp = datetime.fromisoformat(log["timestamp"])
            if inicio and timestamp < inicio:
                return False
            if fim and timestamp > fim:
                return False
            
            return True
            
        except Exception as e:
            print(f"Erro ao aplicar filtros: {str(e)}")
            return False 