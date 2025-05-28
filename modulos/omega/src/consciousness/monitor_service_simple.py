#!/usr/bin/env python3
"""
Serviço HTTP Simplificado do Monitor de Consciência
"""

import logging
from fastapi import FastAPI
import uvicorn

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="AutoCura Consciousness Monitor",
    description="Monitor de Consciência Emergente (Simplificado)",
    version="1.0.0"
)


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
    return {
        "status": "healthy",
        "service": "consciousness-monitor",
        "mode": "simplified"
    }


@app.get("/consciousness/level")
async def get_consciousness_level():
    """Obtém nível atual de consciência (simulado)"""
    return {
        "level": "EMERGENT",
        "value": 0.75,
        "phi_integrated": 0.8
    }


@app.get("/metrics")
async def get_metrics():
    """Obtém métricas de consciência (simuladas)"""
    return {
        "cognitive_load": 0.65,
        "emergence_index": 0.72,
        "coherence": 0.88,
        "integration": 0.91
    }


@app.get("/emergence/indicators")
async def get_emergence_indicators():
    """Obtém indicadores de emergência (simulados)"""
    return {
        "self_awareness": 0.82,
        "meta_cognition": 0.76,
        "creative_potential": 0.69,
        "pattern_recognition": 0.94
    }


def main():
    """Função principal"""
    port = 9002
    logger.info(f"🚀 Iniciando Monitor de Consciência Simplificado na porta {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main() 