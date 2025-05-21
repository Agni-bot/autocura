#!/usr/bin/env python3
"""
Script para executar testes em modo de performance.
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
import time
import psutil
import statistics
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de performance."""
    cpu_percent: float
    memory_percent: float
    memory_used: int
    disk_io_read: int
    disk_io_write: int
    network_io_sent: int
    network_io_recv: int
    execution_time: float

class PerformanceMonitor:
    """Monitor de performance do sistema."""
    
    def __init__(self):
        """Inicializa o monitor de performance."""
        self.process = psutil.Process()
        self.start_time = time.time()
        self.metrics: List[PerformanceMetrics] = []
        
    def collect_metrics(self) -> PerformanceMetrics:
        """
        Coleta métricas de performance.
        
        Returns:
            PerformanceMetrics: Métricas coletadas
        """
        # CPU
        cpu_percent = self.process.cpu_percent()
        
        # Memória
        memory = self.process.memory_info()
        memory_percent = self.process.memory_percent()
        memory_used = memory.rss
        
        # Disco
        disk_io = self.process.io_counters()
        disk_io_read = disk_io.read_bytes
        disk_io_write = disk_io.write_bytes
        
        # Rede
        net_io = psutil.net_io_counters()
        network_io_sent = net_io.bytes_sent
        network_io_recv = net_io.bytes_recv
        
        # Tempo de execução
        execution_time = time.time() - self.start_time
        
        return PerformanceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used=memory_used,
            disk_io_read=disk_io_read,
            disk_io_write=disk_io_write,
            network_io_sent=network_io_sent,
            network_io_recv=network_io_recv,
            execution_time=execution_time
        )
    
    def start_monitoring(self, interval: float = 1.0):
        """
        Inicia monitoramento em background.
        
        Args:
            interval: Intervalo de coleta em segundos
        """
        def monitor():
            while True:
                metrics = self.collect_metrics()
                self.metrics.append(metrics)
                time.sleep(interval)
        
        self.monitor_thread = ThreadPoolExecutor(max_workers=1)
        self.monitor_thread.submit(monitor)
    
    def stop_monitoring(self):
        """Para o monitoramento."""
        self.monitor_thread.shutdown(wait=False)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtém resumo das métricas.
        
        Returns:
            Dict[str, Any]: Resumo das métricas
        """
        if not self.metrics:
            return {}
        
        return {
            "cpu": {
                "min": min(m.cpu_percent for m in self.metrics),
                "max": max(m.cpu_percent for m in self.metrics),
                "mean": statistics.mean(m.cpu_percent for m in self.metrics),
                "median": statistics.median(m.cpu_percent for m in self.metrics)
            },
            "memory": {
                "min": min(m.memory_percent for m in self.metrics),
                "max": max(m.memory_percent for m in self.metrics),
                "mean": statistics.mean(m.memory_percent for m in self.metrics),
                "median": statistics.median(m.memory_percent for m in self.metrics),
                "total_used": max(m.memory_used for m in self.metrics)
            },
            "disk": {
                "total_read": max(m.disk_io_read for m in self.metrics),
                "total_write": max(m.disk_io_write for m in self.metrics)
            },
            "network": {
                "total_sent": max(m.network_io_sent for m in self.metrics),
                "total_recv": max(m.network_io_recv for m in self.metrics)
            },
            "execution_time": max(m.execution_time for m in self.metrics)
        }

class PerformanceTestRunner:
    """Classe responsável por executar testes em modo de performance."""
    
    def __init__(self):
        """Inicializa o runner de testes em performance."""
        self.root_dir = Path(__file__).parent.parent
        self.test_dir = self.root_dir / "tests"
        self.results_dir = self.root_dir / "test-results"
        self.coverage_dir = self.root_dir / "htmlcov"
        self.temp_dir = self.root_dir / "test-temp"
        self.performance_dir = self.root_dir / "performance-reports"
        
    def setup(self):
        """Prepara o ambiente para execução dos testes."""
        logger.info("Preparando ambiente para testes em performance...")
        
        # Cria diretórios necessários
        self.results_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        self.performance_dir.mkdir(exist_ok=True)
        
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
        Executa um arquivo de teste específico em modo performance.
        
        Args:
            test_file: Caminho do arquivo de teste
            
        Returns:
            Dict[str, Any]: Resultado da execução
        """
        logger.info(f"Executando teste em performance: {test_file}")
        
        # Inicia monitor de performance
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
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
            start_time = time.time()
            result = subprocess.run(
                cmd,
                cwd=self.root_dir,
                check=True,
                capture_output=True,
                text=True
            )
            execution_time = time.time() - start_time
            
            # Para monitoramento
            monitor.stop_monitoring()
            
            # Obtém métricas
            performance_metrics = monitor.get_summary()
            
            # Salva métricas
            metrics_file = self.performance_dir / f"{test_file.stem}_metrics.json"
            with open(metrics_file, "w", encoding="utf-8") as f:
                json.dump(performance_metrics, f, indent=2)
            
            return {
                "file": str(test_file),
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode,
                "execution_time": execution_time,
                "performance_metrics": performance_metrics,
                "metrics_file": str(metrics_file)
            }
            
        except subprocess.CalledProcessError as e:
            # Para monitoramento
            monitor.stop_monitoring()
            
            # Obtém métricas
            performance_metrics = monitor.get_summary()
            
            # Salva métricas
            metrics_file = self.performance_dir / f"{test_file.stem}_metrics.json"
            with open(metrics_file, "w", encoding="utf-8") as f:
                json.dump(performance_metrics, f, indent=2)
            
            return {
                "file": str(test_file),
                "success": False,
                "output": e.stdout,
                "error": e.stderr,
                "returncode": e.returncode,
                "execution_time": time.time() - start_time,
                "performance_metrics": performance_metrics,
                "metrics_file": str(metrics_file)
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
        Executa os testes em modo performance.
        
        Returns:
            bool: True se todos os testes passaram, False caso contrário
        """
        logger.info("Iniciando execução dos testes em performance...")
        
        # Obtém arquivos de teste
        test_files = self.get_test_files()
        logger.info(f"Encontrados {len(test_files)} arquivos de teste")
        
        # Executa testes em performance
        results = []
        for test_file in test_files:
            result = self.run_test_file(test_file)
            results.append(result)
            
            if result["success"]:
                logger.info(f"Teste passou: {test_file}")
            else:
                logger.error(f"Teste falhou: {test_file}")
                logger.error(result["error"])
            
            logger.info(f"Tempo de execução: {result['execution_time']:.2f}s")
            logger.info(f"Métricas salvas em: {result['metrics_file']}")
        
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
            f.write("# Relatório de Testes em Performance\n\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Adiciona informações do ambiente
            f.write("## Ambiente\n\n")
            f.write(f"- Python: {sys.version}\n")
            f.write(f"- Sistema: {sys.platform}\n")
            f.write(f"- Diretório: {self.root_dir}\n")
            f.write(f"- CPU: {psutil.cpu_count()} cores\n")
            f.write(f"- Memória: {psutil.virtual_memory().total / (1024**3):.2f} GB\n\n")
            
            # Adiciona resumo dos testes
            f.write("## Resumo dos Testes\n\n")
            total = len(results)
            passed = sum(1 for r in results if r["success"])
            failed = total - passed
            
            f.write(f"- Total de testes: {total}\n")
            f.write(f"- Testes passaram: {passed}\n")
            f.write(f"- Testes falharam: {failed}\n\n")
            
            # Adiciona resumo de performance
            f.write("## Resumo de Performance\n\n")
            
            # Tempo total de execução
            total_time = sum(r["execution_time"] for r in results)
            f.write(f"- Tempo total de execução: {total_time:.2f}s\n")
            
            # Tempo médio por teste
            avg_time = total_time / total
            f.write(f"- Tempo médio por teste: {avg_time:.2f}s\n")
            
            # Teste mais rápido
            fastest = min(results, key=lambda r: r["execution_time"])
            f.write(f"- Teste mais rápido: {fastest['file']} ({fastest['execution_time']:.2f}s)\n")
            
            # Teste mais lento
            slowest = max(results, key=lambda r: r["execution_time"])
            f.write(f"- Teste mais lento: {slowest['file']} ({slowest['execution_time']:.2f}s)\n\n")
            
            # Adiciona detalhes dos testes
            f.write("## Detalhes dos Testes\n\n")
            
            for result in results:
                f.write(f"### {result['file']}\n\n")
                f.write(f"- Status: {'✅ Passou' if result['success'] else '❌ Falhou'}\n")
                f.write(f"- Tempo de execução: {result['execution_time']:.2f}s\n")
                
                if "performance_metrics" in result:
                    metrics = result["performance_metrics"]
                    
                    f.write("\n#### Métricas de Performance\n\n")
                    
                    # CPU
                    f.write("##### CPU\n\n")
                    f.write(f"- Mínimo: {metrics['cpu']['min']:.2f}%\n")
                    f.write(f"- Máximo: {metrics['cpu']['max']:.2f}%\n")
                    f.write(f"- Média: {metrics['cpu']['mean']:.2f}%\n")
                    f.write(f"- Mediana: {metrics['cpu']['median']:.2f}%\n\n")
                    
                    # Memória
                    f.write("##### Memória\n\n")
                    f.write(f"- Mínimo: {metrics['memory']['min']:.2f}%\n")
                    f.write(f"- Máximo: {metrics['memory']['max']:.2f}%\n")
                    f.write(f"- Média: {metrics['memory']['mean']:.2f}%\n")
                    f.write(f"- Mediana: {metrics['memory']['median']:.2f}%\n")
                    f.write(f"- Total usado: {metrics['memory']['total_used'] / (1024**2):.2f} MB\n\n")
                    
                    # Disco
                    f.write("##### Disco\n\n")
                    f.write(f"- Total lido: {metrics['disk']['total_read'] / (1024**2):.2f} MB\n")
                    f.write(f"- Total escrito: {metrics['disk']['total_write'] / (1024**2):.2f} MB\n\n")
                    
                    # Rede
                    f.write("##### Rede\n\n")
                    f.write(f"- Total enviado: {metrics['network']['total_sent'] / (1024**2):.2f} MB\n")
                    f.write(f"- Total recebido: {metrics['network']['total_recv'] / (1024**2):.2f} MB\n\n")
                
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
            f.write("- [Relatórios de Performance](performance-reports/)\n")
        
        logger.info(f"Relatório gerado em: {report_path}")
    
    def cleanup(self):
        """Limpa arquivos temporários."""
        logger.info("Limpando arquivos temporários...")
        
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

def main():
    """Função principal do script."""
    # Inicializa e executa o runner
    runner = PerformanceTestRunner()
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