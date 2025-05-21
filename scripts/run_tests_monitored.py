#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import yaml
import pytest
import logging
import argparse
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge, Summary

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/testes.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Métricas Prometheus
TESTES_TOTAL = Counter('pytest_tests_total', 'Total de testes executados')
TESTES_PASSADOS = Counter('pytest_tests_passed', 'Total de testes passados')
TESTES_FALHADOS = Counter('pytest_tests_failed', 'Total de testes falhados')
TEMPO_EXECUCAO = Summary('pytest_execution_time_seconds', 'Tempo de execução dos testes')
COBERTURA = Gauge('pytest_coverage_percentage', 'Porcentagem de cobertura de código')

def carregar_config():
    """Carrega as configurações do arquivo YAML."""
    try:
        with open('config/testes.yaml', 'r') as f:
            return yaml.safe_load(f)['testes']
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")
        sys.exit(1)

def executar_testes(config):
    """Executa os testes com monitoramento."""
    start_time = time.time()
    
    # Configuração do pytest
    pytest_args = [
        '--cov=src',
        '--cov-report=term-missing',
        '--cov-report=html',
        '--junitxml=test-results.xml',
        '-v'
    ]
    
    if config['performance']['paralelismo'] > 1:
        pytest_args.append(f'-n {config["performance"]["paralelismo"]}')
    
    # Executa os testes
    try:
        resultado = pytest.main(pytest_args)
        
        # Atualiza métricas
        TESTES_TOTAL.inc()
        if resultado == 0:
            TESTES_PASSADOS.inc()
        else:
            TESTES_FALHADOS.inc()
            
        # Atualiza tempo de execução
        TEMPO_EXECUCAO.observe(time.time() - start_time)
        
        # Atualiza cobertura (simplificado)
        with open('coverage/coverage.xml', 'r') as f:
            import xml.etree.ElementTree as ET
            tree = ET.parse(f)
            root = tree.getroot()
            cobertura = float(root.attrib['line-rate']) * 100
            COBERTURA.set(cobertura)
            
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao executar testes: {e}")
        return 1

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Executa testes com monitoramento')
    parser.add_argument('--porta', type=int, default=9091, help='Porta para métricas Prometheus')
    args = parser.parse_args()
    
    # Carrega configurações
    config = carregar_config()
    
    # Inicia servidor de métricas
    start_http_server(args.porta)
    logger.info(f"Servidor de métricas iniciado na porta {args.porta}")
    
    # Executa testes
    logger.info("Iniciando execução dos testes...")
    resultado = executar_testes(config)
    
    # Registra resultado
    if resultado == 0:
        logger.info("Todos os testes passaram!")
    else:
        logger.error(f"Testes falharam com código {resultado}")
    
    return resultado

if __name__ == '__main__':
    sys.exit(main()) 