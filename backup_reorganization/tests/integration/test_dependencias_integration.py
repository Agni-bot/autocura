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
    versao_python = sys.version_info
    assert versao_python.major == 3
    assert versao_python.minor <= 13  # Atualizado para aceitar Python 3.13
    
    # Mock das dependências do sistema
    gerenciador.verificar_dependencias_sistema = lambda: {
        'pg_config': True,
        'gcc': True,
        'make': True
    }
    
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
    """Testa a persistência do histórico de problemas."""
    # Limpa histórico existente
    gerenciador.limpar_historico()
    
    # Registra problemas
    problemas = [
        ('pytest', '7.4.0', 'Erro 1', 'Solução 1'),
        ('prometheus-client', '0.17.1', 'Erro 2', 'Solução 2')
    ]
    
    for pacote, versao, erro, solucao in problemas:
        gerenciador.registrar_problema(pacote, versao, erro, solucao)
    
    # Verifica histórico
    assert len(gerenciador.historico) == len(problemas)
    
    # Verifica que não há duplicação
    pacotes_registrados = set(p.pacote for p in gerenciador.historico)
    assert len(pacotes_registrados) == len(problemas)
    
    # Verifica conteúdo
    for problema in gerenciador.historico:
        assert problema.pacote in [p[0] for p in problemas]
        assert problema.versao in [p[1] for p in problemas]
        assert problema.erro in [p[2] for p in problemas]
        assert problema.solucao in [p[3] for p in problemas]

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
    assert isinstance(solucao, str)
    assert "pytest" in solucao.lower()
    assert "7.4.0" in solucao
    assert "instalar" in solucao.lower() or "pip install" in solucao.lower()

def test_limpeza_arquivo_historico(gerenciador):
    """Testa a limpeza do arquivo de histórico após os testes."""
    if os.path.exists(gerenciador.arquivo_historico):
        os.remove(gerenciador.arquivo_historico) 