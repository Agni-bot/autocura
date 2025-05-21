#!/usr/bin/env python3
"""
Script para executar testes em modo de cobertura.
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
import xml.etree.ElementTree as ET

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CoverageTestRunner:
    """Classe responsável por executar testes em modo de cobertura."""
    
    def __init__(self):
        """Inicializa o runner de testes em cobertura."""
        self.root_dir = Path(__file__).parent.parent
        self.test_dir = self.root_dir / "tests"
        self.results_dir = self.root_dir / "test-results"
        self.coverage_dir = self.root_dir / "htmlcov"
        self.temp_dir = self.root_dir / "test-temp"
        self.coverage_report_dir = self.root_dir / "coverage-reports"
        
    def setup(self):
        """Prepara o ambiente para execução dos testes."""
        logger.info("Preparando ambiente para testes em cobertura...")
        
        # Cria diretórios necessários
        self.results_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        self.coverage_report_dir.mkdir(exist_ok=True)
        
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
        Executa um arquivo de teste específico em modo cobertura.
        
        Args:
            test_file: Caminho do arquivo de teste
            
        Returns:
            Dict[str, Any]: Resultado da execução
        """
        logger.info(f"Executando teste em cobertura: {test_file}")
        
        # Comando base do pytest com cobertura
        cmd = [
            "pytest",
            str(test_file),
            "--verbose",
            "--tb=long",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-report=html",
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
            
            # Gera relatório XML
            cmd = [
                "coverage",
                "xml",
                "-o",
                str(self.coverage_report_dir / "coverage.xml")
            ]
            
            subprocess.run(cmd, check=True)
            
            # Gera relatório HTML
            cmd = [
                "coverage",
                "html",
                "-d",
                str(self.coverage_report_dir / "html")
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
    
    def analyze_coverage(self) -> Dict[str, Any]:
        """
        Analisa relatório de cobertura.
        
        Returns:
            Dict[str, Any]: Análise da cobertura
        """
        logger.info("Analisando relatório de cobertura...")
        
        coverage_file = self.coverage_report_dir / "coverage.xml"
        if not coverage_file.exists():
            logger.error("Arquivo de cobertura não encontrado")
            return {}
        
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            # Obtém métricas gerais
            metrics = root.find(".//coverage")
            if metrics is None:
                return {}
            
            coverage_data = {
                "line_rate": float(metrics.get("line-rate", 0)),
                "branch_rate": float(metrics.get("branch-rate", 0)),
                "lines_covered": int(metrics.get("lines-covered", 0)),
                "lines_valid": int(metrics.get("lines-valid", 0)),
                "branches_covered": int(metrics.get("branches-covered", 0)),
                "branches_valid": int(metrics.get("branches-valid", 0)),
                "packages": []
            }
            
            # Analisa pacotes
            for package in root.findall(".//package"):
                package_data = {
                    "name": package.get("name", ""),
                    "line_rate": float(package.get("line-rate", 0)),
                    "branch_rate": float(package.get("branch-rate", 0)),
                    "complexity": float(package.get("complexity", 0)),
                    "classes": []
                }
                
                # Analisa classes
                for class_elem in package.findall(".//class"):
                    class_data = {
                        "name": class_elem.get("name", ""),
                        "filename": class_elem.get("filename", ""),
                        "line_rate": float(class_elem.get("line-rate", 0)),
                        "branch_rate": float(class_elem.get("branch-rate", 0)),
                        "complexity": float(class_elem.get("complexity", 0)),
                        "methods": []
                    }
                    
                    # Analisa métodos
                    for method in class_elem.findall(".//method"):
                        method_data = {
                            "name": method.get("name", ""),
                            "line_rate": float(method.get("line-rate", 0)),
                            "branch_rate": float(method.get("branch-rate", 0)),
                            "complexity": float(method.get("complexity", 0))
                        }
                        class_data["methods"].append(method_data)
                    
                    package_data["classes"].append(class_data)
                
                coverage_data["packages"].append(package_data)
            
            return coverage_data
            
        except Exception as e:
            logger.error(f"Erro ao analisar cobertura: {e}")
            return {}
    
    def run_tests(self) -> bool:
        """
        Executa os testes em modo cobertura.
        
        Returns:
            bool: True se todos os testes passaram, False caso contrário
        """
        logger.info("Iniciando execução dos testes em cobertura...")
        
        # Obtém arquivos de teste
        test_files = self.get_test_files()
        logger.info(f"Encontrados {len(test_files)} arquivos de teste")
        
        # Executa testes em cobertura
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
        
        # Analisa cobertura
        coverage_data = self.analyze_coverage()
        
        # Gera relatório final
        self.generate_report(results, coverage_data)
        
        # Verifica se todos os testes passaram
        return all(r["success"] for r in results)
    
    def generate_report(self, results: List[Dict[str, Any]], coverage_data: Dict[str, Any]):
        """
        Gera relatório final dos testes.
        
        Args:
            results: Resultados dos testes
            coverage_data: Dados de cobertura
        """
        logger.info("Gerando relatório final...")
        
        # Cria arquivo de relatório
        report_path = self.results_dir / "test_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Relatório de Testes em Cobertura\n\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Adiciona informações do ambiente
            f.write("## Ambiente\n\n")
            f.write(f"- Python: {sys.version}\n")
            f.write(f"- Sistema: {sys.platform}\n")
            f.write(f"- Diretório: {self.root_dir}\n\n")
            
            # Adiciona resumo dos testes
            f.write("## Resumo dos Testes\n\n")
            total = len(results)
            passed = sum(1 for r in results if r["success"])
            failed = total - passed
            
            f.write(f"- Total de testes: {total}\n")
            f.write(f"- Testes passaram: {passed}\n")
            f.write(f"- Testes falharam: {failed}\n\n")
            
            # Adiciona resumo da cobertura
            f.write("## Resumo da Cobertura\n\n")
            
            if coverage_data:
                f.write(f"- Taxa de cobertura de linhas: {coverage_data['line_rate']:.2%}\n")
                f.write(f"- Taxa de cobertura de branches: {coverage_data['branch_rate']:.2%}\n")
                f.write(f"- Linhas cobertas: {coverage_data['lines_covered']}\n")
                f.write(f"- Linhas válidas: {coverage_data['lines_valid']}\n")
                f.write(f"- Branches cobertos: {coverage_data['branches_covered']}\n")
                f.write(f"- Branches válidos: {coverage_data['branches_valid']}\n\n")
                
                # Adiciona detalhes dos pacotes
                f.write("### Pacotes\n\n")
                
                for package in coverage_data["packages"]:
                    f.write(f"#### {package['name']}\n\n")
                    f.write(f"- Taxa de cobertura de linhas: {package['line_rate']:.2%}\n")
                    f.write(f"- Taxa de cobertura de branches: {package['branch_rate']:.2%}\n")
                    f.write(f"- Complexidade: {package['complexity']:.2f}\n\n")
                    
                    # Adiciona detalhes das classes
                    f.write("##### Classes\n\n")
                    
                    for class_elem in package["classes"]:
                        f.write(f"###### {class_elem['name']}\n\n")
                        f.write(f"- Arquivo: {class_elem['filename']}\n")
                        f.write(f"- Taxa de cobertura de linhas: {class_elem['line_rate']:.2%}\n")
                        f.write(f"- Taxa de cobertura de branches: {class_elem['branch_rate']:.2%}\n")
                        f.write(f"- Complexidade: {class_elem['complexity']:.2f}\n\n")
                        
                        # Adiciona detalhes dos métodos
                        f.write("###### Métodos\n\n")
                        
                        for method in class_elem["methods"]:
                            f.write(f"- {method['name']}\n")
                            f.write(f"  - Taxa de cobertura de linhas: {method['line_rate']:.2%}\n")
                            f.write(f"  - Taxa de cobertura de branches: {method['branch_rate']:.2%}\n")
                            f.write(f"  - Complexidade: {method['complexity']:.2f}\n\n")
            
            # Adiciona detalhes dos testes
            f.write("## Detalhes dos Testes\n\n")
            
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
            f.write("- [Cobertura de Código](coverage-reports/html/index.html)\n")
            f.write("- [Relatório XML de Cobertura](coverage-reports/coverage.xml)\n")
        
        logger.info(f"Relatório gerado em: {report_path}")
    
    def cleanup(self):
        """Limpa arquivos temporários."""
        logger.info("Limpando arquivos temporários...")
        
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

def main():
    """Função principal do script."""
    # Inicializa e executa o runner
    runner = CoverageTestRunner()
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