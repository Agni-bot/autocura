"""
Módulo de Integração da Consciência Situacional.
Responsável pela comunicação com outros serviços do sistema.
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading
from queue import Queue
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ConscienciaSituacional.Integracao")

class IntegradorServicos:
    """Classe responsável pela integração com outros serviços."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o integrador.
        
        Args:
            config: Configurações de integração
        """
        self.config = config
        self.sessao = requests.Session()
        self.fila_eventos = Queue()
        self.lock = threading.Lock()
        self._configurar_sessao()
    
    def _configurar_sessao(self):
        """Configura a sessão HTTP."""
        self.sessao.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if 'timeout' in self.config:
            self.sessao.timeout = self.config['timeout']
    
    def obter_metricas(self) -> Dict[str, float]:
        """
        Obtém métricas do serviço de monitoramento.
        
        Returns:
            dict: Métricas coletadas
        """
        try:
            url = f"{self.config['monitoramento_url']}/api/v1/metricas"
            response = self.sessao.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {str(e)}")
            return {}
    
    def obter_logs(self, filtros: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Obtém logs do serviço de observabilidade.
        
        Args:
            filtros: Filtros para busca de logs
            
        Returns:
            list: Logs coletados
        """
        try:
            url = f"{self.config['observabilidade_url']}/api/v1/logs"
            response = self.sessao.get(url, params=filtros)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter logs: {str(e)}")
            return []
    
    def obter_eventos(self) -> List[Dict[str, Any]]:
        """
        Obtém eventos do serviço de diagnóstico.
        
        Returns:
            list: Eventos coletados
        """
        try:
            url = f"{self.config['diagnostico_url']}/api/v1/eventos"
            response = self.sessao.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter eventos: {str(e)}")
            return []
    
    def enviar_contexto(self, contexto: Dict[str, Any]):
        """
        Envia contexto para o serviço de autocorreção.
        
        Args:
            contexto: Contexto a ser enviado
        """
        try:
            url = f"{self.config['autocorrecao_url']}/api/v1/contexto"
            response = self.sessao.post(url, json=contexto)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Erro ao enviar contexto: {str(e)}")
    
    def enviar_projecao(self, projecao: Dict[str, Any]):
        """
        Envia projeção para o serviço de orquestração.
        
        Args:
            projecao: Projeção a ser enviada
        """
        try:
            url = f"{self.config['orquestracao_url']}/api/v1/projecao"
            response = self.sessao.post(url, json=projecao)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Erro ao enviar projeção: {str(e)}")
    
    def iniciar_coleta_eventos(self):
        """Inicia coleta assíncrona de eventos."""
        def _coletar_eventos():
            while True:
                try:
                    eventos = self.obter_eventos()
                    for evento in eventos:
                        self.fila_eventos.put(evento)
                    time.sleep(self.config.get('intervalo_coleta', 5))
                except Exception as e:
                    logger.error(f"Erro na coleta de eventos: {str(e)}")
                    time.sleep(5)
        
        thread = threading.Thread(target=_coletar_eventos, daemon=True)
        thread.start()
    
    def obter_proximo_evento(self) -> Optional[Dict[str, Any]]:
        """
        Obtém próximo evento da fila.
        
        Returns:
            dict: Próximo evento ou None
        """
        try:
            return self.fila_eventos.get_nowait()
        except:
            return None

class AdaptadorPrometheus:
    """Classe responsável pela integração com Prometheus."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o adaptador.
        
        Args:
            config: Configurações do Prometheus
        """
        self.config = config
        self.sessao = requests.Session()
        self._configurar_sessao()
    
    def _configurar_sessao(self):
        """Configura a sessão HTTP."""
        self.sessao.headers.update({
            'Accept': 'application/json'
        })
        
        if 'timeout' in self.config:
            self.sessao.timeout = self.config['timeout']
    
    def consultar_metricas(self, query: str) -> Dict[str, Any]:
        """
        Consulta métricas no Prometheus.
        
        Args:
            query: Query PromQL
            
        Returns:
            dict: Resultado da consulta
        """
        try:
            url = f"{self.config['url']}/api/v1/query"
            response = self.sessao.get(url, params={'query': query})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao consultar métricas: {str(e)}")
            return {}

class AdaptadorGrafana:
    """Classe responsável pela integração com Grafana."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o adaptador.
        
        Args:
            config: Configurações do Grafana
        """
        self.config = config
        self.sessao = requests.Session()
        self._configurar_sessao()
    
    def _configurar_sessao(self):
        """Configura a sessão HTTP."""
        self.sessao.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if 'api_key' in self.config:
            self.sessao.headers.update({
                'Authorization': f"Bearer {self.config['api_key']}"
            })
        
        if 'timeout' in self.config:
            self.sessao.timeout = self.config['timeout']
    
    def obter_dashboards(self) -> List[Dict[str, Any]]:
        """
        Obtém dashboards do Grafana.
        
        Returns:
            list: Dashboards encontrados
        """
        try:
            url = f"{self.config['url']}/api/search"
            response = self.sessao.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter dashboards: {str(e)}")
            return []
    
    def obter_dashboard(self, uid: str) -> Optional[Dict[str, Any]]:
        """
        Obtém detalhes de um dashboard.
        
        Args:
            uid: ID do dashboard
            
        Returns:
            dict: Detalhes do dashboard ou None
        """
        try:
            url = f"{self.config['url']}/api/dashboards/uid/{uid}"
            response = self.sessao.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter dashboard: {str(e)}")
            return None
    
    def criar_dashboard(self, dashboard: Dict[str, Any]) -> bool:
        """
        Cria um novo dashboard.
        
        Args:
            dashboard: Configuração do dashboard
            
        Returns:
            bool: True se criado com sucesso
        """
        try:
            url = f"{self.config['url']}/api/dashboards/db"
            response = self.sessao.post(url, json=dashboard)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Erro ao criar dashboard: {str(e)}")
            return False 