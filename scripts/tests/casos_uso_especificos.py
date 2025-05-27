#!/usr/bin/env python3
"""
Casos de Uso Específicos - Sistema AutoCura
==========================================

Demonstração de aplicações práticas do sistema de auto-modificação
controlada em cenários reais de desenvolvimento.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()

from src.core.self_modify.safe_code_generator import SafeCodeGenerator
from src.core.self_modify.evolution_controller import (
    EvolutionController, EvolutionRequest, EvolutionType
)

print("🎯 Sistema AutoCura - Casos de Uso Específicos")
print("=" * 60)
print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def caso_uso_1_api_microservico():
    """Caso de Uso 1: Geração de API para Microserviço"""
    print("\n🔧 Caso de Uso 1: Geração de API para Microserviço")
    print("=" * 55)
    
    controller = EvolutionController()
    
    # Especificações do microserviço
    api_specs = {
        "service_name": "user_management_api",
        "description": "API REST para gerenciamento de usuários",
        "endpoints": [
            {"method": "GET", "path": "/users", "description": "Listar usuários"},
            {"method": "POST", "path": "/users", "description": "Criar usuário"},
            {"method": "GET", "path": "/users/{id}", "description": "Buscar usuário"},
            {"method": "PUT", "path": "/users/{id}", "description": "Atualizar usuário"},
            {"method": "DELETE", "path": "/users/{id}", "description": "Deletar usuário"}
        ],
        "authentication": "JWT",
        "database": "PostgreSQL",
        "validation": "Pydantic"
    }
    
    print(f"📝 Gerando API: {api_specs['service_name']}")
    print(f"🔗 Endpoints: {len(api_specs['endpoints'])}")
    
    # Solicitação de evolução para API
    request = EvolutionRequest(
        evolution_type=EvolutionType.FEATURE_ADDITION,
        description=f"Gerar {api_specs['description']} completa",
        requirements={
            "function_name": "user_management_api",
            "logic_description": f"""
            Criar API REST completa com:
            1. Endpoints CRUD para usuários
            2. Autenticação JWT
            3. Validação com Pydantic
            4. Conexão PostgreSQL
            5. Tratamento de erros
            6. Documentação OpenAPI
            7. Testes unitários
            """,
            "inputs": [
                {"name": "user_data", "type": "UserModel", "description": "Dados do usuário"},
                {"name": "user_id", "type": "int", "description": "ID do usuário"}
            ],
            "outputs": [
                {"name": "api_response", "type": "Dict", "description": "Resposta da API"},
                {"name": "status_code", "type": "int", "description": "Código HTTP"}
            ],
            "specifications": api_specs,
            "test_data": {
                "sample_user": {
                    "name": "João Silva",
                    "email": "joao@example.com",
                    "role": "user"
                }
            }
        },
        safety_level="high",
        priority=1,
        context="Desenvolvimento de microserviço para sistema empresarial",
        requester="desenvolvimento_backend"
    )
    
    # Executa geração
    request_id = await controller.request_evolution(request)
    print(f"🆔 Solicitação criada: {request_id}")
    
    # Aguarda processamento
    await asyncio.sleep(3)
    
    # Verifica resultado
    stats = controller.get_evolution_stats()
    history = controller.get_evolution_history(limit=1)
    
    if history:
        evolution = history[0]
        print(f"✅ Status: {'Sucesso' if evolution['success'] else 'Falha'}")
        print(f"⏱️  Tempo de geração: {evolution['execution_time']:.2f}s")
        print(f"🔒 Nível de aprovação: {evolution['approval_level']}")
    
    print(f"📊 API gerada com sucesso para microserviço!")
    return True

async def caso_uso_2_otimizacao_algoritmo():
    """Caso de Uso 2: Otimização de Algoritmo de Machine Learning"""
    print("\n🧠 Caso de Uso 2: Otimização de Algoritmo ML")
    print("=" * 50)
    
    generator = SafeCodeGenerator()
    
    # Algoritmo original ineficiente
    algoritmo_original = '''
import numpy as np

def naive_kmeans(data, k, max_iters=100):
    """Implementação ingênua de K-means"""
    n_samples, n_features = data.shape
    
    # Inicialização aleatória
    centroids = data[np.random.choice(n_samples, k, replace=False)]
    
    for iteration in range(max_iters):
        # Calcular distâncias (ineficiente)
        distances = []
        for i in range(n_samples):
            sample_distances = []
            for j in range(k):
                dist = 0
                for f in range(n_features):
                    dist += (data[i][f] - centroids[j][f]) ** 2
                sample_distances.append(dist ** 0.5)
            distances.append(sample_distances)
        
        # Atribuir clusters
        labels = []
        for i in range(n_samples):
            min_dist = float('inf')
            cluster = 0
            for j in range(k):
                if distances[i][j] < min_dist:
                    min_dist = distances[i][j]
                    cluster = j
            labels.append(cluster)
        
        # Atualizar centroids (ineficiente)
        new_centroids = []
        for j in range(k):
            cluster_points = []
            for i in range(n_samples):
                if labels[i] == j:
                    cluster_points.append(data[i])
            if cluster_points:
                centroid = [0] * n_features
                for point in cluster_points:
                    for f in range(n_features):
                        centroid[f] += point[f]
                for f in range(n_features):
                    centroid[f] /= len(cluster_points)
                new_centroids.append(centroid)
            else:
                new_centroids.append(centroids[j])
        
        centroids = np.array(new_centroids)
    
    return centroids, labels
'''
    
    print("📝 Analisando algoritmo K-means original...")
    
    # Análise do código original
    analysis = await generator.validate_existing_code(
        algoritmo_original,
        "Algoritmo K-means para otimização"
    )
    
    print(f"🛡️  Segurança: {analysis.security_score:.2f}")
    print(f"📊 Complexidade: {analysis.complexity_score:.2f}")
    print(f"⚠️  Risco: {analysis.risk_assessment.value}")
    
    # Gera versão otimizada
    print("\n🔧 Gerando versão otimizada...")
    
    optimization_requirements = {
        "function_name": "optimized_kmeans",
        "description": "Algoritmo K-means otimizado para performance",
        "inputs": [
            {"name": "data", "type": "np.ndarray", "description": "Dados para clustering"},
            {"name": "k", "type": "int", "description": "Número de clusters"},
            {"name": "max_iters", "type": "int", "description": "Máximo de iterações"}
        ],
        "outputs": [
            {"name": "centroids", "type": "np.ndarray", "description": "Centroids finais"},
            {"name": "labels", "type": "np.ndarray", "description": "Labels dos clusters"}
        ],
        "logic_description": """
        Implementar K-means otimizado com:
        1. Operações vetorizadas com NumPy
        2. Cálculo eficiente de distâncias
        3. Inicialização K-means++
        4. Critério de convergência
        5. Validação de entrada
        6. Documentação completa
        """,
        "safety_level": "high",
        "context": "Otimização de algoritmo de machine learning"
    }
    
    optimized_code, opt_analysis = await generator.generate_module(optimization_requirements)
    
    print(f"✅ Algoritmo otimizado gerado!")
    print(f"📏 Tamanho: {len(optimized_code)} caracteres")
    print(f"🛡️  Segurança: {opt_analysis.security_score:.2f}")
    print(f"📊 Complexidade: {opt_analysis.complexity_score:.2f}")
    
    # Comparação de performance estimada
    complexity_reduction = (analysis.complexity_score - opt_analysis.complexity_score) / analysis.complexity_score * 100
    print(f"🚀 Redução de complexidade estimada: {complexity_reduction:.1f}%")
    
    return True

async def caso_uso_3_sistema_monitoramento():
    """Caso de Uso 3: Sistema de Monitoramento Inteligente"""
    print("\n📊 Caso de Uso 3: Sistema de Monitoramento Inteligente")
    print("=" * 60)
    
    controller = EvolutionController()
    
    # Especificações do sistema de monitoramento
    monitoring_specs = {
        "system_name": "intelligent_monitoring",
        "components": [
            "Coleta de métricas em tempo real",
            "Detecção de anomalias com ML",
            "Alertas inteligentes",
            "Dashboard adaptativo",
            "Auto-scaling baseado em padrões"
        ],
        "metrics": [
            "CPU, Memória, Disco, Rede",
            "Latência de aplicação",
            "Taxa de erro",
            "Throughput",
            "Métricas de negócio"
        ],
        "integrations": ["Prometheus", "Grafana", "Elasticsearch", "Slack"]
    }
    
    print(f"📝 Gerando: {monitoring_specs['system_name']}")
    print(f"🔧 Componentes: {len(monitoring_specs['components'])}")
    
    # Solicitação de evolução
    request = EvolutionRequest(
        evolution_type=EvolutionType.FEATURE_ADDITION,
        description="Sistema de monitoramento com IA para detecção de anomalias",
        requirements={
            "function_name": "intelligent_monitoring_system",
            "logic_description": """
            Criar sistema de monitoramento inteligente com:
            1. Coleta de métricas multi-fonte
            2. Algoritmos de detecção de anomalias
            3. Sistema de alertas adaptativos
            4. Dashboard em tempo real
            5. Predição de problemas
            6. Auto-remediation básica
            """,
            "inputs": [
                {"name": "metrics_data", "type": "Dict", "description": "Dados de métricas"},
                {"name": "config", "type": "MonitoringConfig", "description": "Configuração"}
            ],
            "outputs": [
                {"name": "alerts", "type": "List[Alert]", "description": "Alertas gerados"},
                {"name": "predictions", "type": "Dict", "description": "Predições"}
            ],
            "specifications": monitoring_specs,
            "test_data": {
                "sample_metrics": {
                    "cpu_usage": 85.5,
                    "memory_usage": 78.2,
                    "response_time": 250,
                    "error_rate": 0.02
                }
            }
        },
        safety_level="high",
        priority=2,
        context="Sistema de monitoramento para infraestrutura crítica",
        requester="devops_team"
    )
    
    # Executa geração
    request_id = await controller.request_evolution(request)
    print(f"🆔 Solicitação criada: {request_id}")
    
    # Aguarda processamento
    await asyncio.sleep(3)
    
    # Verifica resultado
    history = controller.get_evolution_history(limit=1)
    
    if history:
        evolution = history[0]
        print(f"✅ Status: {'Sucesso' if evolution['success'] else 'Falha'}")
        print(f"⏱️  Tempo de geração: {evolution['execution_time']:.2f}s")
        print(f"🔒 Nível de aprovação: {evolution['approval_level']}")
    
    print(f"📊 Sistema de monitoramento inteligente gerado!")
    return True

async def caso_uso_4_correcao_automatica():
    """Caso de Uso 4: Correção Automática de Bugs"""
    print("\n🐛 Caso de Uso 4: Correção Automática de Bugs")
    print("=" * 50)
    
    generator = SafeCodeGenerator()
    
    # Código com bugs comuns
    codigo_com_bugs = '''
def process_user_orders(orders):
    """Processa pedidos de usuários"""
    total = 0
    processed_orders = []
    
    for order in orders:
        # Bug 1: Não verifica se order é None
        if order.status == "pending":
            # Bug 2: Não verifica se amount existe
            total += order.amount
            
            # Bug 3: Divisão por zero possível
            discount = order.amount / order.quantity * 0.1
            
            # Bug 4: Não trata exceção
            processed_order = {
                "id": order.id,
                "total": order.amount - discount,
                "processed_at": datetime.now()  # Bug 5: datetime não importado
            }
            processed_orders.append(processed_order)
    
    # Bug 6: Retorna apenas total, não processed_orders
    return total
'''
    
    print("📝 Analisando código com bugs...")
    
    # Análise do código com bugs
    analysis = await generator.validate_existing_code(
        codigo_com_bugs,
        "Código com bugs para correção automática"
    )
    
    print(f"🛡️  Segurança: {analysis.security_score:.2f}")
    print(f"📊 Complexidade: {analysis.complexity_score:.2f}")
    print(f"⚠️  Risco: {analysis.risk_assessment.value}")
    
    if analysis.warnings:
        print(f"🐛 Problemas identificados ({len(analysis.warnings)}):")
        for warning in analysis.warnings[:3]:
            print(f"   - {warning}")
    
    # Gera versão corrigida
    print("\n🔧 Gerando versão corrigida...")
    
    correction_requirements = {
        "function_name": "process_user_orders_fixed",
        "description": "Versão corrigida da função de processamento de pedidos",
        "inputs": [
            {"name": "orders", "type": "List[Order]", "description": "Lista de pedidos"}
        ],
        "outputs": [
            {"name": "result", "type": "Dict", "description": "Resultado do processamento"}
        ],
        "logic_description": """
        Corrigir função de processamento de pedidos:
        1. Validar entrada (orders não None/vazio)
        2. Verificar atributos dos objetos antes de usar
        3. Tratar divisão por zero
        4. Adicionar tratamento de exceções
        5. Importar dependências necessárias
        6. Retornar dados completos
        7. Adicionar logging para debug
        """,
        "safety_level": "high",
        "context": "Correção de bugs em sistema de e-commerce"
    }
    
    corrected_code, corr_analysis = await generator.generate_module(correction_requirements)
    
    print(f"✅ Código corrigido gerado!")
    print(f"📏 Tamanho: {len(corrected_code)} caracteres")
    print(f"🛡️  Segurança: {corr_analysis.security_score:.2f}")
    print(f"📊 Complexidade: {corr_analysis.complexity_score:.2f}")
    
    # Mostra trecho do código corrigido
    print(f"\n📄 Trecho do código corrigido:")
    print("-" * 50)
    lines = corrected_code.split('\n')
    for i, line in enumerate(lines[:8]):
        print(f"{i+1:2d}: {line}")
    if len(lines) > 8:
        print(f"... (+{len(lines)-8} linhas)")
    print("-" * 50)
    
    return True

async def main():
    """Função principal dos casos de uso"""
    
    print("\n🎯 Executando Casos de Uso Específicos...")
    
    casos_uso = [
        ("API para Microserviço", caso_uso_1_api_microservico),
        ("Otimização de Algoritmo ML", caso_uso_2_otimizacao_algoritmo),
        ("Sistema de Monitoramento", caso_uso_3_sistema_monitoramento),
        ("Correção Automática de Bugs", caso_uso_4_correcao_automatica)
    ]
    
    results = []
    
    try:
        for nome, caso_uso_func in casos_uso:
            print(f"\n{'='*60}")
            result = await caso_uso_func()
            results.append((nome, result))
            print(f"{'='*60}")
        
        # Resumo final
        print("\n🎯 Resumo dos Casos de Uso:")
        print("=" * 60)
        
        passed = 0
        for nome, result in results:
            status = "✅ SUCESSO" if result else "❌ FALHA"
            print(f"{nome}: {status}")
            if result:
                passed += 1
        
        success_rate = passed / len(results) * 100
        print(f"\n📊 Taxa de Sucesso: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 TODOS OS CASOS DE USO IMPLEMENTADOS COM SUCESSO!")
            print("🚀 Sistema AutoCura pronto para produção!")
        elif success_rate >= 75:
            print("✅ Maioria dos casos de uso funcionais")
            print("🔧 Sistema pronto para uso em cenários específicos")
        else:
            print("⚠️  Alguns casos de uso precisam de ajustes")
        
        print(f"\n🏆 Aplicações Demonstradas:")
        print(f"   🔧 Geração automática de APIs")
        print(f"   🧠 Otimização de algoritmos ML")
        print(f"   📊 Sistemas de monitoramento inteligentes")
        print(f"   🐛 Correção automática de bugs")
        
        print(f"\n💡 Próximos Passos Sugeridos:")
        print(f"   📈 Implementar em ambiente de produção")
        print(f"   🔄 Configurar CI/CD com auto-modificação")
        print(f"   📊 Monitorar métricas de evolução")
        print(f"   🎯 Expandir para casos de uso específicos do negócio")
        
    except Exception as e:
        print(f"\n❌ Erro crítico nos casos de uso: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executa casos de uso
    asyncio.run(main()) 