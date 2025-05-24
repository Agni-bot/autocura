#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para executar testes de performance do projeto AutoCura.
Avalia o desempenho do sistema sob diferentes cargas.
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

class ExecutorPerformance:
    """Executor de testes de performance do projeto AutoCura."""

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
        self.dir_resultados = self.raiz / "test-results/performance"
        self.dir_resultados.mkdir(parents=True, exist_ok=True)
        
        # Cenários de teste
        self.cenarios = [
            "carga_baixa",
            "carga_media",
            "carga_alta",
            "estresse",
            "longa_duracao"
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
            import locust
            import psutil
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

    def preparar_ambiente(self) -> bool:
        """Prepara o ambiente para os testes.
        
        Returns:
            bool: True se o ambiente foi preparado com sucesso
        """
        logger.info("Preparando ambiente...")
        
        try:
            # Inicia serviços necessários
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=self.raiz,
                check=True,
                capture_output=True
            )
            
            # Aguarda serviços estarem prontos
            time.sleep(10)
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.erros.append(f"Erro ao preparar ambiente: {str(e)}")
            return False

    def executar_cenario(self, cenario: str, args: List[str] = None) -> bool:
        """Executa um cenário de teste específico.
        
        Args:
            cenario: Nome do cenário
            args: Argumentos adicionais para locust
            
        Returns:
            bool: True se os testes passaram
        """
        logger.info(f"Executando cenário {cenario}...")
        
        # Diretório do cenário
        dir_cenario = self.raiz / "tests/performance" / cenario
        if not dir_cenario.exists():
            self.avisos.append(f"Diretório de cenário não encontrado: {cenario}")
            return False
            
        # Argumentos padrão
        locust_args = [
            sys.executable, "-m", "locust",
            "-f", str(dir_cenario / "locustfile.py"),
            "--headless",
            "--users", "10",
            "--spawn-rate", "1",
            "--run-time", "1m",
            "--html", str(self.dir_resultados / f"report_{cenario}.html")
        ]
        
        # Adiciona argumentos personalizados
        if args:
            locust_args.extend(args)
            
        try:
            # Executa testes
            resultado = subprocess.run(
                locust_args,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Salva resultado
            self.resultados[cenario] = {
                "sucesso": True,
                "saida": resultado.stdout,
                "erro": resultado.stderr
            }
            
            logger.info(f"Cenário {cenario} executado com sucesso!")
            return True
            
        except subprocess.CalledProcessError as e:
            self.resultados[cenario] = {
                "sucesso": False,
                "saida": e.stdout,
                "erro": e.stderr
            }
            
            self.erros.append(f"Erro ao executar cenário {cenario}: {str(e)}")
            return False

    def executar_todos_cenarios(self, args: List[str] = None) -> bool:
        """Executa todos os cenários de teste.
        
        Args:
            args: Argumentos adicionais para locust
            
        Returns:
            bool: True se todos os testes passaram
        """
        logger.info("Executando todos os cenários...")
        
        if not self.verificar_ambiente():
            return False
            
        if not self.preparar_ambiente():
            return False
            
        sucesso = True
        for cenario in self.cenarios:
            if not self.executar_cenario(cenario, args):
                sucesso = False
                
        return sucesso

    def limpar_ambiente(self):
        """Limpa o ambiente após os testes."""
        logger.info("Limpando ambiente...")
        
        try:
            # Para serviços
            subprocess.run(
                ["docker-compose", "down"],
                cwd=self.raiz,
                check=True,
                capture_output=True
            )
            
        except subprocess.CalledProcessError as e:
            self.avisos.append(f"Erro ao limpar ambiente: {str(e)}")

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
        nome_arquivo = f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        caminho_relatorio = self.dir_resultados / nome_arquivo
        
        # Salvar relatório
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2)
            
        return str(caminho_relatorio)

    def executar(self, cenario: str = None, args: List[str] = None) -> Tuple[bool, str]:
        """Executa os testes de performance.
        
        Args:
            cenario: Cenário específico para testar (opcional)
            args: Argumentos adicionais para locust
            
        Returns:
            Tuple[bool, str]: (sucesso, caminho_relatorio)
        """
        logger.info("Iniciando execução de testes de performance...")
        
        try:
            if cenario:
                if cenario not in self.cenarios:
                    self.erros.append(f"Cenário inválido: {cenario}")
                    return False, ""
                    
                sucesso = self.executar_cenario(cenario, args)
            else:
                sucesso = self.executar_todos_cenarios(args)
                
            relatorio = self.gerar_relatorio()
            
            if sucesso:
                logger.info("Testes de performance concluídos com sucesso!")
            else:
                logger.error("Testes de performance encontraram erros!")
                
            if self.avisos:
                logger.warning("Avisos encontrados durante os testes")
                
            return sucesso, relatorio
            
        except Exception as e:
            self.erros.append(f"Erro durante execução: {str(e)}")
            return False, ""
            
        finally:
            self.limpar_ambiente()

def main():
    """Função principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Executa testes de performance do projeto AutoCura")
    parser.add_argument(
        "--cenario",
        choices=["carga_baixa", "carga_media", "carga_alta", "estresse", "longa_duracao"],
        help="Cenário específico para testar"
    )
    parser.add_argument(
        "--args",
        nargs="*",
        help="Argumentos adicionais para locust"
    )
    
    args = parser.parse_args()
    
    executor = ExecutorPerformance()
    sucesso, relatorio = executor.executar(args.cenario, args.args)
    
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