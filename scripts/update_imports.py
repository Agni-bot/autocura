#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para atualizar imports no projeto AutoCura.
Atualiza imports baseado na nova estrutura de módulos.
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

class AtualizadorImports:
    """Atualizador de imports do projeto AutoCura."""

    def __init__(self, raiz: str = "."):
        """Inicializa o atualizador.
        
        Args:
            raiz: Diretório raiz do projeto
        """
        self.raiz = Path(raiz)
        self.erros: List[str] = []
        self.avisos: List[str] = []
        self.arquivos_atualizados = 0
        
        # Mapeamento de imports antigos para novos
        self.mapeamento_imports = {
            'modulos.observabilidade': 'modulos.monitoramento',
            'modulos.guardiao-cognitivo': 'modulos.etica',
            'modulos.gerador-acoes': 'modulos.diagnostico',
            'modulos.integracao': 'modulos.core.integracao'
        }

    def atualizar_imports(self, arquivo: Path) -> bool:
        """Atualiza os imports de um arquivo Python.
        
        Args:
            arquivo: Caminho do arquivo Python
            
        Returns:
            bool: True se o arquivo foi atualizado
        """
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                
            # Parse do arquivo
            tree = ast.parse(conteudo)
            
            # Flag para indicar se houve mudanças
            mudancas = False
            
            # Lista para armazenar as linhas atualizadas
            linhas = conteudo.splitlines()
            
            # Atualiza imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        novo_nome = self._mapear_import(name.name)
                        if novo_nome != name.name:
                            mudancas = True
                            # Atualiza a linha
                            linha = node.lineno - 1
                            linhas[linha] = linhas[linha].replace(
                                name.name, novo_nome
                            )
                            
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        novo_modulo = self._mapear_import(node.module)
                        if novo_modulo != node.module:
                            mudancas = True
                            # Atualiza a linha
                            linha = node.lineno - 1
                            linhas[linha] = linhas[linha].replace(
                                node.module, novo_modulo
                            )
                            
            if mudancas:
                # Salva o arquivo atualizado
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(linhas))
                self.arquivos_atualizados += 1
                logger.info(f"Arquivo atualizado: {arquivo}")
                
            return mudancas
            
        except Exception as e:
            self.erros.append(f"Erro ao atualizar imports de {arquivo}: {str(e)}")
            return False

    def _mapear_import(self, import_name: str) -> str:
        """Mapeia um import antigo para o novo.
        
        Args:
            import_name: Nome do import
            
        Returns:
            str: Nome do import atualizado
        """
        for antigo, novo in self.mapeamento_imports.items():
            if import_name.startswith(antigo):
                return import_name.replace(antigo, novo)
        return import_name

    def atualizar_todos_arquivos(self) -> bool:
        """Atualiza imports em todos os arquivos Python.
        
        Returns:
            bool: True se não houver erros
        """
        logger.info("Atualizando imports em todos os arquivos Python...")
        
        for arquivo in self.raiz.rglob("*.py"):
            if "venv" in str(arquivo) or "env" in str(arquivo):
                continue
                
            self.atualizar_imports(arquivo)
            
        return len(self.erros) == 0

    def executar_atualizacao(self) -> Tuple[bool, List[str], List[str]]:
        """Executa a atualização de imports.
        
        Returns:
            Tuple[bool, List[str], List[str]]: (sucesso, erros, avisos)
        """
        logger.info("Iniciando atualização de imports...")
        
        try:
            self.atualizar_todos_arquivos()
        except Exception as e:
            self.erros.append(f"Erro durante atualização: {str(e)}")
            
        sucesso = len(self.erros) == 0
        
        if sucesso:
            logger.info(f"Atualização concluída! {self.arquivos_atualizados} arquivos atualizados.")
        else:
            logger.error("Atualização encontrou erros!")
            
        if self.avisos:
            logger.warning("Avisos encontrados durante a atualização")
            
        return sucesso, self.erros, self.avisos

def main():
    """Função principal."""
    atualizador = AtualizadorImports()
    sucesso, erros, avisos = atualizador.executar_atualizacao()
    
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