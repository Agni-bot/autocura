#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para validar a estrutura do projeto AutoCura.
Verifica diretórios, arquivos, imports e documentação.
"""

import os
import sys
import ast
import logging
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ValidadorEstrutura:
    """Validador da estrutura do projeto AutoCura."""

    def __init__(self, raiz: str = "."):
        """Inicializa o validador.
        
        Args:
            raiz: Diretório raiz do projeto
        """
        self.raiz = Path(raiz)
        self.erros: List[str] = []
        self.avisos: List[str] = []
        
        # Diretórios obrigatórios
        self.diretorios_obrigatorios = {
            "modulos": {
                "core": ["src", "tests", "docs"],
                "monitoramento": ["src", "tests", "docs"],
                "etica": ["src", "tests", "docs"],
                "diagnostico": ["src", "tests", "docs"]
            },
            "docs": ["api", "arquitetura", "guia_desenvolvimento"],
            "tests": ["unit", "integration", "e2e"],
            "scripts": [],
            "deployment": ["kubernetes", "docker"]
        }
        
        # Arquivos obrigatórios
        self.arquivos_obrigatorios = {
            "": ["README.md", "requirements.txt", "requirements-test.txt"],
            "docs": ["README.md", "arquitetura.md", "guia_desenvolvimento.md"],
            "docs/api": ["README.md"],
            "modulos/core": ["README.md"],
            "modulos/monitoramento": ["README.md"],
            "modulos/etica": ["README.md"],
            "modulos/diagnostico": ["README.md"]
        }

    def validar_diretorios(self) -> bool:
        """Valida a estrutura de diretórios.
        
        Returns:
            bool: True se todos os diretórios obrigatórios existem
        """
        logger.info("Validando diretórios...")
        
        for dir_principal, subdirs in self.diretorios_obrigatorios.items():
            caminho = self.raiz / dir_principal
            if not caminho.exists():
                self.erros.append(f"Diretório obrigatório não encontrado: {dir_principal}")
                continue
                
            for subdir in subdirs:
                subcaminho = caminho / subdir
                if not subcaminho.exists():
                    self.erros.append(
                        f"Subdiretorio obrigatório não encontrado: {dir_principal}/{subdir}"
                    )
                    
        return len(self.erros) == 0

    def validar_arquivos(self) -> bool:
        """Valida a existência dos arquivos obrigatórios.
        
        Returns:
            bool: True se todos os arquivos obrigatórios existem
        """
        logger.info("Validando arquivos...")
        
        for dir_relativo, arquivos in self.arquivos_obrigatorios.items():
            caminho = self.raiz / dir_relativo
            if not caminho.exists():
                self.erros.append(f"Diretório não encontrado: {dir_relativo}")
                continue
                
            for arquivo in arquivos:
                arquivo_caminho = caminho / arquivo
                if not arquivo_caminho.exists():
                    self.erros.append(
                        f"Arquivo obrigatório não encontrado: {dir_relativo}/{arquivo}"
                    )
                    
        return len(self.erros) == 0

    def validar_imports(self, arquivo: Path) -> List[str]:
        """Valida os imports de um arquivo Python.
        
        Args:
            arquivo: Caminho do arquivo Python
            
        Returns:
            List[str]: Lista de erros encontrados
        """
        erros = []
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if not self._validar_modulo(name.name):
                            erros.append(f"Import inválido em {arquivo}: {name.name}")
                elif isinstance(node, ast.ImportFrom):
                    if not self._validar_modulo(node.module):
                        erros.append(f"Import inválido em {arquivo}: {node.module}")
                        
        except Exception as e:
            erros.append(f"Erro ao validar imports de {arquivo}: {str(e)}")
            
        return erros

    def _validar_modulo(self, modulo: str) -> bool:
        """Valida se um módulo é válido.
        
        Args:
            modulo: Nome do módulo
            
        Returns:
            bool: True se o módulo é válido
        """
        # Lista de módulos permitidos
        modulos_permitidos = {
            'modulos.core',
            'modulos.monitoramento',
            'modulos.etica',
            'modulos.diagnostico',
            'shared',
            'tests'
        }
        
        # Módulos de terceiros comuns
        modulos_terceiros = {
            'numpy',
            'pandas',
            'pytest',
            'requests',
            'fastapi',
            'pydantic'
        }
        
        return (
            modulo in modulos_permitidos or
            modulo in modulos_terceiros or
            any(modulo.startswith(m) for m in modulos_permitidos)
        )

    def validar_todos_arquivos_python(self) -> bool:
        """Valida todos os arquivos Python do projeto.
        
        Returns:
            bool: True se não houver erros de import
        """
        logger.info("Validando arquivos Python...")
        
        for arquivo in self.raiz.rglob("*.py"):
            if "venv" in str(arquivo) or "env" in str(arquivo):
                continue
                
            erros = self.validar_imports(arquivo)
            self.erros.extend(erros)
            
        return len(self.erros) == 0

    def validar_documentacao(self) -> bool:
        """Valida a documentação do projeto.
        
        Returns:
            bool: True se a documentação está adequada
        """
        logger.info("Validando documentação...")
        
        # Verifica README.md
        readme = self.raiz / "README.md"
        if not readme.exists():
            self.erros.append("README.md não encontrado")
        else:
            with open(readme, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                if len(conteudo) < 100:
                    self.avisos.append("README.md muito curto")
                    
        # Verifica documentação dos módulos
        for modulo in ["core", "monitoramento", "etica", "diagnostico"]:
            readme_modulo = self.raiz / "modulos" / modulo / "README.md"
            if not readme_modulo.exists():
                self.erros.append(f"README.md não encontrado em modulos/{modulo}")
                
        return len(self.erros) == 0

    def executar_validacao(self) -> Tuple[bool, List[str], List[str]]:
        """Executa todas as validações.
        
        Returns:
            Tuple[bool, List[str], List[str]]: (sucesso, erros, avisos)
        """
        logger.info("Iniciando validação do projeto...")
        
        validacoes = [
            self.validar_diretorios,
            self.validar_arquivos,
            self.validar_todos_arquivos_python,
            self.validar_documentacao
        ]
        
        for validacao in validacoes:
            try:
                validacao()
            except Exception as e:
                self.erros.append(f"Erro na validação {validacao.__name__}: {str(e)}")
                
        sucesso = len(self.erros) == 0
        
        if sucesso:
            logger.info("Validação concluída com sucesso!")
        else:
            logger.error("Validação encontrou erros!")
            
        if self.avisos:
            logger.warning("Avisos encontrados durante a validação")
            
        return sucesso, self.erros, self.avisos

def main():
    """Função principal."""
    validador = ValidadorEstrutura()
    sucesso, erros, avisos = validador.executar_validacao()
    
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