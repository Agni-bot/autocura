#!/usr/bin/env python3
"""
Script para executar testes e gerar relatórios de forma automatizada.
"""
import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestRunner:
    """Classe responsável por executar testes e gerar relatórios."""
    
    def __init__(self):
        """Inicializa o runner de testes."""
        self.root_dir = Path(__file__).parent.parent
        self.test_dir = self.root_dir / "tests"
        self.results_dir = self.root_dir / "test-results"
        self.coverage_dir = self.root_dir / "htmlcov"
        
    def setup(self):
        """Prepara o ambiente para execução dos testes."""
        logger.info("Preparando ambiente para testes...")
        
        # Cria diretórios de resultados se não existirem
        self.results_dir.mkdir(exist_ok=True)
        
        # Limpa resultados anteriores
        if self.coverage_dir.exists():
            shutil.rmtree(self.coverage_dir)
        
        # Ativa ambiente virtual se existir
        venv_path = self.root_dir / "venv"
        if venv_path.exists():
            if sys.platform == "win32":
                activate_script = venv_path / "Scripts" / "activate.bat"
            else:
                activate_script = venv_path / "bin" / "activate"
            
            if activate_script.exists():
                logger.info("Ativando ambiente virtual...")
                os.environ["VIRTUAL_ENV"] = str(venv_path)
                os.environ["PATH"] = f"{venv_path}/bin:{os.environ['PATH']}"
    
    def run_tests(self, args: Optional[List[str]] = None) -> bool:
        """
        Executa os testes com as configurações especificadas.
        
        Args:
            args: Argumentos adicionais para o pytest
            
        Returns:
            bool: True se todos os testes passaram, False caso contrário
        """
        logger.info("Iniciando execução dos testes...")
        
        # Comando base do pytest
        cmd = [
            "pytest",
            "--verbose",
            "--tb=long",
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-fail-under=80",
            "--durations=10",
            "--maxfail=3",
            f"--junitxml={self.results_dir}/junit.xml",
            f"--html={self.results_dir}/report.html"
        ]
        
        # Adiciona argumentos extras se fornecidos
        if args:
            cmd.extend(args)
        
        try:
            # Executa os testes
            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Exibe saída
            print(result.stdout)
            
            # Verifica se houve erros
            if result.returncode != 0:
                logger.error("Testes falharam!")
                print(result.stderr)
                return False
            
            logger.info("Todos os testes passaram com sucesso!")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao executar testes: {e}")
            print(e.stdout)
            print(e.stderr)
            return False
    
    def generate_report(self):
        """Gera relatório final dos testes."""
        logger.info("Gerando relatório final...")
        
        # Cria arquivo de relatório
        report_path = self.results_dir / "test_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Relatório de Testes\n\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Adiciona informações do ambiente
            f.write("## Ambiente\n\n")
            f.write(f"- Python: {sys.version}\n")
            f.write(f"- Sistema: {sys.platform}\n")
            f.write(f"- Diretório: {self.root_dir}\n\n")
            
            # Adiciona links para relatórios
            f.write("## Relatórios\n\n")
            f.write("- [Relatório HTML](report.html)\n")
            f.write("- [Relatório JUnit](junit.xml)\n")
            f.write("- [Cobertura de Código](htmlcov/index.html)\n")
        
        logger.info(f"Relatório gerado em: {report_path}")

def main():
    """Função principal do script."""
    # Obtém argumentos da linha de comando
    args = sys.argv[1:] if len(sys.argv) > 1 else None
    
    # Inicializa e executa o runner
    runner = TestRunner()
    runner.setup()
    
    if runner.run_tests(args):
        runner.generate_report()
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 