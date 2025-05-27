import urllib.request
import urllib.error
import json

print("=== Teste Detalhado do Servidor AutoCura ===\n")

# Lista de endpoints para testar
endpoints = [
    ('/', 'Dashboard HTML'),
    ('/api', 'API Root'),
    ('/api/', 'API Root com barra'),
    ('/api/health', 'Health Check'),
    ('/docs', 'Documentação API'),
    ('/redoc', 'ReDoc'),
]

for endpoint, description in endpoints:
    try:
        url = f'http://localhost:8080{endpoint}'
        print(f"Testando {description} ({endpoint})...")
        
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(request)
        
        content_type = response.headers.get('Content-Type', '')
        status = response.status
        
        print(f"  ✅ Status: {status}")
        print(f"  📄 Content-Type: {content_type}")
        
        if 'json' in content_type:
            data = json.loads(response.read())
            print(f"  📊 Resposta JSON: {json.dumps(data, indent=2)[:200]}...")
        else:
            content = response.read()
            print(f"  📏 Tamanho: {len(content)} bytes")
            
    except urllib.error.HTTPError as e:
        print(f"  ❌ Erro HTTP: {e.code} - {e.reason}")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
    
    print()

# Verifica headers do servidor
print("\n=== Verificando Headers do Servidor ===")
try:
    response = urllib.request.urlopen('http://localhost:8080/')
    print("Headers recebidos:")
    for header, value in response.headers.items():
        print(f"  {header}: {value}")
except Exception as e:
    print(f"Erro ao obter headers: {e}") 