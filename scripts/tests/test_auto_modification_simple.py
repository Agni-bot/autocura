#!/usr/bin/env python3
"""
Teste Simplificado de Auto-Modificação - Sistema AutoCura
========================================================

Teste básico que não depende do Docker para verificar funcionalidades core.
"""

import asyncio
import os
from datetime import datetime

# Configuração da chave OpenAI (opcional para teste básico)
if not os.getenv('OPENAI_API_KEY'):
    print("⚠️  AVISO: Executando em modo simulação (sem OpenAI)")
    print("   Para teste completo, defina: export OPENAI_API_KEY='sua-chave'")

try:
    from src.core.self_modify.safe_code_generator import SafeCodeGenerator, RiskAssessment
    print("✅ SafeCodeGenerator importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar SafeCodeGenerator: {e}")
    exit(1)

async def test_code_validation_only():
    """Teste apenas de validação de código (sem OpenAI)"""
    print("\n🔍 Teste 1: Validação de Código Local")
    print("=" * 50)
    
    try:
        generator = SafeCodeGenerator()
        print("✅ SafeCodeGenerator inicializado")
        
        # Código seguro para teste
        safe_code = '''
def calculate_fibonacci(n: int) -> int:
    """Calcula o n-ésimo número da sequência de Fibonacci"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# Teste da função
result = calculate_fibonacci(10)
print(f"Fibonacci(10) = {result}")
'''
        
        print("📝 Analisando código seguro...")
        
        # Análise local (sem OpenAI)
        local_analysis = generator._analyze_code_locally(safe_code)
        
        print(f"✅ Sintaxe válida: {local_analysis.get('syntax_valid', False)}")
        print(f"🛡️  Score de segurança: {local_analysis.get('security_score', 0):.2f}")
        print(f"📊 Complexidade: {local_analysis.get('complexity_score', 0):.2f}")
        print(f"📏 Linhas de código: {local_analysis.get('line_count', 0)}")
        
        if local_analysis.get('forbidden_imports'):
            print(f"⚠️  Imports proibidos: {local_analysis['forbidden_imports']}")
        else:
            print("✅ Nenhum import proibido encontrado")
            
        if local_analysis.get('dangerous_functions'):
            print(f"🚨 Funções perigosas: {local_analysis['dangerous_functions']}")
        else:
            print("✅ Nenhuma função perigosa encontrada")
        
        # Código perigoso para teste
        print("\n📝 Analisando código perigoso...")
        dangerous_code = '''
import os
import subprocess

def dangerous_function():
    os.system("rm -rf /")  # MUITO PERIGOSO!
    subprocess.call(["curl", "http://malicious-site.com"])
    eval("__import__('os').system('echo hacked')")
'''
        
        dangerous_analysis = generator._analyze_code_locally(dangerous_code)
        
        print(f"❌ Sintaxe válida: {dangerous_analysis.get('syntax_valid', False)}")
        print(f"🚨 Score de segurança: {dangerous_analysis.get('security_score', 0):.2f}")
        print(f"⚠️  Imports proibidos: {dangerous_analysis.get('forbidden_imports', [])}")
        print(f"🚨 Funções perigosas: {dangerous_analysis.get('dangerous_functions', [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_generation_stats():
    """Teste das estatísticas do gerador"""
    print("\n📊 Teste 2: Estatísticas do Sistema")
    print("=" * 50)
    
    try:
        generator = SafeCodeGenerator()
        stats = generator.get_generation_stats()
        
        print("📈 Estatísticas do SafeCodeGenerator:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de estatísticas: {e}")
        return False

async def test_imports_and_structure():
    """Teste da estrutura e imports do sistema"""
    print("\n🏗️  Teste 3: Estrutura e Imports")
    print("=" * 50)
    
    modules_to_test = [
        ("src.core.interfaces", "Interfaces universais"),
        ("src.core.messaging.universal_bus", "Sistema de mensageria"),
        ("src.core.serialization.adaptive_serializer", "Serialização adaptativa"),
        ("src.services.monitoramento.coletor_metricas", "Coletor de métricas"),
        ("src.services.diagnostico.diagnostico", "Sistema de diagnóstico"),
        ("src.seguranca.criptografia", "Criptografia quantum-safe")
    ]
    
    results = {}
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {description}: OK")
            results[module_name] = True
        except ImportError as e:
            print(f"❌ {description}: ERRO - {e}")
            results[module_name] = False
        except Exception as e:
            print(f"⚠️  {description}: AVISO - {e}")
            results[module_name] = False
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\n📊 Taxa de sucesso dos imports: {success_rate:.1f}%")
    
    return success_rate > 70  # Considera sucesso se > 70% dos módulos carregaram

async def main():
    """Função principal de teste simplificado"""
    print("🚀 Teste Simplificado - Sistema AutoCura")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Modo: Simulação (sem Docker/OpenAI)")
    
    tests_results = []
    
    try:
        # Executa testes básicos
        print("\n🧪 Executando testes básicos...")
        
        result1 = await test_code_validation_only()
        tests_results.append(("Validação de Código", result1))
        
        result2 = await test_generation_stats()
        tests_results.append(("Estatísticas", result2))
        
        result3 = await test_imports_and_structure()
        tests_results.append(("Imports e Estrutura", result3))
        
        # Resumo dos resultados
        print("\n📋 Resumo dos Testes:")
        print("=" * 40)
        
        passed = 0
        for test_name, result in tests_results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        success_rate = passed / len(tests_results) * 100
        print(f"\n🎯 Taxa de Sucesso Geral: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Sistema básico funcionando corretamente!")
            print("💡 Próximo passo: Configurar Docker e OpenAI para testes completos")
        elif success_rate >= 60:
            print("⚠️  Sistema parcialmente funcional")
            print("🔧 Alguns módulos precisam de correção")
        else:
            print("❌ Sistema com problemas críticos")
            print("🚨 Revisão necessária antes de prosseguir")
        
    except Exception as e:
        print(f"\n❌ Erro crítico durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executa testes
    asyncio.run(main()) 