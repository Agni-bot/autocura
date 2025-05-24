from prometheus_client import Counter, Gauge, Histogram, Summary
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class EthicalAuditor:
    """Auditor ético do sistema AutoCura"""
    
    def __init__(self):
        self._init_prometheus_metrics()
        self.alertas_eticos = []
        
    def _init_prometheus_metrics(self) -> None:
        """Inicializa métricas Prometheus para auditoria ética"""
        
        # Contadores
        self.violacoes_counter = Counter(
            'autocura_violacoes_eticas_total',
            'Total de violações éticas detectadas',
            ['categoria', 'severidade']
        )
        
        self.alertas_counter = Counter(
            'autocura_alertas_eticos_total',
            'Total de alertas éticos gerados',
            ['tipo', 'status']
        )
        
        # Gauges
        self.indice_equidade = Gauge(
            'autocura_indice_equidade',
            'Índice de equidade do sistema',
            ['componente']
        )
        
        self.nivel_transparencia = Gauge(
            'autocura_nivel_transparencia',
            'Nível de transparência do sistema',
            ['aspecto']
        )
        
        self.indice_privacidade = Gauge(
            'autocura_indice_privacidade',
            'Índice de proteção à privacidade',
            ['tipo_dado']
        )
        
        # Histogramas
        self.tempo_resposta_etica = Histogram(
            'autocura_tempo_resposta_etica_seconds',
            'Tempo de resposta para questões éticas',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
            ['tipo_questao']
        )
        
        # Sumários
        self.tamanho_dados_sensiveis = Summary(
            'autocura_tamanho_dados_sensiveis_bytes',
            'Tamanho dos dados sensíveis processados',
            ['categoria']
        )
        
    def registrar_violacao(self, categoria: str, severidade: str, detalhes: Dict) -> None:
        """Registra uma violação ética detectada"""
        try:
            self.violacoes_counter.labels(categoria=categoria, severidade=severidade).inc()
            
            alerta = {
                "timestamp": datetime.now().isoformat(),
                "categoria": categoria,
                "severidade": severidade,
                "detalhes": detalhes
            }
            self.alertas_eticos.append(alerta)
            
            logger.warning(f"Violacao etica detectada: {categoria} - {severidade}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar violacao etica: {e}")
            
    def atualizar_indice_equidade(self, componente: str, valor: float) -> None:
        """Atualiza o índice de equidade para um componente"""
        try:
            self.indice_equidade.labels(componente=componente).set(valor)
            logger.info(f"Indice de equidade atualizado para {componente}: {valor}")
        except Exception as e:
            logger.error(f"Erro ao atualizar indice de equidade: {e}")
            
    def registrar_tempo_resposta(self, tipo_questao: str, tempo: float) -> None:
        """Registra o tempo de resposta para uma questão ética"""
        try:
            self.tempo_resposta_etica.labels(tipo_questao=tipo_questao).observe(tempo)
        except Exception as e:
            logger.error(f"Erro ao registrar tempo de resposta: {e}")
            
    def registrar_dados_sensiveis(self, categoria: str, tamanho: int) -> None:
        """Registra o tamanho dos dados sensíveis processados"""
        try:
            self.tamanho_dados_sensiveis.labels(categoria=categoria).observe(tamanho)
        except Exception as e:
            logger.error(f"Erro ao registrar dados sensiveis: {e}")
            
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas sobre a auditoria ética"""
        return {
            "total_violacoes": len(self.alertas_eticos),
            "ultima_violacao": self.alertas_eticos[-1] if self.alertas_eticos else None,
            "categorias_mais_frequentes": self._contar_categorias()
        }
        
    def _contar_categorias(self) -> Dict[str, int]:
        """Conta a frequência de cada categoria de violação"""
        contagem = {}
        for alerta in self.alertas_eticos:
            categoria = alerta["categoria"]
            contagem[categoria] = contagem.get(categoria, 0) + 1
        return contagem 