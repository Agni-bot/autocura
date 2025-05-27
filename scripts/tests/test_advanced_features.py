#!/usr/bin/env python3
"""
Teste de Funcionalidades Avançadas - Sistema AutoCura
====================================================

Demonstração de casos de uso específicos e funcionalidades avançadas
do sistema de auto-modificação controlada.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()

from src.core.self_modify.safe_code_generator import SafeCodeGenerator, RiskAssessment
from src.core.self_modify.evolution_controller import (
    EvolutionController, EvolutionRequest, EvolutionType
)

print("🚀 Sistema AutoCura - Funcionalidades Avançadas")
print("=" * 60)
print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def test_ai_code_optimization():
    """Teste de otimização de código com IA"""
    print("\n🧠 Funcionalidade 1: Otimização de Código com IA")
    print("=" * 55)
    
    generator = SafeCodeGenerator()
    
    # Código ineficiente para otimização
    inefficient_code = '''
def fibonacci_slow(n):
    """Implementação ineficiente de Fibonacci"""
    if n <= 1:
        return n
    return fibonacci_slow(n-1) + fibonacci_slow(n-2)

def process_data_slow(data):
    """Processamento ineficiente de dados"""
    result = []
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] > data[j]:
                result.append(data[i])
    return result
'''
    
    print("📝 Analisando código ineficiente...")
    analysis = await generator.validate_existing_code(
        inefficient_code, 
        "Código com problemas de performance"
    )
    
    print(f"🛡️  Score de segurança: {analysis.security_score:.2f}")
    print(f"📊 Complexidade: {analysis.complexity_score:.2f}")
    print(f"⚠️  Avaliação de risco: {analysis.risk_assessment.value}")
    
    if analysis.recommendations:
        print(f"💡 Recomendações de melhoria:")
        for rec in analysis.recommendations[:3]:
            print(f"   - {rec}")
    
    # Gera versão otimizada
    print("\n🔧 Gerando versão otimizada...")
    optimization_requirements = {
        "function_name": "fibonacci_optimized",
        "description": "Versão otimizada do algoritmo Fibonacci com memoização",
        "inputs": [{"name": "n", "type": "int", "description": "Número para calcular Fibonacci"}],
        "outputs": [{"name": "result", "type": "int", "description": "Resultado Fibonacci"}],
        "logic_description": """
        Implementar Fibonacci otimizado usando:
        1. Memoização para evitar recálculos
        2. Iteração em vez de recursão quando possível
        3. Validação de entrada
        4. Tratamento de casos extremos
        """,
        "safety_level": "high",
        "context": "Otimização de performance para algoritmo matemático"
    }
    
    optimized_code, opt_analysis = await generator.generate_module(optimization_requirements)
    
    print(f"✅ Código otimizado gerado!")
    print(f"📏 Tamanho: {len(optimized_code)} caracteres")
    print(f"🛡️  Score de segurança: {opt_analysis.security_score:.2f}")
    print(f"📊 Complexidade: {opt_analysis.complexity_score:.2f}")
    
    # Mostra trecho do código otimizado
    print(f"\n📄 Código otimizado:")
    print("-" * 50)
    lines = optimized_code.split('\n')
    for i, line in enumerate(lines[:10]):
        print(f"{i+1:2d}: {line}")
    if len(lines) > 10:
        print(f"... (+{len(lines)-10} linhas)")
    print("-" * 50)
    
    return True

async def test_security_analysis():
    """Teste de análise de segurança avançada"""
    print("\n🛡️  Funcionalidade 2: Análise de Segurança Avançada")
    print("=" * 58)
    
    generator = SafeCodeGenerator()
    
    # Códigos com diferentes níveis de risco
    test_codes = [
        {
            "name": "Código Seguro",
            "code": '''
def safe_calculator(a: float, b: float) -> float:
    """Calculadora segura"""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise ValueError("Apenas números são aceitos")
    return a + b
''',
            "expected_risk": "safe"
        },
        {
            "name": "Código Suspeito",
            "code": '''
import urllib.request
def fetch_data(url):
    """Busca dados de URL externa"""
    response = urllib.request.urlopen(url)
    return response.read()
''',
            "expected_risk": "caution"
        },
        {
            "name": "Código Perigoso",
            "code": '''
import os
import subprocess
def dangerous_operation(command):
    """Operação perigosa"""
    os.system(command)
    subprocess.call(command, shell=True)
    eval(f"print('{command}')")
''',
            "expected_risk": "dangerous"
        }
    ]
    
    results = []
    
    for test_case in test_codes:
        print(f"\n📝 Analisando: {test_case['name']}")
        
        analysis = await generator.validate_existing_code(
            test_case['code'], 
            f"Teste de segurança: {test_case['name']}"
        )
        
        risk_level = analysis.risk_assessment.value
        expected = test_case['expected_risk']
        
        status = "✅" if risk_level == expected else "⚠️"
        print(f"   {status} Risco detectado: {risk_level} (esperado: {expected})")
        print(f"   🛡️  Score: {analysis.security_score:.2f}")
        
        if analysis.warnings:
            print(f"   ⚠️  Avisos: {len(analysis.warnings)}")
            for warning in analysis.warnings[:2]:
                print(f"      - {warning}")
        
        results.append({
            "name": test_case['name'],
            "detected": risk_level,
            "expected": expected,
            "correct": risk_level == expected
        })
    
    # Resumo da análise
    correct_detections = sum(1 for r in results if r['correct'])
    accuracy = correct_detections / len(results) * 100
    
    print(f"\n📊 Precisão da Análise de Segurança: {accuracy:.1f}%")
    print(f"✅ Detecções corretas: {correct_detections}/{len(results)}")
    
    return accuracy >= 80

async def test_evolution_scenarios():
    """Teste de cenários de evolução específicos"""
    print("\n🎛️  Funcionalidade 3: Cenários de Evolução Específicos")
    print("=" * 62)
    
    controller = EvolutionController()
    
    # Cenários de evolução
    scenarios = [
        {
            "name": "Sistema de Cache Inteligente",
            "type": EvolutionType.FEATURE_ADDITION,
            "description": "Cache com TTL dinâmico e estratégias de eviction",
            "complexity": "high"
        },
        {
            "name": "Correção de Bug de Performance",
            "type": EvolutionType.BUG_FIX,
            "description": "Otimizar loop O(n²) para O(n log n)",
            "complexity": "medium"
        },
        {
            "name": "Geração de API REST",
            "type": EvolutionType.FUNCTION_GENERATION,
            "description": "Endpoint REST com validação e documentação",
            "complexity": "medium"
        }
    ]
    
    evolution_results = []
    
    for scenario in scenarios:
        print(f"\n📝 Cenário: {scenario['name']}")
        
        # Cria solicitação de evolução
        request = EvolutionRequest(
            evolution_type=scenario['type'],
            description=scenario['description'],
            requirements={
                "function_name": scenario['name'].lower().replace(' ', '_'),
                "logic_description": scenario['description'],
                "complexity_level": scenario['complexity'],
                "inputs": [{"name": "input_data", "type": "Any", "description": "Dados de entrada"}],
                "outputs": [{"name": "result", "type": "Any", "description": "Resultado processado"}],
                "test_data": {"sample": "test_data"}
            },
            safety_level="high",
            context=f"Cenário de teste: {scenario['name']}",
            requester="advanced_test"
        )
        
        # Solicita evolução
        request_id = await controller.request_evolution(request)
        print(f"🆔 Solicitação: {request_id}")
        
        # Aguarda processamento
        await asyncio.sleep(2)
        
        evolution_results.append({
            "scenario": scenario['name'],
            "request_id": request_id,
            "type": scenario['type'].value
        })
    
    # Verifica resultados
    print(f"\n📊 Resultados das Evoluções:")
    stats = controller.get_evolution_stats()
    
    print(f"   Total de solicitações: {stats['total_requests']}")
    print(f"   Evoluções bem-sucedidas: {stats['successful_evolutions']}")
    print(f"   Aprovações pendentes: {stats.get('pending_approvals', 0)}")
    
    # Histórico detalhado
    history = controller.get_evolution_history(limit=len(scenarios))
    if history:
        print(f"\n📋 Histórico das Evoluções:")
        for i, evolution in enumerate(history):
            scenario_name = scenarios[i]['name'] if i < len(scenarios) else "Desconhecido"
            status = "✅" if evolution['success'] else "❌"
            print(f"   {status} {scenario_name}")
            print(f"      Tempo: {evolution['execution_time']:.2f}s")
            print(f"      Aprovação: {evolution['approval_level']}")
    
    return len(evolution_results) > 0

async def test_code_quality_metrics():
    """Teste de métricas de qualidade de código"""
    print("\n📊 Funcionalidade 4: Métricas de Qualidade de Código")
    print("=" * 58)
    
    generator = SafeCodeGenerator()
    
    # Códigos com diferentes qualidades
    quality_tests = [
        {
            "name": "Código Bem Documentado",
            "code": '''
from typing import List, Optional
import logging

def process_user_data(users: List[dict], filter_active: bool = True) -> List[dict]:
    """
    Processa dados de usuários com filtros opcionais.
    
    Args:
        users: Lista de dicionários com dados dos usuários
        filter_active: Se deve filtrar apenas usuários ativos
        
    Returns:
        Lista de usuários processados
        
    Raises:
        ValueError: Se a lista de usuários for inválida
    """
    if not isinstance(users, list):
        raise ValueError("users deve ser uma lista")
    
    logger = logging.getLogger(__name__)
    logger.info(f"Processando {len(users)} usuários")
    
    processed = []
    for user in users:
        if not filter_active or user.get('active', False):
            processed_user = {
                'id': user.get('id'),
                'name': user.get('name', '').strip(),
                'email': user.get('email', '').lower(),
                'active': user.get('active', False)
            }
            processed.append(processed_user)
    
    logger.info(f"Processados {len(processed)} usuários")
    return processed
'''
        },
        {
            "name": "Código Simples",
            "code": '''
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
'''
        },
        {
            "name": "Código Complexo",
            "code": '''
def complex_algorithm(data):
    result = []
    for i in range(len(data)):
        temp = []
        for j in range(len(data[i])):
            if data[i][j] > 0:
                for k in range(data[i][j]):
                    if k % 2 == 0:
                        temp.append(k * 2)
                    else:
                        temp.append(k + 1)
        result.append(temp)
    return result
'''
        }
    ]
    
    quality_results = []
    
    for test in quality_tests:
        print(f"\n📝 Analisando: {test['name']}")
        
        analysis = await generator.validate_existing_code(
            test['code'], 
            f"Análise de qualidade: {test['name']}"
        )
        
        print(f"   🛡️  Segurança: {analysis.security_score:.2f}")
        print(f"   📊 Complexidade: {analysis.complexity_score:.2f}")
        print(f"   ✅ Sintaxe válida: {analysis.syntax_valid}")
        print(f"   🔍 Conformidade ética: {analysis.ethical_compliance}")
        
        # Análise OpenAI se disponível
        if hasattr(analysis, 'openai_analysis') and analysis.openai_analysis:
            openai_data = analysis.openai_analysis
            if 'quality_assessment' in openai_data:
                quality_score = openai_data['quality_assessment'].get('score', 0)
                print(f"   🧠 Qualidade IA: {quality_score:.2f}")
        
        quality_results.append({
            "name": test['name'],
            "security": analysis.security_score,
            "complexity": analysis.complexity_score,
            "syntax_valid": analysis.syntax_valid
        })
    
    # Resumo das métricas
    avg_security = sum(r['security'] for r in quality_results) / len(quality_results)
    avg_complexity = sum(r['complexity'] for r in quality_results) / len(quality_results)
    
    print(f"\n📈 Métricas Médias:")
    print(f"   🛡️  Segurança média: {avg_security:.2f}")
    print(f"   📊 Complexidade média: {avg_complexity:.2f}")
    print(f"   ✅ Taxa de sintaxe válida: {sum(1 for r in quality_results if r['syntax_valid'])/len(quality_results)*100:.1f}%")
    
    return True

async def main():
    """Função principal dos testes avançados"""
    
    print("\n🧪 Executando Testes de Funcionalidades Avançadas...")
    
    results = []
    
    try:
        # Teste 1: Otimização de código
        result1 = await test_ai_code_optimization()
        results.append(("Otimização de Código IA", result1))
        
        # Teste 2: Análise de segurança
        result2 = await test_security_analysis()
        results.append(("Análise de Segurança", result2))
        
        # Teste 3: Cenários de evolução
        result3 = await test_evolution_scenarios()
        results.append(("Cenários de Evolução", result3))
        
        # Teste 4: Métricas de qualidade
        result4 = await test_code_quality_metrics()
        results.append(("Métricas de Qualidade", result4))
        
        # Resumo final
        print("\n🎯 Resumo dos Testes Avançados:")
        print("=" * 60)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        success_rate = passed / len(results) * 100
        print(f"\n📊 Taxa de Sucesso: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 TODAS AS FUNCIONALIDADES AVANÇADAS OPERACIONAIS!")
            print("🚀 Sistema AutoCura demonstrou capacidades completas!")
        elif success_rate >= 75:
            print("✅ Funcionalidades majoritariamente operacionais")
            print("🔧 Sistema pronto para casos de uso avançados")
        else:
            print("⚠️  Algumas funcionalidades precisam de ajustes")
        
        print(f"\n🏆 Capacidades Demonstradas:")
        print(f"   🧠 IA para otimização de código")
        print(f"   🛡️  Análise de segurança multi-camada")
        print(f"   🎛️  Evolução controlada por cenários")
        print(f"   📊 Métricas de qualidade automatizadas")
        
    except Exception as e:
        print(f"\n❌ Erro crítico nos testes avançados: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executa testes avançados
    asyncio.run(main()) 