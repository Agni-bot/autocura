import urllib.request
import urllib.error
import json
import time

print("=== Teste de Persistência de Sugestões ===\n")

# 1. Buscar sugestões atuais
print("1. Buscando sugestões atuais...")
response = urllib.request.urlopen('http://localhost:8000/api/evolution/suggestions')
data = json.loads(response.read())
print(f"   Sugestões pendentes: {data['stats']['pending']}")
print(f"   Sugestões aplicadas: {data['stats']['applied_total']}")
print(f"   Total de sugestões disponíveis: {len(data['suggestions'])}")

if data['suggestions']:
    # 2. Aplicar primeira sugestão
    first_suggestion = data['suggestions'][0]
    print(f"\n2. Aplicando sugestão: {first_suggestion['title']}")
    
    apply_data = {
        "suggestion_id": first_suggestion['id'],
        "approved": True,
        "approver": "test_persistence"
    }
    
    req = urllib.request.Request(
        'http://localhost:8000/api/evolution/apply',
        data=json.dumps(apply_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    response = urllib.request.urlopen(req)
    result = json.loads(response.read())
    print(f"   Resultado: {result['message']}")
    
    # 3. Aguardar um pouco
    print("\n3. Aguardando 3 segundos...")
    time.sleep(3)
    
    # 4. Buscar sugestões novamente
    print("\n4. Buscando sugestões após aplicação...")
    response = urllib.request.urlopen('http://localhost:8000/api/evolution/suggestions')
    data_after = json.loads(response.read())
    print(f"   Sugestões pendentes: {data_after['stats']['pending']}")
    print(f"   Sugestões aplicadas: {data_after['stats']['applied_total']}")
    print(f"   Total de sugestões disponíveis: {len(data_after['suggestions'])}")
    
    # 5. Verificar se a sugestão foi removida
    suggestion_ids_after = [s['id'] for s in data_after['suggestions']]
    if first_suggestion['id'] not in suggestion_ids_after:
        print(f"\n✅ SUCESSO! A sugestão '{first_suggestion['id']}' não aparece mais na lista!")
    else:
        print(f"\n❌ ERRO! A sugestão '{first_suggestion['id']}' ainda está na lista!")
        
else:
    print("\n⚠️ Todas as sugestões já foram aplicadas!")
    print("\nResetando sugestões aplicadas...")
    
    # Reset
    req = urllib.request.Request(
        'http://localhost:8000/api/evolution/reset',
        data=b'{}',
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    response = urllib.request.urlopen(req)
    result = json.loads(response.read())
    print(f"Resultado: {result['message']}")
    
print("\n=== Teste concluído ===") 