#!/usr/bin/env python3
"""
Teste da API reorganizada do Sistema AutoCura
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testando API AutoCura Reorganizada")
    print("=" * 50)
    
    # Teste 1: Página principal
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Página principal: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na página principal: {e}")
    
    # Teste 2: Documentação
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"✅ Documentação: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na documentação: {e}")
    
    # Teste 3: Buscar sugestões (vários endpoints possíveis)
    endpoints_to_test = [
        "/suggestions",
        "/api/suggestions", 
        "/buscar_sugestoes",
        "/sugestoes",
        "/get_suggestions"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sugestões encontradas em {endpoint}: {len(data)} sugestões")
                if data:
                    print(f"   Primeira sugestão: {data[0].get('titulo', 'N/A')}")
                break
            else:
                print(f"⚠️ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro em {endpoint}: {e}")
    
    # Teste 4: Health check
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no health check: {e}")

if __name__ == "__main__":
    test_api() 