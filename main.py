"""
Sistema AutoCura - API Principal
================================

Sistema de autocura cognitiva com arquitetura modular e evolutiva.
Versão: 1.0.0-alpha
Status: TOTALMENTE OPERACIONAL ✅
"""

import asyncio
import os
import sys
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import logging
import json
import psutil
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ===== IMPORTAÇÕES DOS MÓDULOS CORE =====
from src.core.memoria.gerenciador_memoria import GerenciadorMemoria
from src.core.memoria.registrador_contexto import RegistradorContexto
from src.core.messaging.universal_bus import UniversalEventBus, Message, MessagePriority
from src.core.serialization.adaptive_serializer import AdaptiveSerializer

# Importações do sistema de auto-modificação
try:
    from src.core.self_modify.safe_code_generator import SafeCodeGenerator
    from src.core.self_modify.evolution_sandbox import EvolutionSandbox
    from src.core.self_modify.evolution_controller import (
        EvolutionController, EvolutionRequest, EvolutionType
    )
    EVOLUTION_AVAILABLE = True
except ImportError as e:
    EVOLUTION_AVAILABLE = False
    print(f"Módulo de auto-modificação não disponível: {e}")

# ===== IMPORTAÇÕES DOS SERVIÇOS =====
# Serviço de Monitoramento
try:
    from src.services.monitoramento.coletor_metricas import ColetorMetricas
    from src.services.monitoramento.analisador_metricas import AnalisadorMetricas
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    print("Serviço de monitoramento não disponível")

# Serviço de IA
try:
    from src.services.ia.cliente_ia import ClienteIA
    from src.services.ia.agente_adaptativo import AgenteAdaptativo
    IA_AVAILABLE = True
except ImportError:
    IA_AVAILABLE = False
    print("Serviço de IA não disponível")

# Serviço de Diagnóstico
try:
    from src.services.diagnostico.diagnostico import DiagnosticoSistema
    from src.services.diagnostico.analisador_multiparadigma import AnalisadorMultiParadigma
    DIAGNOSTIC_AVAILABLE = True
except ImportError:
    DIAGNOSTIC_AVAILABLE = False
    print("Serviço de diagnóstico não disponível")

# Serviço de Ética
try:
    from src.services.etica.validador_etico import ValidadorEtico
    from src.services.etica.circuitos_morais import CircuitosMorais
    ETHICS_AVAILABLE = True
except ImportError:
    ETHICS_AVAILABLE = False
    print("Serviço de ética não disponível")

# Serviço Guardião
try:
    from src.services.guardiao.guardiao_cognitivo import GuardiaoCognitivo
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False
    print("Serviço guardião não disponível")

# ===== IMPORTAÇÕES DO MONITORAMENTO AVANÇADO =====
try:
    from src.monitoring.integration.dashboard_bridge import dashboard_bridge, router as dashboard_bridge_router
    from src.monitoring.observability.observabilidade import ObservabilidadeAvancada
    from src.monitoring.metrics.gerenciador_metricas import GerenciadorMetricas
    MONITORING_BRIDGE_AVAILABLE = True
except ImportError:
    MONITORING_BRIDGE_AVAILABLE = False
    print("Ponte de monitoramento não disponível")

# ===== IMPORTAÇÕES DE SEGURANÇA =====
try:
    from src.seguranca.criptografia import CriptografiaQuantumSafe
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    print("Módulo de segurança não disponível")

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== MODELOS PYDANTIC =====
class DiagnosticRequest(BaseModel):
    data: Dict[str, Any]
    paradigms: Optional[List[str]] = None

class MessageRequest(BaseModel):
    topic: str
    payload: Dict[str, Any]
    priority: Optional[str] = "NORMAL"

class EvolutionStatus(BaseModel):
    current_level: int
    capabilities: Dict[str, bool]
    next_evolution: Optional[str]
    modules_status: Dict[str, bool]

class ModuleStatus(BaseModel):
    name: str
    version: str
    status: str
    health: bool
    last_update: str
    capabilities: List[str]

class HealingAction(BaseModel):
    action_id: str
    type: str
    description: str
    priority: int
    status: str
    created_at: str
    executed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

