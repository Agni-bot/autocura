#!/usr/bin/env python3
"""
Teste de Auto-Modificação Controlada - Sistema AutoCura
======================================================

Script de demonstração das capacidades de auto-modificação
com análise cognitiva via OpenAI e sandbox Docker.
"""

import asyncio
import json
import os
from datetime import datetime

# Configuração da chave OpenAI (necessária para testes)
# Defina a variável de ambiente OPENAI_API_KEY antes de executar
if not os.getenv('OPENAI_API_KEY'):
    print("⚠️  AVISO: Defina a variável OPENAI_API_KEY para testar com OpenAI")
    print("   Exemplo: export OPENAI_API_KEY='sua-chave-aqui'")
    print("   O teste continuará em modo simulação")

from src.core.self_modify.evolution_controller import (
    EvolutionController, EvolutionRequest, EvolutionType
)

async def test_basic_code_generation():
    """Teste básico de geração de código"""
    print("\n🧪 Teste 1: Geração Básica de Código")
    print("=" * 50)
    
    controller = EvolutionController()
    
    # Solicitação de evolução simples
    request = EvolutionRequest(
        evolution_type=EvolutionType.FUNCTION_GENERATION,
        description="Criar função para calcular fibonacci",
        requirements={
            "function_name": "fibonacci",
            "logic_description": "Calcular o n-ésimo número da sequência de Fibonacci",
            "inputs": [{"name": "n", "type": "int", "description": "Posição na sequência"}],
            "outputs": [{"name": "result", "type": "int", "description": "Número de Fibonacci"}],
            "test_data": {"n": 10}
        },
        safety_level="high",
        context="Teste de geração de função matemática",
        requester="test_script"
    )
    
    print(f"📝 Solicitando evolução: {request.description}")
    request_id = await controller.request_evolution(request)
    print(f"🆔 ID da solicitação: {request_id}")
    
    # Aguarda processamento (máximo 60 segundos)
    print("⏳ Aguardando processamento...")
    for i in range(60):
        await asyncio.sleep(1)
        
        # Verifica se completou
        for evolution in controller.completed_evolutions + controller.failed_evolutions:
            if evolution.request_id == request_id:
                print(f"\n✅ Evolução completada em {i+1} segundos")
                
                if evolution.success:
                    print(f"🎯 Status: Sucesso")
                    print(f"🔒 Nível de aprovação: {evolution.approval_level.value}")
                    print(f"⚡ Aplicada automaticamente: {evolution.applied}")
                    
                    if evolution.code_analysis:
                        print(f"🛡️  Score de segurança: {evolution.code_analysis.security_score:.2f}")
                        print(f"⚠️  Avaliação de risco: {evolution.code_analysis.risk_assessment.value}")
                        print(f"✅ Conformidade ética: {evolution.code_analysis.ethical_compliance}")
                    
                    if evolution.sandbox_result:
                        print(f"🐳 Status sandbox: {evolution.sandbox_result.status.value}")
                        print(f"⏱️  Tempo execução: {evolution.sandbox_result.execution_time:.2f}s")
                    
                    if evolution.generated_code:
                        print(f"\n📄 Código gerado ({len(evolution.generated_code)} caracteres):")
                        print("-" * 40)
                        print(evolution.generated_code[:500] + "..." if len(evolution.generated_code) > 500 else evolution.generated_code)
                        print("-" * 40)
                else:
                    print(f"❌ Status: Falha")
                    print(f"💥 Erro: {evolution.error_message}")
                
                return evolution
    
    print("⏰ Timeout - evolução não completou em 60 segundos")
    return None

