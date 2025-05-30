"""
Exemplo de uso do módulo de visualização 4D.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List

from ..visualizacao_4d import Visualizacao4D, Dimensao4D
from ..config import CONFIG

async def gerar_dados_simulados(visualizador: Visualizacao4D, duracao: int = 3600):
    """
    Gera dados simulados para demonstração.
    
    Args:
        visualizador: Instância do visualizador 4D
        duracao: Duração da simulação em segundos
    """
    print("Iniciando geração de dados simulados...")
    
    # Dimensões a serem simuladas
    dimensoes = {
        "performance": {"min": 0, "max": 100, "tendencia": 0.1},
        "saude": {"min": 0, "max": 100, "tendencia": -0.05},
        "latencia": {"min": 0, "max": 1000, "tendencia": 0.2},
        "erros": {"min": 0, "max": 100, "tendencia": 0.15}
    }
    
    # Valores iniciais
    valores = {nome: (d["min"] + d["max"]) / 2 for nome, d in dimensoes.items()}
    
    # Gera dados por duracao segundos
    for _ in range(duracao):
        for nome, config in dimensoes.items():
            # Adiciona tendência
            valores[nome] += config["tendencia"]
            
            # Adiciona ruído
            valores[nome] += random.uniform(-5, 5)
            
            # Mantém dentro dos limites
            valores[nome] = max(config["min"], min(config["max"], valores[nome]))
            
            # Atualiza dimensão
            visualizador.atualizar_dimensao(
                nome,
                valores[nome],
                {"host": "server1", "timestamp": datetime.now()}
            )
        
        await asyncio.sleep(1)

async def demonstrar_visualizacao():
    """Demonstra as funcionalidades da visualização 4D."""
    # Inicializa visualizador
    visualizador = Visualizacao4D(CONFIG)
    
    # Inicia geração de dados em background
    gerador = asyncio.create_task(gerar_dados_simulados(visualizador))
    
    try:
        # Aguarda alguns dados serem gerados
        await asyncio.sleep(10)
        
        # Demonstra obtenção de dimensões
        print("\nDimensões disponíveis:")
        for nome in CONFIG["VISUALIZACAO_DIMENSOES"].keys():
            dimensoes = visualizador.obter_dimensao(nome)
            print(f"- {nome}: {len(dimensoes)} pontos")
        
        # Demonstra estatísticas
        print("\nEstatísticas de performance:")
        estatisticas = visualizador.calcular_estatisticas("performance")
        for nome, valor in estatisticas.items():
            print(f"- {nome}: {valor:.2f}")
        
        # Demonstra detecção de anomalias
        print("\nAnomalias detectadas:")
        anomalias = visualizador.detectar_anomalias("performance")
        for anomalia in anomalias:
            print(f"- Valor: {anomalia['valor']:.2f}, Z-score: {anomalia['z_score']:.2f}")
        
        # Demonstra correlações
        print("\nCorrelações entre dimensões:")
        matriz = visualizador.gerar_matriz_correlacao()
        for dim1 in matriz:
            for dim2, corr in matriz[dim1].items():
                if dim1 != dim2:
                    print(f"- {dim1} x {dim2}: {corr:.2f}")
        
        # Demonstra tendências
        print("\nTendências detectadas:")
        for nome in CONFIG["VISUALIZACAO_DIMENSOES"].keys():
            tendencias = visualizador.detectar_tendencias(nome)
            print(f"- {nome}: {tendencias['tendencia']} (inclinação: {tendencias['inclinacao']:.2f})")
        
        # Demonstra geração de relatório
        print("\nGerando relatório completo...")
        relatorio = visualizador.gerar_relatorio()
        print(f"Relatório gerado com {len(relatorio['dimensoes'])} dimensões")
        
        # Demonstra limpeza de dados antigos
        print("\nLimpando dados antigos...")
        visualizador.limpar_dados_antigos(timedelta(hours=1))
        print("Dados antigos removidos")
        
    finally:
        # Cancela geração de dados
        gerador.cancel()
        try:
            await gerador
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(demonstrar_visualizacao()) 