#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.autocura.dependencias import GerenciadorDependencias, ProblemaDependencia

@pytest.fixture
def gerenciador():
    """Fixture que retorna uma instância do GerenciadorDependencias."""
    return GerenciadorDependencias(arquivo_historico="memoria/test_dependencias.json")

@pytest.fixture
def problema_exemplo():
    """Fixture que retorna um problema de dependência de exemplo."""
    return ProblemaDependencia(
        pacote="test-package",
        versao="1.0.0",
        erro="Erro de teste",
        solucao="Solução de teste",
        data_ocorrencia=datetime.now()
    )

def test_registrar_problema(gerenciador, problema_exemplo):
    """Testa o registro de um novo problema."""
    gerenciador.registrar_problema(
        pacote=problema_exemplo.pacote,
        versao=problema_exemplo.versao,
        erro=problema_exemplo.erro,
        solucao=problema_exemplo.solucao
    )
    
    assert len(gerenciador.historico) == 1
    assert gerenciador.historico[0].pacote == problema_exemplo.pacote
    assert gerenciador.historico[0].versao == problema_exemplo.versao

def test_carregar_historico(gerenciador, problema_exemplo):
    """Testa o carregamento do histórico de problemas."""
    # Registra um problema
    gerenciador.registrar_problema(
        pacote=problema_exemplo.pacote,
        versao=problema_exemplo.versao,
        erro=problema_exemplo.erro,
        solucao=problema_exemplo.solucao
    )
    
    # Cria novo gerenciador para carregar o histórico
    novo_gerenciador = GerenciadorDependencias(arquivo_historico=gerenciador.arquivo_historico)
    
    assert len(novo_gerenciador.historico) == 1
    assert novo_gerenciador.historico[0].pacote == problema_exemplo.pacote

@patch('platform.python_version_tuple')
def test_verificar_compatibilidade_python(mock_version, gerenciador):
    """Testa a verificação de compatibilidade do Python."""
    # Testa versão compatível (3.10)
    mock_version.return_value = ('3', '10', '0')
    assert gerenciador.verificar_compatibilidade_python() is True
    
    # Testa versão incompatível (3.11)
    mock_version.return_value = ('3', '11', '0')
    assert gerenciador.verificar_compatibilidade_python() is False

@patch('subprocess.run')
def test_verificar_dependencias_sistema(mock_run, gerenciador):
    """Testa a verificação de dependências do sistema."""
    # Simula todas as dependências presentes
    mock_run.return_value = MagicMock(returncode=0)
    dependencias = gerenciador.verificar_dependencias_sistema()
    assert all(dependencias.values())
    
    # Simula falta de pg_config
    mock_run.side_effect = FileNotFoundError()
    dependencias = gerenciador.verificar_dependencias_sistema()
    assert not dependencias['pg_config']

def test_sugerir_solucao(gerenciador, problema_exemplo):
    """Testa a sugestão de solução baseada no histórico."""
    # Registra um problema
    gerenciador.registrar_problema(
        pacote=problema_exemplo.pacote,
        versao=problema_exemplo.versao,
        erro=problema_exemplo.erro,
        solucao=problema_exemplo.solucao
    )
    
    # Testa sugestão existente
    solucao = gerenciador.sugerir_solucao(problema_exemplo.pacote, problema_exemplo.versao)
    assert solucao == problema_exemplo.solucao
    
    # Testa sugestão inexistente
    solucao = gerenciador.sugerir_solucao("pacote-inexistente", "1.0.0")
    assert solucao is None

@patch('subprocess.run')
def test_executar_autocura(mock_run, gerenciador):
    """Testa o processo de autocura."""
    # Simula instalação bem-sucedida
    mock_run.return_value = MagicMock(returncode=0)
    assert gerenciador.executar_autocura() is True
    
    # Simula falha na instalação
    mock_run.side_effect = subprocess.CalledProcessError(1, "pip")
    assert gerenciador.executar_autocura() is False

def test_limpeza_arquivo_historico(gerenciador):
    """Testa a limpeza do arquivo de histórico após os testes."""
    if os.path.exists(gerenciador.arquivo_historico):
        os.remove(gerenciador.arquivo_historico) 