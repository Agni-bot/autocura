"""
Módulo de Configuração da Consciência Situacional.
Responsável por gerenciar as configurações do sistema.
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import threading

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ConscienciaSituacional.Config")

class Configurador:
    """Classe responsável por gerenciar configurações."""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o configurador.
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config_path = config_path or os.getenv('CONFIG_PATH', 'config.yaml')
        self.config = {}
        self.lock = threading.Lock()
        self._carregar_config()
    
    def _carregar_config(self):
        """Carrega configurações do arquivo."""
        try:
            path = Path(self.config_path)
            if not path.exists():
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_path}")
                return
            
            with open(path, 'r') as f:
                if path.suffix == '.yaml':
                    self.config = yaml.safe_load(f)
                elif path.suffix == '.json':
                    self.config = json.load(f)
                else:
                    logger.error(f"Formato de arquivo não suportado: {path.suffix}")
        except Exception as e:
            logger.error(f"Erro ao carregar configurações: {str(e)}")
    
    def obter_config(self, chave: str, padrao: Any = None) -> Any:
        """
        Obtém valor de configuração.
        
        Args:
            chave: Chave da configuração
            padrao: Valor padrão se não encontrado
            
        Returns:
            any: Valor da configuração
        """
        with self.lock:
            return self.config.get(chave, padrao)
    
    def definir_config(self, chave: str, valor: Any):
        """
        Define valor de configuração.
        
        Args:
            chave: Chave da configuração
            valor: Valor a ser definido
        """
        with self.lock:
            self.config[chave] = valor
    
    def salvar_config(self):
        """Salva configurações no arquivo."""
        try:
            path = Path(self.config_path)
            with open(path, 'w') as f:
                if path.suffix == '.yaml':
                    yaml.dump(self.config, f)
                elif path.suffix == '.json':
                    json.dump(self.config, f, indent=2)
                else:
                    logger.error(f"Formato de arquivo não suportado: {path.suffix}")
        except Exception as e:
            logger.error(f"Erro ao salvar configurações: {str(e)}")
    
    def obter_config_servico(self, servico: str) -> Dict[str, Any]:
        """
        Obtém configurações de um serviço.
        
        Args:
            servico: Nome do serviço
            
        Returns:
            dict: Configurações do serviço
        """
        return self.obter_config(f'servicos.{servico}', {})
    
    def obter_config_monitoramento(self) -> Dict[str, Any]:
        """
        Obtém configurações de monitoramento.
        
        Returns:
            dict: Configurações de monitoramento
        """
        return self.obter_config('monitoramento', {})
    
    def obter_config_observabilidade(self) -> Dict[str, Any]:
        """
        Obtém configurações de observabilidade.
        
        Returns:
            dict: Configurações de observabilidade
        """
        return self.obter_config('observabilidade', {})
    
    def obter_config_diagnostico(self) -> Dict[str, Any]:
        """
        Obtém configurações de diagnóstico.
        
        Returns:
            dict: Configurações de diagnóstico
        """
        return self.obter_config('diagnostico', {})
    
    def obter_config_autocorrecao(self) -> Dict[str, Any]:
        """
        Obtém configurações de autocorreção.
        
        Returns:
            dict: Configurações de autocorreção
        """
        return self.obter_config('autocorrecao', {})
    
    def obter_config_orquestracao(self) -> Dict[str, Any]:
        """
        Obtém configurações de orquestração.
        
        Returns:
            dict: Configurações de orquestração
        """
        return self.obter_config('orquestracao', {})
    
    def obter_config_prometheus(self) -> Dict[str, Any]:
        """
        Obtém configurações do Prometheus.
        
        Returns:
            dict: Configurações do Prometheus
        """
        return self.obter_config('prometheus', {})
    
    def obter_config_grafana(self) -> Dict[str, Any]:
        """
        Obtém configurações do Grafana.
        
        Returns:
            dict: Configurações do Grafana
        """
        return self.obter_config('grafana', {})

# Configurações padrão
CONFIG_PADRAO = {
    'servicos': {
        'monitoramento': {
            'url': 'http://monitoramento:8080',
            'timeout': 5
        },
        'observabilidade': {
            'url': 'http://observabilidade:8080',
            'timeout': 5
        },
        'diagnostico': {
            'url': 'http://diagnostico:8080',
            'timeout': 5
        },
        'autocorrecao': {
            'url': 'http://autocorrecao:8080',
            'timeout': 5
        },
        'orquestracao': {
            'url': 'http://orquestracao:8080',
            'timeout': 5
        }
    },
    'monitoramento': {
        'intervalo_coleta': 5,
        'retencao_historico': 3600
    },
    'observabilidade': {
        'nivel_log': 'INFO',
        'retencao_logs': 86400
    },
    'diagnostico': {
        'limiar_alerta': 0.8,
        'intervalo_analise': 10
    },
    'autocorrecao': {
        'max_tentativas': 3,
        'intervalo_retry': 5
    },
    'orquestracao': {
        'max_replicas': 10,
        'min_replicas': 1
    },
    'prometheus': {
        'url': 'http://prometheus:9090',
        'timeout': 5
    },
    'grafana': {
        'url': 'http://grafana:3000',
        'timeout': 5
    }
}

# Instância global do configurador
configurador = Configurador() 