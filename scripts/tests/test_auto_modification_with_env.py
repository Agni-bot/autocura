#!/usr/bin/env python3
"""
Teste Completo com Carregamento de .env - Sistema AutoCura
=========================================================

Teste que carrega automaticamente o arquivo .env e testa
o sistema com as configurações reais.
"""

import asyncio
import os
from datetime import datetime

# Carrega variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Arquivo .env carregado com sucesso")
except ImportError:
    print("⚠️  python-dotenv não encontrado. Instalando...")
    import subprocess
    subprocess.check_call(["pip", "install", "python-dotenv"])
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv instalado e .env carregado")
except Exception as e:
    print(f"❌ Erro ao carregar .env: {e}")
    print("   Continuando com variáveis de ambiente do sistema...")

# Verifica configuração
OPENAI_API_KEY = os.getenv('AI_API_KEY')
SIMULATION_MODE = not OPENAI_API_KEY or OPENAI_API_KEY == 'sua-chave-openai-aqui'

print("🚀 Sistema AutoCura - Teste com Configuração Real")
print("=" * 60)
print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if SIMULATION_MODE:
    print("🔧 Modo: SIMULAÇÃO")
    print("   ⚠️  Chave OpenAI não configurada ou é placeholder")
    print("   💡 Configure AI_API_KEY no arquivo .env")
else:
    print("🔧 Modo: COMPLETO (com OpenAI)")
    print(f"   ✅ Chave OpenAI: {OPENAI_API_KEY[:8]}...{OPENAI_API_KEY[-4:]}")

