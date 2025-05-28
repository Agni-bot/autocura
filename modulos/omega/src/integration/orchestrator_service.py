#!/usr/bin/env python3
"""
Serviço HTTP do Orquestrador de Integração
"""

import asyncio
import logging
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modulos.omega.src.integration.integration_orchestrator import IntegrationOrchestrator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="AutoCura Integration Orchestrator",
    description="Orquestrador de Integração entre Módulos",
    version="1.0.0"
)

# Variável global
orchestrator = None


@app.on_event("startup")
async def startup_event():
    """Inicializa o orquestrador na inicialização"""
    global orchestrator
    
    logger.info("🔗 Inicializando Orquestrador de Integração...")
    
    orchestrator = IntegrationOrchestrator()
    await orchestrator.initialize()
    
    logger.info("✅ Orquestrador de Integração inicializado!")


@app.on_event("shutdown")
async def shutdown_event():
    """Finaliza o orquestrador no encerramento"""
    logger.info("🛑 Finalizando Orquestrador de Integração...")
    logger.info("✅ Orquestrador finalizado")


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "service": "Integration Orchestrator",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")
        
    return {
        "status": "healthy",
        "service": "integration-orchestrator",
        "initialized": orchestrator is not None
    }


@app.get("/modules/status")
async def get_modules_status():
    """Obtém status dos módulos"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")
        
    return {
        "modules": {
            name: {
                "state": state.name,
                "health": orchestrator.module_health.get(name, 0.0)
            }
            for name, state in orchestrator.module_states.items()
        }
    }


@app.get("/protocols")
async def get_protocols():
    """Obtém protocolos de comunicação disponíveis"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")
        
    return {
        "protocols": [p.name for p in orchestrator.communication_protocols]
    }


@app.get("/synergies/active")
async def get_active_synergies():
    """Obtém sinergias ativas"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")
        
    return {
        "synergies": list(orchestrator.active_synergies)
    }


@app.post("/integrate/{source}/{target}")
async def integrate_modules(source: str, target: str):
    """Integra dois módulos"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")
        
    try:
        result = await orchestrator.integrate_modules(source, target)
        return {
            "status": "success",
            "source": source,
            "target": target,
            "integration_id": result.get("id")
        }
    except Exception as e:
        logger.error(f"Erro na integração: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/integration")
async def get_integration_metrics():
    """Obtém métricas de integração"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")
        
    return {
        "total_integrations": orchestrator.total_integrations,
        "successful_integrations": orchestrator.successful_integrations,
        "failed_integrations": orchestrator.failed_integrations,
        "average_integration_time": orchestrator.average_integration_time
    }


@app.post("/synergy/detect")
async def detect_synergies():
    """Detecta possíveis sinergias entre módulos"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")
        
    try:
        synergies = await orchestrator.detect_synergies()
        return {
            "status": "success",
            "detected_synergies": synergies
        }
    except Exception as e:
        logger.error(f"Erro na detecção de sinergias: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/communication/logs")
async def get_communication_logs():
    """Obtém logs de comunicação recentes"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orquestrador não inicializado")
        
    return {
        "logs": orchestrator.communication_logs[-100:]  # Últimos 100 logs
    }


def main():
    """Função principal"""
    port = 9004
    logger.info(f"🚀 Iniciando Orquestrador de Integração na porta {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main() 