import pytest
import time
import psutil
import os
from typing import Dict, List
import json
import logging
from datetime import datetime

# Importa módulos para teste
from modulos.ia.src.agents.adaptive_agent import AdaptiveAgent
from modulos.seguranca.src.crypto.quantum_safe import QuantumSafeCrypto
from modulos.observabilidade.src.collectors.multidim_collector import MultiDimensionalCollector

class PerformanceTest:
    """
    Classe para testes de desempenho dos módulos principais.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "modules": {}
        }
        
    def measure_execution_time(self, func, *args, **kwargs) -> float:
        """
        Mede o tempo de execução de uma função.
        """
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        return end_time - start_time
    
    def measure_memory_usage(self, func, *args, **kwargs) -> float:
        """
        Mede o uso de memória de uma função.
        """
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss
        func(*args, **kwargs)
        end_memory = process.memory_info().rss
        return (end_memory - start_memory) / 1024 / 1024  # MB
    
    def test_ia_module(self):
        """
        Testa desempenho do módulo de IA.
        """
        agent = AdaptiveAgent()
        
        # Teste de processamento
        test_data = {"input": "Teste de desempenho"}
        
        execution_time = self.measure_execution_time(
            agent.process_with_best_available,
            test_data
        )
        
        memory_usage = self.measure_memory_usage(
            agent.process_with_best_available,
            test_data
        )
        
        self.results["modules"]["ia"] = {
            "execution_time": execution_time,
            "memory_usage": memory_usage,
            "capabilities": agent.capabilities
        }
    
    def test_security_module(self):
        """
        Testa desempenho do módulo de segurança.
        """
        crypto = QuantumSafeCrypto()
        
        # Teste de criptografia
        test_data = b"Teste de desempenho de criptografia"
        public_key, private_key = crypto.generate_key_pair()
        
        encryption_time = self.measure_execution_time(
            crypto.encrypt,
            test_data,
            public_key
        )
        
        decryption_time = self.measure_execution_time(
            crypto.decrypt,
            crypto.encrypt(test_data, public_key),
            private_key
        )
        
        memory_usage = self.measure_memory_usage(
            crypto.encrypt,
            test_data,
            public_key
        )
        
        self.results["modules"]["seguranca"] = {
            "encryption_time": encryption_time,
            "decryption_time": decryption_time,
            "memory_usage": memory_usage
        }
    
    def test_observability_module(self):
        """
        Testa desempenho do módulo de observabilidade.
        """
        collector = MultiDimensionalCollector()
        
        # Teste de coleta de métricas
        collection_time = self.measure_execution_time(
            collector.collect_classical_metrics
        )
        
        memory_usage = self.measure_memory_usage(
            collector.collect_classical_metrics
        )
        
        self.results["modules"]["observabilidade"] = {
            "collection_time": collection_time,
            "memory_usage": memory_usage
        }
    
    def run_all_tests(self):
        """
        Executa todos os testes de desempenho.
        """
        try:
            self.test_ia_module()
            self.test_security_module()
            self.test_observability_module()
            
            # Salva resultados
            self._save_results()
            
        except Exception as e:
            self.logger.error(f"Erro nos testes de desempenho: {str(e)}")
            raise
    
    def _save_results(self):
        """
        Salva resultados dos testes.
        """
        try:
            results_dir = "reports/performance"
            os.makedirs(results_dir, exist_ok=True)
            
            filename = f"performance_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(results_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=4)
                
            self.logger.info(f"Resultados salvos em: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar resultados: {str(e)}")
            raise

def test_performance():
    """
    Função principal de teste de desempenho.
    """
    performance_test = PerformanceTest()
    performance_test.run_all_tests() 