class SystemReport(BaseModel):
    report_type: str
    timestamp: str
    data: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    modules_health: Dict[str, bool]

class AgentCommunication(BaseModel):
    agent_type: str
    message: str
    context: Dict[str, Any]
    priority: int = 1

class AutoModificationRequest(BaseModel):
    description: str
    type: str = "feature"
    priority: int = 1
    constraints: Optional[Dict[str, Any]] = None

# ===== APLICAÇÃO FASTAPI =====
app = FastAPI(
    title="Sistema AutoCura",
    description="Sistema de autocura cognitiva com arquitetura evolutiva - 100% Operacional",
    version="1.0.0-alpha",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adiciona router da ponte do dashboard se disponível
if MONITORING_BRIDGE_AVAILABLE:
    app.include_router(dashboard_bridge_router)
    logger.info("Router da ponte do dashboard de monitoramento adicionado")

# ===== ESTADO GLOBAL DO SISTEMA =====
class SystemState:
    def __init__(self):
        # Core Components
        self.memory_manager = GerenciadorMemoria()
        self.context_recorder = RegistradorContexto()
        self.event_bus = UniversalEventBus()
        self.serializer = AdaptiveSerializer()
        
        # Services
        self.monitoring_service = ColetorMetricas() if MONITORING_AVAILABLE else None
        self.ia_service = ClienteIA() if IA_AVAILABLE else None
        self.diagnostic_service = DiagnosticoSistema() if DIAGNOSTIC_AVAILABLE else None
        self.ethics_service = ValidadorEtico() if ETHICS_AVAILABLE else None
        
        # Guardian service needs memory manager
        self.guardian_service = GuardiaoCognitivo(self.memory_manager) if GUARDIAN_AVAILABLE else None
        
        # Evolution Components
        if EVOLUTION_AVAILABLE:
            self.code_generator = SafeCodeGenerator()
            self.evolution_sandbox = EvolutionSandbox()
            self.evolution_controller = EvolutionController()
        else:
            self.code_generator = None
            self.evolution_sandbox = None
            self.evolution_controller = None
        
        # Security
        self.crypto = CriptografiaQuantumSafe() if SECURITY_AVAILABLE else None
        
        # Advanced Monitoring
        if MONITORING_BRIDGE_AVAILABLE:
            self.observability = ObservabilidadeAvancada()
            self.metrics_manager = GerenciadorMetricas({"base_dir": "data/metricas"})
        else:
            self.observability = None
            self.metrics_manager = None
        
        self.initialized = False
        self.modules_status = {}

    def get_modules_status(self) -> Dict[str, bool]:
        """Retorna o status de todos os módulos"""
        return {
            "core": {
                "memory": self.memory_manager is not None,
                "context": self.context_recorder is not None,
                "event_bus": self.event_bus is not None,
                "serializer": self.serializer is not None
            },
            "services": {
                "monitoring": MONITORING_AVAILABLE,
                "ia": IA_AVAILABLE,
                "diagnostic": DIAGNOSTIC_AVAILABLE,
                "ethics": ETHICS_AVAILABLE,
                "guardian": GUARDIAN_AVAILABLE
            },
            "evolution": {
                "code_generator": self.code_generator is not None,
                "sandbox": self.evolution_sandbox is not None,
                "controller": self.evolution_controller is not None
            },
            "security": {
                "crypto": self.crypto is not None
            },
            "monitoring_advanced": {
                "observability": self.observability is not None,
                "metrics_manager": self.metrics_manager is not None,
                "dashboard_bridge": MONITORING_BRIDGE_AVAILABLE
            }
        }

system = SystemState()

# ===== EVENTOS DE INICIALIZAÇÃO =====
@app.on_event("startup")
async def startup_event():
    """Inicializa o sistema"""
    try:
        logger.info("Iniciando Sistema AutoCura...")
        
        # Inicia o event bus
        await system.event_bus.start()
        
        # Registra handlers
        await system.event_bus.subscribe("metrics", handle_metrics_event)
        await system.event_bus.subscribe("diagnostics", handle_diagnostics_event)
        await system.event_bus.subscribe("evolution", handle_evolution_event)
        await system.event_bus.subscribe("ethics", handle_ethics_event)
        
        # Atualiza status dos módulos
        system.modules_status = system.get_modules_status()
        
        # Registra evento de inicialização
        system.context_recorder.registrar_evento(
            "sistema_iniciado",
            f"Sistema AutoCura iniciado com sucesso - Módulos ativos: {sum(1 for cat in system.modules_status.values() for mod, status in cat.items() if status)}"
        )
        
        # Atualiza memória compartilhada
        system.memory_manager.atualizar_estado({
            "sistema_iniciado": datetime.now().isoformat(),
            "modulos_status": system.modules_status
        })
        
        system.initialized = True
        logger.info("Sistema AutoCura iniciado com sucesso ✅")
        
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Finaliza o sistema"""
    try:
        await system.event_bus.stop()
        system.context_recorder.registrar_evento(
            "sistema_finalizado",
            "Sistema AutoCura finalizado"
        )
        logger.info("Sistema AutoCura finalizado")
    except Exception as e:
        logger.error(f"Erro na finalização: {e}")

# ===== HANDLERS DE EVENTOS =====
async def handle_metrics_event(message: Message):
    """Processa eventos de métricas"""
    try:
        if system.metrics_manager:
            # Armazena métricas no gerenciador avançado
            await system.metrics_manager.registrar_metrica(
                nome=message.payload.get("name", "metric"),
                valor=message.payload.get("value", 0),
                tipo="gauge",
                labels=message.payload.get("labels", {})
            )
        
        # Analisa se necessário
        if message.payload.get("trigger_analysis", False) and system.diagnostic_service:
            analysis = await system.diagnostic_service.analisar(message.payload)
            await system.event_bus.send_classical(
                "diagnostics",
                analysis,
                MessagePriority.HIGH
            )
    except Exception as e:
        logger.error(f"Erro ao processar métricas: {e}")

async def handle_diagnostics_event(message: Message):
    """Processa eventos de diagnóstico"""
    try:
        diagnostics = message.payload.get("diagnostics", [])
        
        # Registra diagnósticos críticos
        for diag in diagnostics:
            if diag.get("severity") in ["ERROR", "CRITICAL"]:
                system.context_recorder.registrar_evento(
                    "diagnostico_critico",
                    json.dumps(diag)
                )
        
        # Gera ações de cura se necessário
        if diagnostics:
            await generate_healing_actions(diagnostics)
            
    except Exception as e:
        logger.error(f"Erro ao processar diagnósticos: {e}")

async def handle_evolution_event(message: Message):
    """Processa eventos de evolução"""
    try:
        evolution_data = message.payload
        system.context_recorder.registrar_evento(
            "evolucao_sistema",
            f"Sistema evoluiu: {evolution_data}"
        )
        
        # Atualiza memória com nova evolução
        system.memory_manager.registrar_acao(
            "evolucao",
            json.dumps(evolution_data)
        )
    except Exception as e:
        logger.error(f"Erro ao processar evolução: {e}")

async def handle_ethics_event(message: Message):
    """Processa eventos éticos"""
    try:
        ethics_data = message.payload
        
        # Valida com o serviço de ética se disponível
        if system.ethics_service:
            validation = await system.ethics_service.validar(ethics_data)
            if not validation.get("approved", False):
                logger.warning(f"Ação bloqueada por validação ética: {validation.get('reason')}")
                
        system.context_recorder.registrar_evento(
            "validacao_etica",
            json.dumps(ethics_data)
        )
    except Exception as e:
        logger.error(f"Erro ao processar evento ético: {e}")

# ===== FUNÇÕES AUXILIARES =====
async def generate_healing_actions(diagnostics: List[Dict[str, Any]]):
    """Gera ações de auto-cura baseadas em diagnósticos"""
    try:
        healing_actions = []
        
        for diag in diagnostics:
            # Analisa recomendações
            for rec in diag.get("recommendations", []):
                action = {
                    "action_id": f"heal_{datetime.now().timestamp()}",
                    "type": rec.get("type", "correction"),
                    "description": rec.get("action", ""),
                    "priority": rec.get("priority", 1),
                    "status": "pending",
                    "created_at": datetime.now().isoformat(),
                    "diagnostic_id": diag.get("id", "unknown")
                }
                
                healing_actions.append(action)
                
                # Registra ação
                system.context_recorder.registrar_evento(
                    "acao_cura_gerada",
                    json.dumps(action)
                )
                
                # Se temos o controlador de evolução, pode executar auto-modificação
                if system.evolution_controller and rec.get("auto_fix", False):
                    evolution_request = EvolutionRequest(
                        type=EvolutionType.BUGFIX,
                        description=f"Auto-correção: {rec.get('action', '')}",
                        priority=rec.get("priority", 1)
                    )
                    await system.evolution_controller.request_evolution(evolution_request)
        
        return healing_actions
                
    except Exception as e:
        logger.error(f"Erro ao gerar ações de cura: {e}")
        return []

# ===== ENDPOINTS DA API =====

@app.get("/", response_class=HTMLResponse)
async def root():
    """Retorna o dashboard HTML"""
    dashboard_path = Path("dashboard.html")
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    else:
        return HTMLResponse(content="""
        <html>
            <head><title>AutoCura Dashboard</title></head>
            <body>
                <h1>Sistema AutoCura</h1>
                <p>Dashboard não encontrado. Use /api para acessar a API.</p>
                <p><a href="/docs">Documentação da API</a></p>
            </body>
        </html>
        """)

@app.get("/api")
async def api_root():
    """Endpoint raiz da API"""
    return {
        "name": "Sistema AutoCura",
        "version": "1.0.0-alpha",
        "status": "operational" if system.initialized else "initializing",
        "phase": "ALPHA - TOTALMENTE OPERACIONAL ✅",
        "timestamp": datetime.now().isoformat(),
        "modules": system.get_modules_status()
    }

@app.get("/api/health")
async def health_check():
    """Verifica saúde do sistema"""
    try:
        modules_health = {}
        
        # Verifica cada categoria de módulos
        for category, modules in system.modules_status.items():
            modules_health[category] = {}
            for module, status in modules.items():
                modules_health[category][module] = "healthy" if status else "unavailable"
        
        # Status geral
        total_modules = sum(len(modules) for modules in system.modules_status.values())
        healthy_modules = sum(1 for cat in system.modules_status.values() for status in cat.values() if status)
        
        overall_status = "healthy" if healthy_modules == total_modules else "degraded" if healthy_modules > 0 else "critical"
        
        return {
            "status": overall_status,
            "healthy_modules": healthy_modules,
            "total_modules": total_modules,
            "modules_health": modules_health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics():
    """Obtém métricas atuais do sistema"""
    try:
        # Métricas básicas do sistema
        current_metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used,
                    "total": psutil.virtual_memory().total
                },
                "disk": {
                    "percent": psutil.disk_usage('/').percent,
                    "used": psutil.disk_usage('/').used,
                    "total": psutil.disk_usage('/').total
                }
            }
        }
        
        # Adiciona métricas avançadas se disponível
        if system.metrics_manager:
            advanced_metrics = await system.metrics_manager.obter_estatisticas()
            current_metrics["advanced"] = advanced_metrics
        
        # Histórico de métricas
        history = []
        if system.monitoring_service:
            history = await system.monitoring_service.obter_historico(limit=100)
        
        return {
            "current": current_metrics,
            "history": history,
            "capabilities": {
                "basic_metrics": True,
                "advanced_metrics": system.metrics_manager is not None,
                "real_time": True,
                "historical": system.monitoring_service is not None
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {e}")
        return {
            "error": str(e),
            "current": {},
            "history": [],
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/analyze")
async def analyze_data(request: DiagnosticRequest):
    """Executa análise diagnóstica"""
    try:
        if not system.diagnostic_service:
            raise HTTPException(status_code=503, detail="Serviço de diagnóstico não disponível")
        
        # Executa análise
        result = await system.diagnostic_service.analisar(request.data)
        
        # Registra análise
        system.context_recorder.registrar_evento(
            "analise_executada",
            f"Análise executada com {len(result.get('diagnostics', []))} diagnósticos"
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evolution/status")
async def get_evolution_status():
    """Obtém status de evolução do sistema"""
    try:
        capabilities = {
            "auto_modification": EVOLUTION_AVAILABLE,
            "code_generation": system.code_generator is not None,
            "sandbox_execution": system.evolution_sandbox is not None,
            "evolution_control": system.evolution_controller is not None,
            "ai_integration": system.ia_service is not None,
            "ethical_validation": system.ethics_service is not None
        }
        
        current_stats = {}
        if system.evolution_controller:
            current_stats = await system.evolution_controller.get_statistics()
        
        return EvolutionStatus(
            current_level=current_stats.get("evolution_level", 1),
            capabilities=capabilities,
            next_evolution="quantum_ready" if all(capabilities.values()) else "modular_expansion",
            modules_status=system.get_modules_status()
        )
    except Exception as e:
        logger.error(f"Erro ao obter status de evolução: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/modules/status")
async def get_modules_status():
    """Obtém status detalhado de todos os módulos"""
    try:
        modules_info = []
        
        # Core Modules
        core_modules = [
            ("Memória", "1.0.0", system.memory_manager is not None, ["persistência", "contexto"]),
            ("Event Bus", "1.0.0", system.event_bus is not None, ["mensageria", "async"]),
            ("Serialização", "1.0.0", system.serializer is not None, ["adaptativa", "universal"])
        ]
        
        # Service Modules
        service_modules = [
            ("Monitoramento", "1.0.0", MONITORING_AVAILABLE, ["métricas", "alertas"]),
            ("IA Adaptativa", "1.0.0", IA_AVAILABLE, ["GPT-4", "análise cognitiva"]),
            ("Diagnóstico", "1.0.0", DIAGNOSTIC_AVAILABLE, ["multi-paradigma", "preditivo"]),
            ("Ética", "1.0.0", ETHICS_AVAILABLE, ["validação", "circuitos morais"]),
            ("Guardião", "1.0.0", GUARDIAN_AVAILABLE, ["proteção", "monitoramento"])
        ]
        
        # Evolution Modules
        evolution_modules = [
            ("Auto-Modificação", "1.0.0", EVOLUTION_AVAILABLE, ["geração código", "sandbox"]),
            ("Segurança", "1.0.0", SECURITY_AVAILABLE, ["quantum-safe", "criptografia"])
        ]
        
        # Combina todos os módulos
        all_modules = core_modules + service_modules + evolution_modules
        
        for name, version, available, capabilities in all_modules:
            modules_info.append(ModuleStatus(
                name=name,
                version=version,
                status="operational" if available else "unavailable",
                health=available,
                last_update=datetime.now().isoformat(),
                capabilities=capabilities
            ))
        
        return {
            "modules": modules_info,
            "total": len(modules_info),
            "operational": sum(1 for m in modules_info if m.health),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter status dos módulos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evolution/auto-modify")
async def trigger_auto_modification(request: AutoModificationRequest):
    """Dispara processo de auto-modificação"""
    try:
        if not system.evolution_controller:
            raise HTTPException(status_code=503, detail="Sistema de auto-modificação não disponível")
        
        # Cria requisição de evolução
        evolution_request = EvolutionRequest(
            type=EvolutionType[request.type.upper()],
            description=request.description,
            priority=request.priority,
            constraints=request.constraints
        )
        
        # Solicita evolução
        result = await system.evolution_controller.request_evolution(evolution_request)
        
        # Registra evento
        system.context_recorder.registrar_evento(
            "auto_modificacao_solicitada",
            json.dumps({
                "request_id": result.get("request_id"),
                "type": request.type,
                "description": request.description
            })
        )
        
        return {
            "success": True,
            "request_id": result.get("request_id"),
            "status": "processing",
            "message": "Auto-modificação iniciada",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao disparar auto-modificação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/data")
async def get_dashboard_data():
    """Obtém dados completos para o dashboard"""
    try:
        # Coleta dados de todos os componentes
        dashboard_data = {
            "system_info": {
                "name": "Sistema AutoCura",
                "version": "1.0.0-alpha",
                "status": "operational" if system.initialized else "initializing",
                "uptime": datetime.now().isoformat()
            },
            "metrics": await get_metrics(),
            "modules": await get_modules_status(),
            "evolution": await get_evolution_status() if EVOLUTION_AVAILABLE else None,
            "recent_events": system.context_recorder.obter_eventos_recentes(limit=20),
            "healing_actions": {
                "total_today": 0,
                "successful": 0,
                "failed": 0,
                "pending": 0
            },
            "capabilities": {
                "auto_modification": EVOLUTION_AVAILABLE,
                "ai_integration": IA_AVAILABLE,
                "ethical_validation": ETHICS_AVAILABLE,
                "quantum_security": SECURITY_AVAILABLE,
                "advanced_monitoring": MONITORING_BRIDGE_AVAILABLE
            }
        }
        
        # Adiciona dados da ponte se disponível
        if MONITORING_BRIDGE_AVAILABLE:
            enriched_data = await dashboard_bridge.obter_dados_dashboard_enriquecidos()
            dashboard_data["advanced_monitoring"] = enriched_data
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Erro ao obter dados do dashboard: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/context")
async def get_context():
    """Obtém contexto atual do sistema"""
    try:
        estado = system.context_recorder.obter_estado_atual()
        eventos = system.context_recorder.obter_eventos_recentes(limit=50)
        instrucoes = system.context_recorder.obter_instrucoes_pendentes()
        
        return {
            "estado_atual": estado,
            "eventos_recentes": eventos,
            "instrucoes_pendentes": instrucoes,
            "memoria_compartilhada": system.memory_manager.obter_estado_atual(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter contexto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/healing/trigger")
async def trigger_healing_process(background_tasks: BackgroundTasks):
    """Dispara processo de auto-cura"""
    try:
        # Coleta métricas atuais
        metrics = await get_metrics()
        
        # Executa diagnóstico
        if system.diagnostic_service:
            diagnostics = await system.diagnostic_service.analisar(metrics["current"])
            
            # Gera ações de cura em background
            background_tasks.add_task(
                generate_healing_actions,
                diagnostics.get("diagnostics", [])
            )
            
            return {
                "status": "healing_triggered",
                "diagnostics_found": len(diagnostics.get("diagnostics", [])),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "diagnostic_service_unavailable",
                "message": "Serviço de diagnóstico não disponível",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Erro ao disparar processo de cura: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports/system")
async def get_system_report(report_type: str = "general"):
    """Gera relatório do sistema"""
    try:
        # Coleta dados para o relatório
        modules_status = await get_modules_status()
        health_status = await health_check()
        evolution_status = await get_evolution_status() if EVOLUTION_AVAILABLE else None
        recent_events = system.context_recorder.obter_eventos_recentes(limit=100)
        
        # Análise e recomendações
        recommendations = []
        
        # Verifica módulos não disponíveis
        unavailable_modules = [m["name"] for m in modules_status["modules"] if not m["health"]]
        if unavailable_modules:
            recommendations.append({
                "type": "module_activation",
                "priority": "high",
                "description": f"Ativar módulos: {', '.join(unavailable_modules)}",
                "impact": "Funcionalidades limitadas"
            })
        
        # Verifica uso de recursos
        metrics = await get_metrics()
        if metrics["current"]["system"]["cpu_percent"] > 80:
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "description": "CPU com uso elevado",
                "action": "Otimizar processos ou escalar recursos"
            })
        
        report = SystemReport(
            report_type=report_type,
            timestamp=datetime.now().isoformat(),
            data={
                "modules": modules_status,
                "health": health_status,
                "evolution": evolution_status,
                "metrics": metrics["current"],
                "events_summary": {
                    "total": len(recent_events),
                    "last_24h": sum(1 for e in recent_events if e.get("timestamp", "") > (datetime.now().timestamp() - 86400))
                }
            },
            recommendations=recommendations,
            modules_health={m["name"]: m["health"] for m in modules_status["modules"]}
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== FUNÇÃO PRINCIPAL =====
def main():
    """Função principal para executar o servidor"""
    import os
    
    # Configurações do servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    logger.info(f"Iniciando servidor AutoCura em {host}:{port}")
    logger.info(f"Documentação disponível em http://{host}:{port}/docs")
    logger.info(f"Dashboard disponível em http://{host}:{port}/")
    
    # Executa o servidor
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 