import pytest
import redis
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def redis_client():
    return redis.Redis(host='localhost', port=6379, db=0)

@pytest.fixture
def gerenciador(redis_client):
    return GerenciadorMemoria(redis_client=redis_client)

def test_persistencia_redis(gerenciador, redis_client):
    """Testa a persistência de dados no Redis."""
    dados = {
        "estado_sistema": {
            "nivel_autonomia": 1,
            "status": "normal"
        },
        "metricas": {
            "cpu_uso": 60,
            "memoria_uso": 65
        }
    }
    gerenciador.salvar_memoria(dados)
    memoria_redis = redis_client.get("memoria")
    assert memoria_redis is not None
    assert "nivel_autonomia" in memoria_redis.decode()
    assert "cpu_uso" in memoria_redis.decode()

def test_carregar_redis(gerenciador, redis_client):
    """Testa o carregamento de dados do Redis."""
    dados = {
        "estado_sistema": {
            "nivel_autonomia": 1,
            "status": "normal"
        },
        "metricas": {
            "cpu_uso": 60,
            "memoria_uso": 65
        }
    }
    redis_client.set("memoria", str(dados))
    memoria_carregada = gerenciador.carregar_memoria()
    assert memoria_carregada["estado_sistema"]["nivel_autonomia"] == 1
    assert memoria_carregada["metricas"]["cpu_uso"] == 60 