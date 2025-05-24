#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para executar todos os testes do projeto AutoCura.
Inclui testes unitários, de integração e end-to-end.
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

class ExecutorTodosTestes:
    """Executor de todos os testes do projeto AutoCura."""

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
        self.dir_resultados = self.raiz / "test-results"
        self.dir_resultados.mkdir(exist_ok=True)
        
        # Tipos de teste
        self.tipos_teste = [
            "unit",
            "integration",
            "e2e"
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
            import requests
            import docker
            import kubernetes
        except ImportError as e:
            self.erros.append(f"Dependência não encontrada: {str(e)}")
            return False
            
        # Verifica serviços necessários
        try:
            # Verifica Docker
            subprocess.run(
                ["docker", "info"],
                check=True,
                capture_output=True
            )
            
            # Verifica Kubernetes
            subprocess.run(
                ["kubectl", "cluster-info"],
                check=True,
                capture_output=True
            )
            
        except subprocess.CalledProcessError as e:
            self.erros.append(f"Serviço não disponível: {str(e)}")
            return False
            
        return True

    def executar_tipo_teste(self, tipo: str, args: List[str] = None) -> bool:
        """Executa um tipo específico de teste.
        
        Args:
            tipo: Tipo de teste (unit, integration, e2e)
            args: Argumentos adicionais para pytest
            
        Returns:
            bool: True se os testes passaram
        """
        logger.info(f"Executando testes {tipo}...")
        
        # Script específico para o tipo de teste
        script = self.raiz / "scripts" / f"run_tests_{tipo}.py"
        if not script.exists():
            self.erros.append(f"Script não encontrado: {script}")
            return False
            
        # Argumentos para o script
        cmd = [sys.executable, str(script)]
        if args:
            cmd.extend(args)
            
        try:
            # Executa script
            resultado = subprocess.run(
                cmd,
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
        
        if not self.verificar_ambiente():
            return False
            
        sucesso = True
        for tipo in self.tipos_teste:
            if not self.executar_tipo_teste(tipo, args):
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
        nome_arquivo = f"testes_completos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        caminho_relatorio = self.dir_resultados / nome_arquivo
        
        # Salvar relatório
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2)
            
        return str(caminho_relatorio)

    def executar(self, tipo: str = None, args: List[str] = None) -> Tuple[bool, str]:
        """Executa os testes.
        
        Args:
            tipo: Tipo específico de teste (opcional)
            args: Argumentos adicionais para pytest
            
        Returns:
            Tuple[bool, str]: (sucesso, caminho_relatorio)
        """
        logger.info("Iniciando execução de todos os testes...")
        
        try:
            if tipo:
                if tipo not in self.tipos_teste:
                    self.erros.append(f"Tipo de teste inválido: {tipo}")
                    return False, ""
                    
                sucesso = self.executar_tipo_teste(tipo, args)
            else:
                sucesso = self.executar_todos_testes(args)
                
            relatorio = self.gerar_relatorio()
            
            if sucesso:
                logger.info("Todos os testes concluídos com sucesso!")
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
    
    parser = argparse.ArgumentParser(description="Executa todos os testes do projeto AutoCura")
    parser.add_argument(
        "--tipo",
        choices=["unit", "integration", "e2e"],
        help="Tipo específico de teste a executar"
    )
    parser.add_argument(
        "--args",
        nargs="*",
        help="Argumentos adicionais para pytest"
    )
    
    args = parser.parse_args()
    
    executor = ExecutorTodosTestes()
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