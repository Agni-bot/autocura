#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para executar testes do projeto AutoCura.
Suporta testes unitários, de integração e end-to-end.
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExecutorTestes:
    """Executor de testes do projeto AutoCura."""

    def __init__(self, raiz: str = "."):
        """Inicializa o executor.
        
        Args:
            raiz: Diretório raiz do projeto
        """
        self.raiz = Path(raiz)
        self.erros: List[str] = []
        self.avisos: List[str] = []
        self.resultados: Dict[str, Dict] = {}
        
        # Diretórios de teste
        self.diretorios_teste = {
            "unit": "tests/unit",
            "integration": "tests/integration",
            "e2e": "tests/e2e"
        }
        
        # Diretório de resultados
        self.dir_resultados = self.raiz / "test-results"
        self.dir_resultados.mkdir(exist_ok=True)

    def executar_teste(self, tipo: str, args: List[str] = None) -> bool:
        """Executa um tipo específico de teste.
        
        Args:
            tipo: Tipo de teste (unit, integration, e2e)
            args: Argumentos adicionais para pytest
            
        Returns:
            bool: True se os testes passaram
        """
        logger.info(f"Executando testes {tipo}...")
        
        if tipo not in self.diretorios_teste:
            self.erros.append(f"Tipo de teste inválido: {tipo}")
            return False
            
        diretorio = self.diretorios_teste[tipo]
        if not (self.raiz / diretorio).exists():
            self.avisos.append(f"Diretório de testes não encontrado: {diretorio}")
            return False
            
        # Argumentos padrão
        pytest_args = [
            sys.executable, "-m", "pytest",
            str(self.raiz / diretorio),
            "-v",
            "--junitxml", str(self.dir_resultados / f"junit_{tipo}.xml"),
            "--html", str(self.dir_resultados / f"report_{tipo}.html")
        ]
        
        # Adiciona argumentos personalizados
        if args:
            pytest_args.extend(args)
            
        try:
            # Executa testes
            resultado = subprocess.run(
                pytest_args,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Salva resultado
            self.resultados[tipo] = {
                "sucesso": True,
                "saida": resultado.stdout,
                "erro": resultado.stderr
            }
            
            logger.info(f"Testes {tipo} executados com sucesso!")
            return True
            
        except subprocess.CalledProcessError as e:
            self.resultados[tipo] = {
                "sucesso": False,
                "saida": e.stdout,
                "erro": e.stderr
            }
            
            self.erros.append(f"Erro ao executar testes {tipo}: {str(e)}")
            return False

    def executar_todos_testes(self, args: List[str] = None) -> bool:
        """Executa todos os tipos de teste.
        
        Args:
            args: Argumentos adicionais para pytest
            
        Returns:
            bool: True se todos os testes passaram
        """
        logger.info("Executando todos os testes...")
        
        sucesso = True
        for tipo in self.diretorios_teste:
            if not self.executar_teste(tipo, args):
                sucesso = False
                
        return sucesso

    def gerar_relatorio(self) -> str:
        """Gera relatório de testes.
        
        Returns:
            str: Caminho do arquivo de relatório
        """
        logger.info("Gerando relatório...")
        
        relatorio = {
            "data": datetime.now().isoformat(),
            "resultados": self.resultados,
            "erros": self.erros,
            "avisos": self.avisos
        }
        
        # Nome do arquivo de relatório
        nome_arquivo = f"testes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        caminho_relatorio = self.dir_resultados / nome_arquivo
        
        # Salvar relatório
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2)
            
        return str(caminho_relatorio)

    def executar(self, tipo: str = None, args: List[str] = None) -> Tuple[bool, str]:
        """Executa os testes.
        
        Args:
            tipo: Tipo de teste específico (opcional)
            args: Argumentos adicionais para pytest
            
        Returns:
            Tuple[bool, str]: (sucesso, caminho_relatorio)
        """
        logger.info("Iniciando execução de testes...")
        
        try:
            if tipo:
                sucesso = self.executar_teste(tipo, args)
            else:
                sucesso = self.executar_todos_testes(args)
                
            relatorio = self.gerar_relatorio()
            
            if sucesso:
                logger.info("Testes concluídos com sucesso!")
            else:
                logger.error("Testes encontraram erros!")
                
            if self.avisos:
                logger.warning("Avisos encontrados durante os testes")
                
            return sucesso, relatorio
            
        except Exception as e:
            self.erros.append(f"Erro durante execução: {str(e)}")
            return False, ""

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Executa testes do projeto AutoCura")
    parser.add_argument(
        "--tipo",
        choices=["unit", "integration", "e2e"],
        help="Tipo de teste a executar"
    )
    parser.add_argument(
        "--args",
        nargs="*",
        help="Argumentos adicionais para pytest"
    )
    
    args = parser.parse_args()
    
    executor = ExecutorTestes()
    sucesso, relatorio = executor.executar(args.tipo, args.args)
    
    if not sucesso:
        print("\nErros encontrados:")
        for erro in executor.erros:
            print(f"- {erro}")
            
    if executor.avisos:
        print("\nAvisos:")
        for aviso in executor.avisos:
            print(f"- {aviso}")
            
    if relatorio:
        print(f"\nRelatório gerado: {relatorio}")
        
    sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main() 