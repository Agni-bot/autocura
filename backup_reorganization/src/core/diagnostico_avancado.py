import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
import threading
import time
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from ..memoria.gerenciador_memoria import GerenciadorMemoria
from ..core.logger import Logger
from ..core.cache import Cache

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("diagnostico_avancado")

class DiagnosticoAvancado:
    """Sistema de diagnóstico avançado com análise preditiva e correlação de eventos"""
    
    def __init__(self, gerenciador_memoria: GerenciadorMemoria, logger: Logger, cache: Cache):
        self.gerenciador_memoria = gerenciador_memoria
        self.logger = logger
        self.cache = cache
        self.config = self._carregar_config()
        self.modelo_anomalia = None
        self.scaler = StandardScaler()
        self.lock = threading.Lock()
        self.thread_analise = None
        self.running = False
        self.logger.registrar_evento("diagnostico_avancado", "INFO", "Sistema de Diagnóstico Avançado inicializado")
    
    def _carregar_config(self) -> Dict[str, Any]:
        """Carrega a configuração do diagnóstico avançado"""
        try:
            caminho_config = Path("config/diagnostico_avancado.json")
            if caminho_config.exists():
                with open(caminho_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.registrar_evento("diagnostico_avancado", "WARNING", "Arquivo de configuração não encontrado. Usando configuração padrão.")
                return self._criar_config_padrao()
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao carregar configuração", e)
            return self._criar_config_padrao()
    
    def _criar_config_padrao(self) -> Dict[str, Any]:
        """Cria configuração padrão do diagnóstico avançado"""
        return {
            "configuracoes": {
                "intervalo_analise": 300,
                "janela_historico": 86400,
                "min_amostras": 100,
                "threshold_anomalia": 0.95
            },
            "metricas": {
                "cpu": ["percent", "load"],
                "memoria": ["percent", "used"],
                "disco": ["percent", "io"],
                "rede": ["bytes", "packets"],
                "aplicacao": ["latencia", "erros", "requisicoes"]
            },
            "correlacao": {
                "min_correlacao": 0.7,
                "max_lag": 300,
                "janela_analise": 3600
            },
            "predicao": {
                "horizonte": 3600,
                "intervalo_predicao": 300,
                "min_confianca": 0.8
            }
        }
    
    def iniciar(self) -> None:
        """Inicia o sistema de diagnóstico avançado"""
        try:
            if self.running:
                self.logger.registrar_evento("diagnostico_avancado", "WARNING", "Sistema já está em execução")
                return
            
            self.running = True
            self.thread_analise = threading.Thread(target=self._executar_analise)
            self.thread_analise.start()
            
            self.logger.registrar_evento("diagnostico_avancado", "INFO", "Sistema iniciado com sucesso")
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao iniciar sistema", e)
            self.running = False
    
    def parar(self) -> None:
        """Para o sistema de diagnóstico avançado"""
        try:
            if not self.running:
                self.logger.registrar_evento("diagnostico_avancado", "WARNING", "Sistema não está em execução")
                return
            
            self.running = False
            if self.thread_analise:
                self.thread_analise.join()
            
            self.logger.registrar_evento("diagnostico_avancado", "INFO", "Sistema parado com sucesso")
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao parar sistema", e)
    
    def _executar_analise(self) -> None:
        """Executa o processo de análise"""
        try:
            while self.running:
                # Coleta dados históricos
                dados_historicos = self._coletar_dados_historicos()
                
                if len(dados_historicos) >= self.config["configuracoes"]["min_amostras"]:
                    # Treina modelo de anomalia
                    self._treinar_modelo_anomalia(dados_historicos)
                    
                    # Analisa correlações
                    correlacoes = self._analisar_correlacoes(dados_historicos)
                    
                    # Realiza predições
                    predicoes = self._realizar_predicoes(dados_historicos)
                    
                    # Registra resultados
                    self._registrar_resultados(correlacoes, predicoes)
                
                # Aguarda próximo ciclo
                time.sleep(self.config["configuracoes"]["intervalo_analise"])
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro no processo de análise", e)
            self.running = False
    
    def _coletar_dados_historicos(self) -> List[Dict[str, Any]]:
        """Coleta dados históricos para análise"""
        try:
            # Calcula período
            fim = datetime.now()
            inicio = fim - timedelta(seconds=self.config["configuracoes"]["janela_historico"])
            
            # Obtém métricas do cache
            metricas = self.cache.obter("metricas", "historico") or []
            
            # Filtra por período
            dados = [
                m for m in metricas
                if inicio <= datetime.fromisoformat(m["timestamp"]) <= fim
            ]
            
            return dados
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao coletar dados históricos", e)
            return []
    
    def _treinar_modelo_anomalia(self, dados: List[Dict[str, Any]]) -> None:
        """Treina modelo de detecção de anomalias"""
        try:
            # Prepara dados
            features = self._extrair_features(dados)
            
            if len(features) >= self.config["configuracoes"]["min_amostras"]:
                # Normaliza dados
                features_scaled = self.scaler.fit_transform(features)
                
                # Treina modelo
                self.modelo_anomalia = IsolationForest(
                    contamination=0.1,
                    random_state=42
                )
                self.modelo_anomalia.fit(features_scaled)
                
                self.logger.registrar_evento("diagnostico_avancado", "INFO", "Modelo de anomalia treinado com sucesso")
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao treinar modelo de anomalia", e)
    
    def _extrair_features(self, dados: List[Dict[str, Any]]) -> np.ndarray:
        """Extrai features dos dados para análise"""
        try:
            features = []
            
            for dado in dados:
                feature = []
                
                # CPU
                if "cpu" in dado["sistema"]:
                    feature.extend([
                        dado["sistema"]["cpu"]["percent"],
                        dado["sistema"]["cpu"]["load"]
                    ])
                
                # Memória
                if "memoria" in dado["sistema"]:
                    feature.extend([
                        dado["sistema"]["memoria"]["percent"],
                        dado["sistema"]["memoria"]["used"]
                    ])
                
                # Disco
                if "disco" in dado["sistema"]:
                    feature.extend([
                        dado["sistema"]["disco"]["percent"],
                        dado["sistema"]["disco"]["io"]
                    ])
                
                # Rede
                if "rede" in dado["sistema"]:
                    feature.extend([
                        dado["sistema"]["rede"]["bytes"],
                        dado["sistema"]["rede"]["packets"]
                    ])
                
                # Aplicação
                if "aplicacao" in dado:
                    feature.extend([
                        dado["aplicacao"]["latencia"],
                        dado["aplicacao"]["erros"],
                        dado["aplicacao"]["requisicoes"]
                    ])
                
                features.append(feature)
            
            return np.array(features)
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao extrair features", e)
            return np.array([])
    
    def _analisar_correlacoes(self, dados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa correlações entre métricas"""
        try:
            correlacoes = {}
            
            # Prepara dados
            metricas = self._preparar_metricas_correlacao(dados)
            
            # Analisa cada par de métricas
            for metrica1 in metricas:
                for metrica2 in metricas:
                    if metrica1 != metrica2:
                        # Calcula correlação
                        corr = self._calcular_correlacao(
                            metricas[metrica1],
                            metricas[metrica2]
                        )
                        
                        # Registra se correlação significativa
                        if abs(corr) >= self.config["correlacao"]["min_correlacao"]:
                            correlacoes[f"{metrica1}-{metrica2}"] = {
                                "correlacao": corr,
                                "lag": self._calcular_lag(
                                    metricas[metrica1],
                                    metricas[metrica2]
                                )
                            }
            
            return correlacoes
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao analisar correlações", e)
            return {}
    
    def _preparar_metricas_correlacao(self, dados: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Prepara métricas para análise de correlação"""
        try:
            metricas = {}
            
            for dado in dados:
                # CPU
                if "cpu" in dado["sistema"]:
                    if "cpu_percent" not in metricas:
                        metricas["cpu_percent"] = []
                    metricas["cpu_percent"].append(dado["sistema"]["cpu"]["percent"])
                
                # Memória
                if "memoria" in dado["sistema"]:
                    if "memoria_percent" not in metricas:
                        metricas["memoria_percent"] = []
                    metricas["memoria_percent"].append(dado["sistema"]["memoria"]["percent"])
                
                # Disco
                if "disco" in dado["sistema"]:
                    if "disco_percent" not in metricas:
                        metricas["disco_percent"] = []
                    metricas["disco_percent"].append(dado["sistema"]["disco"]["percent"])
                
                # Rede
                if "rede" in dado["sistema"]:
                    if "rede_bytes" not in metricas:
                        metricas["rede_bytes"] = []
                    metricas["rede_bytes"].append(dado["sistema"]["rede"]["bytes"])
                
                # Aplicação
                if "aplicacao" in dado:
                    if "latencia" not in metricas:
                        metricas["latencia"] = []
                    metricas["latencia"].append(dado["aplicacao"]["latencia"])
                    
                    if "erros" not in metricas:
                        metricas["erros"] = []
                    metricas["erros"].append(dado["aplicacao"]["erros"])
            
            return metricas
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao preparar métricas para correlação", e)
            return {}
    
    def _calcular_correlacao(self, serie1: List[float], serie2: List[float]) -> float:
        """Calcula correlação entre duas séries"""
        try:
            # Garante mesmo tamanho
            min_len = min(len(serie1), len(serie2))
            serie1 = serie1[:min_len]
            serie2 = serie2[:min_len]
            
            # Calcula correlação
            return np.corrcoef(serie1, serie2)[0, 1]
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao calcular correlação", e)
            return 0.0
    
    def _calcular_lag(self, serie1: List[float], serie2: List[float]) -> int:
        """Calcula lag entre duas séries"""
        try:
            # Garante mesmo tamanho
            min_len = min(len(serie1), len(serie2))
            serie1 = serie1[:min_len]
            serie2 = serie2[:min_len]
            
            # Calcula correlação para diferentes lags
            max_lag = self.config["correlacao"]["max_lag"]
            lags = range(-max_lag, max_lag + 1)
            correlacoes = []
            
            for lag in lags:
                if lag < 0:
                    corr = np.corrcoef(serie1[-lag:], serie2[:lag])[0, 1]
                else:
                    corr = np.corrcoef(serie1[:-lag], serie2[lag:])[0, 1]
                correlacoes.append(corr)
            
            # Retorna lag com maior correlação
            return lags[np.argmax(np.abs(correlacoes))]
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao calcular lag", e)
            return 0
    
    def _realizar_predicoes(self, dados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Realiza predições de métricas"""
        try:
            predicoes = {}
            
            # Prepara dados
            metricas = self._preparar_metricas_predicao(dados)
            
            # Realiza predições para cada métrica
            for metrica, valores in metricas.items():
                if len(valores) >= self.config["configuracoes"]["min_amostras"]:
                    # Calcula tendência
                    tendencia = self._calcular_tendencia(valores)
                    
                    # Realiza predição
                    predicao = self._predizer_valores(
                        valores,
                        tendencia,
                        self.config["predicao"]["horizonte"]
                    )
                    
                    # Calcula confiança
                    confianca = self._calcular_confianca_predicao(valores, predicao)
                    
                    if confianca >= self.config["predicao"]["min_confianca"]:
                        predicoes[metrica] = {
                            "valores": predicao,
                            "confianca": confianca,
                            "tendencia": tendencia
                        }
            
            return predicoes
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao realizar predições", e)
            return {}
    
    def _preparar_metricas_predicao(self, dados: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Prepara métricas para predição"""
        try:
            metricas = {}
            
            for dado in dados:
                # CPU
                if "cpu" in dado["sistema"]:
                    if "cpu_percent" not in metricas:
                        metricas["cpu_percent"] = []
                    metricas["cpu_percent"].append(dado["sistema"]["cpu"]["percent"])
                
                # Memória
                if "memoria" in dado["sistema"]:
                    if "memoria_percent" not in metricas:
                        metricas["memoria_percent"] = []
                    metricas["memoria_percent"].append(dado["sistema"]["memoria"]["percent"])
                
                # Disco
                if "disco" in dado["sistema"]:
                    if "disco_percent" not in metricas:
                        metricas["disco_percent"] = []
                    metricas["disco_percent"].append(dado["sistema"]["disco"]["percent"])
                
                # Aplicação
                if "aplicacao" in dado:
                    if "latencia" not in metricas:
                        metricas["latencia"] = []
                    metricas["latencia"].append(dado["aplicacao"]["latencia"])
                    
                    if "erros" not in metricas:
                        metricas["erros"] = []
                    metricas["erros"].append(dado["aplicacao"]["erros"])
            
            return metricas
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao preparar métricas para predição", e)
            return {}
    
    def _calcular_tendencia(self, valores: List[float]) -> float:
        """Calcula tendência de uma série"""
        try:
            x = np.arange(len(valores))
            y = np.array(valores)
            
            # Ajusta linha
            z = np.polyfit(x, y, 1)
            
            return z[0]  # Coeficiente angular
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao calcular tendência", e)
            return 0.0
    
    def _predizer_valores(self, valores: List[float], tendencia: float, horizonte: int) -> List[float]:
        """Prediz valores futuros"""
        try:
            # Calcula número de predições
            num_predicoes = horizonte // self.config["predicao"]["intervalo_predicao"]
            
            # Realiza predições
            predicoes = []
            ultimo_valor = valores[-1]
            
            for i in range(num_predicoes):
                # Calcula próximo valor
                proximo_valor = ultimo_valor + (tendencia * self.config["predicao"]["intervalo_predicao"])
                predicoes.append(proximo_valor)
                ultimo_valor = proximo_valor
            
            return predicoes
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao predizer valores", e)
            return []
    
    def _calcular_confianca_predicao(self, valores: List[float], predicoes: List[float]) -> float:
        """Calcula confiança da predição"""
        try:
            if not predicoes:
                return 0.0
            
            # Calcula erro médio
            erro_medio = np.mean(np.abs(np.diff(valores)))
            
            # Calcula confiança
            confianca = 1.0 - (erro_medio / np.mean(valores))
            
            return max(0.0, min(1.0, confianca))
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao calcular confiança da predição", e)
            return 0.0
    
    def _registrar_resultados(self, correlacoes: Dict[str, Any], predicoes: Dict[str, Any]) -> None:
        """Registra resultados da análise"""
        try:
            # Prepara dados
            dados = {
                "timestamp": datetime.now().isoformat(),
                "correlacoes": correlacoes,
                "predicoes": predicoes
            }
            
            # Registra no cache
            self.cache.definir("diagnostico_avancado", "ultimo", dados)
            
            # Registra no log
            self.logger.registrar_diagnostico("avancado", dados)
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao registrar resultados", e)
    
    def obter_resultados(self) -> Dict[str, Any]:
        """Obtém resultados da análise"""
        try:
            return self.cache.obter("diagnostico_avancado", "ultimo") or {}
            
        except Exception as e:
            self.logger.registrar_erro("diagnostico_avancado", "Erro ao obter resultados", e)
            return {} 