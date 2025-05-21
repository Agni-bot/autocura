#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge

# Adiciona o diretório src ao path para importar o módulo de autocura
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.autocura.dependencias import GerenciadorDependencias

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dependencias.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Métricas Prometheus
DEPENDENCIAS_VERIFICADAS = Counter(
    'dependencias_verificadas_total',
    'Total de verificações de dependências realizadas'
)
DEPENDENCIAS_PROBLEMAS = Counter(
    'dependencias_problemas_total',
    'Total de problemas encontrados com dependências'
)
DEPENDENCIAS_AUTOCURADAS = Counter(
    'dependencias_autocuradas_total',
    'Total de problemas autocurados com sucesso'
)
TEMPO_VERIFICACAO = Gauge(
    'dependencias_tempo_verificacao_seconds',
    'Tempo gasto na última verificação de dependências'
)

def verificar_dependencias():
    """Verifica e tenta autocurar problemas de dependências."""
    start_time = time.time()
    
    gerenciador = GerenciadorDependencias()
    
    # Incrementa contador de verificações
    DEPENDENCIAS_VERIFICADAS.inc()
    
    # Verifica compatibilidade do Python
    if not gerenciador.verificar_compatibilidade_python():
        DEPENDENCIAS_PROBLEMAS.inc()
        logger.error("Versão do Python incompatível")
        return False
    
    # Verifica dependências do sistema
    dependencias = gerenciador.verificar_dependencias_sistema()
    if not all(dependencias.values()):
        DEPENDENCIAS_PROBLEMAS.inc()
        logger.error("Dependências do sistema faltando")
        return False
    
    # Tenta instalar dependências
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            check=True
        )
        logger.info("Dependências instaladas com sucesso")
        DEPENDENCIAS_AUTOCURADAS.inc()
        
        # Atualiza tempo de verificação
        TEMPO_VERIFICACAO.set(time.time() - start_time)
        return True
        
    except subprocess.CalledProcessError as e:
        DEPENDENCIAS_PROBLEMAS.inc()
        logger.error(f"Erro ao instalar dependências: {e}")
        
        # Tenta sugerir solução baseada no histórico
        output = e.output.decode() if e.output else str(e)
        for linha in output.split('\n'):
            if "No matching distribution found for" in linha:
                pacote = linha.split("for")[-1].strip()
                versao = pacote.split("==")[-1] if "==" in pacote else "latest"
                pacote = pacote.split("==")[0]
                
                solucao = gerenciador.sugerir_solucao(pacote, versao)
                if solucao:
                    logger.info(f"Solução sugerida para {pacote}: {solucao}")
        
        # Atualiza tempo de verificação
        TEMPO_VERIFICACAO.set(time.time() - start_time)
        return False

def main():
    """Função principal."""
    # Inicia servidor de métricas
    porta = int(os.getenv('PROMETHEUS_PORT', 9092))
    start_http_server(porta)
    logger.info(f"Servidor de métricas iniciado na porta {porta}")
    
    # Loop principal
    while True:
        verificar_dependencias()
        time.sleep(300)  # Verifica a cada 5 minutos

if __name__ == '__main__':
    main() 