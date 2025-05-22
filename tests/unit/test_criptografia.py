import pytest
from src.seguranca.criptografia import GerenciadorCriptografia
import json

@pytest.fixture
def gerenciador():
    """Fixture que fornece uma instância do gerenciador de criptografia para os testes."""
    return GerenciadorCriptografia(
        chave_mestre="chave_teste",
        iteracoes=1000  # Reduzido para testes mais rápidos
    )

def test_inicializacao(gerenciador):
    """Testa a inicialização do gerenciador de criptografia."""
    assert gerenciador.iteracoes == 1000
    assert len(gerenciador.salt) == 16
    assert len(gerenciador.chave_mestre) > 0
    assert len(gerenciador.chave_criptografia) > 0

def test_criptografia_simetrica_string(gerenciador):
    """Testa criptografia simétrica com string."""
    texto_original = "Texto de teste para criptografia"
    
    # Criptografa
    texto_criptografado = gerenciador.criptografar_simetrico(texto_original)
    assert isinstance(texto_criptografado, bytes)
    assert texto_criptografado != texto_original.encode()
    
    # Descriptografa
    texto_descriptografado = gerenciador.descriptografar_simetrico(texto_criptografado)
    assert texto_descriptografado == texto_original

def test_criptografia_simetrica_dict(gerenciador):
    """Testa criptografia simétrica com dicionário."""
    dados_originais = {
        "chave1": "valor1",
        "chave2": 42,
        "chave3": [1, 2, 3]
    }
    
    # Criptografa
    dados_criptografados = gerenciador.criptografar_simetrico(dados_originais)
    assert isinstance(dados_criptografados, bytes)
    
    # Descriptografa
    dados_descriptografados = gerenciador.descriptografar_simetrico(dados_criptografados)
    assert dados_descriptografados == dados_originais

def test_criptografia_assimetrica(gerenciador):
    """Testa criptografia assimétrica."""
    texto_original = "Texto de teste para criptografia assimétrica"
    
    # Criptografa
    texto_criptografado = gerenciador.criptografar_assimetrico(texto_original)
    assert isinstance(texto_criptografado, bytes)
    assert texto_criptografado != texto_original.encode()
    
    # Descriptografa
    texto_descriptografado = gerenciador.descriptografar_assimetrico(texto_criptografado)
    assert texto_descriptografado.decode() == texto_original

def test_exportar_importar_chave_publica(gerenciador):
    """Testa exportação e importação de chave pública."""
    # Exporta chave pública
    chave_publica = gerenciador.exportar_chave_publica()
    assert isinstance(chave_publica, bytes)
    assert b"PUBLIC KEY" in chave_publica
    
    # Cria novo gerenciador
    novo_gerenciador = GerenciadorCriptografia()
    
    # Importa chave pública
    novo_gerenciador.importar_chave_publica(chave_publica)
    
    # Testa criptografia com chave importada
    texto_original = "Texto de teste"
    texto_criptografado = novo_gerenciador.criptografar_assimetrico(texto_original)
    texto_descriptografado = gerenciador.descriptografar_assimetrico(texto_criptografado)
    assert texto_descriptografado.decode() == texto_original

def test_rotacao_chaves(gerenciador):
    """Testa rotação de chaves."""
    # Criptografa dados com chave original
    texto_original = "Texto de teste"
    texto_criptografado_original = gerenciador.criptografar_simetrico(texto_original)
    
    # Rotaciona chaves
    gerenciador.rotacionar_chaves()
    
    # Tenta descriptografar com nova chave
    with pytest.raises(Exception):
        gerenciador.descriptografar_simetrico(texto_criptografado_original)
    
    # Criptografa e descriptografa com nova chave
    texto_criptografado_novo = gerenciador.criptografar_simetrico(texto_original)
    texto_descriptografado = gerenciador.descriptografar_simetrico(texto_criptografado_novo)
    assert texto_descriptografado == texto_original

def test_erro_criptografia_invalida(gerenciador):
    """Testa tratamento de erros com dados inválidos."""
    # Testa criptografia com dados inválidos
    with pytest.raises(Exception):
        gerenciador.criptografar_simetrico(None)
    
    # Testa descriptografia com dados inválidos
    with pytest.raises(Exception):
        gerenciador.descriptografar_simetrico(b"dados_invalidos")
    
    # Testa criptografia assimétrica com dados inválidos
    with pytest.raises(Exception):
        gerenciador.criptografar_assimetrico(None)
    
    # Testa descriptografia assimétrica com dados inválidos
    with pytest.raises(Exception):
        gerenciador.descriptografar_assimetrico(b"dados_invalidos") 