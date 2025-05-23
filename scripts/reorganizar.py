#!/usr/bin/env python3
"""
Script para reorganizar a estrutura de diretórios do projeto Autocura.
"""

import os
import shutil
from pathlib import Path
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mapeamento de diretórios antigos para novos
MAPPING = {
    'src/core': 'modulos/core',
    'src/monitoramento': 'modulos/monitoramento',
    'src/monitoring': 'modulos/monitoramento',
    'src/diagnostico': 'modulos/diagnostico',
    'src/gerador-acoes': 'modulos/gerador-acoes',
    'src/integracao': 'modulos/integracao',
    'src/observabilidade': 'modulos/observabilidade',
    'src/guardiao-cognitivo': 'modulos/guardiao-cognitivo',
    'src/etica': 'modulos/etica',
    'src/utils': 'shared/utils',
    'src/api': 'shared/api',
    'src/events': 'shared/events',
    'src/seguranca': 'modulos/etica/validadores-eticos',
    'src/financas': 'modulos/etica/priorizacao-financeira',
    'src/auditoria': 'modulos/etica/auditoria',
    'src/governanca': 'modulos/etica/governanca',
    'src/registro-decisoes': 'modulos/etica/registro-decisoes',
}

def criar_estrutura_base():
    """Cria a estrutura base de diretórios para cada módulo"""
    for modulo in MAPPING.values():
        Path(modulo).mkdir(parents=True, exist_ok=True)
        # Criar estrutura padrão dentro de cada módulo
        for subdir in ['src', 'tests', 'config', 'docker']:
            Path(f"{modulo}/{subdir}").mkdir(exist_ok=True)

def mover_arquivos():
    """Move os arquivos para suas novas localizações"""
    for src, dest in MAPPING.items():
        if os.path.exists(src):
            # Criar diretório de destino se não existir
            os.makedirs(dest, exist_ok=True)
            
            # Mover arquivos
            for item in os.listdir(src):
                src_path = os.path.join(src, item)
                dest_path = os.path.join(dest, item)
                
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                elif os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)

def criar_arquivos_base():
    """Cria arquivos base necessários para cada módulo"""
    for modulo in MAPPING.values():
        # Criar __init__.py
        with open(f"{modulo}/__init__.py", 'w') as f:
            f.write(f'"""Módulo {os.path.basename(modulo)}"""\n')
        
        # Criar README.md
        with open(f"{modulo}/README.md", 'w') as f:
            f.write(f"# Módulo {os.path.basename(modulo)}\n\n")
            f.write("## Descrição\n\n")
            f.write("## Instalação\n\n")
            f.write("## Uso\n\n")

def main():
    print("Iniciando reorganização do projeto...")
    criar_estrutura_base()
    mover_arquivos()
    criar_arquivos_base()
    print("Reorganização concluída!")

if __name__ == "__main__":
    main() 