#!/usr/bin/env python3
"""
Implementação do monitoramento do sistema.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import psutil
import platform
import os
import time
import threading
from .metricas import MonitoramentoMultidimensional, MetricasSistema
from .recursos import MonitorRecursos
from .notificador import Notificador
from .config import CONFIG

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitorSistema:
    def __init__(self):
        """Inicializa o monitor do sistema."""
        self.logger = logging.getLogger(__name__)
        self.monitor = MonitoramentoMultidimensional()
        self.recursos = MonitorRecursos()
        self.notificador = Notificador()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self.base_dir = Path(__file__).parent.parent.parent
        self.memoria_path = self.base_dir / 'memoria' / 'memoria_compartilhada.json'
        self.estado: Dict[str, Any] = {
            'ciclo_atual': 0,
            'ultima_execucao': None,
            'metricas': {},
            'alertas': [],
            'historico': []
        }
        self.limites = {
            'cpu': 0.8,  # 80%
            'memoria': 0.8,  # 80%
            'disco': 0.9,  # 90%
            'latencia': 1000,  # ms
            'erros': 0.1  # 10%
        }
    
    async def carregar_memoria(self):
        """Carrega o estado atual da memória compartilhada."""
        try:
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
                    self.estado.update(memoria.get('estado_monitoramento', {}))
            logger.info("Memória do monitoramento carregada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar memória do monitoramento: {str(e)}")
            raise
    
    async def coletar_metricas_sistema(self):
        """Coleta métricas do sistema operacional."""
        try:
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'sistema': {
                    'cpu': {
                        'uso_percentual': psutil.cpu_percent(interval=1),
                        'uso_por_core': psutil.cpu_percent(interval=1, percpu=True),
                        'frequencia': psutil.cpu_freq().current if psutil.cpu_freq() else None
                    },
                    'memoria': {
                        'total': psutil.virtual_memory().total,
                        'disponivel': psutil.virtual_memory().available,
                        'uso_percentual': psutil.virtual_memory().percent,
                        'swap_total': psutil.swap_memory().total,
                        'swap_usado': psutil.swap_memory().used
                    },
                    'disco': {
                        'total': psutil.disk_usage('/').total,
                        'usado': psutil.disk_usage('/').used,
                        'livre': psutil.disk_usage('/').free,
                        'uso_percentual': psutil.disk_usage('/').percent
                    },
                    'rede': {
                        'bytes_enviados': psutil.net_io_counters().bytes_sent,
                        'bytes_recebidos': psutil.net_io_counters().bytes_recv,
                        'pacotes_enviados': psutil.net_io_counters().packets_sent,
                        'pacotes_recebidos': psutil.net_io_counters().packets_recv
                    }
                },
                'processos': {
                    'total': len(psutil.pids()),
                    'ativos': len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'running']),
                    'zumbis': len([p for p in psutil.process_iter(['status']) if p.info['status'] == 'zombie'])
                },
                'sistema_operacional': {
                    'nome': platform.system(),
                    'versao': platform.version(),
                    'arquitetura': platform.machine(),
                    'processador': platform.processor()
                }
            }
            
            self.estado['metricas'] = metricas
            logger.info("Métricas do sistema coletadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {str(e)}")
            raise
    
    async def coletar_metricas_aplicacao(self):
        """Coleta métricas específicas da aplicação."""
        try:
            # TODO: Implementar coleta de métricas reais da aplicação
            metricas = {
                'timestamp': datetime.now().isoformat(),
                'aplicacao': {
                    'requisicoes': {
                        'total': 0,
                        'sucesso': 0,
                        'erro': 0,
                        'latencia_media': 0
                    },
                    'recursos': {
                        'conexoes_ativas': 0,
                        'threads_ativas': 0,
                        'cache_hits': 0,
                        'cache_misses': 0
                    },
                    'processamento': {
                        'tarefas_pendentes': 0,
                        'tarefas_concluidas': 0,
                        'tarefas_falhas': 0
                    }
                }
            }
            
            self.estado['metricas'].update(metricas)
            logger.info("Métricas da aplicação coletadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao coletar métricas da aplicação: {str(e)}")
            raise
    
    async def analisar_metricas(self):
        """Analisa as métricas coletadas e gera alertas."""
        try:
            alertas = []
            metricas = self.estado['metricas']
            
            # Análise de CPU
            if metricas['sistema']['cpu']['uso_percentual'] > self.limites['cpu'] * 100:
                alertas.append({
                    'tipo': 'cpu',
                    'nivel': 'alerta',
                    'mensagem': f"Uso de CPU acima do limite: {metricas['sistema']['cpu']['uso_percentual']}%",
                    'timestamp': datetime.now().isoformat()
                })
            
            # Análise de Memória
            if metricas['sistema']['memoria']['uso_percentual'] > self.limites['memoria'] * 100:
                alertas.append({
                    'tipo': 'memoria',
                    'nivel': 'alerta',
                    'mensagem': f"Uso de memória acima do limite: {metricas['sistema']['memoria']['uso_percentual']}%",
                    'timestamp': datetime.now().isoformat()
                })
            
            # Análise de Disco
            if metricas['sistema']['disco']['uso_percentual'] > self.limites['disco'] * 100:
                alertas.append({
                    'tipo': 'disco',
                    'nivel': 'alerta',
                    'mensagem': f"Uso de disco acima do limite: {metricas['sistema']['disco']['uso_percentual']}%",
                    'timestamp': datetime.now().isoformat()
                })
            
            # Análise de Latência
            if metricas['aplicacao']['requisicoes']['latencia_media'] > self.limites['latencia']:
                alertas.append({
                    'tipo': 'latencia',
                    'nivel': 'alerta',
                    'mensagem': f"Latência acima do limite: {metricas['aplicacao']['requisicoes']['latencia_media']}ms",
                    'timestamp': datetime.now().isoformat()
                })
            
            # Análise de Taxa de Erro
            total_requisicoes = metricas['aplicacao']['requisicoes']['total']
            if total_requisicoes > 0:
                taxa_erro = metricas['aplicacao']['requisicoes']['erro'] / total_requisicoes
                if taxa_erro > self.limites['erros']:
                    alertas.append({
                        'tipo': 'erros',
                        'nivel': 'alerta',
                        'mensagem': f"Taxa de erro acima do limite: {taxa_erro * 100}%",
                        'timestamp': datetime.now().isoformat()
                    })
            
            self.estado['alertas'] = alertas
            logger.info(f"Análise de métricas concluída. {len(alertas)} alertas gerados")
        except Exception as e:
            logger.error(f"Erro ao analisar métricas: {str(e)}")
            raise
    
    async def atualizar_historico(self):
        """Atualiza o histórico de métricas e alertas."""
        try:
            historico = {
                'timestamp': datetime.now().isoformat(),
                'metricas': self.estado['metricas'],
                'alertas': self.estado['alertas']
            }
            
            self.estado['historico'].append(historico)
            
            # Manter apenas as últimas 1000 entradas
            if len(self.estado['historico']) > 1000:
                self.estado['historico'] = self.estado['historico'][-1000:]
            
            logger.info("Histórico atualizado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao atualizar histórico: {str(e)}")
            raise
    
    async def atualizar_memoria(self):
        """Atualiza a memória compartilhada com o novo estado."""
        try:
            self.estado['ultima_execucao'] = datetime.now().isoformat()
            self.estado['ciclo_atual'] += 1
            
            # Carrega memória existente
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
            else:
                memoria = {}
            
            # Atualiza estado do monitoramento
            memoria['estado_monitoramento'] = self.estado
            
            # Salva memória atualizada
            with open(self.memoria_path, 'w', encoding='utf-8') as f:
                json.dump(memoria, f, indent=2, ensure_ascii=False)
            
            logger.info("Memória do monitoramento atualizada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao atualizar memória do monitoramento: {str(e)}")
            raise
    
    async def ciclo_monitoramento(self):
        """Executa um ciclo completo de monitoramento."""
        try:
            logger.info("Iniciando ciclo de monitoramento...")
            
            await self.carregar_memoria()
            await self.coletar_metricas_sistema()
            await self.coletar_metricas_aplicacao()
            await self.analisar_metricas()
            await self.atualizar_historico()
            await self.atualizar_memoria()
            
            logger.info("Ciclo de monitoramento concluído com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro durante o ciclo de monitoramento: {str(e)}")
            raise
    
    async def executar_continuamente(self, intervalo: int = 60):  # 60 segundos
        """Executa ciclos de monitoramento continuamente."""
        while True:
            try:
                await self.ciclo_monitoramento()
                await asyncio.sleep(intervalo)
            except Exception as e:
                logger.error(f"Erro no ciclo contínuo de monitoramento: {str(e)}")
                await asyncio.sleep(intervalo)  # Aguarda antes de tentar novamente

    def iniciar(self):
        """Inicia o monitoramento em uma thread separada."""
        if self._thread is not None and self._thread.is_alive():
            self.logger.warning("Monitor já está em execução")
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._loop_monitoramento)
        self._thread.daemon = True
        self._thread.start()
        self.logger.info("Monitor iniciado")
        
    def parar(self):
        """Para o monitoramento."""
        self._running = False
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        self.logger.info("Monitor parado")
        
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

async def main():
    """Função principal."""
    monitor = MonitorSistema()
    await monitor.executar_continuamente()

if __name__ == '__main__':
    asyncio.run(main()) 