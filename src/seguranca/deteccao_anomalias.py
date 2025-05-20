from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MetricasSeguranca:
    cpu_usage: float
    memoria_usage: float
    latencia: float
    requests_por_segundo: float
    erro_rate: float
    auth_failures: int
    timestamp: datetime

class DetectorAnomalias:
    def __init__(self,
                 contamination: float = 0.1,
                 window_size: int = 100,
                 threshold_score: float = -0.5):
        """
        Inicializa o detector de anomalias.
        
        Args:
            contamination: Proporção esperada de anomalias no dataset
            window_size: Tamanho da janela de análise
            threshold_score: Limite para considerar uma observação como anômala
        """
        self.contamination = contamination
        self.window_size = window_size
        self.threshold_score = threshold_score
        
        self.modelo = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        self.metricas_historico: List[MetricasSeguranca] = []
        self.anomalias_detectadas: List[Dict] = []
        
        logger.info("Detector de anomalias inicializado com sucesso")

    def _preparar_features(self, metricas: List[MetricasSeguranca]) -> np.ndarray:
        """
        Prepara as features para o modelo de detecção.
        
        Args:
            metricas: Lista de métricas de segurança
            
        Returns:
            np.ndarray: Array com as features normalizadas
        """
        features = []
        for m in metricas:
            features.append([
                m.cpu_usage,
                m.memoria_usage,
                m.latencia,
                m.requests_por_segundo,
                m.erro_rate,
                m.auth_failures
            ])
        return np.array(features)

    def registrar_metricas(self, metricas: MetricasSeguranca) -> None:
        """
        Registra novas métricas para análise.
        
        Args:
            metricas: Objeto contendo as métricas atuais
        """
        self.metricas_historico.append(metricas)
        # Mantém apenas as últimas window_size métricas
        if len(self.metricas_historico) > self.window_size:
            self.metricas_historico.pop(0)

    def treinar_modelo(self) -> None:
        """
        Treina o modelo de detecção de anomalias com os dados históricos.
        """
        if len(self.metricas_historico) < self.window_size:
            logger.warning("Dados insuficientes para treinar o modelo")
            return
            
        # Prepara features
        X = self._preparar_features(self.metricas_historico)
        
        # Normaliza os dados
        X_scaled = self.scaler.fit_transform(X)
        
        # Treina o modelo
        self.modelo.fit(X_scaled)
        logger.info("Modelo de detecção de anomalias treinado com sucesso")

    def detectar_anomalias(self) -> List[Dict]:
        """
        Detecta anomalias nas métricas mais recentes.
        
        Returns:
            List[Dict]: Lista de anomalias detectadas
        """
        if len(self.metricas_historico) < self.window_size:
            return []
            
        # Prepara features
        X = self._preparar_features(self.metricas_historico)
        
        # Normaliza os dados
        X_scaled = self.scaler.transform(X)
        
        # Obtém scores de anomalia
        scores = self.modelo.score_samples(X_scaled)
        
        # Identifica anomalias
        anomalias = []
        for i, score in enumerate(scores):
            if score < self.threshold_score:
                metrica = self.metricas_historico[i]
                anomalia = {
                    "timestamp": metrica.timestamp.isoformat(),
                    "score": float(score),
                    "metricas": {
                        "cpu_usage": metrica.cpu_usage,
                        "memoria_usage": metrica.memoria_usage,
                        "latencia": metrica.latencia,
                        "requests_por_segundo": metrica.requests_por_segundo,
                        "erro_rate": metrica.erro_rate,
                        "auth_failures": metrica.auth_failures
                    }
                }
                anomalias.append(anomalia)
                self.anomalias_detectadas.append(anomalia)
                
        return anomalias

    def obter_estatisticas(self) -> Dict:
        """
        Retorna estatísticas sobre as anomalias detectadas.
        
        Returns:
            Dict: Dicionário com estatísticas
        """
        if not self.anomalias_detectadas:
            return {
                "total_anomalias": 0,
                "ultima_anomalia": None,
                "metricas_mais_afetadas": {}
            }
            
        # Calcula estatísticas
        total_anomalias = len(self.anomalias_detectadas)
        ultima_anomalia = self.anomalias_detectadas[-1]
        
        # Identifica métricas mais afetadas
        metricas_afetadas = {
            "cpu_usage": 0,
            "memoria_usage": 0,
            "latencia": 0,
            "requests_por_segundo": 0,
            "erro_rate": 0,
            "auth_failures": 0
        }
        
        for anomalia in self.anomalias_detectadas:
            for metrica, valor in anomalia["metricas"].items():
                if valor > 0:
                    metricas_afetadas[metrica] += 1
                    
        return {
            "total_anomalias": total_anomalias,
            "ultima_anomalia": ultima_anomalia,
            "metricas_mais_afetadas": metricas_afetadas
        }

    def limpar_historico(self, dias: int = 7) -> None:
        """
        Limpa o histórico de anomalias mais antigo que o período especificado.
        
        Args:
            dias: Número de dias para manter no histórico
        """
        cutoff = datetime.now() - timedelta(days=dias)
        self.anomalias_detectadas = [
            a for a in self.anomalias_detectadas
            if datetime.fromisoformat(a["timestamp"]) > cutoff
        ]
        logger.info(f"Histórico de anomalias limpo, mantendo dados dos últimos {dias} dias") 