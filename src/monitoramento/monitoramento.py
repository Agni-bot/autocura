"""
Módulo principal de monitoramento do sistema AutoCura.
"""

import time
import threading
from typing import Dict, List, Optional
import logging
from .metricas import MonitoramentoMultidimensional, MetricasSistema
from .recursos import MonitorRecursos
from .notificador import Notificador
from .config import CONFIG

class Monitoramento:
    def __init__(self):
        """Inicializa o sistema de monitoramento."""
        self.logger = logging.getLogger(__name__)
        self.monitor = MonitoramentoMultidimensional()
        self.recursos = MonitorRecursos()
        self.notificador = Notificador()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        
    def iniciar(self):
        """Inicia o monitoramento em uma thread separada."""
        if self._thread is not None and self._thread.is_alive():
            self.logger.warning("Monitoramento já está em execução")
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._loop_monitoramento)
        self._thread.daemon = True
        self._thread.start()
        self.logger.info("Monitoramento iniciado")
        
    def parar(self):
        """Para o monitoramento."""
        self._running = False
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        self.logger.info("Monitoramento parado")
        
    def _loop_monitoramento(self):
        """Loop principal de monitoramento."""
        while self._running:
            try:
                # Coleta métricas
                metricas = self.monitor.coletar_metricas()
                
                # Verifica alertas
                alertas = self.monitor.verificar_alertas(metricas)
                
                # Envia notificações
                for alerta in alertas:
                    self.notificador.enviar_alerta(alerta)
                    
                # Analisa tendências
                analise = self.monitor.analisar_metricas()
                
                # Verifica uso de recursos
                uso_recursos = self.recursos.obter_metricas()
                
                # Se uso de recursos estiver alto, tenta limpar
                if any(v > 80 for v in uso_recursos.values() if isinstance(v, (int, float))):
                    self.recursos.limpar_recursos()
                    
                # Aguarda próximo ciclo
                time.sleep(CONFIG.METRICS_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {str(e)}")
                time.sleep(5)  # Aguarda um pouco antes de tentar novamente
                
    def obter_metricas(self) -> Dict:
        """Obtém métricas atuais do sistema."""
        try:
            metricas = self.monitor.coletar_metricas()
            analise = self.monitor.analisar_metricas()
            recursos = self.recursos.obter_metricas()
            
            return {
                'metricas': {
                    'throughput': metricas.throughput,
                    'taxa_erro': metricas.taxa_erro,
                    'latencia': metricas.latencia,
                    'uso_recursos': metricas.uso_recursos
                },
                'analise': analise,
                'recursos': recursos
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas: {str(e)}")
            return {}
            
    def obter_historico(self, metrica: str, limite: int = 100) -> List[float]:
        """Obtém histórico de uma métrica específica."""
        try:
            return self.monitor.obter_historico(metrica, limite)
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {str(e)}")
            return []
            
    def obter_processos(self) -> List[Dict]:
        """Obtém lista de processos com uso de recursos."""
        try:
            return self.recursos.obter_processos()
        except Exception as e:
            self.logger.error(f"Erro ao obter processos: {str(e)}")
            return [] 