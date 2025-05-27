"""
Automatizador de Testes do Sistema de Autocura.

Este módulo gerencia a execução automatizada de testes unitários e de integração,
incluindo validação de cobertura, geração de relatórios e notificações.
"""

import os
import sys
import pytest
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutomatizadorTestes:
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o automatizador de testes.
        
        Args:
            config: Dicionário com configurações opcionais
        """
        self.config = config or {}
        self.raiz_projeto = Path(__file__).parent.parent.parent
        self.cobertura_minima = self.config.get('cobertura_minima', 80)
        self.timeout = self.config.get('timeout', 300)  # 5 minutos
        
    def executar_testes_unitarios(self) -> bool:
        """
        Executa os testes unitários do projeto.
        
        Returns:
            bool: True se todos os testes passaram, False caso contrário
        """
        logger.info("Iniciando execução dos testes unitários...")
        
        try:
            resultado = pytest.main([
                str(self.raiz_projeto / "tests"),
                "--cov=src",
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-fail-under={}".format(self.cobertura_minima),
                "-v"
            ])
            
            return resultado == 0
            
        except Exception as e:
            logger.error(f"Erro ao executar testes unitários: {str(e)}")
            return False
            
    def executar_testes_integracao(self) -> bool:
        """
        Executa os testes de integração do projeto.
        
        Returns:
            bool: True se todos os testes passaram, False caso contrário
        """
        logger.info("Iniciando execução dos testes de integração...")
        
        try:
            resultado = pytest.main([
                str(self.raiz_projeto / "tests/integration"),
                "-v",
                "--timeout={}".format(self.timeout)
            ])
            
            return resultado == 0
            
        except Exception as e:
            logger.error(f"Erro ao executar testes de integração: {str(e)}")
            return False
            
    def gerar_relatorio(self, resultados: Dict[str, bool]) -> str:
        """
        Gera um relatório detalhado da execução dos testes.
        
        Args:
            resultados: Dicionário com os resultados dos testes
            
        Returns:
            str: Caminho do arquivo de relatório gerado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        relatorio_path = self.raiz_projeto / "relatorios" / f"testes_{timestamp}.md"
        
        with open(relatorio_path, "w", encoding="utf-8") as f:
            f.write("# Relatório de Testes\n\n")
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            for tipo_teste, sucesso in resultados.items():
                status = "✅ Passou" if sucesso else "❌ Falhou"
                f.write(f"## {tipo_teste}\n")
                f.write(f"Status: {status}\n\n")
                
        return str(relatorio_path)
        
    def executar_todos_testes(self) -> bool:
        """
        Executa todos os testes do projeto e gera relatório.
        
        Returns:
            bool: True se todos os testes passaram, False caso contrário
        """
        logger.info("Iniciando execução completa dos testes...")
        
        resultados = {
            "Testes Unitários": self.executar_testes_unitarios(),
            "Testes de Integração": self.executar_testes_integracao()
        }
        
        relatorio_path = self.gerar_relatorio(resultados)
        logger.info(f"Relatório gerado em: {relatorio_path}")
        
        return all(resultados.values())

def main():
    """Função principal para execução via linha de comando."""
    automatizador = AutomatizadorTestes()
    sucesso = automatizador.executar_todos_testes()
    
    if not sucesso:
        logger.error("Alguns testes falharam!")
        sys.exit(1)
        
    logger.info("Todos os testes passaram com sucesso!")
    sys.exit(0)

if __name__ == "__main__":
    main() 