async def test_code_validation():
    """Teste de validação de código existente"""
    print("\n🔍 Teste 2: Validação de Código")
    print("=" * 50)
    
    controller = EvolutionController()
    
    # Código seguro para teste
    safe_code = '''
def calculate_sum(numbers: list) -> int:
    """Calcula a soma de uma lista de números"""
    if not isinstance(numbers, list):
        raise ValueError("Input deve ser uma lista")
    
    total = 0
    for num in numbers:
        if isinstance(num, (int, float)):
            total += num
    
    return total
'''
    
    print("📝 Validando código seguro...")
    analysis = await controller.code_generator.validate_existing_code(
        safe_code, "Teste de validação - código seguro"
    )
    
    print(f"✅ Sintaxe válida: {analysis.syntax_valid}")
    print(f"🛡️  Score de segurança: {analysis.security_score:.2f}")
    print(f"⚠️  Avaliação de risco: {analysis.risk_assessment.value}")
    print(f"🎯 Conformidade ética: {analysis.ethical_compliance}")
    print(f"📊 Score de complexidade: {analysis.complexity_score:.2f}")
    
    if analysis.warnings:
        print(f"⚠️  Avisos: {len(analysis.warnings)}")
        for warning in analysis.warnings[:3]:
            print(f"   - {warning}")
    
    if analysis.recommendations:
        print(f"💡 Recomendações: {len(analysis.recommendations)}")
        for rec in analysis.recommendations[:3]:
            print(f"   - {rec}")
    
    # Código perigoso para teste
    print("\n📝 Validando código perigoso...")
    dangerous_code = '''
import os
import subprocess

def dangerous_function():
    os.system("rm -rf /")  # MUITO PERIGOSO!
    subprocess.call(["curl", "http://malicious-site.com"])
    eval("__import__('os').system('echo hacked')")
'''
    
    analysis2 = await controller.code_generator.validate_existing_code(
        dangerous_code, "Teste de validação - código perigoso"
    )
    
    print(f"❌ Sintaxe válida: {analysis2.syntax_valid}")
    print(f"🚨 Score de segurança: {analysis2.security_score:.2f}")
    print(f"🔴 Avaliação de risco: {analysis2.risk_assessment.value}")
    print(f"⚠️  Avisos: {len(analysis2.warnings)}")
    
    return analysis, analysis2

async def test_sandbox_execution():
    """Teste de execução no sandbox"""
    print("\n🐳 Teste 3: Execução no Sandbox")
    print("=" * 50)
    
    controller = EvolutionController()
    
    # Código simples para teste
    test_code = '''
def hello_world():
    """Função de teste simples"""
    message = "Hello from AutoCura Evolution!"
    print(message)
    return message

# Executa a função
result = hello_world()
print(f"Resultado: {result}")
'''
    
    print("🐳 Executando código no sandbox...")
    result = await controller.sandbox.test_evolution(
        test_code, 
        {"test_input": "hello"}, 
        timeout=30
    )
    
    print(f"📊 Status: {result.status.value}")
    print(f"🔢 Código de saída: {result.exit_code}")
    print(f"⏱️  Tempo de execução: {result.execution_time:.2f}s")
    
    if result.stdout:
        print(f"📤 STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print(f"📥 STDERR:")
        print(result.stderr)
    
    if result.test_results:
        print(f"🧪 Resultados do teste:")
        print(json.dumps(result.test_results, indent=2))
    
    return result

async def test_evolution_stats():
    """Teste de estatísticas de evolução"""
    print("\n📊 Teste 4: Estatísticas do Sistema")
    print("=" * 50)
    
    controller = EvolutionController()
    
    stats = controller.get_evolution_stats()
    
    print("📈 Estatísticas de Evolução:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for subkey, subvalue in value.items():
                print(f"    {subkey}: {subvalue}")
        else:
            print(f"  {key}: {value}")
    
    return stats

async def main():
    """Função principal de teste"""
    print("🚀 Sistema de Auto-Modificação Controlada - AutoCura")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  MODO SIMULAÇÃO: Alguns testes podem falhar sem chave OpenAI")
    
    try:
        # Executa testes sequencialmente
        await test_basic_code_generation()
        await test_code_validation()
        await test_sandbox_execution()
        await test_evolution_stats()
        
        print("\n🎉 Todos os testes concluídos!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executa testes
    asyncio.run(main()) 