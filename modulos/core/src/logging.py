"""Sistema de logging do módulo core."""

import json
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .interfaces import LoggingInterface
from .config.config import config

class JsonFormatter(logging.Formatter):
    """Formatador de logs em JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata um registro de log em JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adiciona campos extras
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        # Adiciona exceção se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

class StructuredLogger(LoggingInterface):
    """Logger estruturado com suporte a JSON."""
    
    def __init__(self, name: str):
        """Inicializa o logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Configura handlers
        self._setup_handlers()
        
        # Armazena logs em memória
        self._logs: List[Dict[str, Any]] = []
        
    def _setup_handlers(self) -> None:
        """Configura os handlers do logger."""
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(console_handler)
        
        # Handler para arquivo
        os.makedirs(os.path.dirname(config.LOG_FILE_PATH), exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            config.LOG_FILE_PATH,
            maxBytes=config.LOG_MAX_SIZE,
            backupCount=config.LOG_BACKUP_COUNT
        )
        file_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(file_handler)
        
    async def log(self, level: str, message: str, **kwargs) -> None:
        """Registra uma mensagem de log."""
        log_entry = {
            "level": level,
            "message": message,
            "timestamp": datetime.now(),
            **kwargs
        }
        
        # Adiciona ao armazenamento em memória
        self._logs.append(log_entry)
        
        # Registra no logger
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=kwargs)
        
    async def get_logs(self, level: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Recupera logs com filtros opcionais."""
        filtered_logs = self._logs
        
        if level:
            filtered_logs = [log for log in filtered_logs if log["level"] == level]
            
        if start_time:
            filtered_logs = [log for log in filtered_logs 
                           if log["timestamp"] >= start_time]
            
        if end_time:
            filtered_logs = [log for log in filtered_logs 
                           if log["timestamp"] <= end_time]
            
        return filtered_logs
        
    async def clear_logs(self) -> None:
        """Limpa os logs armazenados em memória."""
        self._logs.clear()
        
    def get_logger(self) -> logging.Logger:
        """Retorna o logger subjacente."""
        return self.logger

# Instância global do logger
logger = StructuredLogger("core") 