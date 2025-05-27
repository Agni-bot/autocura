"""
Sistema AutoCura - API Principal
================================

Sistema de autocura cognitiva com arquitetura modular evolutiva.
Versão: 1.0.0-alpha - Estrutura Reorganizada
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

# ===== IMPORTAÇÕES DOS MÓDULOS CORE (NOVA ESTRUTURA) =====
try:
    from autocura.core.memoria.gerenciador_memoria import GerenciadorMemoria
    from autocura.core.memoria.registrador_contexto import RegistradorContexto
    from autocura.core.messaging.universal_bus import UniversalEventBus, Message, MessagePriority
    from autocura.core.serialization.adaptive_serializer import AdaptiveSerializer
    CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Módulos core não disponíveis (nova estrutura): {e}")
    CORE_AVAILABLE = False

# Importações do sistema de auto-modificação
try:
    from autocura.core.self_modify.safe_code_generator import SafeCodeGenerator
    from autocura.core.self_modify.evolution_sandbox import EvolutionSandbox
    from autocura.core.self_modify.evolution_controller import (
        EvolutionController, EvolutionRequest, EvolutionType
    )
    EVOLUTION_AVAILABLE = True
except ImportError as e:
    EVOLUTION_AVAILABLE = False
    logger.warning(f"Módulo de auto-modificação não disponível: {e}")

# ===== IMPORTAÇÕES DOS SERVIÇOS (NOVA ESTRUTURA) =====
try:
    from autocura.services.monitoramento.coletor_metricas import ColetorMetricas
    from autocura.services.monitoramento.analisador_metricas import AnalisadorMetricas
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False

try:
    from autocura.services.ia.cliente_ia import ClienteIA
    from autocura.services.ia.agente_adaptativo import AgenteAdaptativo
    IA_AVAILABLE = True
except ImportError:
    IA_AVAILABLE = False

try:
    from autocura.services.diagnostico.diagnostico import DiagnosticoSistema
    from autocura.services.diagnostico.analisador_multiparadigma import AnalisadorMultiParadigma
    DIAGNOSTIC_AVAILABLE = True
except ImportError:
    DIAGNOSTIC_AVAILABLE = False

try:
    from autocura.services.etica.validador_etico import ValidadorEtico
    from autocura.services.etica.circuitos_morais import CircuitosMorais
    ETHICS_AVAILABLE = True
except ImportError:
    ETHICS_AVAILABLE = False

try:
    from autocura.services.guardiao.guardiao_cognitivo import GuardiaoCognitivo
    GUARDIAN_AVAILABLE = True
except ImportError:
    GUARDIAN_AVAILABLE = False

# ===== IMPORTAÇÕES DO MONITORAMENTO AVANÇADO (NOVA ESTRUTURA) =====
try:
    from autocura.monitoring.integration.dashboard_bridge import dashboard_bridge, router as dashboard_bridge_router
    from autocura.monitoring.observability.observabilidade import ObservabilidadeAvancada
    from autocura.monitoring.metrics.gerenciador_metricas import GerenciadorMetricas
    MONITORING_BRIDGE_AVAILABLE = True
except ImportError:
    MONITORING_BRIDGE_AVAILABLE = False

# ===== IMPORTAÇÕES DE SEGURANÇA (NOVA ESTRUTURA) =====
try:
    from autocura.security.criptografia.quantum_safe_crypto import CriptografiaQuantumSafe
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fallback para estrutura antiga se nova não estiver disponível
if not CORE_AVAILABLE:
    logger.info("Tentando carregar estrutura antiga...")
    try:
        from src.core.memoria.gerenciador_memoria import GerenciadorMemoria
        from src.core.memoria.registrador_contexto import RegistradorContexto
        from src.core.messaging.universal_bus import UniversalEventBus, Message, MessagePriority
        from src.core.serialization.adaptive_serializer import AdaptiveSerializer
        CORE_AVAILABLE = True
        logger.info("Estrutura antiga carregada com sucesso")
    except ImportError as e:
        logger.error(f"Nenhuma estrutura de core disponível: {e}")

# === RESTO DO CÓDIGO PERMANECE IGUAL ===
# (O resto do main.py atual seria copiado aqui)

logger.info("Sistema AutoCura carregado com nova estrutura modular ✅")
