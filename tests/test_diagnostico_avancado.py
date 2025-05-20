import unittest
from unittest.mock import Mock, patch
import json
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

from src.core.diagnostico_avancado import DiagnosticoAvancado
from src.memoria.gerenciador_memoria import GerenciadorMemoria
from src.core.logger import Logger
from src.core.cache import Cache

class TestDiagnosticoAvancado(unittest.TestCase):
    """Testes unitários para o módulo de diagnóstico avançado"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.gerenciador_memoria = Mock(spec=GerenciadorMemoria)
        self.logger = Mock(spec=Logger)
        self.cache = Mock(spec=Cache)
        
        # Cria diretório de configuração se não existir
        Path("config").mkdir(exist_ok=True)
        
        # Cria arquivo de configuração de teste
        self.config_teste = {
            "configuracoes": {
                "intervalo_analise": 1,
                "janela_historico": 3600,
                "min_amostras": 10,
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
        
        with open("config/diagnostico_avancado.json", "w") as f:
            json.dump(self.config_teste, f)
        
        self.diagnostico = DiagnosticoAvancado(
            self.gerenciador_memoria,
            self.logger,
            self.cache
        )
    
    def tearDown(self):
        """Limpeza após os testes"""
        # Remove arquivo de configuração de teste
        Path("config/diagnostico_avancado.json").unlink(missing_ok=True)
    
    def test_inicializacao(self):
        """Testa inicialização do diagnóstico avançado"""
        self.assertIsNotNone(self.diagnostico)
        self.assertEqual(self.diagnostico.config, self.config_teste)
        self.assertIsNone(self.diagnostico.modelo_anomalia)
        self.assertFalse(self.diagnostico.running)
    
    def test_carregar_config(self):
        """Testa carregamento de configuração"""
        config = self.diagnostico._carregar_config()
        self.assertEqual(config, self.config_teste)
    
    def test_criar_config_padrao(self):
        """Testa criação de configuração padrão"""
        config = self.diagnostico._criar_config_padrao()
        self.assertIn("configuracoes", config)
        self.assertIn("metricas", config)
        self.assertIn("correlacao", config)
        self.assertIn("predicao", config)
    
    def test_iniciar_parar(self):
        """Testa inicialização e parada do sistema"""
        self.diagnostico.iniciar()
        self.assertTrue(self.diagnostico.running)
        self.assertIsNotNone(self.diagnostico.thread_analise)
        
        self.diagnostico.parar()
        self.assertFalse(self.diagnostico.running)
    
    def test_coletar_dados_historicos(self):
        """Testa coleta de dados históricos"""
        # Simula dados no cache
        dados_teste = [
            {
                "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(),
                "sistema": {
                    "cpu": {"percent": 50.0, "load": 1.0},
                    "memoria": {"percent": 60.0, "used": 1024},
                    "disco": {"percent": 70.0, "io": 100},
                    "rede": {"bytes": 1000, "packets": 100}
                },
                "aplicacao": {
                    "latencia": 100,
                    "erros": 0,
                    "requisicoes": 1000
                }
            }
            for i in range(20)
        ]
        
        self.cache.obter.return_value = dados_teste
        
        dados = self.diagnostico._coletar_dados_historicos()
        self.assertEqual(len(dados), 20)
    
    def test_extrair_features(self):
        """Testa extração de features"""
        dados_teste = [
            {
                "sistema": {
                    "cpu": {"percent": 50.0, "load": 1.0},
                    "memoria": {"percent": 60.0, "used": 1024},
                    "disco": {"percent": 70.0, "io": 100},
                    "rede": {"bytes": 1000, "packets": 100}
                },
                "aplicacao": {
                    "latencia": 100,
                    "erros": 0,
                    "requisicoes": 1000
                }
            }
        ]
        
        features = self.diagnostico._extrair_features(dados_teste)
        self.assertEqual(features.shape[0], 1)
        self.assertEqual(features.shape[1], 11)  # Número total de features
    
    def test_calcular_correlacao(self):
        """Testa cálculo de correlação"""
        serie1 = [1, 2, 3, 4, 5]
        serie2 = [2, 4, 6, 8, 10]
        
        corr = self.diagnostico._calcular_correlacao(serie1, serie2)
        self.assertAlmostEqual(corr, 1.0)
    
    def test_calcular_lag(self):
        """Testa cálculo de lag"""
        serie1 = [1, 2, 3, 4, 5]
        serie2 = [0, 1, 2, 3, 4]
        
        lag = self.diagnostico._calcular_lag(serie1, serie2)
        self.assertEqual(lag, 1)
    
    def test_calcular_tendencia(self):
        """Testa cálculo de tendência"""
        valores = [1, 2, 3, 4, 5]
        
        tendencia = self.diagnostico._calcular_tendencia(valores)
        self.assertAlmostEqual(tendencia, 1.0)
    
    def test_predizer_valores(self):
        """Testa predição de valores"""
        valores = [1, 2, 3, 4, 5]
        tendencia = 1.0
        horizonte = 300
        
        predicoes = self.diagnostico._predizer_valores(valores, tendencia, horizonte)
        self.assertEqual(len(predicoes), 1)  # horizonte/intervalo_predicao
        self.assertAlmostEqual(predicoes[0], 6.0)
    
    def test_calcular_confianca_predicao(self):
        """Testa cálculo de confiança da predição"""
        valores = [1, 2, 3, 4, 5]
        predicoes = [6, 7, 8]
        
        confianca = self.diagnostico._calcular_confianca_predicao(valores, predicoes)
        self.assertGreaterEqual(confianca, 0.0)
        self.assertLessEqual(confianca, 1.0)
    
    def test_registrar_resultados(self):
        """Testa registro de resultados"""
        correlacoes = {"cpu-memoria": {"correlacao": 0.8, "lag": 0}}
        predicoes = {"cpu": {"valores": [50], "confianca": 0.9, "tendencia": 0.1}}
        
        self.diagnostico._registrar_resultados(correlacoes, predicoes)
        
        self.cache.definir.assert_called_once()
        self.logger.registrar_diagnostico.assert_called_once()
    
    def test_obter_resultados(self):
        """Testa obtenção de resultados"""
        resultados_teste = {
            "timestamp": datetime.now().isoformat(),
            "correlacoes": {"cpu-memoria": {"correlacao": 0.8, "lag": 0}},
            "predicoes": {"cpu": {"valores": [50], "confianca": 0.9, "tendencia": 0.1}}
        }
        
        self.cache.obter.return_value = resultados_teste
        
        resultados = self.diagnostico.obter_resultados()
        self.assertEqual(resultados, resultados_teste)

if __name__ == "__main__":
    unittest.main() 