try:
    from src.core.self_modify.safe_code_generator import SafeCodeGenerator, RiskAssessment
    from src.core.self_modify.evolution_controller import (
        EvolutionController, EvolutionRequest, EvolutionType
    )
    print("✅ Módulos de auto-modificação importados com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    exit(1)

async def test_openai_connection():
    """Testa conexão com OpenAI"""
    print("\n🔗 Teste 1: Conexão com OpenAI")
    print("=" * 40)
    
    if SIMULATION_MODE:
        print("⚠️  Pulando teste de conexão (modo simulação)")
        return False
    
    try:
        generator = SafeCodeGenerator(OPENAI_API_KEY)
        
        # Teste simples de geração
        requirements = {
            "function_name": "test_connection",
            "description": "Função de teste para verificar conexão",
            "inputs": [],
            "outputs": [],
            "logic_description": "Retorna uma mensagem de teste",
            "safety_level": "high"
        }
        
        print("📡 Testando conexão com OpenAI...")
        code, analysis = await generator.generate_module(requirements)
        
        print("✅ Conexão com OpenAI estabelecida!")
        print(f"🧠 Análise cognitiva: {analysis.openai_analysis.get('summary', 'OK')}")
        print(f"🛡️  Score de segurança: {analysis.security_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão com OpenAI: {e}")
        return False

async def test_advanced_code_generation():
    """Teste de geração avançada de código"""
    print("\n🧠 Teste 2: Geração Avançada de Código")
    print("=" * 45)
    
    try:
        generator = SafeCodeGenerator(OPENAI_API_KEY if not SIMULATION_MODE else None)
        
        # Função mais complexa
        requirements = {
            "function_name": "data_processor",
            "description": "Processador de dados com validação e transformação",
            "inputs": [
                {"name": "data", "type": "List[Dict]", "description": "Lista de dados para processar"},
                {"name": "filters", "type": "Dict", "description": "Filtros a aplicar"}
            ],
            "outputs": [
                {"name": "processed_data", "type": "List[Dict]", "description": "Dados processados"},
                {"name": "stats", "type": "Dict", "description": "Estatísticas do processamento"}
            ],
            "logic_description": """
            1. Validar entrada de dados
            2. Aplicar filtros especificados
            3. Transformar dados conforme regras
            4. Calcular estatísticas
            5. Retornar dados processados e estatísticas
            """,
            "safety_level": "high",
            "context": "Sistema de processamento de dados empresariais"
        }
        
        print("📝 Gerando função complexa de processamento...")
        code, analysis = await generator.generate_module(requirements)
        
        print(f"✅ Código gerado com sucesso!")
        print(f"📏 Tamanho: {len(code)} caracteres")
        print(f"🛡️  Score de segurança: {analysis.security_score:.2f}")
        print(f"⚠️  Avaliação de risco: {analysis.risk_assessment.value}")
        print(f"✅ Conformidade ética: {analysis.ethical_compliance}")
        print(f"📊 Complexidade: {analysis.complexity_score:.2f}")
        
        # Mostra parte do código
        print(f"\n📄 Trecho do código gerado:")
        print("-" * 50)
        lines = code.split('\n')
        for i, line in enumerate(lines[:15]):
            print(f"{i+1:2d}: {line}")
        if len(lines) > 15:
            print(f"... (+{len(lines)-15} linhas)")
        print("-" * 50)
        
        # Análise detalhada se disponível
        if not SIMULATION_MODE and analysis.openai_analysis:
            openai_analysis = analysis.openai_analysis
            print(f"\n🧠 Análise Cognitiva OpenAI:")
            
            if 'security_assessment' in openai_analysis:
                sec = openai_analysis['security_assessment']
                print(f"   🛡️  Segurança: {sec.get('score', 0):.2f}")
                if sec.get('risks'):
                    print(f"   ⚠️  Riscos: {', '.join(sec['risks'][:3])}")
            
            if 'quality_assessment' in openai_analysis:
                qual = openai_analysis['quality_assessment']
                print(f"   📊 Qualidade: {qual.get('score', 0):.2f}")
                if qual.get('strengths'):
                    print(f"   ✅ Pontos fortes: {', '.join(qual['strengths'][:2])}")
            
            print(f"   📝 Recomendação: {openai_analysis.get('overall_recommendation', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na geração avançada: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_evolution_system():
    """Teste do sistema de evolução completo"""
    print("\n🎛️  Teste 3: Sistema de Evolução Completo")
    print("=" * 50)
    
    try:
        controller = EvolutionController(OPENAI_API_KEY if not SIMULATION_MODE else None)
        
        # Solicitação de evolução complexa
        request = EvolutionRequest(
            evolution_type=EvolutionType.FEATURE_ADDITION,
            description="Implementar sistema de cache inteligente",
            requirements={
                "function_name": "intelligent_cache",
                "logic_description": """
                Sistema de cache que:
                1. Armazena dados com TTL dinâmico
                2. Implementa estratégias de eviction inteligentes
                3. Monitora hit rate e performance
                4. Auto-ajusta parâmetros baseado no uso
                """,
                "inputs": [
                    {"name": "key", "type": "str", "description": "Chave do cache"},
                    {"name": "value", "type": "Any", "description": "Valor a cachear"},
                    {"name": "ttl", "type": "Optional[int]", "description": "TTL em segundos"}
                ],
                "outputs": [
                    {"name": "cached_value", "type": "Any", "description": "Valor do cache"},
                    {"name": "cache_stats", "type": "Dict", "description": "Estatísticas do cache"}
                ],
                "test_data": {
                    "test_keys": ["user:123", "config:app", "data:temp"],
                    "test_values": [{"id": 123}, {"theme": "dark"}, [1, 2, 3]]
                }
            },
            safety_level="high",
            priority=2,
            context="Sistema de cache para aplicação de alta performance",
            requester="test_system"
        )
        
        print("📝 Solicitando evolução do sistema...")
        request_id = await controller.request_evolution(request)
        print(f"🆔 ID da solicitação: {request_id}")
        
        # Aguarda processamento
        print("⏳ Aguardando processamento...")
        await asyncio.sleep(3)  # Tempo para processamento
        
        # Verifica resultados
        stats = controller.get_evolution_stats()
        print(f"\n📊 Estatísticas de Evolução:")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for subkey, subvalue in value.items():
                    print(f"    {subkey}: {subvalue}")
            else:
                print(f"  {key}: {value}")
        
        # Histórico detalhado
        history = controller.get_evolution_history(limit=3)
        if history:
            print(f"\n📋 Histórico Recente:")
            for evolution in history:
                status = "✅" if evolution['success'] else "❌"
                applied = "🚀" if evolution.get('applied') else "⏳"
                print(f"  {status} {applied} {evolution['request_id']}")
                print(f"      Tempo: {evolution['execution_time']:.2f}s")
                print(f"      Aprovação: {evolution['approval_level']}")
        
        # Aprovações pendentes
        pending = controller.get_pending_approvals()
        if pending:
            print(f"\n⏳ Aprovações Pendentes ({len(pending)}):")
            for approval in pending:
                print(f"  - {approval['request_id']}: {approval['approval_level']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no sistema de evolução: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Função principal do teste completo"""
    
    results = []
    
    try:
        # Executa testes
        print("\n🧪 Executando bateria de testes completa...")
        
        result1 = await test_openai_connection()
        results.append(("Conexão OpenAI", result1))
        
        result2 = await test_advanced_code_generation()
        results.append(("Geração Avançada", result2))
        
        result3 = await test_evolution_system()
        results.append(("Sistema de Evolução", result3))
        
        # Resumo final
        print("\n🎯 Resumo dos Testes:")
        print("=" * 50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        success_rate = passed / len(results) * 100
        print(f"\n📊 Taxa de Sucesso: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("🚀 Sistema AutoCura totalmente operacional!")
        elif success_rate >= 80:
            print("✅ Sistema majoritariamente funcional")
            print("🔧 Pequenos ajustes podem ser necessários")
        elif success_rate >= 60:
            print("⚠️  Sistema parcialmente funcional")
            print("🛠️  Correções necessárias")
        else:
            print("❌ Sistema com problemas críticos")
            print("🚨 Revisão completa necessária")
        
        # Informações de configuração
        print(f"\n⚙️  Configuração Utilizada:")
        print(f"   Modo: {'Simulação' if SIMULATION_MODE else 'Completo'}")
        print(f"   OpenAI: {'Não configurado' if SIMULATION_MODE else 'Configurado'}")
        print(f"   Arquivo .env: {'Carregado' if os.path.exists('.env') else 'Não encontrado'}")
        
    except Exception as e:
        print(f"\n❌ Erro crítico durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executa testes
    asyncio.run(main()) 