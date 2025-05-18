"""
Módulo de Monitoramento - Aplicação Flask

Este módulo implementa a API REST para o serviço de monitoramento.
"""

from flask import Flask, request, jsonify
import time
import logging
from monitoramento import ColetorMetricas, AnalisadorMetricas, GeradorAlertas

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("Monitoramento")

# Inicializa a aplicação Flask
app = Flask(__name__)

# Inicializa componentes
coletor = ColetorMetricas()
analisador = AnalisadorMetricas(coletor)
gerador_alertas = GeradorAlertas(analisador)

@app.route('/health', methods=['GET'])
def health_check():
    """Verifica a saúde do serviço."""
    return jsonify({"status": "healthy"})

@app.route('/ready', methods=['GET'])
def ready_check():
    """
    Verifica se o serviço está pronto para operação.
        
    Returns:
        dict: Status de prontidão
    """
    if not coletor or not analisador or not gerador_alertas:
        return jsonify({"status": "not ready", "reason": "Components not initialized"}), 503
    return jsonify({"status": "ready", "timestamp": time.time()})

@app.route('/api/metricas', methods=['GET'])
def listar_metricas():
    """
    Lista todas as métricas coletadas.
    
    Returns:
        dict: Lista de métricas
    """
    try:
        metricas = coletor.coletar_metricas()
        return jsonify([m.to_dict() for m in metricas]), 200
    except Exception as e:
        logger.error(f"Erro ao listar métricas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/metricas/<metrica_id>', methods=['GET'])
def obter_metrica(metrica_id):
    """
    Obtém uma métrica específica.
    
    Args:
        metrica_id: ID da métrica
        
    Returns:
        dict: Dados da métrica
    """
    try:
        metricas = coletor.coletar_metricas()
        metrica = next((m for m in metricas if m.id == metrica_id), None)
        
        if not metrica:
            return jsonify({"error": f"Métrica {metrica_id} não encontrada"}), 404
        
        return jsonify(metrica.to_dict()), 200
    except Exception as e:
        logger.error(f"Erro ao obter métrica: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analise', methods=['GET'])
def analisar_metricas():
    """
    Realiza análise das métricas coletadas.
    
    Returns:
        dict: Resultados da análise
    """
    try:
        resultados = analisador.analisar_metricas()
        return jsonify(resultados), 200
    except Exception as e:
        logger.error(f"Erro ao analisar métricas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/alertas', methods=['GET'])
def gerar_alertas():
    """
    Gera alertas baseados na análise de métricas.
    
    Returns:
        dict: Lista de alertas gerados
    """
    try:
        resultados = analisador.analisar_metricas()
        alertas = gerador_alertas.avaliar_alertas(resultados)
        return jsonify(alertas), 200
    except Exception as e:
        logger.error(f"Erro ao gerar alertas: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Inicia o servidor
    app.run(host='0.0.0.0', port=8080) 