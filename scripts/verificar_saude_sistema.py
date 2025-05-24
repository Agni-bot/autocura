#!/usr/bin/env python3
"""
Script de Verificação de Saúde do Sistema AutoCura
=================================================

Este script executa verificações completas da saúde do sistema,
incluindo módulos, APIs, dependências e integridade dos dados.
"""

import asyncio
import json
import sys
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import importlib.util

class SystemHealthChecker:
    """Verificador de saúde do sistema"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "timestamp": time.time(),
            "overall_status": "unknown",
            "checks": {},
            "summary": {},
            "recommendations": []
        }
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Executa todas as verificações de saúde"""
        print("🔍 Iniciando verificação completa de saúde do sistema...")
        
        # Lista de verificações a executar
        checks = [
            ("structure", self._check_project_structure),
            ("dependencies", self._check_dependencies),
            ("imports", self._check_imports),
            ("api_health", self._check_api_health),
            ("modules", self._check_modules),
            ("database", self._check_database_connections),
            ("memory", self._check_memory_integrity),
            ("configuration", self._check_configuration),
            ("tests", self._check_test_status),
            ("logs", self._check_logs_health)
        ]
        
        for check_name, check_func in checks:
            print(f"⏳ Executando verificação: {check_name}")
            try:
                result = await check_func()
                self.results["checks"][check_name] = result
                print(f"✅ {check_name}: {result['status']}")
            except Exception as e:
                self.results["checks"][check_name] = {
                    "status": "error",
                    "error": str(e),
                    "details": {}
                }
                print(f"❌ {check_name}: ERRO - {e}")
        
        # Calcula status geral
        self._calculate_overall_status()
        self._generate_summary()
        self._generate_recommendations()
        
        return self.results
    
    async def _check_project_structure(self) -> Dict[str, Any]:
        """Verifica estrutura do projeto"""
        required_dirs = [
            "src", "modulos", "tests", "docs", "config", 
            "scripts", "docker", "reports"
        ]
        required_files = [
            "main.py", "README.md", "requirements.txt",
            "memoria_compartilhada.json"
        ]
        
        missing_dirs = []
        missing_files = []
        
        for directory in required_dirs:
            if not Path(directory).exists():
                missing_dirs.append(directory)
        
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
        
        status = "healthy" if not missing_dirs and not missing_files else "warning"
        
        return {
            "status": status,
            "details": {
                "missing_directories": missing_dirs,
                "missing_files": missing_files,
                "total_dirs_checked": len(required_dirs),
                "total_files_checked": len(required_files)
            }
        }
    
    async def _check_dependencies(self) -> Dict[str, Any]:
        """Verifica dependências do Python"""
        try:
            # Lê requirements.txt
            if Path("requirements.txt").exists():
                with open("requirements.txt", "r") as f:
                    requirements = f.read().splitlines()
            else:
                requirements = []
            
            missing_packages = []
            installed_packages = []
            
            for req in requirements:
                if req.strip() and not req.startswith("#"):
                    package_name = req.split("==")[0].split(">=")[0].split("<=")[0]
                    try:
                        importlib.import_module(package_name.replace("-", "_"))
                        installed_packages.append(package_name)
                    except ImportError:
                        missing_packages.append(package_name)
            
            status = "healthy" if not missing_packages else "error"
            
            return {
                "status": status,
                "details": {
                    "total_requirements": len(requirements),
                    "installed_packages": installed_packages,
                    "missing_packages": missing_packages
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "details": {"error": str(e)}
            }
    
    async def _check_imports(self) -> Dict[str, Any]:
        """Verifica importações críticas"""
        critical_imports = [
            "fastapi",
            "uvicorn", 
            "pydantic",
            "asyncio",
            "json",
            "pathlib"
        ]
        
        failed_imports = []
        successful_imports = []
        
        for module_name in critical_imports:
            try:
                importlib.import_module(module_name)
                successful_imports.append(module_name)
            except ImportError:
                failed_imports.append(module_name)
        
        status = "healthy" if not failed_imports else "error"
        
        return {
            "status": status,
            "details": {
                "successful_imports": successful_imports,
                "failed_imports": failed_imports,
                "total_checked": len(critical_imports)
            }
        }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Verifica saúde da API"""
        endpoints_to_check = [
            "/",
            "/health", 
            "/metrics",
            "/modules/status",
            "/dashboard/data"
        ]
        
        api_status = {}
        api_running = False
        
        try:
            # Verifica se API está respondendo
            response = requests.get(f"{self.base_url}/", timeout=5)
            api_running = response.status_code == 200
            
            if api_running:
                for endpoint in endpoints_to_check:
                    try:
                        resp = requests.get(f"{self.base_url}{endpoint}", timeout=3)
                        api_status[endpoint] = {
                            "status_code": resp.status_code,
                            "response_time": resp.elapsed.total_seconds(),
                            "healthy": resp.status_code < 400
                        }
                    except Exception as e:
                        api_status[endpoint] = {
                            "status_code": None,
                            "error": str(e),
                            "healthy": False
                        }
        except Exception as e:
            api_running = False
        
        status = "healthy" if api_running and all(ep.get("healthy", False) for ep in api_status.values()) else "error"
        
        return {
            "status": status,
            "details": {
                "api_running": api_running,
                "endpoints": api_status,
                "base_url": self.base_url
            }
        }
    
    async def _check_modules(self) -> Dict[str, Any]:
        """Verifica módulos do sistema"""
        modules_path = Path("modulos")
        expected_modules = [
            "observabilidade", "ia", "seguranca", 
            "diagnostico", "monitoramento"
        ]
        
        found_modules = []
        missing_modules = []
        module_details = {}
        
        for module_name in expected_modules:
            module_path = modules_path / module_name
            if module_path.exists():
                found_modules.append(module_name)
                module_details[module_name] = {
                    "has_src": (module_path / "src").exists(),
                    "has_tests": (module_path / "tests").exists(),
                    "has_readme": (module_path / "README.md").exists(),
                    "python_files": len(list(module_path.rglob("*.py")))
                }
            else:
                missing_modules.append(module_name)
        
        status = "healthy" if not missing_modules else "warning"
        
        return {
            "status": status,
            "details": {
                "found_modules": found_modules,
                "missing_modules": missing_modules,
                "module_details": module_details,
                "total_expected": len(expected_modules)
            }
        }
    
    async def _check_database_connections(self) -> Dict[str, Any]:
        """Verifica conexões com banco de dados"""
        # Por enquanto, verifica apenas Redis (se estiver configurado)
        connections = {}
        
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            r.ping()
            connections["redis"] = {"status": "connected", "host": "localhost", "port": 6379}
        except Exception as e:
            connections["redis"] = {"status": "error", "error": str(e)}
        
        # Placeholder para outras conexões (PostgreSQL, etc.)
        
        all_connected = all(conn.get("status") == "connected" for conn in connections.values())
        status = "healthy" if all_connected else "warning"
        
        return {
            "status": status,
            "details": {
                "connections": connections,
                "total_connections": len(connections)
            }
        }
    
    async def _check_memory_integrity(self) -> Dict[str, Any]:
        """Verifica integridade da memória compartilhada"""
        memory_file = Path("memoria_compartilhada.json")
        
        if not memory_file.exists():
            return {
                "status": "error",
                "details": {"error": "Arquivo de memória compartilhada não encontrado"}
            }
        
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                memory_data = json.load(f)
            
            # Verifica estruturas essenciais
            required_keys = [
                "log_eventos", "memoria_tecnica", "estado_atual",
                "historico_interacoes"
            ]
            
            missing_keys = [key for key in required_keys if key not in memory_data]
            
            status = "healthy" if not missing_keys else "warning"
            
            return {
                "status": status,
                "details": {
                    "file_size": memory_file.stat().st_size,
                    "total_events": len(memory_data.get("log_eventos", [])),
                    "missing_keys": missing_keys,
                    "last_update": memory_data.get("ultima_atualizacao", "unknown")
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "details": {"error": str(e)}
            }
    
    async def _check_configuration(self) -> Dict[str, Any]:
        """Verifica arquivos de configuração"""
        config_files = [
            "config/config.yaml",
            "docker/docker-compose.yml"
        ]
        
        found_configs = []
        missing_configs = []
        
        for config_file in config_files:
            if Path(config_file).exists():
                found_configs.append(config_file)
            else:
                missing_configs.append(config_file)
        
        status = "healthy" if not missing_configs else "warning"
        
        return {
            "status": status,
            "details": {
                "found_configs": found_configs,
                "missing_configs": missing_configs,
                "total_checked": len(config_files)
            }
        }
    
    async def _check_test_status(self) -> Dict[str, Any]:
        """Verifica status dos testes"""
        try:
            # Executa pytest para verificar status dos testes
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=no", "-q"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse da saída
            output_lines = result.stdout.split('\n')
            
            # Procura por informações de testes
            test_info = {}
            for line in output_lines:
                if "passed" in line or "failed" in line or "error" in line:
                    test_info["summary"] = line.strip()
                    break
            
            status = "healthy" if result.returncode == 0 else "warning"
            
            return {
                "status": status,
                "details": {
                    "return_code": result.returncode,
                    "test_summary": test_info.get("summary", "No summary available"),
                    "stdout": result.stdout[:500],  # Limita saída
                    "stderr": result.stderr[:500] if result.stderr else ""
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "details": {"error": str(e)}
            }
    
    async def _check_logs_health(self) -> Dict[str, Any]:
        """Verifica saúde dos logs"""
        logs_dir = Path("logs")
        
        if not logs_dir.exists():
            return {
                "status": "warning",
                "details": {"error": "Diretório de logs não encontrado"}
            }
        
        log_files = list(logs_dir.glob("*.log"))
        
        recent_logs = []
        old_logs = []
        current_time = time.time()
        
        for log_file in log_files:
            file_age = current_time - log_file.stat().st_mtime
            if file_age < 86400:  # 24 horas
                recent_logs.append(str(log_file))
            else:
                old_logs.append(str(log_file))
        
        status = "healthy" if recent_logs else "warning"
        
        return {
            "status": status,
            "details": {
                "total_log_files": len(log_files),
                "recent_logs": recent_logs,
                "old_logs": old_logs,
                "logs_directory": str(logs_dir)
            }
        }
    
    def _calculate_overall_status(self) -> None:
        """Calcula status geral do sistema"""
        statuses = [check.get("status", "error") for check in self.results["checks"].values()]
        
        if "error" in statuses:
            self.results["overall_status"] = "error"
        elif "warning" in statuses:
            self.results["overall_status"] = "warning"
        else:
            self.results["overall_status"] = "healthy"
    
    def _generate_summary(self) -> None:
        """Gera resumo das verificações"""
        checks = self.results["checks"]
        
        self.results["summary"] = {
            "total_checks": len(checks),
            "healthy_checks": len([c for c in checks.values() if c.get("status") == "healthy"]),
            "warning_checks": len([c for c in checks.values() if c.get("status") == "warning"]),
            "error_checks": len([c for c in checks.values() if c.get("status") == "error"]),
            "overall_health_percentage": round(
                (len([c for c in checks.values() if c.get("status") == "healthy"]) / len(checks)) * 100, 2
            )
        }
    
    def _generate_recommendations(self) -> None:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        for check_name, check_result in self.results["checks"].items():
            if check_result.get("status") == "error":
                if check_name == "dependencies":
                    missing = check_result.get("details", {}).get("missing_packages", [])
                    if missing:
                        recommendations.append(f"Instalar pacotes faltantes: {', '.join(missing)}")
                
                elif check_name == "api_health":
                    recommendations.append("Verificar se a API está rodando e acessível")
                
                elif check_name == "imports":
                    failed = check_result.get("details", {}).get("failed_imports", [])
                    if failed:
                        recommendations.append(f"Corrigir importações falhando: {', '.join(failed)}")
            
            elif check_result.get("status") == "warning":
                if check_name == "structure":
                    missing_dirs = check_result.get("details", {}).get("missing_directories", [])
                    missing_files = check_result.get("details", {}).get("missing_files", [])
                    if missing_dirs:
                        recommendations.append(f"Criar diretórios faltantes: {', '.join(missing_dirs)}")
                    if missing_files:
                        recommendations.append(f"Criar arquivos faltantes: {', '.join(missing_files)}")
                
                elif check_name == "modules":
                    missing = check_result.get("details", {}).get("missing_modules", [])
                    if missing:
                        recommendations.append(f"Implementar módulos faltantes: {', '.join(missing)}")
        
        self.results["recommendations"] = recommendations
    
    def save_report(self, filename: str = "health_check_report.json") -> None:
        """Salva relatório de saúde"""
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        report_path = reports_dir / filename
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Relatório salvo em: {report_path}")
    
    def print_summary(self) -> None:
        """Imprime resumo dos resultados"""
        print("\n" + "="*60)
        print("📊 RESUMO DA VERIFICAÇÃO DE SAÚDE")
        print("="*60)
        
        summary = self.results["summary"]
        status = self.results["overall_status"]
        
        # Status geral
        status_emoji = "✅" if status == "healthy" else "⚠️" if status == "warning" else "❌"
        print(f"\n{status_emoji} Status Geral: {status.upper()}")
        print(f"📈 Saúde do Sistema: {summary['overall_health_percentage']}%")
        
        # Resumo de verificações
        print(f"\n📋 Verificações Executadas: {summary['total_checks']}")
        print(f"✅ Saudáveis: {summary['healthy_checks']}")
        print(f"⚠️  Avisos: {summary['warning_checks']}")
        print(f"❌ Erros: {summary['error_checks']}")
        
        # Recomendações
        if self.results["recommendations"]:
            print(f"\n💡 RECOMENDAÇÕES ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results["recommendations"], 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*60)

async def main():
    """Função principal"""
    print("🏥 VERIFICADOR DE SAÚDE DO SISTEMA AUTOCURA")
    print("=" * 50)
    
    checker = SystemHealthChecker()
    results = await checker.run_all_checks()
    
    # Imprime resumo
    checker.print_summary()
    
    # Salva relatório
    checker.save_report()
    
    # Retorna código de saída baseado no status
    if results["overall_status"] == "healthy":
        sys.exit(0)
    elif results["overall_status"] == "warning":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main()) 