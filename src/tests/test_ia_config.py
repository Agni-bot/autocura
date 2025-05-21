"""
Testes para a configuração da API de IA
"""
import pytest
from src.config.ia_config import IAConfig
import os

def test_configuracao_basica():
    """Testa se as configurações básicas estão sendo carregadas corretamente."""
    # Simula variáveis de ambiente
    os.environ["AI_API_KEY"] = "chave-teste"
    os.environ["AI_API_ENDPOINT"] = "https://api.teste.com/v1"
    
    config = IAConfig()
    
    assert config.API_KEY == "chave-teste"
    assert config.API_ENDPOINT == "https://api.teste.com/v1"
    assert config.validate() is True

def test_configuracao_sem_chave():
    """Testa se a validação falha quando não há chave de API."""
    if "AI_API_KEY" in os.environ:
        del os.environ["AI_API_KEY"]
    
    config = IAConfig()
    
    with pytest.raises(ValueError, match="AI_API_KEY não configurada"):
        config.validate()

def test_configuracoes_avancadas():
    """Testa se as configurações avançadas estão com valores corretos."""
    config = IAConfig()
    
    assert isinstance(config.RATE_LIMIT_CALLS, int)
    assert isinstance(config.CACHE_TTL, int)
    assert isinstance(config.ETHICAL_MIN_CONFIDENCE, float)
    assert isinstance(config.TEMPERATURE, float)
    
    assert 0 <= config.ETHICAL_MIN_CONFIDENCE <= 1
    assert 0 <= config.TEMPERATURE <= 1

def test_configuracoes_seguranca():
    """Testa as configurações de segurança."""
    os.environ["AI_API_SSL_VERIFY"] = "true"
    os.environ["AI_API_ENCRYPT_PAYLOAD"] = "true"
    
    config = IAConfig()
    
    assert config.SSL_VERIFY is True
    assert config.ENCRYPT_PAYLOAD is True 