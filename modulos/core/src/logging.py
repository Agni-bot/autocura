"""Sistema de logging do core."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from .interfaces import LoggingInterface

class StructuredLogger(LoggingInterface):
    """Implementação do sistema de logging estruturado."""
    
    def __init__(self, log_file: str = "logs/app.log",
                 log_format: str = "json",
                 log_level: str = "INFO"):
        self.log_file = log_file
        self.log_format = log_format
        self.log_level = getattr(logging, log_level.upper())
        
        # Configura o logger
        self.logger = logging.getLogger("core")
        self.logger.setLevel(self.log_level)
        
        # Cria diretório de logs se não existir
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configura handler de arquivo
        file_handler = logging.FileHandler(log_file)
        if log_format == "json":
            file_handler.setFormatter(JsonFormatter())
        else:
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
        self.logger.addHandler(file_handler)
        
        # Configura handler de console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(console_handler)
        
        self._logs: List[Dict[str, Any]] = []
        self._max_logs = 1000
    
    async def log(self, level: str, message: str, **kwargs) -> None:
        """Registra uma mensagem de log."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level.upper(),
            'message': message,
            **kwargs
        }
        
        # Adiciona ao histórico em memória
        self._logs.append(log_entry)
        if len(self._logs) > self._max_logs:
            self._logs = self._logs[-self._max_logs:]
        
        # Registra no logger
        log_method = getattr(self.logger, level.lower())
        if self.log_format == "json":
            log_method(json.dumps(log_entry))
        else:
            log_method(message, extra=kwargs)
    
    async def get_logs(self, level: Optional[str] = None,
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recupera logs com filtros opcionais."""
        filtered_logs = self._logs
        
        if level:
            filtered_logs = [log for log in filtered_logs 
                           if log['level'] == level.upper()]
        
        if start_time:
            filtered_logs = [log for log in filtered_logs 
                           if log['timestamp'] >= start_time]
        
        if end_time:
            filtered_logs = [log for log in filtered_logs 
                           if log['timestamp'] <= end_time]
        
        return filtered_logs
    
    def clear_logs(self) -> None:
        """Limpa o histórico de logs em memória."""
        self._logs.clear()

class JsonFormatter(logging.Formatter):
    """Formatador de logs em JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o registro de log em JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adiciona campos extras
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data) 