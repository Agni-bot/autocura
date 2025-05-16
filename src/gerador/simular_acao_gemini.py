import requests
import json

# Configuração do endpoint do gerador de ações
ENDPOINT = "http://localhost:8080/api/acoes"

# Diagnóstico de exemplo
payload = {
    "diagnosticos": [
        {
            "id": "diag1",
            "tipo": "ANOMALIA",
            "descricao": "Consumo de CPU acima do esperado",
            "causa_raiz": "Processo de indexação em loop",
            "impacto": "Risco de indisponibilidade",
            "prioridade": 5,
            "padroes": [],
            "timestamp": 1715000000
        }
    ]
}

print("Enviando diagnóstico de exemplo para o gerador de ações...")
response = requests.post(ENDPOINT, json=payload)

if response.status_code == 200:
    planos = response.json()
    print("\nPlanos de ação gerados:")
    for plano in planos:
        print(f"\nPlano: {plano['id']}")
        for acao in plano['acoes']:
            print(f"  - Tipo: {acao['tipo']}")
            print(f"    Descrição: {acao['descricao']}")
            print(f"    Impacto esperado: {acao['impacto_esperado']}")
            print(f"    Comentários (Gemini):\n      {acao['comentarios'][0] if acao['comentarios'] else 'Sem análise'}")
else:
    print(f"Erro ao gerar ações: {response.status_code} - {response.text}") 