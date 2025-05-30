"""
Exemplo de integração entre o sistema de diagnóstico e a visualização 4D.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List

from ..diagnostico import SistemaDiagnostico, Problema, StatusDiagnostico, Severidade
from ..visualizacao_4d import Visualizacao4D, Dimensao4D
from ..config import CONFIG

async def simular_sistema(
    diagnostico: SistemaDiagnostico,
    visualizador: Visualizacao4D,
    duracao: int = 3600
):
    """
    Simula o comportamento do sistema para demonstração.
    
    Args:
        diagnostico: Instância do sistema de diagnóstico
        visualizador: Instância do visualizador 4D
        duracao: Duração da simulação em segundos
    """
    print("Iniciando simulação do sistema...")
    
    # Métricas iniciais
    metricas = {
        "cpu": 50.0,
        "memoria": 60.0,
        "latencia": 100.0,
        "erros": 1.0
    }
    
    # Simula o sistema por duracao segundos
    for _ in range(duracao):
        # Simula variações nas métricas
        for nome in metricas:
            # Adiciona ruído
            metricas[nome] += random.uniform(-5, 5)
            
            # Mantém dentro dos limites
            if nome in ["cpu", "memoria", "erros"]:
                metricas[nome] = max(0, min(100, metricas[nome]))
            else:  # latencia
                metricas[nome] = max(0, min(1000, metricas[nome]))
            
            # Atualiza dimensão 4D
            visualizador.atualizar_dimensao(
                nome,
                metricas[nome],
                {"host": "server1", "timestamp": datetime.now()}
            )
        
        # Analisa métricas para diagnóstico
        problemas = diagnostico.analisar_metricas(metricas)
        
        # Registra problemas encontrados
        for problema in problemas:
            diagnostico.registrar_problema(problema)
            
            # Adiciona métricas ao problema
            for nome, valor in metricas.items():
                problema.metricas[nome] = valor
            
            # Adiciona logs
            diagnostico.adicionar_log(
                problema.id,
                f"Problema detectado: {problema.titulo}",
                {"severidade": problema.severidade.value}
            )
        
        await asyncio.sleep(1)

async def demonstrar_integracao():
    """Demonstra a integração entre diagnóstico e visualização 4D."""
    # Inicializa sistemas
    diagnostico = SistemaDiagnostico()
    visualizador = Visualizacao4D(CONFIG)
    
    # Inicia simulação em background
    simulador = asyncio.create_task(simular_sistema(diagnostico, visualizador))
    
    try:
        # Aguarda alguns dados serem gerados
        await asyncio.sleep(10)
        
        # Demonstra problemas detectados
        print("\nProblemas detectados:")
        problemas = diagnostico.listar_problemas()
        for problema in problemas:
            print(f"- {problema.titulo} (Severidade: {problema.severidade.value})")
            
            # Obtém métricas do problema
            print("  Métricas:")
            for nome, valor in problema.metricas.items():
                print(f"  - {nome}: {valor:.2f}")
            
            # Obtém logs do problema
            print("  Logs:")
            for log in problema.logs:
                print(f"  - {log}")
        
        # Demonstra análise de correlações
        print("\nCorrelações entre métricas:")
        matriz = visualizador.gerar_matriz_correlacao()
        for dim1 in matriz:
            for dim2, corr in matriz[dim1].items():
                if dim1 != dim2:
                    print(f"- {dim1} x {dim2}: {corr:.2f}")
        
        # Demonstra detecção de anomalias
        print("\nAnomalias detectadas:")
        for nome in ["cpu", "memoria", "latencia", "erros"]:
            anomalias = visualizador.detectar_anomalias(nome)
            if anomalias:
                print(f"\n{nome}:")
                for anomalia in anomalias:
                    print(f"- Valor: {anomalia['valor']:.2f}, Z-score: {anomalia['z_score']:.2f}")
        
        # Demonstra tendências
        print("\nTendências detectadas:")
        for nome in ["cpu", "memoria", "latencia", "erros"]:
            tendencias = visualizador.detectar_tendencias(nome)
            print(f"- {nome}: {tendencias['tendencia']} (inclinação: {tendencias['inclinacao']:.2f})")
        
        # Demonstra geração de relatório
        print("\nGerando relatório completo...")
        relatorio = visualizador.gerar_relatorio()
        print(f"Relatório gerado com {len(relatorio['dimensoes'])} dimensões")
        
        # Demonstra atualização de status
        if problemas:
            problema = problemas[0]
            print(f"\nAtualizando status do problema {problema.id}...")
            diagnostico.atualizar_status(problema.id, StatusDiagnostico.RESOLVIDO)
            print(f"Status atualizado para: {StatusDiagnostico.RESOLVIDO.value}")
        
    finally:
        # Cancela simulação
        simulador.cancel()
        try:
            await simulador
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(demonstrar_integracao()) 