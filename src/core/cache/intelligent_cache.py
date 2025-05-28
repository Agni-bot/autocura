"""
Sistema de Cache Inteligente com Predição ML
Otimiza o uso de cache baseado em padrões de acesso
"""

import json
import redis
import hashlib
from typing import Any, Dict, Callable, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression
import pickle
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

class AccessPredictor:
    """Preditor de padrões de acesso usando ML"""
    
    def __init__(self):
        self.access_history = defaultdict(list)
        self.model = LinearRegression()
        self.is_trained = False
        self.min_history = 10
        
    def record_access(self, key: str, timestamp: float):
        """Registra um acesso ao cache"""
        self.access_history[key].append(timestamp)
        
        # Limita histórico para economizar memória
        if len(self.access_history[key]) > 1000:
            self.access_history[key] = self.access_history[key][-500:]
    
    def predict(self, key: str, context: Dict = None) -> float:
        """Prediz a probabilidade de acesso futuro (0-1)"""
        history = self.access_history.get(key, [])
        
        if len(history) < self.min_history:
            # Sem histórico suficiente, usa heurística
            return self._heuristic_prediction(key, context)
        
        # Extrai features do histórico
        features = self._extract_features(history)
        
        # Se modelo não está treinado, treina agora
        if not self.is_trained:
            self._train_model()
        
        try:
            # Predição usando modelo
            prediction = self.model.predict([features])[0]
            return max(0, min(1, prediction))  # Clamp entre 0 e 1
        except Exception as e:
            logger.warning(f"Erro na predição ML: {e}")
            return self._heuristic_prediction(key, context)
    
    def _extract_features(self, history: list) -> list:
        """Extrai features estatísticas do histórico"""
        if not history:
            return [0] * 6
        
        # Converte para array numpy
        timestamps = np.array(history)
        current_time = datetime.now().timestamp()
        
        # Features
        features = [
            len(history),  # Número total de acessos
            current_time - timestamps[-1] if len(timestamps) > 0 else 0,  # Tempo desde último acesso
            np.mean(np.diff(timestamps)) if len(timestamps) > 1 else 0,  # Intervalo médio entre acessos
            np.std(np.diff(timestamps)) if len(timestamps) > 1 else 0,  # Desvio padrão dos intervalos
            self._calculate_trend(timestamps),  # Tendência de acesso
            self._calculate_periodicity(timestamps)  # Periodicidade
        ]
        
        return features
    
    def _calculate_trend(self, timestamps: np.ndarray) -> float:
        """Calcula tendência de acesso (crescente/decrescente)"""
        if len(timestamps) < 2:
            return 0
        
        # Regressão linear simples
        x = np.arange(len(timestamps)).reshape(-1, 1)
        y = timestamps.reshape(-1, 1)
        
        try:
            reg = LinearRegression().fit(x, y)
            return reg.coef_[0][0]
        except:
            return 0
    
    def _calculate_periodicity(self, timestamps: np.ndarray) -> float:
        """Calcula score de periodicidade dos acessos"""
        if len(timestamps) < 3:
            return 0
        
        intervals = np.diff(timestamps)
        if len(intervals) < 2:
            return 0
        
        # Calcula autocorrelação
        mean = np.mean(intervals)
        var = np.var(intervals)
        
        if var == 0:
            return 1.0  # Perfeitamente periódico
        
        # Autocorrelação normalizada
        autocorr = np.correlate(intervals - mean, intervals - mean, mode='valid')[0]
        return autocorr / (var * len(intervals))
    
    def _heuristic_prediction(self, key: str, context: Dict = None) -> float:
        """Predição heurística quando não há dados suficientes"""
        score = 0.5  # Base score
        
        # Ajusta baseado no contexto
        if context:
            # Prioriza dados críticos
            if context.get('critical', False):
                score += 0.3
            
            # Considera tipo de dado
            data_type = context.get('type', '')
            if data_type in ['user_session', 'api_response']:
                score += 0.2
            elif data_type in ['static_config', 'reference_data']:
                score += 0.1
            
            # Considera fonte da requisição
            if context.get('source') == 'api':
                score += 0.1
        
        return min(1.0, score)
    
    def _train_model(self):
        """Treina o modelo com dados históricos"""
        X = []
        y = []
        
        # Prepara dados de treino
        for key, history in self.access_history.items():
            if len(history) >= self.min_history:
                features = self._extract_features(history[:-1])
                # Target: se houve acesso próximo
                target = 1 if len(history) > 1 and (history[-1] - history[-2]) < 300 else 0
                
                X.append(features)
                y.append(target)
        
        if len(X) >= 10:
            try:
                self.model.fit(X, y)
                self.is_trained = True
                logger.info("Modelo de predição de cache treinado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao treinar modelo: {e}")


