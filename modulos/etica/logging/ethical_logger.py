import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from prometheus_client import Counter, Gauge, Histogram

class EthicalLogger:
    def __init__(self):
        # Configuração do logger
        self.logger = logging.getLogger('ethical_logger')
        self.logger.setLevel(logging.INFO)
        
        # Handler para arquivo
        file_handler = logging.FileHandler('logs/ethical_audit.log')
        file_handler.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adiciona handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Métricas Prometheus
        self.violacoes_counter = Counter(
            'autocura_violacoes_eticas_total',
            'Total de violações éticas detectadas',
            ['categoria', 'severidade']
        )
        
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
            'Índice de privacidade do sistema',
            ['tipo_dado']
        )
        
        self.tempo_resposta = Histogram(
            'autocura_tempo_resposta_etica_seconds',
            'Tempo de resposta para questões éticas',
            ['tipo_questao']
        )
        
        self.dados_sensiveis = Histogram(
            'autocura_tamanho_dados_sensiveis_bytes',
            'Tamanho dos dados sensíveis processados',
            ['categoria']
        )

    def registrar_violacao(self, categoria: str, severidade: str, detalhes: Dict[str, Any]):
        """Registra uma violação ética detectada"""
        self.violacoes_counter.labels(categoria=categoria, severidade=severidade).inc()
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'tipo': 'violacao_etica',
            'categoria': categoria,
            'severidade': severidade,
            'detalhes': detalhes
        }
        
        self.logger.warning(f"Violacao Etica Detectada: {json.dumps(log_data)}")

    def atualizar_indice_equidade(self, componente: str, valor: float):
        """Atualiza o índice de equidade para um componente"""
        self.indice_equidade.labels(componente=componente).set(valor)
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'tipo': 'indice_equidade',
            'componente': componente,
            'valor': valor
        }
        
        self.logger.info(f"Indice de Equidade Atualizado: {json.dumps(log_data)}")

    def atualizar_transparencia(self, aspecto: str, valor: float):
        """Atualiza o nível de transparência para um aspecto"""
        self.nivel_transparencia.labels(aspecto=aspecto).set(valor)
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'tipo': 'nivel_transparencia',
            'aspecto': aspecto,
            'valor': valor
        }
        
        self.logger.info(f"Nivel de Transparencia Atualizado: {json.dumps(log_data)}")

    def atualizar_privacidade(self, tipo_dado: str, valor: float):
        """Atualiza o índice de privacidade para um tipo de dado"""
        self.indice_privacidade.labels(tipo_dado=tipo_dado).set(valor)
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'tipo': 'indice_privacidade',
            'tipo_dado': tipo_dado,
            'valor': valor
        }
        
        self.logger.info(f"Indice de Privacidade Atualizado: {json.dumps(log_data)}")

    def registrar_tempo_resposta(self, tipo_questao: str, tempo_segundos: float):
        """Registra o tempo de resposta para uma questão ética"""
        self.tempo_resposta.labels(tipo_questao=tipo_questao).observe(tempo_segundos)
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'tipo': 'tempo_resposta',
            'tipo_questao': tipo_questao,
            'tempo_segundos': tempo_segundos
        }
        
        self.logger.info(f"Tempo de Resposta Registrado: {json.dumps(log_data)}")

    def registrar_dados_sensiveis(self, categoria: str, tamanho_bytes: int):
        """Registra o processamento de dados sensíveis"""
        self.dados_sensiveis.labels(categoria=categoria).observe(tamanho_bytes)
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'tipo': 'dados_sensiveis',
            'categoria': categoria,
            'tamanho_bytes': tamanho_bytes
        }
        
        self.logger.info(f"Dados Sensiveis Processados: {json.dumps(log_data)}")

    def registrar_evento_etico(self, tipo: str, dados: Dict[str, Any], nivel: str = 'INFO'):
        """Registra um evento ético genérico"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'tipo': tipo,
            **dados
        }
        
        log_message = f"Evento Etico: {json.dumps(log_data)}"
        
        if nivel == 'WARNING':
            self.logger.warning(log_message)
        elif nivel == 'ERROR':
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)

    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre os logs éticos"""
        return {
            'total_violacoes': self.violacoes_counter._value.get(),
            'indices_equidade': {
                label: self.indice_equidade.labels(**label)._value.get()
                for label in self.indice_equidade._metrics
            },
            'niveis_transparencia': {
                label: self.nivel_transparencia.labels(**label)._value.get()
                for label in self.nivel_transparencia._metrics
            },
            'indices_privacidade': {
                label: self.indice_privacidade.labels(**label)._value.get()
                for label in self.indice_privacidade._metrics
            }
        } 