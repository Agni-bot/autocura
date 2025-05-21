"""
Cliente para API de IA Avançada
"""
import requests
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from ..config.ia_config import ia_config
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

class ClienteIA:
    """Cliente para interação com a API de IA."""
    
    def __init__(self):
        """Inicializa o cliente da API de IA."""
        self.config = ia_config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.API_KEY}",
            "Content-Type": "application/json",
            "X-Organization": self.config.API_ORGANIZATION or ""
        })
        
        # Métricas Prometheus
        if self.config.METRICS_ENABLED:
            self.metricas = {
                "requisicoes_total": Counter(
                    f"{self.config.METRICS_PREFIX}_requisicoes_total",
                    "Total de requisições para a API de IA",
                    ["tipo", "modelo", "status"]
                ),
                "tempo_resposta": Histogram(
                    f"{self.config.METRICS_PREFIX}_tempo_resposta_segundos",
                    "Tempo de resposta da API de IA",
                    ["tipo", "modelo"]
                ),
                "tokens_utilizados": Counter(
                    f"{self.config.METRICS_PREFIX}_tokens_total",
                    "Total de tokens utilizados",
                    ["tipo", "modelo"]
                )
            }
    
    def validar_etica(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida uma decisão usando o modelo ético da IA.
        
        Args:
            decisao: Dicionário contendo os dados da decisão
            
        Returns:
            Dicionário com o resultado da validação
        """
        try:
            endpoint = f"{self.config.API_ENDPOINT}/validacao-etica"
            
            payload = {
                "model": self.config.ETHICAL_MODEL,
                "decisao": decisao,
                "min_confidence": self.config.ETHICAL_MIN_CONFIDENCE,
                "review_required": self.config.ETHICAL_REVIEW_REQUIRED
            }
            
            response = self._fazer_requisicao("POST", endpoint, payload)
            
            if response.get("validacao", {}).get("confianca", 0) < self.config.ETHICAL_MIN_CONFIDENCE:
                logger.warning(f"Validação ética com baixa confiança: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Erro na validação ética: {str(e)}")
            if self.config.FALLBACK_ENABLED:
                return self._validacao_etica_fallback(decisao)
            raise
    
    def analisar_impacto(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa o impacto potencial de uma ação.
        
        Args:
            acao: Dicionário contendo os dados da ação
            
        Returns:
            Dicionário com a análise de impacto
        """
        try:
            endpoint = f"{self.config.API_ENDPOINT}/analise-impacto"
            
            payload = {
                "model": self.config.PRIMARY_MODEL,
                "acao": acao,
                "context_window": self.config.CONTEXT_WINDOW,
                "max_tokens": self.config.MAX_TOKENS
            }
            
            return self._fazer_requisicao("POST", endpoint, payload)
            
        except Exception as e:
            logger.error(f"Erro na análise de impacto: {str(e)}")
            if self.config.FALLBACK_ENABLED:
                return self._analise_impacto_fallback(acao)
            raise
    
    def gerar_insights(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera insights a partir dos dados do sistema.
        
        Args:
            dados: Dicionário contendo os dados para análise
            
        Returns:
            Dicionário com insights gerados
        """
        try:
            endpoint = f"{self.config.API_ENDPOINT}/insights"
            
            payload = {
                "model": self.config.PRIMARY_MODEL,
                "dados": dados,
                "temperature": self.config.TEMPERATURE,
                "max_tokens": self.config.MAX_TOKENS
            }
            
            return self._fazer_requisicao("POST", endpoint, payload)
            
        except Exception as e:
            logger.error(f"Erro na geração de insights: {str(e)}")
            if self.config.FALLBACK_ENABLED:
                return self._insights_fallback(dados)
            raise
    
    def _fazer_requisicao(self, metodo: str, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Faz uma requisição para a API com retry e métricas."""
        start_time = datetime.now()
        
        for tentativa in range(self.config.MAX_RETRIES + 1):
            try:
                response = self.session.request(
                    method=metodo,
                    url=endpoint,
                    json=payload,
                    timeout=self.config.TIMEOUT,
                    verify=self.config.SSL_VERIFY
                )
                
                response.raise_for_status()
                dados = response.json()
                
                if self.config.METRICS_ENABLED:
                    self.metricas["requisicoes_total"].labels(
                        tipo=payload.get("model", "unknown"),
                        modelo=payload.get("model", "unknown"),
                        status="success"
                    ).inc()
                    
                    self.metricas["tempo_resposta"].labels(
                        tipo=payload.get("model", "unknown"),
                        modelo=payload.get("model", "unknown")
                    ).observe((datetime.now() - start_time).total_seconds())
                    
                    if "usage" in dados:
                        self.metricas["tokens_utilizados"].labels(
                            tipo=payload.get("model", "unknown"),
                            modelo=payload.get("model", "unknown")
                        ).inc(dados["usage"].get("total_tokens", 0))
                
                return dados
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na tentativa {tentativa + 1} de {self.config.MAX_RETRIES + 1}: {str(e)}")
                
                if self.config.METRICS_ENABLED:
                    self.metricas["requisicoes_total"].labels(
                        tipo=payload.get("model", "unknown"),
                        modelo=payload.get("model", "unknown"),
                        status="error"
                    ).inc()
                
                if tentativa < self.config.MAX_RETRIES:
                    continue
                raise
    
    def _validacao_etica_fallback(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Implementação local de fallback para validação ética."""
        logger.warning("Usando fallback local para validação ética")
        return {
            "aprovada": False,
            "confianca": 0.0,
            "motivo": "Fallback local - validação conservadora"
        }
    
    def _analise_impacto_fallback(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """Implementação local de fallback para análise de impacto."""
        logger.warning("Usando fallback local para análise de impacto")
        return {
            "risco": 1.0,
            "impacto": "alto",
            "confianca": 0.0,
            "motivo": "Fallback local - análise conservadora"
        }
    
    def _insights_fallback(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Implementação local de fallback para geração de insights."""
        logger.warning("Usando fallback local para geração de insights")
        return {
            "insights": [],
            "confianca": 0.0,
            "motivo": "Fallback local - sem insights disponíveis"
        } 