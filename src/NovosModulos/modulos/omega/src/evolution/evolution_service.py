#!/usr/bin/env python3
"""
Serviço HTTP do Motor de Evolução
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

from modulos.omega.src.evolution.evolution_engine import EvolutionEngine

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="AutoCura Evolution Engine",
    description="Motor de Evolução Adaptativa",
    version="1.0.0"
)

# Variável global
engine = None


@app.on_event("startup")
async def startup_event():
    """Inicializa o motor na inicialização"""
    global engine
    
    logger.info("🧬 Inicializando Motor de Evolução...")
    
    engine = EvolutionEngine()
    await engine.initialize()
    
    logger.info("✅ Motor de Evolução inicializado!")


@app.on_event("shutdown")
async def shutdown_event():
    """Finaliza o motor no encerramento"""
    logger.info("🛑 Finalizando Motor de Evolução...")
    logger.info("✅ Motor finalizado")


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "service": "Evolution Engine",
        "status": "online",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Verifica saúde do serviço"""
    if not engine:
        raise HTTPException(status_code=503, detail="Motor não inicializado")
        
    return {
        "status": "healthy",
        "service": "evolution-engine",
        "initialized": engine is not None
    }


@app.get("/population/status")
async def get_population_status():
    """Obtém status da população"""
    if not engine:
        raise HTTPException(status_code=503, detail="Motor não inicializado")
        
    return {
        "generation": engine.generation,
        "population_size": len(engine.population),
        "best_fitness": engine.best_fitness,
        "average_fitness": engine.average_fitness
    }


@app.post("/evolve")
async def trigger_evolution():
    """Dispara um ciclo de evolução"""
    if not engine:
        raise HTTPException(status_code=503, detail="Motor não inicializado")
        
    try:
        await engine.evolve()
        return {
            "status": "success",
            "generation": engine.generation,
            "best_fitness": engine.best_fitness
        }
    except Exception as e:
        logger.error(f"Erro na evolução: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/strategies")
async def get_evolution_strategies():
    """Obtém estratégias de evolução disponíveis"""
    if not engine:
        raise HTTPException(status_code=503, detail="Motor não inicializado")
        
    return {
        "strategies": [s.name for s in engine.evolution_strategies]
    }


@app.get("/genome/{genome_id}")
async def get_genome(genome_id: str):
    """Obtém informações de um genoma específico"""
    if not engine:
        raise HTTPException(status_code=503, detail="Motor não inicializado")
        
    genome = engine.get_genome(genome_id)
    if not genome:
        raise HTTPException(status_code=404, detail="Genoma não encontrado")
        
    return JSONResponse(content=genome.to_dict())


@app.post("/mutate/{genome_id}")
async def mutate_genome(genome_id: str):
    """Aplica mutação em um genoma"""
    if not engine:
        raise HTTPException(status_code=503, detail="Motor não inicializado")
        
    try:
        mutated = await engine.mutate_genome(genome_id)
        return {
            "status": "success",
            "original_id": genome_id,
            "mutated_id": mutated.id
        }
    except Exception as e:
        logger.error(f"Erro na mutação: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fitness/history")
async def get_fitness_history():
    """Obtém histórico de fitness"""
    if not engine:
        raise HTTPException(status_code=503, detail="Motor não inicializado")
        
    return {
        "history": engine.fitness_history[-100:],  # Últimas 100 gerações
        "current_generation": engine.generation
    }


def main():
    """Função principal"""
    port = 9003
    logger.info(f"🚀 Iniciando Motor de Evolução na porta {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    main() 