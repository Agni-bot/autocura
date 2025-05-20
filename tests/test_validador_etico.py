"""
Testes do validador ético do sistema.
"""
import pytest
from datetime import datetime
from typing import Dict, Any

from src.etica.validador_etico import ValidadorEtico
from src.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def validador():
    """Fixture que fornece uma instância do validador ético para os testes."""
    gerenciador_memoria = GerenciadorMemoria()
    return ValidadorEtico(gerenciador_memoria)

def test_validacao_decisao_manutencao():
    """Testa a validação ética de uma decisão de manutenção."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão de manutenção
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "baixo",
            "reversivel": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.8
    assert len(resultado["validacoes"]) > 0

def test_validacao_decisao_hotfix():
    """Testa a validação ética de uma decisão de hotfix."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão de hotfix
    decisao = {
        "id": "test_2",
        "tipo": "hotfix",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "medio",
            "reversivel": True,
            "urgencia": "alta",
            "testes": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.9
    assert len(resultado["validacoes"]) > 0

def test_validacao_decisao_refatoracao():
    """Testa a validação ética de uma decisão de refatoração."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão de refatoração
    decisao = {
        "id": "test_3",
        "tipo": "refatoracao",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "medio",
            "reversivel": True,
            "testes": True,
            "revisao": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.85
    assert len(resultado["validacoes"]) > 0

def test_validacao_decisao_redesign():
    """Testa a validação ética de uma decisão de redesign."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão de redesign
    decisao = {
        "id": "test_4",
        "tipo": "redesign",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "alto",
            "reversivel": True,
            "testes": True,
            "revisao": True,
            "aprovacao": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.95
    assert len(resultado["validacoes"]) > 0

def test_rejeicao_decisao_sem_documentacao():
    """Testa a rejeição de uma decisão sem documentação."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão sem documentação
    decisao = {
        "id": "test_5",
        "tipo": "manutencao",
        "contexto": {
            "documentacao": False,
            "rastreavel": True,
            "explicavel": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == False
    assert "documentacao" in resultado["motivos_rejeicao"]

def test_rejeicao_decisao_sem_rastreabilidade():
    """Testa a rejeição de uma decisão sem rastreabilidade."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão sem rastreabilidade
    decisao = {
        "id": "test_6",
        "tipo": "hotfix",
        "contexto": {
            "documentacao": True,
            "rastreavel": False,
            "explicavel": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == False
    assert "rastreabilidade" in resultado["motivos_rejeicao"]

def test_rejeicao_decisao_sem_explicabilidade():
    """Testa a rejeição de uma decisão sem explicabilidade."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão sem explicabilidade
    decisao = {
        "id": "test_7",
        "tipo": "refatoracao",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": False
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == False
    assert "explicabilidade" in resultado["motivos_rejeicao"]

def test_validacao_impacto_alto():
    """Testa a validação de uma decisão com impacto alto."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão com impacto alto
    decisao = {
        "id": "test_8",
        "tipo": "redesign",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "alto",
            "reversivel": True,
            "testes": True,
            "revisao": True,
            "aprovacao": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.95
    assert "impacto_alto" in resultado["validacoes"]

def test_validacao_impacto_baixo():
    """Testa a validação de uma decisão com impacto baixo."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão com impacto baixo
    decisao = {
        "id": "test_9",
        "tipo": "manutencao",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "baixo",
            "reversivel": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.8
    assert "impacto_baixo" in resultado["validacoes"]

def test_validacao_urgencia():
    """Testa a validação de uma decisão com urgencia."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão com urgencia
    decisao = {
        "id": "test_10",
        "tipo": "hotfix",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "medio",
            "reversivel": True,
            "urgencia": "alta",
            "testes": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.9
    assert "urgencia" in resultado["validacoes"]

def test_validacao_reversibilidade():
    """Testa a validação de uma decisão com reversibilidade."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão com reversibilidade
    decisao = {
        "id": "test_11",
        "tipo": "refatoracao",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "medio",
            "reversivel": True,
            "testes": True,
            "revisao": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.85
    assert "reversibilidade" in resultado["validacoes"]

def test_validacao_testes():
    """Testa a validação de uma decisão com testes."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão com testes
    decisao = {
        "id": "test_12",
        "tipo": "hotfix",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "medio",
            "reversivel": True,
            "urgencia": "alta",
            "testes": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.9
    assert "testes" in resultado["validacoes"]

def test_validacao_revisao():
    """Testa a validação de uma decisão com revisão."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão com revisão
    decisao = {
        "id": "test_13",
        "tipo": "refatoracao",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "medio",
            "reversivel": True,
            "testes": True,
            "revisao": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.85
    assert "revisao" in resultado["validacoes"]

def test_validacao_aprovacao():
    """Testa a validação de uma decisão com aprovação."""
    validador = ValidadorEtico(GerenciadorMemoria())
    
    # Simular decisão com aprovação
    decisao = {
        "id": "test_14",
        "tipo": "redesign",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True,
            "impacto": "alto",
            "reversivel": True,
            "testes": True,
            "revisao": True,
            "aprovacao": True
        }
    }
    
    # Validar decisão
    resultado = validador.validar_decisao(decisao)
    
    # Verificar resultado
    assert resultado["aprovada"] == True
    assert resultado["nivel_confianca"] >= 0.95
    assert "aprovacao" in resultado["validacoes"] 