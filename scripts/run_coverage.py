#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para executar testes de cobertura do projeto AutoCura.
Analisa a cobertura de código dos testes unitários.
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

class ExecutorCobertura:
    """Executor de testes de cobertura do projeto AutoCura."""

    def __init__(self, raiz: str = "."):
        """Inicializa o executor.
        
        Args:
            raiz: Diretório raiz do projeto
        """
        self.raiz = Path(raiz)
        self.erros: List[str] = []
        self.avisos: List[str] = []
        self.resultados: Dict[str, Dict] = {}
        
        # Diretório de resultados
        self.dir_resultados = self.raiz / "test-results/coverage"
        self.dir_resultados.mkdir(parents=True, exist_ok=True)
        
        # Módulos a testar
        self.modulos = [
            "core",
            "monitoramento",
            "etica",
            "diagnostico"
        ]

    def verificar_ambiente(self) -> bool:
        """Verifica se o ambiente está pronto para os testes.
        
        Returns:
            bool: True se o ambiente está pronto
        """
        logger.info("Verificando ambiente...")
        
        # Verifica dependências
        try:
            import pytest
            import pytest_cov
        except ImportError as e:
            self.erros.append(f"Dependência não encontrada: {str(e)}")
            return False
            
        return True

    def executar_cobertura_modulo(self, modulo: str, args: List[str] = None) -> bool:
        """Executa testes de cobertura para um módulo específico.
        
        Args:
            modulo: Nome do módulo
            args: Argumentos adicionais para pytest
            
        Returns:
            bool: True se os testes passaram
        """
        logger.info(f"Executando cobertura para {modulo}...")
        
        # Diretório de testes do módulo
        dir_teste = self.raiz / "tests/unit" / modulo
        if not dir_teste.exists():
            self.avisos.append(f"Diretório de testes não encontrado para {modulo}")
            return False
            
        # Argumentos padrão
        pytest_args = [
            sys.executable, "-m", "pytest",
            str(dir_teste),
            "-v",
            "--cov", f"modulos/{modulo}",
            "--cov-report", "term-missing",
            "--cov-report", "html",
            "--cov-report", "xml",
            "--cov-fail-under", "80",
            "--junitxml", str(self.dir_resultados / f"junit_{modulo}.xml"),
            "--html", str(self.dir_resultados / f"report_{modulo}.html")
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
            self.resultados[modulo] = {
                "sucesso": True,
                "saida": resultado.stdout,
                "erro": resultado.stderr
            }
            
            logger.info(f"Cobertura de {modulo} executada com sucesso!")
            return True
            
        except subprocess.CalledProcessError as e:
            self.resultados[modulo] = {
                "sucesso": False,
                "saida": e.stdout,
                "erro": e.stderr
            }
            
            self.erros.append(f"Erro ao executar cobertura de {modulo}: {str(e)}")
            return False

    def executar_toda_cobertura(self, args: List[str] = None) -> bool:
        """Executa testes de cobertura para todos os módulos.
        
        Args:
            args: Argumentos adicionais para pytest
            
        Returns:
            bool: True se todos os testes passaram
        """
        logger.info("Executando cobertura para todos os módulos...")
        
        if not self.verificar_ambiente():
            return False
            
        sucesso = True
        for modulo in self.modulos:
            if not self.executar_cobertura_modulo(modulo, args):
                sucesso = False
                
        return sucesso

    def gerar_relatorio(self) -> str:
        """Gera relatório de cobertura.
        
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
        nome_arquivo = f"cobertura_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        caminho_relatorio = self.dir_resultados / nome_arquivo
        
        # Salvar relatório
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2)
            
        return str(caminho_relatorio)

    def executar(self, modulo: str = None, args: List[str] = None) -> Tuple[bool, str]:
        """Executa os testes de cobertura.
        
        Args:
            modulo: Módulo específico para testar (opcional)
            args: Argumentos adicionais para pytest
            
        Returns:
            Tuple[bool, str]: (sucesso, caminho_relatorio)
        """
        logger.info("Iniciando execução de testes de cobertura...")
        
        try:
            if modulo:
                if modulo not in self.modulos:
                    self.erros.append(f"Módulo inválido: {modulo}")
                    return False, ""
                    
                sucesso = self.executar_cobertura_modulo(modulo, args)
            else:
                sucesso = self.executar_toda_cobertura(args)
                
            relatorio = self.gerar_relatorio()
            
            if sucesso:
                logger.info("Testes de cobertura concluídos com sucesso!")
            else:
                logger.error("Testes de cobertura encontraram erros!")
                
            if self.avisos:
                logger.warning("Avisos encontrados durante os testes")
                
            return sucesso, relatorio
            
        except Exception as e:
            self.erros.append(f"Erro durante execução: {str(e)}")
            return False, ""

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Executa testes de cobertura do projeto AutoCura")
    parser.add_argument(
        "--modulo",
        choices=["core", "monitoramento", "etica", "diagnostico"],
        help="Módulo específico para testar"
    )
    parser.add_argument(
        "--args",
        nargs="*",
        help="Argumentos adicionais para pytest"
    )
    
    args = parser.parse_args()
    
    executor = ExecutorCobertura()
    sucesso, relatorio = executor.executar(args.modulo, args.args)
    
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