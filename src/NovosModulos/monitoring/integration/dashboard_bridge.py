"""
Dashboard Bridge - Integração entre Dashboard HTML e Módulo de Monitoramento
===========================================================================

Este módulo conecta o dashboard HTML simples com o módulo de monitoramento
avançado, permitindo que ambos trabalhem em conjunto.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging

# Importações do módulo de monitoramento
try:
    from ..metrics.gerenciador_metricas import GerenciadorMetricas, Metrica
    from ..observability.observabilidade import VisualizadorHolografico, EventoSistema
    from ..observability.observador import ObservadorSistema
except ImportError:
    # Fallbacks para desenvolvimento
    class Metrica:
        def __init__(self, id=None, nome=None, tipo=None, valor=None, timestamp=None, labels=None, descricao=None, unidade=None):
            self.id = id
            self.nome = nome
            self.tipo = tipo
            self.valor = valor
            self.timestamp = timestamp or datetime.now()
            self.labels = labels or {}
            self.descricao = descricao
            self.unidade = unidade
    
    class GerenciadorMetricas:
        def __init__(self, config): pass
        async def obter_estatisticas(self): return {}
        async def buscar_metricas(self, **kwargs): return []
        async def obter_metrica(self, metrica_id): return None
        async def configurar_alerta(self, metrica_id, tipo, valor): return False
    
    class VisualizadorHolografico:
        def __init__(self, **kwargs): pass
        def visualizar_metricas_temporais(self, **kwargs): return ""
    
    class ObservadorSistema:
        def __init__(self, **kwargs): pass
        async def obter_status_sistema(self): return {}

logger = logging.getLogger(__name__)

class DashboardBridge:
    """
    Ponte entre o dashboard HTML e o módulo de monitoramento avançado.
    
    Esta classe integra as funcionalidades do módulo de monitoramento
    com o dashboard HTML, fornecendo dados enriquecidos e visualizações
    avançadas.
    """
    
    def __init__(self):
        """Inicializa a ponte do dashboard."""
        self.config = {
            "base_dir": "data/metricas",
            "alertas_enabled": True,
            "visualizacoes_enabled": True
        }
        
        # Inicializa componentes do monitoramento
        self.gerenciador_metricas = GerenciadorMetricas(self.config)
        self.visualizador = VisualizadorHolografico(diretorio_saida="static/visualizacoes")
        self.observador = ObservadorSistema()
        
        # Cache para otimização
        self.cache_metricas = {}
        self.cache_timestamp = None
        self.cache_ttl = 30  # 30 segundos
        
        logger.info("Dashboard Bridge inicializado")
    
    async def obter_dados_dashboard_enriquecidos(self) -> Dict[str, Any]:
        """
        Obtém dados enriquecidos para o dashboard HTML.
        
        Combina dados básicos do sistema com métricas avançadas
        do módulo de monitoramento.
        
        Returns:
            Dicionário com dados enriquecidos para o dashboard
        """
        try:
            # Verifica cache
            agora = datetime.now()
            if (self.cache_timestamp and 
                (agora - self.cache_timestamp).seconds < self.cache_ttl):
                return self.cache_metricas
            
            # Obtém dados básicos do sistema
            dados_basicos = await self._obter_dados_basicos()
            
            # Obtém métricas avançadas
            metricas_avancadas = await self._obter_metricas_avancadas()
            
            # Obtém status do observador
            status_observador = await self.observador.obter_status_sistema()
            
            # Obtém estatísticas do gerenciador
            estatisticas = await self.gerenciador_metricas.obter_estatisticas()
            
            # Combina todos os dados
            dados_enriquecidos = {
                **dados_basicos,
                "metricas_avancadas": metricas_avancadas,
                "observador_status": status_observador,
                "estatisticas_metricas": estatisticas,
                "capacidades_monitoramento": {
                    "visualizacao_holografica": True,
                    "alertas_inteligentes": True,
                    "analise_preditiva": True,
                    "correlacao_metricas": True,
                    "deteccao_anomalias": True
                },
                "timestamp": agora.isoformat()
            }
            
            # Atualiza cache
            self.cache_metricas = dados_enriquecidos
            self.cache_timestamp = agora
            
            return dados_enriquecidos
            
        except Exception as e:
            logger.error(f"Erro ao obter dados enriquecidos: {e}")
            return await self._obter_dados_basicos()
    
    async def _obter_dados_basicos(self) -> Dict[str, Any]:
        """Obtém dados básicos do sistema (fallback)."""
        import psutil
        
        return {
            "system_metrics": {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('C:\\').percent if os.name == 'nt' else psutil.disk_usage('/').percent
            },
            "module_status": {
                "total": 5,
                "healthy": 5,
                "degraded": 0,
                "failed": 0
            },
            "recent_events": [],
            "healing_actions": {
                "total_today": 0,
                "successful": 0,
                "failed": 0
            }
        }
    
    async def _obter_metricas_avancadas(self) -> Dict[str, Any]:
        """Obtém métricas avançadas do gerenciador."""
        try:
            # Busca métricas por tipo
            metricas_cpu = await self.gerenciador_metricas.buscar_metricas(tipo="gauge", labels={"component": "cpu"})
            metricas_memoria = await self.gerenciador_metricas.buscar_metricas(tipo="gauge", labels={"component": "memory"})
            metricas_disco = await self.gerenciador_metricas.buscar_metricas(tipo="gauge", labels={"component": "disk"})
            
            return {
                "cpu_detalhado": [self._metrica_to_dict(m) for m in metricas_cpu],
                "memoria_detalhada": [self._metrica_to_dict(m) for m in metricas_memoria],
                "disco_detalhado": [self._metrica_to_dict(m) for m in metricas_disco],
                "total_metricas": len(metricas_cpu) + len(metricas_memoria) + len(metricas_disco)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter métricas avançadas: {e}")
            return {}
    
    def _metrica_to_dict(self, metrica: Metrica) -> Dict[str, Any]:
        """Converte métrica para dicionário."""
        return {
            "id": metrica.id,
            "nome": metrica.nome,
            "tipo": metrica.tipo,
            "valor": metrica.valor,
            "timestamp": metrica.timestamp.isoformat(),
            "labels": metrica.labels,
            "descricao": metrica.descricao,
            "unidade": metrica.unidade
        }
    
    async def gerar_visualizacao_temporal(self, metrica_ids: List[str]) -> str:
        """
        Gera visualização temporal para métricas específicas.
        
        Args:
            metrica_ids: Lista de IDs das métricas
            
        Returns:
            Caminho da visualização gerada
        """
        try:
            # Obtém métricas
            metricas = []
            for metrica_id in metrica_ids:
                metrica = await self.gerenciador_metricas.obter_metrica(metrica_id)
                if metrica:
                    metricas.append(metrica)
            
            if not metricas:
                return ""
            
            # Gera visualização
            caminho = self.visualizador.visualizar_metricas_temporais(
                metricas=metricas,
                titulo="Evolução Temporal - Dashboard AutoCura",
                salvar=True
            )
            
            return caminho
            
        except Exception as e:
            logger.error(f"Erro ao gerar visualização: {e}")
            return ""
    
    async def configurar_alerta_dashboard(self, metrica_id: str, tipo: str, valor: Any) -> bool:
        """
        Configura alerta para uma métrica via dashboard.
        
        Args:
            metrica_id: ID da métrica
            tipo: Tipo do alerta
            valor: Valor do alerta
            
        Returns:
            True se configurado com sucesso
        """
        try:
            return await self.gerenciador_metricas.configurar_alerta(metrica_id, tipo, valor)
        except Exception as e:
            logger.error(f"Erro ao configurar alerta: {e}")
            return False
    
    async def obter_alertas_ativos(self) -> List[Dict[str, Any]]:
        """
        Obtém alertas ativos do sistema.
        
        Returns:
            Lista de alertas ativos
        """
        try:
            # TODO: Implementar busca de alertas ativos
            # Por enquanto retorna lista vazia
            return []
        except Exception as e:
            logger.error(f"Erro ao obter alertas: {e}")
            return []

# Instância global da ponte
dashboard_bridge = DashboardBridge()

# Router FastAPI para endpoints da ponte
router = APIRouter(prefix="/api/dashboard-bridge", tags=["Dashboard Bridge"])

@router.get("/dados-enriquecidos")
async def get_dados_enriquecidos():
    """Endpoint para obter dados enriquecidos do dashboard."""
    try:
        dados = await dashboard_bridge.obter_dados_dashboard_enriquecidos()
        return JSONResponse(content=dados)
    except Exception as e:
        logger.error(f"Erro no endpoint dados-enriquecidos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/visualizacao-temporal")
async def gerar_visualizacao(metrica_ids: List[str]):
    """Endpoint para gerar visualização temporal."""
    try:
        caminho = await dashboard_bridge.gerar_visualizacao_temporal(metrica_ids)
        return {"caminho": caminho, "sucesso": bool(caminho)}
    except Exception as e:
        logger.error(f"Erro no endpoint visualizacao-temporal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configurar-alerta")
async def configurar_alerta(metrica_id: str, tipo: str, valor: float):
    """Endpoint para configurar alertas."""
    try:
        sucesso = await dashboard_bridge.configurar_alerta_dashboard(metrica_id, tipo, valor)
        return {"sucesso": sucesso}
    except Exception as e:
        logger.error(f"Erro no endpoint configurar-alerta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alertas-ativos")
async def get_alertas_ativos():
    """Endpoint para obter alertas ativos."""
    try:
        alertas = await dashboard_bridge.obter_alertas_ativos()
        return {"alertas": alertas}
    except Exception as e:
        logger.error(f"Erro no endpoint alertas-ativos: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 