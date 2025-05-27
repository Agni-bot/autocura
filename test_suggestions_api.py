import urllib.request
import urllib.error
import json

print("=== Teste dos Endpoints de Sugestões ===\n")

# 1. Teste de buscar sugestões
try:
    print("1. Testando GET /api/evolution/suggestions...")
    response = urllib.request.urlopen('http://localhost:8000/api/evolution/suggestions')
    data = json.loads(response.read())
    print(f"✅ Sucesso! {len(data.get('suggestions', []))} sugestões encontradas")
    
    # Mostra primeira sugestão
    if data.get('suggestions'):
        first = data['suggestions'][0]
        print(f"\nPrimeira sugestão:")
        print(f"  ID: {first['id']}")
        print(f"  Título: {first['title']}")
        print(f"  Tipo: {first['type']}")
        print(f"  Prioridade: {first['priority']}")
except Exception as e:
    print(f"❌ Erro: {e}")

# 2. Teste de preview
try:
    print("\n2. Testando GET /api/evolution/preview/perf-opt-001...")
    response = urllib.request.urlopen('http://localhost:8000/api/evolution/preview/perf-opt-001')
    data = json.loads(response.read())
    print(f"✅ Preview obtido com sucesso!")
    print(f"  Tem código: {'Sim' if data.get('code') else 'Não'}")
    print(f"  Tem descrição: {'Sim' if data.get('description') else 'Não'}")
except Exception as e:
    print(f"❌ Erro: {e}")

# 3. Teste de aplicar sugestão
try:
    print("\n3. Testando POST /api/evolution/apply...")
    
    # Dados para enviar
    apply_data = {
        "suggestion_id": "perf-opt-001",
        "approved": True,
        "approver": "test_script"
    }
    
    # Prepara requisição POST
    req = urllib.request.Request(
        'http://localhost:8000/api/evolution/apply',
        data=json.dumps(apply_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    response = urllib.request.urlopen(req)
    data = json.loads(response.read())
    
    if data.get('success'):
        print(f"✅ Aplicação bem sucedida!")
        print(f"  Mensagem: {data.get('message')}")
        print(f"  Tempo de execução: {data.get('execution_time')}s")
    else:
        print(f"❌ Falha na aplicação: {data.get('message')}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# 4. Teste de estatísticas
try:
    print("\n4. Testando GET /api/evolution/stats...")
    response = urllib.request.urlopen('http://localhost:8000/api/evolution/stats')
    data = json.loads(response.read())
    print(f"✅ Estatísticas obtidas com sucesso!")
    print(f"  Pendentes: {data.get('pending', 0)}")
    print(f"  Aplicadas hoje: {data.get('applied_today', 0)}")
    print(f"  Taxa de aceitação: {data.get('acceptance_rate', 0)}%")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n=== Teste concluído ===") 