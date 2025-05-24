import pytest
import os
import json
from typing import Dict
from ..src.crypto.quantum_safe import QuantumSafeCrypto

@pytest.fixture
def crypto(tmp_path):
    """Fixture que cria uma instância de criptografia com diretório temporário."""
    config_path = os.path.join(tmp_path, "config", "security_config.json")
    return QuantumSafeCrypto(config_path=config_path)

def test_crypto_initialization(crypto):
    """Testa inicialização do módulo de criptografia."""
    assert isinstance(crypto.config, dict)
    assert "algorithms" in crypto.config
    assert "key_sizes" in crypto.config
    assert "hybrid_mode" in crypto.config
    assert "rotation_interval" in crypto.config

def test_load_config(crypto):
    """Testa carregamento de configuração."""
    config = crypto._load_config()
    assert isinstance(config, dict)
    assert config["algorithms"]["key_exchange"] == "CRYSTALS-Kyber"
    assert config["algorithms"]["signature"] == "CRYSTALS-Dilithium"
    assert config["algorithms"]["encryption"] == "CRYSTALS-Kyber"

def test_create_default_config(crypto):
    """Testa criação de configuração padrão."""
    config = crypto._create_default_config()
    assert isinstance(config, dict)
    assert config["key_sizes"]["CRYSTALS-Kyber"] == 2048
    assert config["key_sizes"]["CRYSTALS-Dilithium"] == 2048
    assert config["hybrid_mode"] is True
    assert config["rotation_interval"] == 86400

def test_generate_key_pair(crypto):
    """Testa geração de par de chaves."""
    public_key, private_key = crypto.generate_key_pair()
    assert isinstance(public_key, bytes)
    assert isinstance(private_key, bytes)
    assert len(public_key) > 0
    assert len(private_key) > 0

def test_encrypt_decrypt(crypto):
    """Testa criptografia e descriptografia."""
    # Gera par de chaves
    public_key, private_key = crypto.generate_key_pair()
    
    # Dados de teste
    test_data = b"Teste de criptografia quantum-safe"
    
    # Criptografa
    encrypted = crypto.encrypt(test_data, public_key)
    assert isinstance(encrypted, bytes)
    assert len(encrypted) > 0
    
    # Descriptografa
    decrypted = crypto.decrypt(encrypted, private_key)
    assert isinstance(decrypted, bytes)
    assert decrypted == test_data

def test_sign_verify(crypto):
    """Testa assinatura e verificação."""
    # Gera par de chaves
    public_key, private_key = crypto.generate_key_pair()
    
    # Dados de teste
    test_data = b"Teste de assinatura quantum-safe"
    
    # Assina
    signature = crypto.sign(test_data, private_key)
    assert isinstance(signature, bytes)
    assert len(signature) > 0
    
    # Verifica
    is_valid = crypto.verify(test_data, signature, public_key)
    assert is_valid is True
    
    # Testa verificação com dados modificados
    modified_data = b"Dados modificados"
    is_valid = crypto.verify(modified_data, signature, public_key)
    assert is_valid is False 