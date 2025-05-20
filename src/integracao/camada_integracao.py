#!/usr/bin/env python3
"""
Implementação da camada de integração do sistema.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import aiohttp
import websockets
import redis
import msgpack
import yaml
from src.monitoramento.coletor_metricas import Metrica
from src.diagnostico.rede_neural import Diagnostico
from src.acoes.gerador_acoes import Acao

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CamadaIntegracao:
    """Camada de integração responsável pela comunicação entre componentes."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Inicializa a camada de integração."""
        self.config = config
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Endpoints configurados
        self.endpoints = {
            "prometheus": config.get("prometheus_url", "http://localhost:9090"),
            "loki": config.get("loki_url", "http://localhost:3100"),
            "grafana": config.get("grafana_url", "http://localhost:3000"),
            "kubernetes": config.get("kubernetes_url", "http://localhost:8001"),
            "redis": config.get("redis_url", "redis://localhost:6379")
        }
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Adiciona headers de autenticação se configurados
        if "auth_token" in config:
            self.headers["Authorization"] = f"Bearer {config['auth_token']}"
        
        logger.info("Camada de integração inicializada")

    async def inicializar(self):
        """Inicializa a sessão HTTP."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            logger.info("Sessão HTTP inicializada")

    async def finalizar(self):
        """Finaliza a sessão HTTP."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Sessão HTTP finalizada")

    async def enviar_metricas(
        self,
        metricas: List[Metrica],
        endpoint: str = "prometheus"
    ) -> bool:
        """Envia métricas para o endpoint especificado."""
        if not self.session:
            await self.inicializar()
        
        url = f"{self.endpoints[endpoint]}/api/v1/write"
        
        # Prepara payload
        payload = []
        for metrica in metricas:
            payload.append({
                "name": metrica.nome,
                "value": metrica.valor,
                "type": metrica.tipo,
                "labels": metrica.labels,
                "timestamp": metrica.timestamp.isoformat()
            })
        
        # Tenta enviar com retry
        for tentativa in range(self.max_retries):
            try:
                async with self.session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Métricas enviadas com sucesso para {endpoint}")
                        return True
                    else:
                        logger.warning(
                            f"Falha ao enviar métricas para {endpoint}, "
                            f"status: {response.status}"
                        )
            except Exception as e:
                logger.error(
                    f"Erro ao enviar métricas para {endpoint}, "
                    f"tentativa {tentativa + 1}: {str(e)}"
                )
                if tentativa < self.max_retries - 1:
                    await asyncio.sleep(2 ** tentativa)  # Backoff exponencial
        
        return False

    async def enviar_diagnostico(
        self,
        diagnostico: Diagnostico,
        endpoint: str = "grafana"
    ) -> bool:
        """Envia diagnóstico para o endpoint especificado."""
        if not self.session:
            await self.inicializar()
        
        url = f"{self.endpoints[endpoint]}/api/diagnostics"
        
        # Prepara payload
        payload = {
            "timestamp": diagnostico.timestamp.isoformat(),
            "anomalia_detectada": diagnostico.anomalia_detectada,
            "score_anomalia": diagnostico.score_anomalia,
            "padrao_detectado": diagnostico.padrao_detectado,
            "confianca": diagnostico.confianca,
            "metricas_relevantes": diagnostico.metricas_relevantes,
            "recomendacoes": diagnostico.recomendacoes
        }
        
        # Tenta enviar com retry
        for tentativa in range(self.max_retries):
            try:
                async with self.session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Diagnóstico enviado com sucesso para {endpoint}")
                        return True
                    else:
                        logger.warning(
                            f"Falha ao enviar diagnóstico para {endpoint}, "
                            f"status: {response.status}"
                        )
            except Exception as e:
                logger.error(
                    f"Erro ao enviar diagnóstico para {endpoint}, "
                    f"tentativa {tentativa + 1}: {str(e)}"
                )
                if tentativa < self.max_retries - 1:
                    await asyncio.sleep(2 ** tentativa)
        
        return False

    async def enviar_acao(
        self,
        acao: Acao,
        endpoint: str = "kubernetes"
    ) -> bool:
        """Envia ação para o endpoint especificado."""
        if not self.session:
            await self.inicializar()
        
        url = f"{self.endpoints[endpoint]}/api/actions"
        
        # Prepara payload
        payload = {
            "id": acao.id,
            "tipo": acao.tipo,
            "descricao": acao.descricao,
            "prioridade": acao.prioridade,
            "timestamp": acao.timestamp.isoformat(),
            "parametros": acao.parametros,
            "status": acao.status
        }
        
        # Tenta enviar com retry
        for tentativa in range(self.max_retries):
            try:
                async with self.session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Ação enviada com sucesso para {endpoint}")
                        return True
                    else:
                        logger.warning(
                            f"Falha ao enviar ação para {endpoint}, "
                            f"status: {response.status}"
                        )
            except Exception as e:
                logger.error(
                    f"Erro ao enviar ação para {endpoint}, "
                    f"tentativa {tentativa + 1}: {str(e)}"
                )
                if tentativa < self.max_retries - 1:
                    await asyncio.sleep(2 ** tentativa)
        
        return False

    async def obter_metricas(
        self,
        query: str,
        endpoint: str = "prometheus",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Obtém métricas do endpoint especificado."""
        if not self.session:
            await self.inicializar()
        
        url = f"{self.endpoints[endpoint]}/api/v1/query"
        
        # Prepara parâmetros
        params = {"query": query}
        if start_time:
            params["start"] = start_time.isoformat()
        if end_time:
            params["end"] = end_time.isoformat()
        
        # Tenta obter com retry
        for tentativa in range(self.max_retries):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Métricas obtidas com sucesso de {endpoint}")
                        return data.get("data", {}).get("result", [])
                    else:
                        logger.warning(
                            f"Falha ao obter métricas de {endpoint}, "
                            f"status: {response.status}"
                        )
            except Exception as e:
                logger.error(
                    f"Erro ao obter métricas de {endpoint}, "
                    f"tentativa {tentativa + 1}: {str(e)}"
                )
                if tentativa < self.max_retries - 1:
                    await asyncio.sleep(2 ** tentativa)
        
        return []

    async def obter_logs(
        self,
        query: str,
        endpoint: str = "loki",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtém logs do endpoint especificado."""
        if not self.session:
            await self.inicializar()
        
        url = f"{self.endpoints[endpoint]}/api/v1/query"
        
        # Prepara parâmetros
        params = {
            "query": query,
            "limit": limit
        }
        
        # Tenta obter com retry
        for tentativa in range(self.max_retries):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Logs obtidos com sucesso de {endpoint}")
                        return data.get("data", {}).get("result", [])
                    else:
                        logger.warning(
                            f"Falha ao obter logs de {endpoint}, "
                            f"status: {response.status}"
                        )
            except Exception as e:
                logger.error(
                    f"Erro ao obter logs de {endpoint}, "
                    f"tentativa {tentativa + 1}: {str(e)}"
                )
                if tentativa < self.max_retries - 1:
                    await asyncio.sleep(2 ** tentativa)
        
        return []

    async def verificar_saude_endpoint(
        self,
        endpoint: str
    ) -> Dict[str, Any]:
        """Verifica a saúde do endpoint especificado."""
        if not self.session:
            await self.inicializar()
        
        url = f"{self.endpoints[endpoint]}/health"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "ok",
                        "endpoint": endpoint,
                        "details": data
                    }
                else:
                    return {
                        "status": "error",
                        "endpoint": endpoint,
                        "error": f"Status code: {response.status}"
                    }
        except Exception as e:
            return {
                "status": "error",
                "endpoint": endpoint,
                "error": str(e)
            }

    async def verificar_saude_todos_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Verifica a saúde de todos os endpoints configurados."""
        resultados = {}
        
        for endpoint in self.endpoints:
            resultado = await self.verificar_saude_endpoint(endpoint)
            resultados[endpoint] = resultado
        
        return resultados

async def main():
    """Função principal."""
    integracao = CamadaIntegracao()
    await integracao.executar_continuamente()

if __name__ == '__main__':
    asyncio.run(main()) 