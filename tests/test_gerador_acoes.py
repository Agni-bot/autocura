"""
Testes do gerador de ações do sistema.
"""
import pytest
from datetime import datetime
from typing import Dict, Any

from src.acoes.gerador_acoes import GeradorAcoes

@pytest.fixture
def gerador():
    """Fixture que fornece uma instância do gerador de ações para os testes."""
    return GeradorAcoes()

def test_gerar_acao_manutencao():
    """Testa a geração de ação de manutenção."""
    gerador = GeradorAcoes()
    
    # Simular contexto
    contexto = {
        "tipo": "manutencao",
        "prioridade": "alta",
        "descricao": "Corrigir bug crítico",
        "componente": "api",
        "impacto": "alto"
    }
    
    # Gerar ação
    acao = gerador.gerar_acao(contexto)
    
    # Verificar resultado
    assert acao["tipo"] == "manutencao"
    assert acao["prioridade"] == "alta"
    assert acao["status"] == "pendente"
    assert acao["componente"] == "api"
    assert acao["impacto"] == "alto"

def test_gerar_acao_hotfix():
    """Testa a geração de ação de hotfix."""
    gerador = GeradorAcoes()
    
    # Simular contexto
    contexto = {
        "tipo": "hotfix",
        "prioridade": "critica",
        "descricao": "Corrigir vulnerabilidade de segurança",
        "componente": "autenticacao",
        "impacto": "critico"
    }
    
    # Gerar ação
    acao = gerador.gerar_acao(contexto)
    
    # Verificar resultado
    assert acao["tipo"] == "hotfix"
    assert acao["prioridade"] == "critica"
    assert acao["status"] == "pendente"
    assert acao["componente"] == "autenticacao"
    assert acao["impacto"] == "critico"

def test_gerar_acao_refatoracao():
    """Testa a geração de ação de refatoração."""
    gerador = GeradorAcoes()
    
    # Simular contexto
    contexto = {
        "tipo": "refatoracao",
        "prioridade": "media",
        "descricao": "Melhorar estrutura do código",
        "componente": "core",
        "impacto": "medio"
    }
    
    # Gerar ação
    acao = gerador.gerar_acao(contexto)
    
    # Verificar resultado
    assert acao["tipo"] == "refatoracao"
    assert acao["prioridade"] == "media"
    assert acao["status"] == "pendente"
    assert acao["componente"] == "core"
    assert acao["impacto"] == "medio"

def test_gerar_acao_redesign():
    """Testa a geração de ação de redesign."""
    gerador = GeradorAcoes()
    
    # Simular contexto
    contexto = {
        "tipo": "redesign",
        "prioridade": "baixa",
        "descricao": "Redesenhar interface do usuário",
        "componente": "frontend",
        "impacto": "baixo"
    }
    
    # Gerar ação
    acao = gerador.gerar_acao(contexto)
    
    # Verificar resultado
    assert acao["tipo"] == "redesign"
    assert acao["prioridade"] == "baixa"
    assert acao["status"] == "pendente"
    assert acao["componente"] == "frontend"
    assert acao["impacto"] == "baixo"

def test_verificar_dependencias():
    """Testa a verificação de dependências."""
    gerador = GeradorAcoes()
    
    # Simular ação com dependências
    acao = {
        "id": "test_1",
        "tipo": "manutencao",
        "dependencias": [
            {"id": "dep_1", "status": "concluida"},
            {"id": "dep_2", "status": "concluida"}
        ]
    }
    
    # Verificar dependências
    resultado = gerador.verificar_dependencias(acao)
    
    # Verificar resultado
    assert resultado == True

def test_verificar_dependencias_pendentes():
    """Testa a verificação de dependências pendentes."""
    gerador = GeradorAcoes()
    
    # Simular ação com dependências pendentes
    acao = {
        "id": "test_1",
        "tipo": "manutencao",
        "dependencias": [
            {"id": "dep_1", "status": "concluida"},
            {"id": "dep_2", "status": "pendente"}
        ]
    }
    
    # Verificar dependências
    resultado = gerador.verificar_dependencias(acao)
    
    # Verificar resultado
    assert resultado == False

