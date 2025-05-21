#!/usr/bin/env python3
"""
Script para executar testes em sequência.
"""
import os
import sys
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict, Any
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SequentialTestRunner:
    """Classe responsável por executar testes em sequência."""
    
    def __init__(self):
        """Inicializa o runner de testes sequenciais."""
        self.root_dir = Path(__file__).parent.parent
        self.test_dir = self.root_dir / "tests"
        self.results_dir = self.root_dir / "test-results"
        self.coverage_dir = self.root_dir / "htmlcov"
        self.temp_dir = self.root_dir / "test-temp"
        
    def setup(self):
        """Prepara o ambiente para execução dos testes."""
        logger.info("Preparando ambiente para testes sequenciais...")
        
        # Cria diretórios necessários
        self.results_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
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
    
    def get_test_files(self) -> List[Path]:
        """
        Obtém lista de arquivos de teste.
        
        Returns:
            List[Path]: Lista de arquivos de teste
        """
        test_files = []
        for path in self.test_dir.rglob("test_*.py"):
            if "unit" in str(path) or "integration" in str(path):
                test_files.append(path)
        return test_files
    
    def run_test_file(self, test_file: Path) -> Dict[str, Any]:
        """
        Executa um arquivo de teste específico.
        
        Args:
            test_file: Caminho do arquivo de teste
            
        Returns:
            Dict[str, Any]: Resultado da execução
        """
        logger.info(f"Executando teste: {test_file}")
        
        # Comando base do pytest
        cmd = [
            "pytest",
            str(test_file),
            "--verbose",
            "--tb=long",
            "--cov=src",
            "--cov-report=term-missing",
            f"--junitxml={self.temp_dir}/{test_file.stem}.xml",
            f"--html={self.temp_dir}/{test_file.stem}.html"
        ]
        
        try:
            # Executa o teste
            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "file": str(test_file),
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "file": str(test_file),
                "success": False,
                "output": e.stdout,
                "error": e.stderr,
                "returncode": e.returncode
            }
    
    def merge_coverage(self):
        """Mescla relatórios de cobertura."""
        logger.info("Mesclando relatórios de cobertura...")
        
        # Comando para mesclar cobertura
        cmd = [
            "coverage",
            "combine",
            str(self.temp_dir / "*.coverage")
        ]
        
        try:
            subprocess.run(cmd, check=True)
            
            # Gera relatório final
            cmd = [
                "coverage",
                "report",
                "-m",
                "--fail-under=80"
            ]
            
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao mesclar cobertura: {e}")
    
    def merge_reports(self):
        """Mescla relatórios de teste."""
        logger.info("Mesclando relatórios de teste...")
        
        # Mescla relatórios JUnit
        junit_files = list(self.temp_dir.glob("*.xml"))
        if junit_files:
            cmd = [
                "junitparser",
                "merge",
                *[str(f) for f in junit_files],
                str(self.results_dir / "junit.xml")
            ]
            
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Erro ao mesclar relatórios JUnit: {e}")
        
        # Mescla relatórios HTML
        html_files = list(self.temp_dir.glob("*.html"))
        if html_files:
            # TODO: Implementar mesclagem de relatórios HTML
            pass
    
    def run_tests(self) -> bool:
        """
        Executa os testes em sequência.
        
        Returns:
            bool: True se todos os testes passaram, False caso contrário
        """
        logger.info("Iniciando execução dos testes em sequência...")
        
        # Obtém arquivos de teste
        test_files = self.get_test_files()
        logger.info(f"Encontrados {len(test_files)} arquivos de teste")
        
        # Executa testes em sequência
        results = []
        for test_file in test_files:
            result = self.run_test_file(test_file)
            results.append(result)
            
            if result["success"]:
                logger.info(f"Teste passou: {test_file}")
            else:
                logger.error(f"Teste falhou: {test_file}")
                logger.error(result["error"])
        
        # Mescla relatórios
        self.merge_coverage()
        self.merge_reports()
        
        # Gera relatório final
        self.generate_report(results)
        
        # Verifica se todos os testes passaram
        return all(r["success"] for r in results)
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """
        Gera relatório final dos testes.
        
        Args:
            results: Resultados dos testes
        """
        logger.info("Gerando relatório final...")
        
        # Cria arquivo de relatório
        report_path = self.results_dir / "test_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Relatório de Testes Sequenciais\n\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Adiciona informações do ambiente
            f.write("## Ambiente\n\n")
            f.write(f"- Python: {sys.version}\n")
            f.write(f"- Sistema: {sys.platform}\n")
            f.write(f"- Diretório: {self.root_dir}\n\n")
            
            # Adiciona resumo dos testes
            f.write("## Resumo\n\n")
            total = len(results)
            passed = sum(1 for r in results if r["success"])
            failed = total - passed
            
            f.write(f"- Total de testes: {total}\n")
            f.write(f"- Testes passaram: {passed}\n")
            f.write(f"- Testes falharam: {failed}\n\n")
            
            # Adiciona detalhes dos testes
            f.write("## Detalhes\n\n")
            
            for result in results:
                f.write(f"### {result['file']}\n\n")
                f.write(f"- Status: {'✅ Passou' if result['success'] else '❌ Falhou'}\n")
                
                if not result["success"]:
                    f.write("\nErro:\n```\n")
                    f.write(result["error"])
                    f.write("\n```\n")
                
                f.write("\n")
            
            # Adiciona links para relatórios
            f.write("## Relatórios\n\n")
            f.write("- [Relatório HTML](report.html)\n")
            f.write("- [Relatório JUnit](junit.xml)\n")
            f.write("- [Cobertura de Código](htmlcov/index.html)\n")
        
        logger.info(f"Relatório gerado em: {report_path}")
    
    def cleanup(self):
        """Limpa arquivos temporários."""
        logger.info("Limpando arquivos temporários...")
        
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

def main():
    """Função principal do script."""
    # Inicializa e executa o runner
    runner = SequentialTestRunner()
    runner.setup()
    
    try:
        if runner.run_tests():
            logger.info("Todos os testes passaram com sucesso!")
            sys.exit(0)
        else:
            logger.error("Alguns testes falharam!")
            sys.exit(1)
    finally:
        runner.cleanup()

if __name__ == "__main__":
    main() 