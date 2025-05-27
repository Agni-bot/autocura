#!/usr/bin/env python3
"""
Diagnóstico do main.py - Sistema AutoCura
Detecta problemas de importação e dependências
"""

import sys
import subprocess
import importlib.util

def test_import(module_name, fallback_message="Módulo não disponível"):
    """Testa importação de um módulo"""
    try:
        if '.' in module_name:
            # Módulo do projeto
            spec = importlib.util.spec_from_file_location(
                module_name.split('.')[-1], 
                module_name.replace('.', '/') + '.py'
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"✅ {module_name}: OK")
                return True
        else:
            # Módulo padrão
            __import__(module_name)
            print(f"✅ {module_name}: OK")
            return True
    except Exception as e:
        print(f"❌ {module_name}: {str(e)}")
        return False

def check_docker_containers():
    """Verifica status dos containers Docker"""
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        print("\n=== STATUS CONTAINERS ===")
        lines = result.stdout.split('\n')
        for line in lines:
            if 'autocura' in line:
                print(f"🐳 {line}")
        return True
    except Exception as e:
        print(f"❌ Docker error: {e}")
        return False

def check_docker_logs():
    """Verifica logs do container da API"""
    try:
        result = subprocess.run(
            ['docker', 'logs', '--tail', '20', 'autocura-api-1'], 
            capture_output=True, text=True
        )
        print("\n=== LOGS API CONTAINER ===")
        print(result.stdout)
        if result.stderr:
            print("ERROS:")
            print(result.stderr)
        return True
    except Exception as e:
        print(f"❌ Logs error: {e}")
        return False

def test_basic_dependencies():
    """Testa dependências básicas"""
    print("=== TESTE DEPENDÊNCIAS BÁSICAS ===")
    
    basic_deps = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'redis',
        'psutil',
        'requests'
    ]
    
    success_count = 0
    for dep in basic_deps:
        if test_import(dep):
            success_count += 1
    
    print(f"\n✅ {success_count}/{len(basic_deps)} dependências básicas OK")
    return success_count == len(basic_deps)

def test_project_modules():
    """Testa módulos do projeto"""
    print("\n=== TESTE MÓDULOS PROJETO ===")
    
    project_modules = [
        'src.core.memoria.gerenciador_memoria',
        'src.core.memoria.registrador_contexto', 
        'src.core.messaging.universal_bus',
        'src.core.serialization.adaptive_serializer'
    ]
    
    success_count = 0
    for module in project_modules:
        if test_import(module):
            success_count += 1
    
    print(f"\n✅ {success_count}/{len(project_modules)} módulos projeto OK")
    return success_count > 0

def test_main_execution():
    """Testa execução do main.py"""
    print("\n=== TESTE MAIN.PY ===")
    try:
        # Tenta importar apenas para verificar sintaxe
        import main
        print("✅ main.py: Sintaxe OK")
        return True
    except Exception as e:
        print(f"❌ main.py: {str(e)}")
        print("\nDetalhes do erro:")
        import traceback
        traceback.print_exc()
        return False

def suggest_fixes():
    """Sugere correções baseadas nos problemas encontrados"""
    print("\n=== SUGESTÕES DE CORREÇÃO ===")
    
    print("1. 🔧 Instalar dependências faltantes:")
    print("   pip install -r requirements.txt")
    
    print("\n2. 🐳 Reiniciar containers Docker:")
    print("   docker-compose -f docker/docker-compose.simple.yml down")
    print("   docker-compose -f docker/docker-compose.simple.yml up -d")
    
    print("\n3. 🔍 Verificar estrutura de diretórios:")
    print("   Garantir que src/ contém todos os módulos necessários")
    
    print("\n4. 🚀 Executar main.py diretamente:")
    print("   python main.py")

def main():
    """Execução principal do diagnóstico"""
    print("🔍 DIAGNÓSTICO SISTEMA AUTOCURA")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.executable}")
    
    # Testes
    deps_ok = test_basic_dependencies()
    modules_ok = test_project_modules() 
    main_ok = test_main_execution()
    
    # Docker
    check_docker_containers()
    check_docker_logs()
    
    # Resultado
    print("\n" + "=" * 50)
    print("📊 RESUMO DIAGNÓSTICO")
    print(f"✅ Dependências: {'OK' if deps_ok else 'FALHA'}")
    print(f"✅ Módulos projeto: {'OK' if modules_ok else 'FALHA'}")  
    print(f"✅ main.py: {'OK' if main_ok else 'FALHA'}")
    
    if not (deps_ok and modules_ok and main_ok):
        suggest_fixes()
    else:
        print("\n🎉 Sistema parece estar funcionando corretamente!")
        print("   Se ainda há problemas, verifique os logs do Docker acima.")

if __name__ == "__main__":
    main() 