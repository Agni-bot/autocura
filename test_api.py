import urllib.request
import json

try:
    # Testa a raiz (dashboard)
    response = urllib.request.urlopen('http://localhost:8080/')
    content = response.read().decode('utf-8')
    print("Dashboard está acessível!")
    print(f"Tamanho do conteúdo: {len(content)} bytes")
    
    # Testa o endpoint de saúde
    try:
        response = urllib.request.urlopen('http://localhost:8080/api/health')
        data = json.loads(response.read())
        print("\nAPI Health Check:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"\nErro no endpoint /api/health: {e}")
    
    # Testa o endpoint principal
    try:
        response = urllib.request.urlopen('http://localhost:8080/api')
        data = json.loads(response.read())
        print("\nAPI Root:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"\nErro no endpoint /api: {e}")
    
except Exception as e:
    print(f"Erro ao conectar com o servidor: {e}")
    print("Verifique se o servidor está rodando na porta 8080") 