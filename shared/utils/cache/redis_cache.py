from typing import Any, Optional
import redis
from redis.cluster import RedisCluster
import json
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class CacheDistribuido:
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 6379,
                 password: Optional[str] = None,
                 use_cluster: bool = True):
        """
        Inicializa o cache distribuído usando Redis.
        
        Args:
            host: Host do Redis
            port: Porta do Redis
            password: Senha do Redis (opcional)
            use_cluster: Se deve usar Redis Cluster
        """
        try:
            if use_cluster:
                self.client = RedisCluster(
                    host=host,
                    port=port,
                    password=password,
                    decode_responses=True
                )
            else:
                self.client = redis.Redis(
                    host=host,
                    port=port,
                    password=password,
                    decode_responses=True
                )
            logger.info("Cache distribuído inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar cache distribuído: {str(e)}")
            raise

    def set(self, 
            key: str, 
            value: Any, 
            ttl: Optional[int] = None) -> bool:
        """
        Armazena um valor no cache.
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos (opcional)
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            serialized_value = json.dumps(value)
            if ttl:
                return self.client.setex(key, ttl, serialized_value)
            return self.client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Erro ao armazenar no cache: {str(e)}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Recupera um valor do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor armazenado ou None se não encontrado
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar do cache: {str(e)}")
            return None

    def delete(self, key: str) -> bool:
        """
        Remove um valor do cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.error(f"Erro ao deletar do cache: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """
        Verifica se uma chave existe no cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            bool: True se existe, False caso contrário
        """
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Erro ao verificar existência no cache: {str(e)}")
            return False

    def clear(self) -> bool:
        """
        Limpa todo o cache.
        
        Returns:
            bool: True se sucesso, False caso contrário
        """
        try:
            return bool(self.client.flushdb())
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
            return False 