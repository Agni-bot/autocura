#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para monitorar dependências do projeto AutoCura.
Verifica versões, vulnerabilidades e atualizações disponíveis.
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitorDependencias:
    """Monitor de dependências do projeto AutoCura."""

    def __init__(self, raiz: str = "."):
        """Inicializa o monitor.
        
        Args:
            raiz: Diretório raiz do projeto
        """
        self.raiz = Path(raiz)
        self.erros: List[str] = []
        self.avisos: List[str] = []
        self.dependencias: Dict[str, Dict] = {}
        
        # Arquivos de dependências
        self.arquivos_deps = {
            "requirements.txt": "pip",
            "requirements-test.txt": "pip",
            "package.json": "npm",
            "go.mod": "go"
        }

    def verificar_pip(self, arquivo: Path) -> Dict:
        """Verifica dependências Python.
        
        Args:
            arquivo: Caminho do arquivo requirements.txt
            
        Returns:
            Dict: Informações das dependências
        """
        try:
            # Instalar pip-tools se necessário
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pip-tools"],
                check=True,
                capture_output=True
            )
            
            # Gerar requirements.txt com versões fixas
            subprocess.run(
                [sys.executable, "-m", "pip-compile", str(arquivo)],
                check=True,
                capture_output=True
            )
            
            # Obter lista de pacotes instalados
            resultado = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                check=True,
                capture_output=True,
                text=True
            )
            
            pacotes = json.loads(resultado.stdout)
            
            # Verificar vulnerabilidades
            resultado = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json"],
                check=True,
                capture_output=True,
                text=True
            )
            
            vulnerabilidades = json.loads(resultado.stdout)
            
            return {
                "tipo": "pip",
                "pacotes": pacotes,
                "vulnerabilidades": vulnerabilidades
            }
            
        except subprocess.CalledProcessError as e:
            self.erros.append(f"Erro ao verificar dependências Python: {str(e)}")
            return {}

    def verificar_npm(self, arquivo: Path) -> Dict:
        """Verifica dependências Node.js.
        
        Args:
            arquivo: Caminho do arquivo package.json
            
        Returns:
            Dict: Informações das dependências
        """
        try:
            # Verificar vulnerabilidades
            resultado = subprocess.run(
                ["npm", "audit", "--json"],
                check=True,
                capture_output=True,
                text=True
            )
            
            vulnerabilidades = json.loads(resultado.stdout)
            
            # Listar pacotes
            resultado = subprocess.run(
                ["npm", "list", "--json"],
                check=True,
                capture_output=True,
                text=True
            )
            
            pacotes = json.loads(resultado.stdout)
            
            return {
                "tipo": "npm",
                "pacotes": pacotes,
                "vulnerabilidades": vulnerabilidades
            }
            
        except subprocess.CalledProcessError as e:
            self.erros.append(f"Erro ao verificar dependências Node.js: {str(e)}")
            return {}

    def verificar_go(self, arquivo: Path) -> Dict:
        """Verifica dependências Go.
        
        Args:
            arquivo: Caminho do arquivo go.mod
            
        Returns:
            Dict: Informações das dependências
        """
        try:
            # Verificar vulnerabilidades
            resultado = subprocess.run(
                ["gosec", "-fmt", "json", "./..."],
                check=True,
                capture_output=True,
                text=True
            )
            
            vulnerabilidades = json.loads(resultado.stdout)
            
            # Listar dependências
            resultado = subprocess.run(
                ["go", "list", "-m", "all"],
                check=True,
                capture_output=True,
                text=True
            )
            
            pacotes = resultado.stdout.splitlines()
            
            return {
                "tipo": "go",
                "pacotes": pacotes,
                "vulnerabilidades": vulnerabilidades
            }
            
        except subprocess.CalledProcessError as e:
            self.erros.append(f"Erro ao verificar dependências Go: {str(e)}")
            return {}

    def verificar_dependencias(self) -> bool:
        """Verifica todas as dependências do projeto.
        
        Returns:
            bool: True se não houver erros
        """
        logger.info("Verificando dependências...")
        
        for arquivo, tipo in self.arquivos_deps.items():
            caminho = self.raiz / arquivo
            if not caminho.exists():
                self.avisos.append(f"Arquivo de dependências não encontrado: {arquivo}")
                continue
                
            if tipo == "pip":
                self.dependencias[arquivo] = self.verificar_pip(caminho)
            elif tipo == "npm":
                self.dependencias[arquivo] = self.verificar_npm(caminho)
            elif tipo == "go":
                self.dependencias[arquivo] = self.verificar_go(caminho)
                
        return len(self.erros) == 0

    def gerar_relatorio(self) -> str:
        """Gera relatório de dependências.
        
        Returns:
            str: Caminho do arquivo de relatório
        """
        logger.info("Gerando relatório...")
        
        relatorio = {
            "data": datetime.now().isoformat(),
            "dependencias": self.dependencias,
            "erros": self.erros,
            "avisos": self.avisos
        }
        
        # Criar diretório de relatórios se não existir
        dir_relatorios = self.raiz / "relatorios"
        dir_relatorios.mkdir(exist_ok=True)
        
        # Nome do arquivo de relatório
        nome_arquivo = f"dependencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        caminho_relatorio = dir_relatorios / nome_arquivo
        
        # Salvar relatório
        with open(caminho_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2)
            
        return str(caminho_relatorio)

    def executar_monitoramento(self) -> Tuple[bool, str]:
        """Executa o monitoramento de dependências.
        
        Returns:
            Tuple[bool, str]: (sucesso, caminho_relatorio)
        """
        logger.info("Iniciando monitoramento de dependências...")
        
        try:
            self.verificar_dependencias()
            relatorio = self.gerar_relatorio()
            
            sucesso = len(self.erros) == 0
            
            if sucesso:
                logger.info("Monitoramento concluído com sucesso!")
            else:
                logger.error("Monitoramento encontrou erros!")
                
            if self.avisos:
                logger.warning("Avisos encontrados durante o monitoramento")
                
            return sucesso, relatorio
            
        except Exception as e:
            self.erros.append(f"Erro durante monitoramento: {str(e)}")
            return False, ""

def main():
    """Função principal."""
    monitor = MonitorDependencias()
    sucesso, relatorio = monitor.executar_monitoramento()
    
    if not sucesso:
        print("\nErros encontrados:")
        for erro in monitor.erros:
            print(f"- {erro}")
            
    if monitor.avisos:
        print("\nAvisos:")
        for aviso in monitor.avisos:
            print(f"- {aviso}")
            
    if relatorio:
        print(f"\nRelatório gerado: {relatorio}")
        
    sys.exit(0 if sucesso else 1)

if __name__ == "__main__":
    main() 