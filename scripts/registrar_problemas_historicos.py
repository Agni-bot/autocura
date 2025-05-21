#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime

# Adiciona o diretório src ao path para importar o módulo de autocura
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.autocura.dependencias import GerenciadorDependencias

def registrar_problemas_historicos():
    """Registra os problemas históricos de dependências."""
    gerenciador = GerenciadorDependencias()
    
    # Problema 1: psycopg2-binary
    gerenciador.registrar_problema(
        pacote="psycopg2-binary",
        versao="2.9.9",
        erro="Error: pg_config executable not found.",
        solucao="Instalar manualmente a versão binária mais recente (pip install psycopg2-binary) e alterar requirements.txt para psycopg2-binary>=2.9.10"
    )
    
    # Problema 2: mkdocs-autorefs
    gerenciador.registrar_problema(
        pacote="mkdocs-autorefs",
        versao="0.5.1",
        erro="No matching distribution found for mkdocs-autorefs==0.5.1",
        solucao="Ajustar para a versão mais próxima disponível (mkdocs-autorefs==0.5.0) e remover plugins GitBook do requirements.txt"
    )
    
    # Problema 3: tensorflow
    gerenciador.registrar_problema(
        pacote="tensorflow",
        versao="2.15.0",
        erro="No matching distribution found for tensorflow==2.15.0",
        solucao="Usar Python 3.10 para o projeto, pois versões mais recentes do Python não são suportadas pelo TensorFlow"
    )

if __name__ == '__main__':
    registrar_problemas_historicos() 