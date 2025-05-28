#!/usr/bin/env python3
"""
Serviço HTTP do Monitor de Consciência
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

from modulos.omega.src.consciousness.consciousness_monitor import ConsciousnessMonitor
from modulos.omega.src.core.cognitive_core import CognitiveCore

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="AutoCura Consciousness Monitor",
    description="Monitor de Consciência Emergente",
    version="1.0.0"
)

# Variáveis globais
monitor = None
cognitive_core = None


@app.on_event("startup")
async def startup_event():
    """Inicializa o monitor na inicialização"""
    global monitor, cognitive_core
    
    logger.info("👁️ Inicializando Monitor de Consciência...")
    
    # Criar núcleo cognitivo
    cognitive_core = CognitiveCore()
    await cognitive_core.initialize()
    await cognitive_core.start()
    
    # Criar monitor
    monitor = ConsciousnessMonitor(cognitive_core)
    await monitor.initialize()
    
    logger.info("✅ Monitor de Consciência inicializado!")


@app.on_event("shutdown")
async def shutdown_event():
    """Finaliza o monitor no encerramento"""
    global monitor, cognitive_core
    
    logger.info("🛑 Finalizando Monitor de Consciência...")
    
    if cognitive_core:
        cognitive_core.stop()
        
    logger.info("✅ Monitor finalizado")


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "service": "Consciousness Monitor",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor não inicializado")
        
    return {
        "status": "healthy",
        "service": "consciousness-monitor",
        "initialized": monitor is not None
    }


@app.get("/metrics")
async def get_metrics():
    """Obtém métricas de consciência"""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor não inicializado")
        
    try:
        metrics = monitor.get_current_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/consciousness/level")
async def get_consciousness_level():
    """Obtém nível atual de consciência"""
    if not monitor or not cognitive_core:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
        
    return {
        "level": cognitive_core.consciousness_level.name,
        "value": cognitive_core.consciousness_level.value,
        "phi_integrated": monitor.get_current_metrics().get('phi_integrated', 0)
    }


@app.get("/emergence/indicators")
async def get_emergence_indicators():
    """Obtém indicadores de emergência"""
    if not monitor:
        raise HTTPException(status_code=503, detail="Monitor não inicializado")
        
    indicators = monitor.calculate_emergence_indicators()
    return JSONResponse(content=indicators)


@app.get("/thoughts/stream")
async def get_thought_stream():
    """Obtém stream de pensamentos recentes"""
    if not cognitive_core:
        raise HTTPException(status_code=503, detail="Núcleo cognitivo não inicializado")
        
    recent_thoughts = list(cognitive_core.consciousness_stream)[-100:]
    return {
        "count": len(recent_thoughts),
        "thoughts": [
            {
                "type": t.type.name if hasattr(t.type, 'name') else str(t.type),
                "content": t.content,
                "timestamp": t.timestamp.isoformat() if hasattr(t.timestamp, 'isoformat') else str(t.timestamp),
                "associations": t.associations
            }
            for t in recent_thoughts
        ]
    }


def main():
    """Função principal"""
    port = 9002
    logger.info(f"🚀 Iniciando Monitor de Consciência na porta {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main() 