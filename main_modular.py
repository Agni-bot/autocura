#!/usr/bin/env python3
"""
Sistema AutoCura - Main Modular
===============================

Versão modular do sistema AutoCura com nova estrutura organizacional.
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tentativa de importações modulares com fallbacks
modules_status = {
    "core": False,
    "services": False,
    "monitoring": False,
    "security": False
}

# === IMPORTAÇÕES CORE ===
try:
    from autocura.core.memoria.gerenciador_memoria import GerenciadorMemoria
    from autocura.core.memoria.registrador_contexto import RegistradorContexto
    modules_status["core"] = True
    logger.info("✅ Módulos core carregados da nova estrutura")
except ImportError as e:
    logger.warning(f"⚠️ Módulos core não disponíveis na nova estrutura: {e}")
    try:
        from src.core.memoria.gerenciador_memoria import GerenciadorMemoria
        from src.core.memoria.registrador_contexto import RegistradorContexto
        modules_status["core"] = True
        logger.info("✅ Módulos core carregados da estrutura antiga")
    except ImportError:
        logger.error("❌ Nenhuma estrutura core disponível")

# === IMPORTAÇÕES SERVICES ===
try:
    from autocura.services.diagnostico import DiagnosticoSistema, RealSuggestionsDetector
    modules_status["services"] = True
    logger.info("✅ Serviços carregados da nova estrutura")
except ImportError as e:
    logger.warning(f"⚠️ Serviços não disponíveis na nova estrutura: {e}")
    try:
        from src.services.diagnostico.diagnostico import DiagnosticoSistema
        from src.services.diagnostico.real_suggestions import RealSuggestionsDetector
        modules_status["services"] = True
        logger.info("✅ Serviços carregados da estrutura antiga")
    except ImportError:
        logger.error("❌ Nenhum serviço disponível")
        # Cria classes mock para evitar erros
        class DiagnosticoSistema:
            def __init__(self): pass
        class RealSuggestionsDetector:
            def __init__(self): pass
            def detect_real_problems(self): return []

# === IMPORTAÇÕES MONITORING ===
try:
    from autocura.monitoring.metrics.gerenciador_metricas import GerenciadorMetricas
    modules_status["monitoring"] = True
    logger.info("✅ Monitoramento carregado da nova estrutura")
except ImportError:
    try:
        from src.monitoring.metrics.gerenciador_metricas import GerenciadorMetricas
        modules_status["monitoring"] = True
        logger.info("✅ Monitoramento carregado da estrutura antiga")
    except ImportError:
        logger.warning("⚠️ Monitoramento não disponível")

# === APLICAÇÃO FASTAPI ===
app = FastAPI(
    title="Sistema AutoCura - Modular",
    description="Sistema de autocura cognitiva com nova estrutura modular",
    version="1.0.0-modular",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === ESTADO GLOBAL ===
class ModularSystemState:
    def __init__(self):
        self.start_time = datetime.now()
        self.modules_loaded = modules_status
        
        # Inicializa componentes disponíveis
        if modules_status["core"]:
            try:
                self.memory_manager = GerenciadorMemoria()
                self.context_recorder = RegistradorContexto()
                logger.info("✅ Componentes core inicializados")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar core: {e}")
        
        if modules_status["services"]:
            try:
                self.diagnostic_service = DiagnosticoSistema()
                self.suggestions_detector = RealSuggestionsDetector()
                logger.info("✅ Serviços inicializados")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar serviços: {e}")
        
        if modules_status["monitoring"]:
            try:
                self.metrics_manager = GerenciadorMetricas({"base_dir": "data/metricas"})
                logger.info("✅ Monitoramento inicializado")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar monitoramento: {e}")

system_state = ModularSystemState()

# === ENDPOINTS ===

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "name": "Sistema AutoCura - Modular",
        "version": "1.0.0-modular",
        "status": "operational",
        "structure": "new_modular",
        "start_time": system_state.start_time.isoformat(),
        "modules_loaded": system_state.modules_loaded,
        "message": "🚀 Nova estrutura modular funcionando!"
    }

@app.get("/api/health")
async def health_check():
    """Verificação de saúde do sistema"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - system_state.start_time).total_seconds(),
        "modules": system_state.modules_loaded,
        "structure_type": "modular",
        "components": {
            "memory_manager": hasattr(system_state, 'memory_manager'),
            "diagnostic_service": hasattr(system_state, 'diagnostic_service'),
            "metrics_manager": hasattr(system_state, 'metrics_manager')
        }
    }
    
    # Determina status geral
    total_modules = len(system_state.modules_loaded)
    loaded_modules = sum(1 for status in system_state.modules_loaded.values() if status)
    
    if loaded_modules == 0:
        health_status["status"] = "critical"
    elif loaded_modules < total_modules:
        health_status["status"] = "degraded"
    else:
        health_status["status"] = "healthy"
    
    return health_status

