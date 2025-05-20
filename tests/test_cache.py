import pytest
from src.cache.redis_cache import CacheDistribuido
import time

@pytest.fixture
def cache():
    """Fixture que fornece uma instância do cache para os testes."""
    return CacheDistribuido(use_cluster=False)

def test_set_get(cache):
    """Testa operações básicas de set e get."""
    # Teste com string
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"
    
    # Teste com dicionário
    test_dict = {"key": "value", "number": 42}
    cache.set("test_dict", test_dict)
    assert cache.get("test_dict") == test_dict
    
    # Teste com lista
    test_list = [1, 2, 3, 4, 5]
    cache.set("test_list", test_list)
    assert cache.get("test_list") == test_list

def test_ttl(cache):
    """Testa o funcionamento do TTL (Time To Live)."""
    cache.set("ttl_key", "ttl_value", ttl=1)
    assert cache.get("ttl_key") == "ttl_value"
    time.sleep(2)
    assert cache.get("ttl_key") is None

def test_delete(cache):
    """Testa a operação de delete."""
    cache.set("delete_key", "delete_value")
    assert cache.exists("delete_key")
    cache.delete("delete_key")
    assert not cache.exists("delete_key")

def test_exists(cache):
    """Testa a verificação de existência de chaves."""
    assert not cache.exists("non_existent_key")
    cache.set("existent_key", "value")
    assert cache.exists("existent_key")

def test_clear(cache):
    """Testa a limpeza do cache."""
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert cache.exists("key1")
    assert cache.exists("key2")
    cache.clear()
    assert not cache.exists("key1")
    assert not cache.exists("key2")

def test_error_handling(cache):
    """Testa o tratamento de erros."""
    # Teste com valor inválido
    with pytest.raises(Exception):
        cache.set("error_key", object())  # Objeto não serializável
    
    # Teste com chave inválida
    assert cache.get(None) is None
    assert cache.delete(None) is False 