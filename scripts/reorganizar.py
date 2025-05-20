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

# Diretórios a serem reorganizados
REORGANIZACAO = {
    # Módulos principais
    'src/GeradorAcoes': 'src/gerador',
    'src/consciencia_situacional': 'src/core/consciencia',
    'src/conscienciaSituacional': 'src/core/consciencia',
    'src/autocorrection': 'src/core/autocorrecao',
    'src/guardiaoCognitivo': 'src/guardiao',
    'src/will': 'src/core/will',
    
    # Módulos de ML/AI
    'src/interpretability': 'src/core/interpretabilidade',
    'src/validation': 'src/core/validacao',
    'src/synthesis': 'src/core/sintese',
    'src/prediction': 'src/core/predicao',
    'src/adaptation': 'src/core/adaptacao',
    
    # Arquivos soltos
    'src/monitoramento.py': 'src/monitoramento/monitoramento.py',
    'src/gerador.py': 'src/gerador/gerador.py',
    'src/diagnostico.py': 'src/diagnostico/diagnostico.py',
}

def criar_diretorio(path: Path):
    """Cria um diretório se não existir."""
    if not path.exists():
        path.mkdir(parents=True)
        logger.info(f"Diretório criado: {path}")

def mover_arquivo(origem: Path, destino: Path):
    """Move um arquivo para o novo local."""
    if origem.exists():
        # Cria diretório de destino se necessário
        destino.parent.mkdir(parents=True, exist_ok=True)
        
        # Move o arquivo
        shutil.move(str(origem), str(destino))
        logger.info(f"Arquivo movido: {origem} -> {destino}")

def reorganizar():
    """Reorganiza os diretórios conforme a nova estrutura."""
    # Diretório base do projeto
    base_dir = Path(__file__).parent.parent
    
    # Cria diretórios principais se não existirem
    diretorios_principais = [
        'config',
        'docs',
        'grafana',
        'kubernetes',
        'logs',
        'memoria',
        'prometheus',
        'scripts',
        'src',
        'tests',
        'verificar'
    ]
    
    for dir_name in diretorios_principais:
        criar_diretorio(base_dir / dir_name)
    
    # Reorganiza diretórios e arquivos
    for origem, destino in REORGANIZACAO.items():
        origem_path = base_dir / origem
        destino_path = base_dir / destino
        
        if origem_path.exists():
            if origem_path.is_dir():
                # Move diretório
                if destino_path.exists():
                    # Se destino existe, move conteúdo
                    for item in origem_path.iterdir():
                        shutil.move(str(item), str(destino_path / item.name))
                    # Remove diretório origem vazio
                    origem_path.rmdir()
                else:
                    # Move diretório inteiro
                    shutil.move(str(origem_path), str(destino_path))
                logger.info(f"Diretório movido: {origem} -> {destino}")
            else:
                # Move arquivo
                mover_arquivo(origem_path, destino_path)
    
    # Limpa diretórios vazios
    for dir_path in base_dir.rglob('*'):
        if dir_path.is_dir() and not any(dir_path.iterdir()):
            try:
                dir_path.rmdir()
                logger.info(f"Diretório vazio removido: {dir_path}")
            except OSError:
                pass

if __name__ == '__main__':
    try:
        reorganizar()
        logger.info("Reorganização concluída com sucesso!")
    except Exception as e:
        logger.error(f"Erro durante a reorganização: {str(e)}")
        raise 