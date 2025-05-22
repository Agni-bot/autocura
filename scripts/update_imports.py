import os
import re
from pathlib import Path

def update_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Mapeamento de imports antigos para novos
    import_mapping = {
        'src.metricas': 'src.monitoring.metrics',
        'src.observabilidade': 'src.monitoring.observability',
        'src.cache': 'src.utils.cache',
        'src.logs': 'src.utils.logs',
        'src.config': 'src.core.config',
        'src.testes': 'tests.unit',
        'src.tests': 'tests.unit',
        'src.sandbox': 'examples',
        'src.exemplos': 'examples',
        'src.kubernetes': 'deploy.kubernetes',
        'src.orquestrador': 'src.orchestration',
        'src.orquestracao': 'src.orchestration',
        'src.diagnostico': 'src.services.diagnostico',
        'src.etica': 'src.services.etica',
        'src.gerador': 'src.services.gerador',
        'src.guardiao': 'src.services.guardiao',
        'src.memoria': 'src.services.memoria',
    }

    # Atualizar imports
    for old, new in import_mapping.items():
        content = re.sub(
            f'from {old}\\.',
            f'from {new}.',
            content
        )
        content = re.sub(
            f'import {old}\\.',
            f'import {new}.',
            content
        )

    # Salvar arquivo atualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                update_imports(file_path)

if __name__ == '__main__':
    # Processar diretórios principais
    directories = ['src', 'tests', 'scripts']
    for directory in directories:
        process_directory(directory) 