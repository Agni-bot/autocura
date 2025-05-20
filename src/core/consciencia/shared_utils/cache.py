# src/conscienciaSituacional/shared_utils/cache.py
import redis
import json
import os
import functools
import hashlib

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

class RedisCache:
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT):
        if REDIS_ENABLED:
            try:
                self.client = redis.Redis(host=host, port=port, db=0, socket_connect_timeout=1)
                self.client.ping() # Verificar conexão
                print(f"Cache Redis conectado em {host}:{port}")
                self.enabled = True
            except redis.exceptions.ConnectionError as e:
                print(f"ERRO: Não foi possível conectar ao Redis em {host}:{port} - {e}. Cache desabilitado.")
                self.client = None
                self.enabled = False
        else:
            print("Cache Redis desabilitado via configuração.")
            self.client = None
            self.enabled = False

    def get(self, key):
        if not self.enabled or not self.client:
            return None
        try:
            cached_value = self.client.get(key)
            if cached_value:
                print(f"Cache HIT para a chave: {key}")
                return json.loads(cached_value.decode("utf-8"))
            print(f"Cache MISS para a chave: {key}")
            return None
        except redis.exceptions.RedisError as e:
            print(f"Erro no Redis ao buscar chave {key}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON do cache para chave {key}: {e}")
            return None # Dado corrompido, tratar como miss

    def set(self, key, value, ttl_seconds=3600):
        if not self.enabled or not self.client:
            return
        try:
            serialized_value = json.dumps(value)
            self.client.setex(key, ttl_seconds, serialized_value)
            print(f"Cache SET para a chave: {key} com TTL: {ttl_seconds}s")
        except redis.exceptions.RedisError as e:
            print(f"Erro no Redis ao definir chave {key}: {e}")
        except TypeError as e:
            print(f"Erro ao serializar valor para cache (chave {key}): {e}")

    def delete(self, key):
        if not self.enabled or not self.client:
            return
        try:
            self.client.delete(key)
            print(f"Cache DELETE para a chave: {key}")
        except redis.exceptions.RedisError as e:
            print(f"Erro no Redis ao deletar chave {key}: {e}")

# Instância global do cache para ser usada pelo decorador
# A inicialização real pode depender da configuração da aplicação (ex: dentro da classe ConscienciaSituacionalService)
# Por simplicidade, vamos instanciar aqui, mas isso pode ser problemático para testes unitários ou múltiplas instâncias.
# Uma melhor abordagem seria injetar a instância do cache.
global_redis_cache_instance = RedisCache()

def generate_cache_key(prefix: str, func_name: str, args, kwargs) -> str:
    """Gera uma chave de cache baseada no prefixo, nome da função e argumentos."""
    # Serializar args e kwargs de forma consistente
    # Usar hashlib para criar um hash dos argumentos se eles forem complexos ou longos
    arg_representation = f"{args}-{sorted(kwargs.items())}"
    arg_hash = hashlib.md5(arg_representation.encode("utf-8")).hexdigest()
    return f"{prefix}:{func_name}:{arg_hash}"

def cache(key_prefix: str = "cache", ttl_seconds: int = 3600):
    """
    Decorador de cache que usa a instância global do RedisCache.
    key_prefix: um prefixo para a chave de cache (ex: nome do módulo ou da função).
    ttl_seconds: tempo de vida para a entrada de cache em segundos.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not global_redis_cache_instance.enabled:
                return func(*args, **kwargs) # Cache desabilitado, chama a função diretamente

            cache_key = generate_cache_key(key_prefix, func.__name__, args, kwargs)
            
            cached_result = global_redis_cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Cache miss, executa a função
            result = func(*args, **kwargs)
            
            # Armazena o resultado no cache
            global_redis_cache_instance.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator

