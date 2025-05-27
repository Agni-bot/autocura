#!/usr/bin/env python3
"""
Teste simples da API de Sugestões
"""

import urllib.request
import json

def test_api():
    try:
        print("Testando API...")
        response = urllib.request.urlopen('http://localhost:8001/evolution/suggestions')
        data = json.load(response)
        print(f"Status: OK")
        print(f"Sugestoes encontradas: {len(data['suggestions'])}")
        
        for i, suggestion in enumerate(data['suggestions'], 1):
            print(f"  {i}. {suggestion['type'].upper()}: {suggestion['title']} ({suggestion['priority']})")
        
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    test_api() 