"""Sistema de armazenamento do módulo core."""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .interfaces import StorageInterface
from .config.config import config
from .logging import logger

class Storage(StorageInterface):
    """Sistema de armazenamento persistente."""
    
    def __init__(self):
        """Inicializa o sistema de armazenamento."""
        self._storage: Dict[str, Any] = {}
        self._storage_type = config.STORAGE_TYPE
        self._initialized = False
        
    async def initialize(self) -> None:
        """Inicializa o sistema de armazenamento."""
        if self._initialized:
            return
            
        if self._storage_type == "file":
            await self._load_from_file()
        elif self._storage_type == "redis":
            await self._init_redis()
        elif self._storage_type == "postgres":
            await self._init_postgres()
            
        self._initialized = True
        await logger.log("INFO", f"Sistema de armazenamento inicializado: {self._storage_type}")
        
    async def shutdown(self) -> None:
        """Desliga o sistema de armazenamento."""
        if not self._initialized:
            return
            
        if self._storage_type == "file":
            await self._save_to_file()
        elif self._storage_type == "redis":
            await self._close_redis()
        elif self._storage_type == "postgres":
            await self._close_postgres()
            
        self._initialized = False
        await logger.log("INFO", "Sistema de armazenamento desligado")
        
    async def store(self, key: str, value: Any) -> None:
        """Armazena um valor."""
        if not self._initialized:
            await logger.log("WARNING", "Tentativa de armazenar com sistema não inicializado")
            return
            
        # Adiciona metadados
        entry = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self._storage[key] = entry
        
        # Persiste mudanças
        if self._storage_type == "file":
            await self._save_to_file()
            
        await logger.log("DEBUG", f"Valor armazenado: {key}")
        
    async def retrieve(self, key: str) -> Any:
        """Recupera um valor."""
        if not self._initialized:
            await logger.log("WARNING", "Tentativa de recuperar com sistema não inicializado")
            return None
            
        entry = self._storage.get(key)
        if entry:
            # Atualiza timestamp de acesso
            entry["updated_at"] = datetime.now().isoformat()
            return entry["value"]
        return None
        
    async def delete(self, key: str) -> None:
        """Remove um valor."""
        if not self._initialized:
            await logger.log("WARNING", "Tentativa de deletar com sistema não inicializado")
            return
            
        if key in self._storage:
            del self._storage[key]
            
            # Persiste mudanças
            if self._storage_type == "file":
                await self._save_to_file()
                
            await logger.log("DEBUG", f"Valor removido: {key}")
            
    async def list_keys(self, pattern: str) -> List[str]:
        """Lista chaves que correspondem a um padrão."""
        if not self._initialized:
            await logger.log("WARNING", "Tentativa de listar com sistema não inicializado")
            return []
            
        import re
        regex = re.compile(pattern)
        return [k for k in self._storage.keys() if regex.match(k)]
        
    async def _load_from_file(self) -> None:
        """Carrega dados do arquivo."""
        try:
            if os.path.exists("storage.json"):
                with open("storage.json", "r") as f:
                    self._storage = json.load(f)
        except Exception as e:
            await logger.log("ERROR", f"Erro ao carregar arquivo de armazenamento: {e}")
            
    async def _save_to_file(self) -> None:
        """Salva dados no arquivo."""
        try:
            with open("storage.json", "w") as f:
                json.dump(self._storage, f)
        except Exception as e:
            await logger.log("ERROR", f"Erro ao salvar arquivo de armazenamento: {e}")
            
    async def _init_redis(self) -> None:
        """Inicializa conexão com Redis."""
        try:
            import redis
            self._redis = redis.Redis(
                host=config.STORAGE_HOST,
                port=config.STORAGE_PORT,
                db=config.STORAGE_DB,
                password=config.STORAGE_PASSWORD
            )
        except Exception as e:
            await logger.log("ERROR", f"Erro ao conectar com Redis: {e}")
            raise
            
    async def _close_redis(self) -> None:
        """Fecha conexão com Redis."""
        if hasattr(self, "_redis"):
            self._redis.close()
            
    async def _init_postgres(self) -> None:
        """Inicializa conexão com PostgreSQL."""
        try:
            import asyncpg
            self._pool = await asyncpg.create_pool(
                host=config.STORAGE_HOST,
                port=config.STORAGE_PORT,
                user=config.STORAGE_USER,
                password=config.STORAGE_PASSWORD,
                database=config.STORAGE_DB
            )
        except Exception as e:
            await logger.log("ERROR", f"Erro ao conectar com PostgreSQL: {e}")
            raise
            
    async def _close_postgres(self) -> None:
        """Fecha conexão com PostgreSQL."""
        if hasattr(self, "_pool"):
            await self._pool.close()

# Instância global do sistema de armazenamento
storage = Storage() 