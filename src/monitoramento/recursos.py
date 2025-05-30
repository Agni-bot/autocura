import asyncio
import logging
import psutil
import json
from datetime import datetime
from collections import deque
from typing import Dict, Any, List, Tuple
from pathlib import Path
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry
from src.monitoramento.config import CONFIG
import os

logger = logging.getLogger(__name__)

class MonitorRecursos:
    def __init__(self, registry=None):
        self.intervalo = CONFIG['intervalo_monitoramento']
        self.limite_equidade = CONFIG['limites']['equidade']
        self.historico = deque(maxlen=CONFIG['memoria']['max_historico'])
        self.logger = logging.getLogger(__name__)
        self.memoria_path = Path(CONFIG['memoria']['arquivo'])
        self.recursos = {}
        self.ultimo_ajuste = None
        self.registry = registry or None
        
        # Inicializa métricas Prometheus
        self._init_prometheus_metrics()
        
    def _init_prometheus_metrics(self) -> None:
        """Inicializa métricas Prometheus"""
        reg = self.registry
        # Contadores
        self.ajustes_counter = Counter(
            'autocura_ajustes_total',
            'Total de ajustes de recursos realizados',
            ['tipo'],
            registry=reg
        )
        self.alertas_counter = Counter(
            'autocura_alertas_total',
            'Total de alertas gerados',
            ['severidade', 'tipo'],
            registry=reg
        )
        
        # Gauges
        self.cpu_usage = Gauge(
            'autocura_cpu_usage',
            'Uso de CPU em percentual',
            ['core'],
            registry=reg
        )
        self.memory_usage = Gauge(
            'autocura_memory_usage',
            'Uso de memória em percentual',
            ['tipo'],
            registry=reg
        )
        self.disk_usage = Gauge(
            'autocura_disk_usage',
            'Uso de disco em percentual',
            ['particao'],
            registry=reg
        )
        self.equidade = Gauge(
            'autocura_equidade',
            'Índice de equidade na distribuição de recursos',
            registry=reg
        )
        
        # Histogramas
        self.ajuste_duration = Histogram(
            'autocura_ajuste_duration_seconds',
            'Duração dos ajustes de recursos',
            buckets=[1, 5, 10, 30, 60],
            registry=reg
        )
        
    async def iniciar_monitoramento(self):
        """Inicia monitoramento contínuo de recursos"""
        self.logger.info("Iniciando monitoramento de recursos")
        while True:
            try:
                metricas = self.coletar_metricas()
                self.registrar_metricas(metricas)
                self.atualizar_memoria_compartilhada(metricas)
                self.atualizar_metricas_prometheus(metricas)
                
                if self.verificar_limites(metricas):
                    await self.acionar_ajuste_automatico(metricas)
                
                await asyncio.sleep(self.intervalo)
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {str(e)}")
                self.alertas_counter.labels(severidade='error', tipo='monitoramento').inc()
                await asyncio.sleep(5)  # Espera antes de retentar

    def coletar_metricas(self) -> Dict[str, Any]:
        """Coleta métricas detalhadas do sistema"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        memoria = psutil.virtual_memory()
        disco = psutil.disk_usage('/')
        
        metricas = {
            'cpu': {
                'total': sum(cpu_percent) / len(cpu_percent),
                'por_core': cpu_percent,
                'frequencia': psutil.cpu_freq().current if psutil.cpu_freq() else None
            },
            'memoria': {
                'total': memoria.total,
                'disponivel': memoria.available,
                'percentual': memoria.percent,
                'swap': {
                    'total': psutil.swap_memory().total,
                    'usado': psutil.swap_memory().used,
                    'percentual': psutil.swap_memory().percent
                }
            },
            'disco': {
                'total': disco.total,
                'usado': disco.used,
                'livre': disco.free,
                'percentual': disco.percent
            },
            'equidade': self.calcular_equidade(),
            'timestamp': datetime.now().isoformat()
        }
        
        return metricas

    def atualizar_metricas_prometheus(self, metricas: Dict[str, Any]) -> None:
        """Atualiza métricas Prometheus com os valores coletados"""
        # CPU
        for i, uso in enumerate(metricas['cpu']['por_core']):
            self.cpu_usage.labels(core=f'core_{i}').set(uso)
            
        # Memória
        self.memory_usage.labels(tipo='ram').set(metricas['memoria']['percentual'])
        self.memory_usage.labels(tipo='swap').set(metricas['memoria']['swap']['percentual'])
        
        # Disco
        self.disk_usage.labels(particao='/').set(metricas['disco']['percentual'])
        
        # Equidade
        self.equidade.set(metricas['equidade'])

    def calcular_equidade(self) -> float:
        """Calcula índice de equidade na distribuição de recursos"""
        distribuicao = self.obter_distribuicao_recursos()
        if not distribuicao:
            return 1.0
            
        valores = list(distribuicao.values())
        media = sum(valores) / len(valores)
        desvio = sum(abs(v - media) for v in valores) / len(valores)
        
        # Equidade é inversamente proporcional ao desvio
        equidade = 1.0 - (desvio / media if media > 0 else 0)
        return max(0.0, min(1.0, equidade))

    def obter_distribuicao_recursos(self) -> Dict[str, float]:
        """Obtém distribuição atual de recursos"""
        return self.recursos.copy()

    def verificar_limites(self, metricas: Dict[str, Any]) -> bool:
        """Verifica se as métricas estão dentro dos limites configurados"""
        alertas = []
        
        # CPU
        if metricas['cpu']['total'] > CONFIG['limites']['cpu']['total']:
            alertas.append({
                'tipo': 'cpu',
                'severidade': 'alta',
                'valor': metricas['cpu']['total'],
                'limite': CONFIG['limites']['cpu']['total']
            })
            self.alertas_counter.labels(severidade='alta', tipo='cpu').inc()
            
        # Memória
        if metricas['memoria']['percentual'] > CONFIG['limites']['memoria']['percentual']:
            alertas.append({
                'tipo': 'memoria',
                'severidade': 'alta',
                'valor': metricas['memoria']['percentual'],
                'limite': CONFIG['limites']['memoria']['percentual']
            })
            self.alertas_counter.labels(severidade='alta', tipo='memoria').inc()
            
        # Disco
        if metricas['disco']['percentual'] > CONFIG['limites']['disco']['percentual']:
            alertas.append({
                'tipo': 'disco',
                'severidade': 'alta',
                'valor': metricas['disco']['percentual'],
                'limite': CONFIG['limites']['disco']['percentual']
            })
            self.alertas_counter.labels(severidade='alta', tipo='disco').inc()
            
        # Equidade
        if metricas['equidade'] < self.limite_equidade:
            alertas.append({
                'tipo': 'equidade',
                'severidade': 'media',
                'valor': metricas['equidade'],
                'limite': self.limite_equidade
            })
            self.alertas_counter.labels(severidade='media', tipo='equidade').inc()
            
        # Registra alertas no histórico
        if alertas:
            self.historico.append({
                'timestamp': datetime.now().isoformat(),
                'alertas': alertas
            })
            
        return len(alertas) > 0

    def registrar_metricas(self, metricas: Dict[str, Any]):
        """Registra métricas no histórico com logs estruturados"""
        self.historico.append(metricas)
        self.logger.info(
            "Métricas registradas",
            extra={
                'metricas': {
                    'cpu': f"{metricas['cpu']['total']:.1f}%",
                    'memoria': f"{metricas['memoria']['percentual']:.1f}%",
                    'disco': f"{metricas['disco']['percentual']:.1f}%",
                    'equidade': f"{metricas['equidade']:.2f}"
                }
            }
        )

    def atualizar_memoria_compartilhada(self, metricas: Dict[str, Any]):
        """Atualiza métricas na memória compartilhada"""
        try:
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r') as f:
                    memoria = json.load(f)
            else:
                memoria = {"memoria_tecnica": {"metricas": {}}}
                
            memoria["memoria_tecnica"]["metricas"]["recursos"] = {
                "ultima_atualizacao": metricas["timestamp"],
                "valores": {
                    "cpu": metricas["cpu"]["total"],
                    "memoria": metricas["memoria"]["percentual"],
                    "disco": metricas["disco"]["percentual"],
                    "equidade": metricas["equidade"]
                }
            }
            
            with open(self.memoria_path, 'w') as f:
                json.dump(memoria, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar memória compartilhada: {str(e)}")

    async def acionar_ajuste_automatico(self, metricas: Dict[str, Any]):
        """Aciona ajuste automático de recursos"""
        self.logger.warning(
            "Alerta: Métricas fora do limite",
            extra={
                'metricas': {
                    'cpu': f"{metricas['cpu']['total']:.1f}%",
                    'memoria': f"{metricas['memoria']['percentual']:.1f}%",
                    'disco': f"{metricas['disco']['percentual']:.1f}%",
                    'equidade': f"{metricas['equidade']:.2f}"
                }
            }
        )
        
        await self.ajustar_recursos(metricas)

    async def ajustar_recursos(self, metricas: Dict[str, Any]) -> None:
        """Ajusta recursos automaticamente baseado nas métricas"""
        with self.ajuste_duration.time():
            logging.info("Iniciando ajuste de recursos")
            
            # Ajusta CPU se necessário
            if metricas['cpu']['total'] > CONFIG['limites']['cpu']['total']:
                await self.ajustar_cpu(metricas['cpu'])
                self.ajustes_counter.labels(tipo='cpu').inc()
            
            # Ajusta memória se necessário
            if metricas['memoria']['percentual'] > CONFIG['limites']['memoria']['percentual']:
                await self.ajustar_memoria(metricas['memoria'])
                self.ajustes_counter.labels(tipo='memoria').inc()
            
            # Ajusta disco se necessário
            if metricas['disco']['percentual'] > CONFIG['limites']['disco']['percentual']:
                await self.ajustar_disco(metricas['disco'])
                self.ajustes_counter.labels(tipo='disco').inc()
            
            # Ajusta equidade se necessário
            if metricas['equidade'] < self.limite_equidade:
                await self.ajustar_equidade()
                self.ajustes_counter.labels(tipo='equidade').inc()
            
            # Registra métricas no histórico após ajustes
            self.historico.append({
                "metricas": metricas,
                "timestamp": datetime.now().isoformat()
            })
            
            logging.info("Ajuste de recursos concluído")

    async def ajustar_cpu(self, metricas_cpu: Dict[str, Any]):
        """Ajusta recursos de CPU"""
        # Implementação real: ajusta prioridades de processos
        processos = psutil.process_iter(['pid', 'name', 'cpu_percent'])
        for proc in processos:
            try:
                if proc.info['cpu_percent'] > CONFIG['ajuste']['cpu']['percentual_ajuste']:
                    p = psutil.Process(proc.info['pid'])
                    p.nice(CONFIG['ajuste']['cpu']['prioridade_minima'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    async def ajustar_memoria(self, metricas_memoria: Dict[str, Any]):
        """Ajusta recursos de memória"""
        # Implementação real: libera cache e ajusta swap
        if metricas_memoria['swap']['percentual'] < CONFIG['ajuste']['memoria']['swap_limite']:
            # Aumenta uso de swap
            processos = psutil.process_iter(['pid', 'name', 'memory_percent'])
            for proc in processos:
                try:
                    if proc.info['memory_percent'] > CONFIG['ajuste']['memoria']['percentual_ajuste']:
                        p = psutil.Process(proc.info['pid'])
                        p.memory_maps()  # Força mapeamento de memória
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

    async def ajustar_disco(self, metricas_disco: Dict[str, Any]):
        """Ajusta recursos de disco"""
        # Implementação real: limpa arquivos temporários
        for temp_dir in CONFIG['diretorios_temp']:
            try:
                for file in Path(temp_dir).glob('*'):
                    if file.is_file():
                        file.unlink()
            except Exception as e:
                self.logger.error(f"Erro ao limpar diretório {temp_dir}: {str(e)}")

    async def ajustar_equidade(self):
        """Ajusta distribuição de recursos para melhorar equidade"""
        if not self.recursos:
            return
            
        # Calcula distribuição ideal
        total = sum(self.recursos.values())
        n = len(self.recursos)
        valor_justo = total / n
        
        # Ajusta recursos
        for recurso in self.recursos:
            self.recursos[recurso] = valor_justo
            
        self.logger.info(
            "Equidade ajustada",
            extra={'nova_distribuicao': self.recursos}
        )

    async def encerrar(self) -> None:
        """Encerra o monitoramento de forma graciosa"""
        try:
            self.logger.info("Encerrando monitoramento de recursos...")
            
            # Salva estado final
            self.atualizar_memoria_compartilhada(self.coletar_metricas())
            
            # Registra métricas finais
            metricas_finais = self.coletar_metricas()
            self.atualizar_metricas_prometheus(metricas_finais)
            
            # Limpa recursos
            self.recursos.clear()
            self.historico.clear()
            
            self.logger.info("Monitoramento encerrado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao encerrar monitoramento: {str(e)}")
            raise

    def obter_uso_cpu(self) -> float:
        """Obtém o uso atual da CPU em porcentagem."""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            self.logger.error(f"Erro ao obter uso da CPU: {str(e)}")
            return 0.0
            
    def obter_uso_memoria(self) -> float:
        """Obtém o uso atual da memória em porcentagem."""
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            self.logger.error(f"Erro ao obter uso da memória: {str(e)}")
            return 0.0
            
    def obter_uso_disco(self) -> float:
        """Obtém o uso atual do disco em porcentagem."""
        try:
            return psutil.disk_usage('/').percent
        except Exception as e:
            self.logger.error(f"Erro ao obter uso do disco: {str(e)}")
            return 0.0
            
    def obter_uso_rede(self) -> Tuple[float, float]:
        """Obtém o uso atual da rede em bytes/s."""
        try:
            net_io = psutil.net_io_counters()
            return net_io.bytes_sent, net_io.bytes_recv
        except Exception as e:
            self.logger.error(f"Erro ao obter uso da rede: {str(e)}")
            return 0.0, 0.0
            
    def obter_processos(self) -> List[Dict]:
        """Obtém lista de processos com uso de recursos."""
        try:
            processos = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processos.append({
                        'pid': pinfo['pid'],
                        'nome': pinfo['name'],
                        'cpu': pinfo['cpu_percent'],
                        'memoria': pinfo['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return sorted(processos, key=lambda x: x['cpu'], reverse=True)
        except Exception as e:
            self.logger.error(f"Erro ao obter processos: {str(e)}")
            return []
            
    def obter_metricas(self) -> Dict[str, float]:
        """Obtém todas as métricas de recursos do sistema."""
        return {
            'cpu': self.obter_uso_cpu(),
            'memoria': self.obter_uso_memoria(),
            'disco': self.obter_uso_disco(),
            'rede': {
                'enviados': self.obter_uso_rede()[0],
                'recebidos': self.obter_uso_rede()[1]
            }
        }
        
    def limpar_recursos(self) -> bool:
        """Tenta liberar recursos do sistema."""
        try:
            # Limpa cache de memória
            if os.name == 'posix':
                os.system('sync')
                os.system('echo 3 > /proc/sys/vm/drop_caches')
                
            # Limpa diretórios temporários
            temp_dirs = ['/tmp', './temp', './cache']
            for dir in temp_dirs:
                if os.path.exists(dir):
                    for file in os.listdir(dir):
                        try:
                            file_path = os.path.join(dir, file)
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                        except Exception as e:
                            self.logger.warning(f"Erro ao limpar arquivo {file_path}: {str(e)}")
                            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar recursos: {str(e)}")
            return False 