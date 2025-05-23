from fastapi import APIRouter, HTTPException
from typing import List, Dict
import random
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard():
    # Status do sistema
    status_sistema = "Operacional" if random.random() > 0.1 else "Degradado"
    
    # Métricas do sistema
    metricas = {
        "labels": [(datetime.now() - timedelta(minutes=i)).strftime("%H:%M") for i in range(10, 0, -1)],
        "cpu": [round(random.uniform(20, 80), 2) for _ in range(10)],
        "memoria": [round(random.uniform(30, 90), 2) for _ in range(10)]
    }
    
    # Alertas
    alertas = {
        "labels": ["Crítico", "Alerta", "Info"],
        "values": [
            random.randint(0, 5),
            random.randint(0, 10),
            random.randint(0, 15)
        ]
    }
    
    # Últimas ações
    ultimas_acoes = []
    tipos = ["Otimização", "Manutenção", "Correção"]
    status_list = ["Pendente", "Em Execução", "Concluída", "Falha"]
    
    for i in range(5):
        ultimas_acoes.append({
            "id": i + 1,
            "tipo": random.choice(tipos),
            "descricao": f"Ação {i+1} para melhoria do sistema",
            "status": random.choice(status_list),
            "data": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
        })
    
    return {
        "status_sistema": status_sistema,
        "acoes_pendentes": random.randint(0, 10),
        "alertas_ativos": random.randint(0, 15),
        "performance": round(random.uniform(70, 100), 1),
        "metricas": metricas,
        "alertas": alertas,
        "ultimas_acoes": ultimas_acoes
    }

@router.get("/metricas")
async def get_metricas():
    return {
        "throughput": round(random.uniform(100, 1000), 2),
        "taxa_erro": round(random.uniform(0, 5), 2),
        "latencia": round(random.uniform(10, 100), 2)
    }

@router.get("/alertas")
async def get_alertas():
    severidades = ["alert-warning", "alert-danger", "alert-info"]
    alertas = []
    
    for i in range(random.randint(0, 5)):
        alertas.append({
            "titulo": f"Alerta {i+1}",
            "descricao": f"Descrição do alerta {i+1}",
            "severidade": random.choice(severidades),
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat()
        })
    
    return alertas

@router.get("/acoes")
async def get_acoes():
    tipos = ["Otimização", "Manutenção", "Correção"]
    acoes = []
    
    for i in range(random.randint(0, 5)):
        acoes.append({
            "tipo": random.choice(tipos),
            "descricao": f"Ação {i+1} para melhoria do sistema",
            "prioridade": random.randint(1, 5)
        })
    
    return acoes 