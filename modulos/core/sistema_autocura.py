from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
import statistics
import math

class SistemaAutocura:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metricas = {}
        self.historico = []
        self.recursos = {}
        
    async def monitorar_recursos(self):
        """Monitora recursos do sistema em tempo real"""
        while True:
            try:
                metricas = await self.coletar_metricas()
                self.metricas = metricas
                self.historico.append({
                    'timestamp': datetime.now(),
                    'metricas': metricas
                })
                
                if len(self.historico) > 1000:  # Mantém histórico limitado
                    self.historico.pop(0)
                    
                await self.verificar_limites()
                await asyncio.sleep(30)  # Intervalo de monitoramento
                
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {str(e)}")
                await asyncio.sleep(5)
                
    async def coletar_metricas(self) -> Dict:
        """Coleta métricas do sistema"""
        return {
            'cpu': self._obter_uso_cpu(),
            'memoria': self._obter_uso_memoria(),
            'equidade': self._calcular_equidade()
        }
        
    def _obter_uso_cpu(self) -> float:
        """Obtém uso de CPU"""
        import psutil
        return psutil.cpu_percent()
        
    def _obter_uso_memoria(self) -> float:
        """Obtém uso de memória"""
        import psutil
        return psutil.virtual_memory().percent
        
    def _calcular_equidade(self) -> float:
        """Calcula índice de equidade na distribuição de recursos"""
        if not self.recursos:
            return 1.0
        distribuicao = self.obter_distribuicao_recursos()
        if not distribuicao:
            return 1.0
        valores = list(distribuicao.values())
        if all(math.isclose(v, valores[0], rel_tol=1e-9) for v in valores):
            return 1.0
        media = statistics.mean(valores)
        if media == 0:
            return 1.0
        desvio = statistics.stdev(valores)
        equidade = 1.0 - (desvio / media)
        return max(0.0, min(1.0, equidade))
            
    def obter_distribuicao_recursos(self) -> Dict[str, float]:
        """Obtém distribuição atual de recursos"""
        return self.recursos.copy()
        
    async def verificar_limites(self):
        """Verifica se métricas estão dentro dos limites"""
        # Atualiza métricas antes de verificar
        self.metricas = await self.coletar_metricas()
        if self.metricas.get('equidade', 1.0) < 0.85:
            await self.ajustar_recursos()
        else:
            # Mesmo que não haja ajuste, registra métricas para rastreabilidade
            self.historico.append({
                'timestamp': datetime.now(),
                'metricas': {
                    'cpu': self._obter_uso_cpu(),
                    'memoria': self._obter_uso_memoria(),
                    'equidade': self._calcular_equidade()
                }
            })
            
    async def ajustar_recursos(self):
        """Ajusta recursos para melhorar equidade"""
        self.logger.info("Iniciando ajuste de recursos")
        if self.recursos:
            total = sum(self.recursos.values())
            n = len(self.recursos)
            if n > 0:
                valor_justo = float(total) / n
                for k in self.recursos:
                    self.recursos[k] = float(valor_justo)
        # Debug: print valores após ajuste
        valores = list(self.recursos.values())
        media = statistics.mean(valores) if valores else 0
        desvio = statistics.stdev(valores) if len(valores) > 1 else 0
        equidade = self._calcular_equidade()
        print(f"[DEBUG] valores={valores}, media={media}, desvio={desvio}, equidade={equidade}")
        # Após ajuste, registra métricas no histórico
        self.historico.append({
            'timestamp': datetime.now(),
            'metricas': {
                'cpu': self._obter_uso_cpu(),
                'memoria': self._obter_uso_memoria(),
                'equidade': equidade
            }
        })
        await asyncio.sleep(1)  # Simula tempo de ajuste
        self.logger.info("Ajuste de recursos concluído")

    def processar_dados(self, dados: dict, max_retries: int = 1) -> dict:
        """
        Processa dados recebidos simulando sucesso e suporte a retries.
        Args:
            dados (dict): Dados de entrada
            max_retries (int): Número máximo de tentativas em caso de falha
        Returns:
            dict: Resultado do processamento
        """
        tentativas = 0
        while tentativas < max_retries:
            try:
                # Simula processamento (poderia incluir lógica real)
                return {
                    'status': 'success',
                    'id': dados.get('id'),
                    'processado_em': datetime.now().isoformat()
                }
            except Exception:
                tentativas += 1
        return {'status': 'error', 'id': dados.get('id'), 'processado_em': None} 