"""
EvolutionController - Controlador de Auto-Modificação
===================================================

Controlador principal que integra geração de código seguro e sandbox
com o sistema de evolução existente.
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import logging

from .safe_code_generator import SafeCodeGenerator, CodeAnalysis, RiskAssessment
from ..sandbox.evolution_sandbox import EvolutionSandbox, SandboxResult, SandboxStatus

logger = logging.getLogger(__name__)

class EvolutionType(Enum):
    """Tipos de evolução"""
    FUNCTION_GENERATION = "function_generation"
    MODULE_ENHANCEMENT = "module_enhancement"
    BUG_FIX = "bug_fix"
    OPTIMIZATION = "optimization"
    FEATURE_ADDITION = "feature_addition"

class ApprovalLevel(Enum):
    """Níveis de aprovação necessários"""
    AUTOMATIC = "automatic"
    REVIEW_REQUIRED = "review_required"
    HUMAN_APPROVAL = "human_approval"
    COMMITTEE_APPROVAL = "committee_approval"

@dataclass
class EvolutionRequest:
    """Solicitação de evolução"""
    evolution_type: EvolutionType
    description: str
    requirements: Dict
    priority: int = 1
    safety_level: str = "medium"
    context: str = ""
    requester: str = "system"
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class EvolutionResult:
    """Resultado de uma evolução"""
    request_id: str
    success: bool
    generated_code: Optional[str]
    code_analysis: Optional[CodeAnalysis]
    sandbox_result: Optional[SandboxResult]
    approval_level: ApprovalLevel
    applied: bool
    error_message: Optional[str]
    timestamp: str
    execution_time: float

class EvolutionController:
    """
    Controlador principal de auto-modificação controlada
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Inicializa o controlador de evolução
        
        Args:
            openai_api_key: Chave da API OpenAI
        """
        self.code_generator = SafeCodeGenerator(openai_api_key)
        self.sandbox = EvolutionSandbox()
        
        # Filas de evolução
        self.pending_evolutions = []
        self.completed_evolutions = []
        self.failed_evolutions = []
        
        # Configurações de aprovação
        self.approval_rules = {
            RiskAssessment.SAFE: ApprovalLevel.AUTOMATIC,
            RiskAssessment.CAUTION: ApprovalLevel.REVIEW_REQUIRED,
            RiskAssessment.DANGEROUS: ApprovalLevel.HUMAN_APPROVAL,
            RiskAssessment.BLOCKED: ApprovalLevel.COMMITTEE_APPROVAL
        }
        
        # Estatísticas
        self.stats = {
            "total_requests": 0,
            "successful_evolutions": 0,
            "failed_evolutions": 0,
            "automatic_approvals": 0,
            "manual_approvals": 0,
            "blocked_evolutions": 0
        }
        
        logger.info("EvolutionController inicializado")
    
    async def request_evolution(self, request: EvolutionRequest) -> str:
        """
        Solicita uma evolução do sistema
        
        Args:
            request: Solicitação de evolução
            
        Returns:
            str: ID da solicitação
        """
        request_id = f"evo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.pending_evolutions)}"
        
        logger.info(f"Nova solicitação de evolução: {request_id}")
        logger.info(f"Tipo: {request.evolution_type.value}")
        logger.info(f"Descrição: {request.description}")
        
        # Adiciona à fila
        self.pending_evolutions.append((request_id, request))
        self.stats["total_requests"] += 1
        
        # Processa em background
        asyncio.create_task(self._process_evolution(request_id, request))
        
        return request_id
    
    async def _process_evolution(self, request_id: str, request: EvolutionRequest):
        """Processa uma solicitação de evolução"""
        
        start_time = datetime.now()
        
        try:
            logger.info(f"Processando evolução {request_id}")
            
            # 1. Gera código
            generated_code, code_analysis = await self._generate_code(request)
            
            if not generated_code:
                raise Exception("Falha na geração de código")
            
            # 2. Testa em sandbox
            sandbox_result = await self._test_in_sandbox(generated_code, request)
            
            # 3. Determina nível de aprovação
            approval_level = self._determine_approval_level(code_analysis, sandbox_result)
            
            # 4. Aplica se aprovado automaticamente
            applied = False
            if approval_level == ApprovalLevel.AUTOMATIC and sandbox_result.status == SandboxStatus.COMPLETED:
                applied = await self._apply_evolution(generated_code, request)
            
            # 5. Registra resultado
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = EvolutionResult(
                request_id=request_id,
                success=True,
                generated_code=generated_code,
                code_analysis=code_analysis,
                sandbox_result=sandbox_result,
                approval_level=approval_level,
                applied=applied,
                error_message=None,
                timestamp=datetime.now().isoformat(),
                execution_time=execution_time
            )
            
            self.completed_evolutions.append(result)
            self.stats["successful_evolutions"] += 1
            
            if applied:
                self.stats["automatic_approvals"] += 1
                logger.info(f"Evolução {request_id} aplicada automaticamente")
            else:
                logger.info(f"Evolução {request_id} requer aprovação: {approval_level.value}")
            
        except Exception as e:
            logger.error(f"Erro ao processar evolução {request_id}: {e}")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = EvolutionResult(
                request_id=request_id,
                success=False,
                generated_code=None,
                code_analysis=None,
                sandbox_result=None,
                approval_level=ApprovalLevel.COMMITTEE_APPROVAL,
                applied=False,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
                execution_time=execution_time
            )
            
            self.failed_evolutions.append(result)
            self.stats["failed_evolutions"] += 1
        
        finally:
            # Remove da fila de pendentes
            self.pending_evolutions = [
                (id, req) for id, req in self.pending_evolutions 
                if id != request_id
            ]
    
    async def _generate_code(self, request: EvolutionRequest) -> Tuple[Optional[str], Optional[CodeAnalysis]]:
        """Gera código para a evolução"""
        
        try:
            # Converte request para formato do gerador
            requirements = {
                "function_name": request.requirements.get("function_name", "evolved_function"),
                "description": request.description,
                "inputs": request.requirements.get("inputs", []),
                "outputs": request.requirements.get("outputs", []),
                "logic_description": request.requirements.get("logic_description", request.description),
                "safety_level": request.safety_level,
                "context": f"Evolution Type: {request.evolution_type.value}\n{request.context}"
            }
            
            return await self.code_generator.generate_module(requirements)
            
        except Exception as e:
            logger.error(f"Erro na geração de código: {e}")
            return None, None
    
    async def _test_in_sandbox(self, code: str, request: EvolutionRequest) -> SandboxResult:
        """Testa código no sandbox"""
        
        try:
            test_data = request.requirements.get("test_data", {})
            return await self.sandbox.test_evolution(code, test_data)
            
        except Exception as e:
            logger.error(f"Erro no teste sandbox: {e}")
            return SandboxResult(
                status=SandboxStatus.FAILED,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=0,
                resource_usage={},
                test_results={},
                timestamp=datetime.now().isoformat(),
                error_message=str(e)
            )
    
    def _determine_approval_level(self, code_analysis: CodeAnalysis, 
                                sandbox_result: SandboxResult) -> ApprovalLevel:
        """Determina nível de aprovação necessário"""
        
        # Baseado na análise de código
        base_approval = self.approval_rules.get(
            code_analysis.risk_assessment, 
            ApprovalLevel.HUMAN_APPROVAL
        )
        
        # Aumenta nível se sandbox falhou
        if sandbox_result.status != SandboxStatus.COMPLETED:
            if base_approval == ApprovalLevel.AUTOMATIC:
                base_approval = ApprovalLevel.REVIEW_REQUIRED
            elif base_approval == ApprovalLevel.REVIEW_REQUIRED:
                base_approval = ApprovalLevel.HUMAN_APPROVAL
        
        # Considera conformidade ética
        if not code_analysis.ethical_compliance:
            base_approval = ApprovalLevel.HUMAN_APPROVAL
        
        return base_approval
    
    async def _apply_evolution(self, code: str, request: EvolutionRequest) -> bool:
        """Aplica evolução ao sistema"""
        
        try:
            # Por enquanto, apenas simula aplicação
            # Em implementação real, integraria com sistema de módulos
            
            logger.info(f"Aplicando evolução: {request.evolution_type.value}")
            logger.info(f"Código gerado ({len(code)} caracteres)")
            
            # TODO: Implementar aplicação real baseada no tipo de evolução
            if request.evolution_type == EvolutionType.FUNCTION_GENERATION:
                return await self._apply_function_generation(code, request)
            elif request.evolution_type == EvolutionType.MODULE_ENHANCEMENT:
                return await self._apply_module_enhancement(code, request)
            elif request.evolution_type == EvolutionType.BUG_FIX:
                return await self._apply_bug_fix(code, request)
            else:
                logger.warning(f"Tipo de evolução não implementado: {request.evolution_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao aplicar evolução: {e}")
            return False
    
    async def _apply_function_generation(self, code: str, request: EvolutionRequest) -> bool:
        """Aplica geração de nova função"""
        # Implementação futura: adicionar função ao módulo apropriado
        logger.info("Simulando aplicação de nova função")
        return True
    
    async def _apply_module_enhancement(self, code: str, request: EvolutionRequest) -> bool:
        """Aplica melhoria em módulo existente"""
        # Implementação futura: modificar módulo existente
        logger.info("Simulando melhoria de módulo")
        return True
    
    async def _apply_bug_fix(self, code: str, request: EvolutionRequest) -> bool:
        """Aplica correção de bug"""
        # Implementação futura: aplicar correção
        logger.info("Simulando correção de bug")
        return True
    
    async def approve_evolution(self, request_id: str, approved: bool, 
                              approver: str = "human") -> bool:
        """
        Aprova ou rejeita uma evolução pendente
        
        Args:
            request_id: ID da solicitação
            approved: Se foi aprovada
            approver: Quem aprovou
            
        Returns:
            bool: Sucesso da operação
        """
        try:
            # Encontra evolução nos resultados
            evolution = None
            for evo in self.completed_evolutions:
                if evo.request_id == request_id and not evo.applied:
                    evolution = evo
                    break
            
            if not evolution:
                logger.warning(f"Evolução {request_id} não encontrada ou já aplicada")
                return False
            
            if approved:
                # Aplica evolução
                request = next((req for id, req in self.pending_evolutions if id == request_id), None)
                if request and evolution.generated_code:
                    applied = await self._apply_evolution(evolution.generated_code, request)
                    evolution.applied = applied
                    
                    if applied:
                        self.stats["manual_approvals"] += 1
                        logger.info(f"Evolução {request_id} aprovada e aplicada por {approver}")
                    else:
                        logger.error(f"Falha ao aplicar evolução {request_id}")
                        return False
                else:
                    logger.error(f"Dados da evolução {request_id} não encontrados")
                    return False
            else:
                # Rejeita evolução
                self.stats["blocked_evolutions"] += 1
                logger.info(f"Evolução {request_id} rejeitada por {approver}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao aprovar evolução {request_id}: {e}")
            return False
    
    def get_pending_approvals(self) -> List[Dict]:
        """Retorna evoluções pendentes de aprovação"""
        
        pending = []
        for evolution in self.completed_evolutions:
            if not evolution.applied and evolution.approval_level != ApprovalLevel.AUTOMATIC:
                pending.append({
                    "request_id": evolution.request_id,
                    "approval_level": evolution.approval_level.value,
                    "risk_assessment": evolution.code_analysis.risk_assessment.value if evolution.code_analysis else "unknown",
                    "timestamp": evolution.timestamp,
                    "description": "Evolução pendente de aprovação"
                })
        
        return pending
    
    def get_evolution_stats(self) -> Dict:
        """Retorna estatísticas de evolução"""
        
        return {
            **self.stats,
            "pending_evolutions": len(self.pending_evolutions),
            "pending_approvals": len(self.get_pending_approvals()),
            "code_generator_stats": self.code_generator.get_generation_stats(),
            "sandbox_stats": self.sandbox.get_sandbox_stats()
        }
    
    def get_evolution_history(self, limit: int = 50) -> List[Dict]:
        """Retorna histórico de evoluções"""
        
        all_evolutions = self.completed_evolutions + self.failed_evolutions
        all_evolutions.sort(key=lambda x: x.timestamp, reverse=True)
        
        history = []
        for evolution in all_evolutions[:limit]:
            history.append({
                "request_id": evolution.request_id,
                "success": evolution.success,
                "applied": evolution.applied,
                "approval_level": evolution.approval_level.value,
                "execution_time": evolution.execution_time,
                "timestamp": evolution.timestamp,
                "error_message": evolution.error_message
            })
        
        return history
    
    async def validate_system_code(self, module_path: str) -> CodeAnalysis:
        """Valida código existente do sistema"""
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return await self.code_generator.validate_existing_code(
                code, 
                f"Validação do módulo: {module_path}"
            )
            
        except Exception as e:
            logger.error(f"Erro ao validar código {module_path}: {e}")
            raise
    
    def cleanup(self):
        """Limpeza de recursos"""
        self.sandbox.cleanup_all()
        logger.info("EvolutionController finalizado") 