def test_executar_acao_manutencao():
    """Testa a execução de ação de manutenção."""
    gerador = GeradorAcoes()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "manutencao",
        "status": "pendente",
        "componente": "api"
    }
    
    # Executar ação
    resultado = gerador.executar_acao(acao)
    
    # Verificar resultado
    assert resultado["status"] == "concluida"
    assert resultado["sucesso"] == True
    assert resultado["timestamp_conclusao"] is not None

def test_executar_acao_hotfix():
    """Testa a execução de ação de hotfix."""
    gerador = GeradorAcoes()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "hotfix",
        "status": "pendente",
        "componente": "autenticacao"
    }
    
    # Executar ação
    resultado = gerador.executar_acao(acao)
    
    # Verificar resultado
    assert resultado["status"] == "concluida"
    assert resultado["sucesso"] == True
    assert resultado["timestamp_conclusao"] is not None

def test_executar_acao_refatoracao():
    """Testa a execução de ação de refatoração."""
    gerador = GeradorAcoes()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "refatoracao",
        "status": "pendente",
        "componente": "core"
    }
    
    # Executar ação
    resultado = gerador.executar_acao(acao)
    
    # Verificar resultado
    assert resultado["status"] == "concluida"
    assert resultado["sucesso"] == True
    assert resultado["timestamp_conclusao"] is not None

def test_executar_acao_redesign():
    """Testa a execução de ação de redesign."""
    gerador = GeradorAcoes()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "redesign",
        "status": "pendente",
        "componente": "frontend"
    }
    
    # Executar ação
    resultado = gerador.executar_acao(acao)
    
    # Verificar resultado
    assert resultado["status"] == "concluida"
    assert resultado["sucesso"] == True
    assert resultado["timestamp_conclusao"] is not None

def test_obter_estatisticas():
    """Testa a obtenção de estatísticas."""
    gerador = GeradorAcoes()
    
    # Simular ações
    acoes = [
        {"id": "test_1", "status": "concluida"},
        {"id": "test_2", "status": "pendente"},
        {"id": "test_3", "status": "concluida"}
    ]
    
    # Obter estatísticas
    estatisticas = gerador.obter_estatisticas(acoes)
    
    # Verificar resultado
    assert estatisticas["total"] == 3
    assert estatisticas["concluidas"] == 2
    assert estatisticas["pendentes"] == 1

def test_obter_acoes_pendentes():
    """Testa a obtenção de ações pendentes."""
    gerador = GeradorAcoes()
    
    # Simular ações
    acoes = [
        {"id": "test_1", "status": "concluida"},
        {"id": "test_2", "status": "pendente"},
        {"id": "test_3", "status": "concluida"}
    ]
    
    # Obter ações pendentes
    pendentes = gerador.obter_acoes_pendentes(acoes)
    
    # Verificar resultado
    assert len(pendentes) == 1
    assert pendentes[0]["id"] == "test_2"

def test_obter_acoes_concluidas():
    """Testa a obtenção de ações concluídas."""
    gerador = GeradorAcoes()
    
    # Simular ações
    acoes = [
        {"id": "test_1", "status": "concluida"},
        {"id": "test_2", "status": "pendente"},
        {"id": "test_3", "status": "concluida"}
    ]
    
    # Obter ações concluídas
    concluidas = gerador.obter_acoes_concluidas(acoes)
    
    # Verificar resultado
    assert len(concluidas) == 2
    assert concluidas[0]["id"] == "test_1"
    assert concluidas[1]["id"] == "test_3"

def test_obter_acoes_por_tipo():
    """Testa a obtenção de ações por tipo."""
    gerador = GeradorAcoes()
    
    # Simular ações
    acoes = [
        {"id": "test_1", "tipo": "manutencao"},
        {"id": "test_2", "tipo": "hotfix"},
        {"id": "test_3", "tipo": "manutencao"}
    ]
    
    # Obter ações por tipo
    manutencoes = gerador.obter_acoes_por_tipo(acoes, "manutencao")
    hotfixes = gerador.obter_acoes_por_tipo(acoes, "hotfix")
    
    # Verificar resultado
    assert len(manutencoes) == 2
    assert len(hotfixes) == 1
    assert manutencoes[0]["id"] == "test_1"
    assert manutencoes[1]["id"] == "test_3"
    assert hotfixes[0]["id"] == "test_2" 