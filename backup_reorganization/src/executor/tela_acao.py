"""
Módulo de Interface de Ação Necessária

Este módulo implementa a tela que exibe ações antes da execução,
permitindo aprovação manual quando necessário.
"""

import logging
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TelaAcao")

@dataclass
class AcaoNecessaria:
    """Representa uma ação que precisa ser executada"""
    id: str
    tipo: str
    descricao: str
    impacto: str
    risco: float
    manual_ref: str
    timestamp: float
    aprovacao_necessaria: bool

class TelaAcaoNecessaria:
    """
    Interface para exibir ações antes da execução.
    
    Esta classe implementa a tela que mostra:
    1. O que será feito
    2. Por que é necessário
    3. Impacto esperado
    4. Referência ao manual
    """
    
    def __init__(self):
        """Inicializa a interface"""
        self.acoes_pendentes = {}
        
    def exibir_acao(self, acao: Dict[str, Any]) -> Optional[AcaoNecessaria]:
        """
        Exibe uma ação e aguarda aprovação se necessário.
        
        Args:
            acao: Ação a ser exibida
            
        Returns:
            AcaoNecessaria: Ação formatada para exibição
        """
        try:
            # Formata a ação para exibição
            acao_formatada = self._formatar_acao(acao)
            
            # Exibe a ação
            self._mostrar_acao(acao_formatada)
            
            # Registra a ação
            self.acoes_pendentes[acao_formatada.id] = acao_formatada
            
            return acao_formatada
            
        except Exception as e:
            logger.error(f"Erro ao exibir ação: {e}")
            return None
    
    def _formatar_acao(self, acao: Dict[str, Any]) -> AcaoNecessaria:
        """
        Formata uma ação para exibição.
        
        Args:
            acao: Ação a ser formatada
            
        Returns:
            AcaoNecessaria: Ação formatada
        """
        return AcaoNecessaria(
            id=acao.get("id", f"acao_{datetime.now().timestamp()}"),
            tipo=acao.get("tipo", "DESCONHECIDO"),
            descricao=self._gerar_descricao(acao),
            impacto=self._avaliar_impacto(acao),
            risco=float(acao.get("risco", 1.0)),
            manual_ref=self._obter_referencia_manual(acao),
            timestamp=datetime.now().timestamp(),
            aprovacao_necessaria=self._requer_aprovacao(acao)
        )
    
    def _gerar_descricao(self, acao: Dict[str, Any]) -> str:
        """Gera uma descrição clara da ação"""
        tipo = acao.get("tipo", "").lower()
        if tipo == "hotfix":
            return f"Será aplicado um hotfix para corrigir {acao.get('descricao', 'problema')}"
        elif tipo == "refatoracao":
            return f"Será realizada uma refatoração para melhorar {acao.get('descricao', 'componente')}"
        elif tipo == "redesign":
            return f"Será feito um redesign para otimizar {acao.get('descricao', 'sistema')}"
        return acao.get("descricao", "Ação não especificada")
    
    def _avaliar_impacto(self, acao: Dict[str, Any]) -> str:
        """Avalia e descreve o impacto da ação"""
        impactos = []
        if "servicos_afetados" in acao:
            impactos.append(f"Serviços afetados: {', '.join(acao['servicos_afetados'])}")
        if "tempo_estimado" in acao:
            impactos.append(f"Tempo estimado: {acao['tempo_estimado']}")
        if "recursos_necessarios" in acao:
            impactos.append(f"Recursos necessários: {', '.join(acao['recursos_necessarios'])}")
        
        if not impactos:
            return "Impacto não especificado"
        return ". ".join(impactos)
    
    def _obter_referencia_manual(self, acao: Dict[str, Any]) -> str:
        """Obtém a referência relevante do manual"""
        tipo = acao.get("tipo", "").lower()
        if tipo == "hotfix":
            return "Manual Seção 4.2 - Procedimentos de Hotfix"
        elif tipo == "refatoracao":
            return "Manual Seção 4.3 - Guia de Refatoração"
        elif tipo == "redesign":
            return "Manual Seção 4.4 - Processo de Redesign"
        return "Manual Seção 4.1 - Procedimentos Gerais"
    
    def _requer_aprovacao(self, acao: Dict[str, Any]) -> bool:
        """Determina se a ação requer aprovação manual"""
        # Ações com risco alto sempre requerem aprovação
        if acao.get("risco", 0) > 0.7:
            return True
        
        # Ações que afetam serviços críticos requerem aprovação
        servicos_criticos = {"autenticacao", "banco_dados", "api_gateway"}
        if any(s in servicos_criticos for s in acao.get("servicos_afetados", [])):
            return True
        
        # Ações de redesign sempre requerem aprovação
        if acao.get("tipo", "").lower() == "redesign":
            return True
        
        return False
    
    def _mostrar_acao(self, acao: AcaoNecessaria):
        """
        Exibe a ação formatada no console.
        
        Args:
            acao: Ação a ser exibida
        """
        print("\n" + "="*80)
        print("AÇÃO NECESSÁRIA")
        print("="*80)
        print(f"\nID: {acao.id}")
        print(f"Tipo: {acao.tipo}")
        print(f"\nO que será feito:")
        print(f"  {acao.descricao}")
        print(f"\nImpacto esperado:")
        print(f"  {acao.impacto}")
        print(f"\nNível de risco: {acao.risco*100:.1f}%")
        print(f"\nReferência: {acao.manual_ref}")
        
        if acao.aprovacao_necessaria:
            print("\nEsta ação requer aprovação manual!")
        
        print("\n" + "="*80) 