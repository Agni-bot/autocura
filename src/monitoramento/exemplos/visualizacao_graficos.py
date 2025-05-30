"""
Exemplo de visualização 4D com gráficos interativos usando Streamlit.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import random
from typing import Dict, List

from ..visualizacao_4d import Visualizacao4D, Dimensao4D
from ..config import CONFIG

def criar_dataframe_dimensao(dimensoes: List[Dimensao4D]) -> pd.DataFrame:
    """
    Converte uma lista de dimensões em um DataFrame.
    
    Args:
        dimensoes: Lista de dimensões 4D
        
    Returns:
        DataFrame com os dados da dimensão
    """
    dados = []
    for d in dimensoes:
        dados.append({
            "timestamp": d.timestamp,
            "valor": d.valor,
            "host": d.contexto.get("host", "desconhecido"),
            "tipo": d.contexto.get("tipo", "desconhecido")
        })
    return pd.DataFrame(dados)

def plotar_serie_temporal(df: pd.DataFrame, titulo: str):
    """
    Plota uma série temporal usando Plotly.
    
    Args:
        df: DataFrame com os dados
        titulo: Título do gráfico
    """
    fig = px.line(
        df,
        x="timestamp",
        y="valor",
        color="host",
        title=titulo,
        labels={"valor": "Valor", "timestamp": "Tempo"}
    )
    st.plotly_chart(fig)

def plotar_correlacao(matriz: Dict[str, Dict[str, float]]):
    """
    Plota a matriz de correlação usando Plotly.
    
    Args:
        matriz: Matriz de correlação
    """
    # Converte matriz para DataFrame
    df = pd.DataFrame(matriz)
    
    # Cria heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale="RdBu",
        zmin=-1,
        zmax=1
    ))
    
    fig.update_layout(
        title="Matriz de Correlação",
        xaxis_title="Dimensões",
        yaxis_title="Dimensões"
    )
    
    st.plotly_chart(fig)

def plotar_anomalias(df: pd.DataFrame, anomalias: List[Dict], titulo: str):
    """
    Plota série temporal com anomalias destacadas.
    
    Args:
        df: DataFrame com os dados
        anomalias: Lista de anomalias detectadas
        titulo: Título do gráfico
    """
    fig = go.Figure()
    
    # Adiciona linha da série temporal
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["valor"],
        mode="lines",
        name="Série Temporal"
    ))
    
    # Adiciona pontos das anomalias
    for anomalia in anomalias:
        fig.add_trace(go.Scatter(
            x=[anomalia["timestamp"]],
            y=[anomalia["valor"]],
            mode="markers",
            marker=dict(
                size=10,
                color="red",
                symbol="star"
            ),
            name=f"Anomalia (Z-score: {anomalia['z_score']:.2f})"
        ))
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Tempo",
        yaxis_title="Valor"
    )
    
    st.plotly_chart(fig)

def plotar_tendencias(df: pd.DataFrame, tendencias: Dict, titulo: str):
    """
    Plota série temporal com linha de tendência.
    
    Args:
        df: DataFrame com os dados
        tendencias: Dicionário com informações da tendência
        titulo: Título do gráfico
    """
    fig = go.Figure()
    
    # Adiciona linha da série temporal
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["valor"],
        mode="lines",
        name="Série Temporal"
    ))
    
    # Adiciona linha de tendência
    x = np.array(range(len(df)))
    y = tendencias["inclinacao"] * x + tendencias["intercepto"]
    
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=y,
        mode="lines",
        line=dict(dash="dash", color="red"),
        name=f"Tendência ({tendencias['tendencia']})"
    ))
    
    fig.update_layout(
        title=f"{titulo} - R²: {tendencias['r2']:.2f}",
        xaxis_title="Tempo",
        yaxis_title="Valor"
    )
    
    st.plotly_chart(fig)

async def gerar_dados_simulados(visualizador: Visualizacao4D, duracao: int = 3600):
    """
    Gera dados simulados para demonstração.
    
    Args:
        visualizador: Instância do visualizador 4D
        duracao: Duração da simulação em segundos
    """
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

def main():
    """Função principal da aplicação Streamlit."""
    st.title("Visualização 4D - AutoCura")
    
    # Inicializa visualizador
    visualizador = Visualizacao4D(CONFIG)
    
    # Sidebar para configurações
    st.sidebar.title("Configurações")
    
    # Seleção de dimensão
    dimensao = st.sidebar.selectbox(
        "Dimensão",
        list(CONFIG["VISUALIZACAO_DIMENSOES"].keys())
    )
    
    # Seleção de período
    periodo = st.sidebar.slider(
        "Período (horas)",
        min_value=1,
        max_value=24,
        value=6
    )
    
    # Botão para atualizar dados
    if st.sidebar.button("Atualizar Dados"):
        # Inicia geração de dados em background
        asyncio.run(gerar_dados_simulados(visualizador, periodo * 3600))
    
    # Obtém dados da dimensão selecionada
    dimensoes = visualizador.obter_dimensao(
        dimensao,
        timedelta(hours=periodo)
    )
    
    if dimensoes:
        # Converte para DataFrame
        df = criar_dataframe_dimensao(dimensoes)
        
        # Exibe estatísticas
        st.subheader("Estatísticas")
        estatisticas = visualizador.calcular_estatisticas(dimensao)
        col1, col2, col3 = st.columns(3)
        col1.metric("Média", f"{estatisticas['media']:.2f}")
        col2.metric("Mediana", f"{estatisticas['mediana']:.2f}")
        col3.metric("Desvio Padrão", f"{estatisticas['desvio_padrao']:.2f}")
        
        # Plota série temporal
        st.subheader("Série Temporal")
        plotar_serie_temporal(df, f"Série Temporal - {dimensao}")
        
        # Exibe anomalias
        st.subheader("Anomalias")
        anomalias = visualizador.detectar_anomalias(dimensao)
        if anomalias:
            plotar_anomalias(df, anomalias, f"Anomalias - {dimensao}")
            for anomalia in anomalias:
                st.write(f"- Valor: {anomalia['valor']:.2f}, Z-score: {anomalia['z_score']:.2f}")
        else:
            st.write("Nenhuma anomalia detectada.")
        
        # Exibe tendências
        st.subheader("Tendências")
        tendencias = visualizador.detectar_tendencias(dimensao)
        plotar_tendencias(df, tendencias, f"Tendências - {dimensao}")
        st.write(f"Tendência: {tendencias['tendencia']}")
        st.write(f"Inclinação: {tendencias['inclinacao']:.2f}")
        st.write(f"R²: {tendencias['r2']:.2f}")
        
        # Exibe correlações
        st.subheader("Correlações")
        matriz = visualizador.gerar_matriz_correlacao()
        plotar_correlacao(matriz)
        
        # Exibe relatório
        if st.sidebar.button("Gerar Relatório"):
            st.subheader("Relatório Completo")
            relatorio = visualizador.gerar_relatorio()
            st.json(relatorio)
    else:
        st.warning("Nenhum dado disponível para a dimensão selecionada.")

if __name__ == "__main__":
    main() 