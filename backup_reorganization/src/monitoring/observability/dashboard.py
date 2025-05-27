from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..services.auth import get_current_active_user
from ..services.utils import format_response
import httpx

router = APIRouter()
templates = Jinja2Templates(directory="src/portal/templates")

@router.get("/overview")
async def get_dashboard_overview(
    current_user: str = Depends(get_current_active_user)
):
    """Retorna a visão geral do dashboard."""
    try:
        # Aqui você implementaria a lógica para buscar os dados do dashboard
        # Por enquanto, retornamos dados de exemplo
        overview = {
            "system_status": {
                "health": "healthy",
                "uptime": "99.99%",
                "last_incident": (datetime.utcnow() - timedelta(days=2)).isoformat()
            },
            "metrics": {
                "cpu": {
                    "current": 45,
                    "trend": "stable",
                    "threshold": 80
                },
                "memory": {
                    "current": 60,
                    "trend": "stable",
                    "threshold": 85
                },
                "disk": {
                    "current": 40,
                    "trend": "stable",
                    "threshold": 90
                }
            },
            "alerts": {
                "active": 2,
                "critical": 0,
                "warning": 2
            },
            "incidents": {
                "open": 1,
                "resolved_today": 0,
                "total_this_week": 2
            }
        }
        return format_response(overview)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_dashboard_metrics(
    current_user: str = Depends(get_current_active_user),
    time_range: str = "1h"
):
    """Retorna as métricas para o dashboard."""
    try:
        # Aqui você implementaria a lógica para buscar as métricas
        # Por enquanto, retornamos dados de exemplo
        metrics = {
            "cpu": {
                "data": [
                    {
                        "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                        "value": 45 + (i % 10)
                    }
                    for i in range(60)
                ],
                "threshold": 80
            },
            "memory": {
                "data": [
                    {
                        "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                        "value": 60 + (i % 5)
                    }
                    for i in range(60)
                ],
                "threshold": 85
            },
            "disk": {
                "data": [
                    {
                        "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                        "value": 40 + (i % 3)
                    }
                    for i in range(60)
                ],
                "threshold": 90
            }
        }
        return format_response(metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_dashboard_alerts(
    current_user: str = Depends(get_current_active_user),
    status: Optional[str] = None
):
    """Retorna os alertas para o dashboard."""
    try:
        # Aqui você implementaria a lógica para buscar os alertas
        # Por enquanto, retornamos dados de exemplo
        alerts = [
            {
                "id": f"alert_{i}",
                "title": f"Alerta {i}",
                "severity": "warning",
                "status": "active",
                "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                "source": "monitoring",
                "description": f"Descrição do alerta {i}",
                "actions": [
                    {
                        "id": "ack",
                        "label": "Reconhecer",
                        "type": "button"
                    },
                    {
                        "id": "view",
                        "label": "Ver Detalhes",
                        "type": "link",
                        "url": f"/monitoring/alerts/{i}"
                    }
                ]
            }
            for i in range(5)
        ]
        
        if status:
            alerts = [a for a in alerts if a["status"] == status]
        
        return format_response(alerts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/incidents")
async def get_dashboard_incidents(
    current_user: str = Depends(get_current_active_user),
    status: Optional[str] = None
):
    """Retorna os incidentes para o dashboard."""
    try:
        # Aqui você implementaria a lógica para buscar os incidentes
        # Por enquanto, retornamos dados de exemplo
        incidents = [
            {
                "id": f"incident_{i}",
                "title": f"Incidente {i}",
                "severity": "high",
                "status": "open",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "affected_components": ["server1", "app1"],
                "description": f"Descrição do incidente {i}",
                "actions": [
                    {
                        "id": "resolve",
                        "label": "Resolver",
                        "type": "button"
                    },
                    {
                        "id": "view",
                        "label": "Ver Detalhes",
                        "type": "link",
                        "url": f"/incidents/{i}"
                    }
                ]
            }
            for i in range(3)
        ]
        
        if status:
            incidents = [i for i in incidents if i["status"] == status]
        
        return format_response(incidents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/custom-widgets")
async def get_custom_widgets(
    current_user: str = Depends(get_current_active_user)
):
    """Retorna os widgets personalizados do dashboard."""
    try:
        # Aqui você implementaria a lógica para buscar os widgets personalizados
        # Por enquanto, retornamos dados de exemplo
        widgets = [
            {
                "id": f"widget_{i}",
                "title": f"Widget {i}",
                "type": "chart",
                "data": {
                    "labels": [f"Label {j}" for j in range(5)],
                    "values": [j * 10 for j in range(5)]
                },
                "position": {
                    "x": i * 2,
                    "y": 0,
                    "width": 2,
                    "height": 2
                }
            }
            for i in range(4)
        ]
        return format_response(widgets)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/layout")
async def update_dashboard_layout(
    layout: Dict,
    current_user: str = Depends(get_current_active_user)
):
    """Atualiza o layout do dashboard."""
    try:
        # Aqui você implementaria a lógica para atualizar o layout
        # Por enquanto, apenas simulamos a operação
        return format_response({
            "message": "Layout do dashboard atualizado com sucesso",
            "layout": layout
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/will-dashboard", response_class=HTMLResponse)
async def will_dashboard(request: Request):
    status = None
    decision = None
    try:
        async with httpx.AsyncClient() as client:
            status_resp = await client.get("http://localhost:5000/api/will/status")
            if status_resp.status_code == 200:
                status = status_resp.json()
            decision_resp = await client.post("http://localhost:5000/api/will/decision", json={"asset": "EURUSD", "volume": 0.1})
            if decision_resp.status_code == 200:
                decision = decision_resp.json()
    except Exception as e:
        status = {"error": str(e)}
    return templates.TemplateResponse("will_dashboard.html", {"request": request, "status": status, "decision": decision})

@router.get("/diagnostico-holografico", response_class=HTMLResponse)
async def diagnostico_holografico(request: Request):
    diagnostico_status = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:9082/api/status")
            if resp.status_code == 200:
                diagnostico_status = resp.json()
    except Exception as e:
        diagnostico_status = {"error": str(e)}
    return templates.TemplateResponse("diagnostico_holografico.html", {"request": request, "diagnostico_status": diagnostico_status})

@router.get("/mapa-dependencias", response_class=HTMLResponse)
async def mapa_dependencias(request: Request):
    dependencies = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8084/dependencies/app1")
            if resp.status_code == 200:
                dependencies = resp.json()
    except Exception as e:
        dependencies = {"error": str(e)}
    return templates.TemplateResponse("mapa_dependencias.html", {"request": request, "dependencies": dependencies})

@router.get("/configuracoes", response_class=HTMLResponse)
async def configuracoes(request: Request):
    return templates.TemplateResponse("configuracoes.html", {"request": request})

@router.get("/metricas", response_class=HTMLResponse)
async def metricas(request: Request):
    metricas = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:9080/api/metricas")
            if resp.status_code == 200:
                metricas = resp.json()
    except Exception as e:
        metricas = {"error": str(e)}
    return templates.TemplateResponse("metricas.html", {"request": request, "metricas": metricas})

@router.get("/alertas", response_class=HTMLResponse)
async def alertas(request: Request):
    alertas = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:9080/api/alertas")
            if resp.status_code == 200:
                alertas = resp.json()
    except Exception as e:
        alertas = {"error": str(e)}
    return templates.TemplateResponse("alertas.html", {"request": request, "alertas": alertas})

@router.get("/incidentes", response_class=HTMLResponse)
async def incidentes(request: Request):
    incidentes = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:9080/api/incidentes")
            if resp.status_code == 200:
                incidentes = resp.json()
    except Exception as e:
        incidentes = {"error": str(e)}
    return templates.TemplateResponse("incidentes.html", {"request": request, "incidentes": incidentes})

@router.get("/relatorios", response_class=HTMLResponse)
async def relatorios(request: Request):
    relatorios = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:9080/api/relatorios")
            if resp.status_code == 200:
                relatorios = resp.json()
    except Exception as e:
        relatorios = {"error": str(e)}
    return templates.TemplateResponse("relatorios.html", {"request": request, "relatorios": relatorios})

@router.get("/documentacao", response_class=HTMLResponse)
async def documentacao(request: Request):
    # Exibe link para Swagger do Will
    return templates.TemplateResponse("documentacao.html", {"request": request, "swagger_url": "http://localhost:5000/docs"})

@router.get("/analise-preditiva", response_class=HTMLResponse)
async def analise_preditiva(request: Request):
    predicao = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8084/predictions/cpu")
            if resp.status_code == 200:
                predicao = resp.json()
    except Exception as e:
        predicao = {"error": str(e)}
    return templates.TemplateResponse("analise_preditiva.html", {"request": request, "predicao": predicao})

@router.get("/visualizacao-holografica", response_class=HTMLResponse)
async def visualizacao_holografica(request: Request):
    visualization = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:8084/visualization")
            if resp.status_code == 200:
                visualization = resp.json()
    except Exception as e:
        visualization = {"error": str(e)}
    return templates.TemplateResponse("visualizacao_holografica.html", {"request": request, "visualization": visualization})

@router.get("/integracoes", response_class=HTMLResponse)
async def integracoes(request: Request):
    gerador_status = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:9081/api/status")
            if resp.status_code == 200:
                gerador_status = resp.json()
    except Exception as e:
        gerador_status = {"error": str(e)}
    return templates.TemplateResponse("integracoes.html", {"request": request, "gerador_status": gerador_status}) 