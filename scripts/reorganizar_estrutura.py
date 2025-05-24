#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para reorganizar a estrutura do projeto AutoCura.
Move arquivos para suas novas localizações e atualiza imports.
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ReorganizadorEstrutura:
    """Reorganizador da estrutura do projeto AutoCura."""

    def __init__(self, raiz: str = "."):
        """Inicializa o reorganizador.
        
        Args:
            raiz: Diretório raiz do projeto
        """
        self.raiz = Path(raiz)
        self.erros: List[str] = []
        self.avisos: List[str] = []
        
        # Mapeamento de diretórios antigos para novos
        self.mapeamento_diretorios = {
            "src/observabilidade": "modulos/monitoramento/src",
            "src/etica": "modulos/etica/src",
            "src/diagnostico": "modulos/diagnostico/src",
            "src/core": "modulos/core/src",
            "tests/observabilidade": "modulos/monitoramento/tests",
            "tests/etica": "modulos/etica/tests",
            "tests/diagnostico": "modulos/diagnostico/tests",
            "tests/core": "modulos/core/tests",
            "docs/observabilidade": "modulos/monitoramento/docs",
            "docs/etica": "modulos/etica/docs",
            "docs/diagnostico": "modulos/diagnostico/docs",
            "docs/core": "modulos/core/docs"
        }
        
        # Arquivos a serem movidos
        self.arquivos_mover = {
            "scripts/diagnostico_*.sh": "modulos/diagnostico/scripts/",
            "scripts/0*_*.sh": "deployment/scripts/",
            "scripts/build_*.sh": "deployment/build/",
            "shared/api/*": "modulos/core/src/api/",
            "shared/events/*": "modulos/core/src/events/",
            "shared/utils/*": "modulos/core/src/utils/"
        }

    def criar_diretorios(self) -> bool:
        """Cria diretórios necessários.
        
        Returns:
            bool: True se todos os diretórios foram criados
        """
        logger.info("Criando diretórios...")
        
        diretorios = set()
        
        # Adiciona diretórios do mapeamento
        for destino in self.mapeamento_diretorios.values():
            diretorios.add(destino)
            
        # Adiciona diretórios de arquivos a mover
        for destino in self.arquivos_mover.values():
            diretorios.add(destino)
            
        # Cria diretórios
        for diretorio in diretorios:
            caminho = self.raiz / diretorio
            try:
                caminho.mkdir(parents=True, exist_ok=True)
                logger.info(f"Diretório criado: {diretorio}")
            except Exception as e:
                self.erros.append(f"Erro ao criar diretório {diretorio}: {str(e)}")
                
        return len(self.erros) == 0

    def mover_arquivos(self) -> bool:
        """Move arquivos para suas novas localizações.
        
        Returns:
            bool: True se todos os arquivos foram movidos
        """
        logger.info("Movendo arquivos...")
        
        # Move diretórios
        for origem, destino in self.mapeamento_diretorios.items():
            origem_path = self.raiz / origem
            destino_path = self.raiz / destino
            
            if not origem_path.exists():
                self.avisos.append(f"Diretório de origem não encontrado: {origem}")
                continue
                
            try:
                # Move arquivos
                for arquivo in origem_path.glob("**/*"):
                    if arquivo.is_file():
                        rel_path = arquivo.relative_to(origem_path)
                        novo_caminho = destino_path / rel_path
                        novo_caminho.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(arquivo), str(novo_caminho))
                        logger.info(f"Arquivo movido: {arquivo} -> {novo_caminho}")
                        
                # Remove diretório de origem se vazio
                if not any(origem_path.iterdir()):
                    origem_path.rmdir()
                    logger.info(f"Diretório removido: {origem}")
                    
            except Exception as e:
                self.erros.append(f"Erro ao mover {origem}: {str(e)}")
                
        # Move arquivos específicos
        for padrao, destino in self.arquivos_mover.items():
            destino_path = self.raiz / destino
            destino_path.mkdir(parents=True, exist_ok=True)
            
            for arquivo in self.raiz.glob(padrao):
                try:
                    novo_caminho = destino_path / arquivo.name
                    shutil.move(str(arquivo), str(novo_caminho))
                    logger.info(f"Arquivo movido: {arquivo} -> {novo_caminho}")
                except Exception as e:
                    self.erros.append(f"Erro ao mover {arquivo}: {str(e)}")
                    
        return len(self.erros) == 0

    def limpar_arquivos_temporarios(self) -> bool:
        """Remove arquivos temporários.
        
        Returns:
            bool: True se todos os arquivos foram removidos
        """
        logger.info("Limpando arquivos temporários...")
        
        arquivos_remover = [
            "memoria_test.json",
            "testes.log",
            "output.json",
            "memoria_compartilhada.json.bak"
        ]
        
        for arquivo in arquivos_remover:
            caminho = self.raiz / arquivo
            if caminho.exists():
                try:
                    caminho.unlink()
                    logger.info(f"Arquivo removido: {arquivo}")
                except Exception as e:
                    self.erros.append(f"Erro ao remover {arquivo}: {str(e)}")
                    
        return len(self.erros) == 0

    def executar_reorganizacao(self) -> Tuple[bool, List[str], List[str]]:
        """Executa a reorganização do projeto.
        
        Returns:
            Tuple[bool, List[str], List[str]]: (sucesso, erros, avisos)
        """
        logger.info("Iniciando reorganização do projeto...")
        
        try:
            self.criar_diretorios()
            self.mover_arquivos()
            self.limpar_arquivos_temporarios()
            
            sucesso = len(self.erros) == 0
            
            if sucesso:
                logger.info("Reorganização concluída com sucesso!")
            else:
                logger.error("Reorganização encontrou erros!")
                
            if self.avisos:
                logger.warning("Avisos encontrados durante a reorganização")
                
            return sucesso, self.erros, self.avisos
            
        except Exception as e:
            self.erros.append(f"Erro durante reorganização: {str(e)}")
            return False, self.erros, self.avisos

def main():
    """Função principal."""
    reorganizador = ReorganizadorEstrutura()
    sucesso, erros, avisos = reorganizador.executar_reorganizacao()
    
    if not sucesso:
        print("\nErros encontrados:")
        for erro in erros:
            print(f"- {erro}")
            
    if avisos:
        print("\nAvisos:")
        for aviso in avisos:
            print(f"- {aviso}")
            
    sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main() 