@app.get("/api/modules")
async def get_modules_info():
    """Informações detalhadas dos módulos"""
    return {
        "total_modules": len(system_state.modules_loaded),
        "loaded_modules": sum(1 for status in system_state.modules_loaded.values() if status),
        "modules_status": system_state.modules_loaded,
        "structure_info": {
            "type": "modular",
            "base_path": "autocura/",
            "fallback_enabled": True,
            "migration_completed": True
        }
    }

@app.get("/api/structure")
async def get_structure_info():
    """Informações sobre a estrutura modular"""
    structure_info = {
        "structure_type": "modular",
        "organization": {
            "core": {
                "path": "autocura/core/",
                "status": modules_status["core"],
                "components": ["memoria", "messaging", "interfaces", "self_modify"]
            },
            "services": {
                "path": "autocura/services/",
                "status": modules_status["services"],
                "components": ["ia", "diagnostico", "monitoramento", "etica", "guardiao"]
            },
            "monitoring": {
                "path": "autocura/monitoring/",
                "status": modules_status["monitoring"],
                "components": ["metrics", "observability", "integration"]
            },
            "security": {
                "path": "autocura/security/",
                "status": modules_status["security"],
                "components": ["criptografia", "deteccao"]
            }
        },
        "docker": {
            "new_dockerfile": "deployment/docker/Dockerfile.modular",
            "new_compose": "deployment/docker/docker-compose.modular.yml"
        },
        "migration": {
            "completed": True,
            "backup_location": "backup_reorganization/",
            "report_file": "reorganization_report.json"
        }
    }
    
    return structure_info

@app.get("/api/test/suggestions")
async def test_suggestions():
    """Testa sistema de sugestões se disponível"""
    if not modules_status["services"]:
        return {"error": "Serviços não carregados"}
    
    try:
        if hasattr(system_state, 'suggestions_detector'):
            suggestions = system_state.suggestions_detector.detect_real_problems()
            return {
                "test": "suggestions",
                "status": "success",
                "suggestions_count": len(suggestions),
                "suggestions": suggestions[:3]  # Primeiras 3 apenas
            }
        else:
            return {"error": "Detector de sugestões não disponível"}
    except Exception as e:
        return {"error": f"Erro no teste: {str(e)}"}

# === INICIALIZAÇÃO ===
@app.on_event("startup")
async def startup_event():
    """Inicialização do sistema"""
    logger.info("🚀 Iniciando Sistema AutoCura Modular...")
    
    if modules_status["core"] and hasattr(system_state, 'context_recorder'):
        system_state.context_recorder.registrar_evento(
            "sistema_modular_iniciado",
            f"Sistema modular iniciado - Módulos carregados: {sum(modules_status.values())}/{len(modules_status)}"
        )
    
    logger.info("✅ Sistema AutoCura Modular iniciado com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    """Finalização do sistema"""
    logger.info("🔄 Finalizando Sistema AutoCura Modular...")
    
    if modules_status["core"] and hasattr(system_state, 'context_recorder'):
        system_state.context_recorder.registrar_evento(
            "sistema_modular_finalizado",
            "Sistema modular finalizado"
        )
    
    logger.info("✅ Sistema AutoCura Modular finalizado")

def main():
    """Função principal"""
    print("🚀 Sistema AutoCura - Estrutura Modular")
    print("=" * 50)
    print(f"📊 Módulos carregados: {sum(modules_status.values())}/{len(modules_status)}")
    print(f"🏗️  Estrutura: {'Modular' if any(modules_status.values()) else 'Fallback'}")
    print("🌐 Acesso: http://localhost:8001")
    print("📚 Docs: http://localhost:8001/docs")
    print("=" * 50)
    
    # Executa o servidor
    uvicorn.run(
        "main_modular:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main() 