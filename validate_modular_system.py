#!/usr/bin/env python3
"""
Script de Validação Completa do Sistema Modular AutoCura
========================================================

Executa todos os testes para validar que a reorganização modular
foi bem-sucedida e o sistema está operacional.
"""

import requests
import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime

class ModularSystemValidator:
    """Validador completo do sistema modular"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.docker_url = "http://localhost:8001"  # Mesmo para docker
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []

    def log_test(self, test_name: str, success: bool, message: str = "", data: dict = None):
        """Registra resultado de um teste"""
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if message:
            print(f"  📝 {message}")
        if data:
            print(f"  📊 Dados: {json.dumps(data, indent=2)}")
        
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def test_api_connectivity(self):
        """Teste 1: Conectividade da API"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Conectividade API",
                    True,
                    f"API respondendo na porta 8001",
                    {"version": data.get("version"), "status": data.get("status")}
                )
                return True
            else:
                self.log_test("Conectividade API", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Conectividade API", False, f"Erro de conexão: {str(e)}")
            return False

    def test_health_endpoint(self):
        """Teste 2: Endpoint de saúde"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                modules_loaded = sum(1 for status in data.get("modules", {}).values() if status)
                total_modules = len(data.get("modules", {}))
                
                self.log_test(
                    "Health Check",
                    True,
                    f"Status: {data.get('status')} - Módulos: {modules_loaded}/{total_modules}",
                    data.get("modules")
                )
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Erro: {str(e)}")
            return False

    def test_modular_structure(self):
        """Teste 3: Estrutura modular"""
        try:
            response = requests.get(f"{self.base_url}/api/structure", timeout=10)
            if response.status_code == 200:
                data = response.json()
                structure_type = data.get("structure_type")
                organization = data.get("organization", {})
                
                if structure_type == "modular":
                    modules_count = len(organization)
                    self.log_test(
                        "Estrutura Modular",
                        True,
                        f"Tipo: {structure_type} - Módulos organizados: {modules_count}",
                        {"modules": list(organization.keys())}
                    )
                    return True
                else:
                    self.log_test("Estrutura Modular", False, f"Tipo inválido: {structure_type}")
                    return False
            else:
                self.log_test("Estrutura Modular", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Estrutura Modular", False, f"Erro: {str(e)}")
            return False

    def test_modules_loading(self):
        """Teste 4: Carregamento de módulos"""
        try:
            response = requests.get(f"{self.base_url}/api/modules", timeout=10)
            if response.status_code == 200:
                data = response.json()
                total = data.get("total_modules", 0)
                loaded = data.get("loaded_modules", 0)
                modules_status = data.get("modules_status", {})
                
                success = loaded > 0  # Pelo menos 1 módulo deve estar carregado
                self.log_test(
                    "Carregamento de Módulos",
                    success,
                    f"Módulos carregados: {loaded}/{total}",
                    modules_status
                )
                return success
            else:
                self.log_test("Carregamento de Módulos", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Carregamento de Módulos", False, f"Erro: {str(e)}")
            return False

    def test_docker_deployment(self):
        """Teste 5: Deployment Docker"""
        try:
            # Verifica se containers estão rodando
            result = subprocess.run(['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                containers = result.stdout
                autocura_containers = [line for line in containers.split('\n') 
                                     if 'autocura' in line.lower()]
                
                if autocura_containers:
                    self.log_test(
                        "Deployment Docker",
                        True,
                        f"Containers AutoCura encontrados: {len(autocura_containers)}",
                        {"containers": autocura_containers}
                    )
                    return True
                else:
                    self.log_test("Deployment Docker", False, "Nenhum container AutoCura encontrado")
                    return False
            else:
                self.log_test("Deployment Docker", False, "Erro ao executar docker ps")
                return False
        except Exception as e:
            self.log_test("Deployment Docker", False, f"Erro: {str(e)}")
            return False

    def test_file_structure(self):
        """Teste 6: Estrutura de arquivos"""
        try:
            autocura_dir = Path("autocura")
            expected_modules = ["core", "services", "monitoring", "security", "utils", "api"]
            
            if not autocura_dir.exists():
                self.log_test("Estrutura de Arquivos", False, "Diretório autocura/ não encontrado")
                return False
            
            existing_modules = [d.name for d in autocura_dir.iterdir() if d.is_dir()]
            found_modules = [m for m in expected_modules if m in existing_modules]
            
            success = len(found_modules) >= 4  # Pelo menos 4 módulos principais
            self.log_test(
                "Estrutura de Arquivos",
                success,
                f"Módulos encontrados: {len(found_modules)}/{len(expected_modules)}",
                {"found": found_modules, "expected": expected_modules}
            )
            return success
        except Exception as e:
            self.log_test("Estrutura de Arquivos", False, f"Erro: {str(e)}")
            return False

    def test_backup_integrity(self):
        """Teste 7: Integridade do backup"""
        try:
            backup_dir = Path("backup_reorganization")
            
            if not backup_dir.exists():
                self.log_test("Integridade do Backup", False, "Diretório de backup não encontrado")
                return False
            
            # Verifica se backup contém estrutura antiga
            backup_contents = list(backup_dir.iterdir())
            has_src = any('src' in item.name for item in backup_contents)
            has_main = any('main.py' in item.name for item in backup_contents)
            
            success = has_src and has_main
            self.log_test(
                "Integridade do Backup",
                success,
                f"Backup completo: src={has_src}, main.py={has_main}",
                {"backup_items": [item.name for item in backup_contents]}
            )
            return success
        except Exception as e:
            self.log_test("Integridade do Backup", False, f"Erro: {str(e)}")
            return False

    def test_fallback_mechanism(self):
        """Teste 8: Mecanismo de fallback"""
        try:
            # Este teste verifica se o sistema ainda pode funcionar
            # mesmo com falhas parciais de importação
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                # Sistema deve estar operacional mesmo em estado "degraded"
                success = status in ["healthy", "degraded"]
                self.log_test(
                    "Mecanismo de Fallback",
                    success,
                    f"Sistema operacional com status: {status}",
                    {"fallback_active": status == "degraded"}
                )
                return success
            else:
                self.log_test("Mecanismo de Fallback", False, "API não responsiva")
                return False
        except Exception as e:
            self.log_test("Mecanismo de Fallback", False, f"Erro: {str(e)}")
            return False

    def generate_report(self):
        """Gera relatório final da validação"""
        total_tests = self.tests_passed + self.tests_failed
        success_rate = (self.tests_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "validation_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "tests_passed": self.tests_passed,
                "tests_failed": self.tests_failed,
                "success_rate": round(success_rate, 2)
            },
            "overall_status": "PASSED" if success_rate >= 75 else "FAILED",
            "results": self.results
        }
        
        # Salva relatório
        report_file = Path("validation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report

    def run_all_tests(self):
        """Executa todos os testes de validação"""
        print("🚀 Iniciando Validação Completa do Sistema Modular AutoCura")
        print("=" * 60)
        
        tests = [
            self.test_api_connectivity,
            self.test_health_endpoint,
            self.test_modular_structure,
            self.test_modules_loading,
            self.test_docker_deployment,
            self.test_file_structure,
            self.test_backup_integrity,
            self.test_fallback_mechanism
        ]
        
        for i, test in enumerate(tests, 1):
            print(f"\n📋 Teste {i}/{len(tests)}: {test.__doc__.split(':')[1].strip()}")
            test()
            time.sleep(1)  # Pausa entre testes
        
        print("\n" + "=" * 60)
        print("📊 GERANDO RELATÓRIO FINAL...")
        
        report = self.generate_report()
        
        print("\n🎯 RESULTADO FINAL:")
        print(f"   Status: {report['overall_status']}")
        print(f"   Testes: {report['summary']['tests_passed']}/{report['summary']['total_tests']} passaram")
        print(f"   Taxa de sucesso: {report['summary']['success_rate']}%")
        
        if report['overall_status'] == "PASSED":
            print("\n✅ SISTEMA MODULAR VALIDADO COM SUCESSO!")
            print("🚀 Pronto para produção e evolução contínua.")
        else:
            print("\n⚠️ ALGUNS TESTES FALHARAM")
            print("🔧 Revisar problemas identificados antes do deploy.")
        
        print(f"\n📄 Relatório completo salvo em: validation_report.json")
        
        return report['overall_status'] == "PASSED"

def main():
    """Função principal"""
    validator = ModularSystemValidator()
    success = validator.run_all_tests()
    
    # Retorna código de saída apropriado
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 