class IntelligentCacheManager:
    """Gerenciador de Cache Inteligente com Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.predictor = AccessPredictor()
        self.usage_patterns = defaultdict(dict)
        self.performance_metrics = {
            'hits': 0,
            'misses': 0,
            'predictions_correct': 0,
            'predictions_total': 0
        }
        
    def _generate_key(self, key: str, namespace: str = "autocura") -> str:
        """Gera chave única para o cache"""
        return f"{namespace}:{key}"
    
    async def smart_cache(self, key: str, data: Any, context: Dict = None):
        """Armazena dados com TTL inteligente baseado em predição"""
        # Registra acesso
        self.predictor.record_access(key, datetime.now().timestamp())
        
        # Prediz probabilidade de acesso futuro
        access_score = self.predictor.predict(key, context)
        
        # Define TTL baseado na predição
        ttl = self._calculate_ttl(access_score, context)
        
        # Serializa dados
        serialized_data = json.dumps(data)
        
        # Armazena no Redis com TTL
        cache_key = self._generate_key(key)
        self.redis_client.setex(cache_key, ttl, serialized_data)
        
        # Atualiza padrões de uso
        self._update_usage_patterns(key, access_score, ttl)
        
        logger.debug(f"Cache armazenado: {key} (score: {access_score:.2f}, TTL: {ttl}s)")
    
    def _calculate_ttl(self, access_score: float, context: Dict = None) -> int:
        """Calcula TTL baseado no score de acesso e contexto"""
        # TTL base em segundos
        base_ttl = {
            0.9: 7200,   # 2 horas para dados muito acessados
            0.8: 3600,   # 1 hora
            0.7: 1800,   # 30 minutos
            0.6: 900,    # 15 minutos
            0.5: 600,    # 10 minutos
            0.4: 300,    # 5 minutos
            0.0: 180     # 3 minutos para dados pouco acessados
        }
        
        # Encontra TTL apropriado
        ttl = base_ttl[0.0]
        for threshold, value in sorted(base_ttl.items(), reverse=True):
            if access_score >= threshold:
                ttl = value
                break
        
        # Ajusta baseado no contexto
        if context:
            # Dados críticos têm TTL maior
            if context.get('critical', False):
                ttl = int(ttl * 1.5)
            
            # Dados voláteis têm TTL menor
            if context.get('volatile', False):
                ttl = int(ttl * 0.5)
            
            # TTL customizado
            if 'ttl' in context:
                ttl = context['ttl']
        
        return max(60, min(86400, ttl))  # Entre 1 minuto e 24 horas
    
    async def get_with_fallback(self, key: str, fallback_fn: Callable, context: Dict = None) -> Any:
        """Obtém do cache com fallback para função original"""
        cache_key = self._generate_key(key)
        
        # Tenta obter do cache
        cached = self.redis_client.get(cache_key)
        
        if cached:
            # Hit no cache
            self.performance_metrics['hits'] += 1
            self.predictor.record_access(key, datetime.now().timestamp())
            
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                logger.error(f"Erro ao decodificar cache para {key}")
                # Remove entrada corrompida
                self.redis_client.delete(cache_key)
        
        # Miss no cache
        self.performance_metrics['misses'] += 1
        
        # Executa função fallback
        if asyncio.iscoroutinefunction(fallback_fn):
            data = await fallback_fn()
        else:
            data = fallback_fn()
        
        # Armazena resultado no cache
        await self.smart_cache(key, data, context)
        
        return data
    
    def _update_usage_patterns(self, key: str, access_score: float, ttl: int):
        """Atualiza padrões de uso para análise"""
        pattern = self.usage_patterns[key]
        
        pattern['last_access'] = datetime.now().isoformat()
        pattern['access_score'] = access_score
        pattern['ttl'] = ttl
        pattern['access_count'] = pattern.get('access_count', 0) + 1
        
        # Calcula média móvel do score
        if 'avg_score' not in pattern:
            pattern['avg_score'] = access_score
        else:
            pattern['avg_score'] = (pattern['avg_score'] * 0.9 + access_score * 0.1)
    
    async def get_performance_metrics(self) -> Dict:
        """Retorna métricas de performance do cache"""
        total_requests = self.performance_metrics['hits'] + self.performance_metrics['misses']
        hit_rate = self.performance_metrics['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'hit_rate': hit_rate,
            'total_hits': self.performance_metrics['hits'],
            'total_misses': self.performance_metrics['misses'],
            'total_requests': total_requests,
            'prediction_accuracy': (
                self.performance_metrics['predictions_correct'] / 
                self.performance_metrics['predictions_total']
            ) if self.performance_metrics['predictions_total'] > 0 else 0,
            'active_keys': len(self.usage_patterns),
            'model_trained': self.predictor.is_trained
        }
    
    async def optimize_cache(self):
        """Otimiza o cache removendo entradas não utilizadas"""
        current_time = datetime.now()
        keys_to_remove = []
        
        for key, pattern in self.usage_patterns.items():
            # Remove padrões não acessados há mais de 1 hora
            last_access = datetime.fromisoformat(pattern['last_access'])
            if (current_time - last_access) > timedelta(hours=1):
                keys_to_remove.append(key)
        
        # Remove chaves
        for key in keys_to_remove:
            cache_key = self._generate_key(key)
            self.redis_client.delete(cache_key)
            del self.usage_patterns[key]
        
        logger.info(f"Cache otimizado: {len(keys_to_remove)} chaves removidas")
        
        return len(keys_to_remove)
    
    def save_model(self, filepath: str = "cache_predictor.pkl"):
        """Salva o modelo de predição"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.predictor, f)
        logger.info(f"Modelo de predição salvo em {filepath}")
    
    def load_model(self, filepath: str = "cache_predictor.pkl"):
        """Carrega o modelo de predição"""
        try:
            with open(filepath, 'rb') as f:
                self.predictor = pickle.load(f)
            logger.info(f"Modelo de predição carregado de {filepath}")
        except FileNotFoundError:
            logger.warning(f"Arquivo de modelo não encontrado: {filepath}")


# Singleton global do cache
_cache_instance = None

def get_cache_manager() -> IntelligentCacheManager:
    """Retorna instância singleton do cache manager"""
    global _cache_instance
    if _cache_instance is None:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
        _cache_instance = IntelligentCacheManager(redis_url)
    return _cache_instance 