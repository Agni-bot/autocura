#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pytest
import subprocess
from datetime import datetime
from src.autocura.dependencias import GerenciadorDependencias

@pytest.fixture(scope="module")
def gerenciador():
    """Fixture que retorna uma instância do GerenciadorDependencias."""
    return GerenciadorDependencias(arquivo_historico="memoria/test_dependencias_integration.json")

@pytest.fixture(scope="module")
def requirements_teste():
    """Fixture que cria um requirements.txt temporário para testes."""
    arquivo = "requirements_teste.txt"
    with open(arquivo, "w") as f:
        f.write("pytest==7.4.0\n")
        f.write("prometheus-client==0.17.1\n")
    yield arquivo
    os.remove(arquivo)

def test_fluxo_completo_autocura(gerenciador, requirements_teste):
    """Testa o fluxo completo de autocura com um pacote real."""
    # Registra um problema conhecido
    gerenciador.registrar_problema(
        pacote="pytest",
        versao="7.4.0",
        erro="No matching distribution found for pytest==7.4.0",
        solucao="Instalar pytest com versão específica: pip install pytest==7.4.0"
    )
    
    # Verifica compatibilidade do Python
    assert gerenciador.verificar_compatibilidade_python() is True
    
    # Verifica dependências do sistema
    dependencias = gerenciador.verificar_dependencias_sistema()
    assert all(dependencias.values())
    
    # Tenta instalar dependências
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', requirements_teste],
            check=True,
            capture_output=True
        )
        assert True
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Falha ao instalar dependências: {e.output.decode()}")

def test_historico_persistencia(gerenciador):
    """Testa a persistência do histórico entre instâncias."""
    # Registra problemas
    problemas = [
        ("pytest", "7.4.0", "Erro 1", "Solução 1"),
        ("prometheus-client", "0.17.1", "Erro 2", "Solução 2")
    ]
    
    for pacote, versao, erro, solucao in problemas:
        gerenciador.registrar_problema(pacote, versao, erro, solucao)
    
    # Cria novo gerenciador
    novo_gerenciador = GerenciadorDependencias(arquivo_historico=gerenciador.arquivo_historico)
    
    # Verifica se os problemas foram carregados
    assert len(novo_gerenciador.historico) == len(problemas)
    for i, (pacote, versao, _, _) in enumerate(problemas):
        assert novo_gerenciador.historico[i].pacote == pacote
        assert novo_gerenciador.historico[i].versao == versao

def test_sugestao_solucao_integracao(gerenciador):
    """Testa a sugestão de solução em um cenário real."""
    # Registra um problema
    gerenciador.registrar_problema(
        pacote="pytest",
        versao="7.4.0",
        erro="No matching distribution found for pytest==7.4.0",
        solucao="Instalar pytest com versão específica: pip install pytest==7.4.0"
    )
    
    # Tenta obter solução
    solucao = gerenciador.sugerir_solucao("pytest", "7.4.0")
    assert solucao is not None
    assert "pip install" in solucao

def test_limpeza_arquivo_historico(gerenciador):
    """Testa a limpeza do arquivo de histórico após os testes."""
    if os.path.exists(gerenciador.arquivo_historico):
        os.remove(gerenciador.arquivo_historico) 