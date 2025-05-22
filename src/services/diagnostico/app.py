from flask import Flask, request, jsonify
from core import AnalisadorMetricas, GeradorDiagnosticos, obter_metricas_do_monitoramento
import logging
import json
import os
from datetime import datetime

# Configuração do Flask
app = Flask(__name__)

# Configuração do logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'diagnostico.log')
)
logger = logging.getLogger(__name__)

# Carrega configurações
def carregar_configuracoes():
    try:
        with open('config/sistema.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {str(e)}")
        return {}

config = carregar_configuracoes()

# Inicializa componentes
analisador = AnalisadorMetricas()
gerador = GeradorDiagnosticos()

@app.route('/health', methods=['GET'])
def health_check():
    """Verifica a saúde do serviço."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'diagnostico'
    })

@app.route('/ready', methods=['GET'])
def ready_check():
    """
    Verifica se o serviço está pronto para operação.
        
    Returns:
        dict: Status de prontidão
    """
    if not analisador or not gerador:
        return jsonify({"status": "not ready", "reason": "Components not initialized"}), 503
    return jsonify({"status": "ready"})

@app.route('/api/diagnosticos', methods=['POST'])
def gerar_diagnosticos():
    """
    Gera diagnósticos baseados nas métricas do monitoramento.
    
    Returns:
        dict: Lista de diagnósticos gerados
    """
    try:
        # Obtém métricas do monitoramento
        metricas = obter_metricas_do_monitoramento()
        
        # Analisa métricas
        padroes = analisador.analisar_metricas(metricas)
        
        # Gera diagnósticos
        diagnosticos = gerador.gerar_diagnosticos(padroes)
        
        return jsonify([d.to_dict() for d in diagnosticos]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analisar', methods=['POST'])
def analisar_problema():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        # Extrai informações do problema
        problema = dados.get('problema', {})
        metricas = dados.get('metricas', {})
        logs = dados.get('logs', [])

        # Realiza análise do problema
        analise = {
            'tipo': identificar_tipo_problema(problema, metricas),
            'severidade': calcular_severidade(metricas),
            'causas_provaveis': identificar_causas(problema, metricas, logs),
            'impacto': avaliar_impacto(problema, metricas),
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(analise)

    except Exception as e:
        logger.error(f"Erro ao analisar problema: {str(e)}")
        return jsonify({'erro': str(e)}), 500

def identificar_tipo_problema(problema, metricas):
    """Identifica o tipo do problema com base nas métricas e logs."""
    # Implementar lógica de identificação
    return "desempenho"  # Exemplo

def calcular_severidade(metricas):
    """Calcula a severidade do problema."""
    # Implementar lógica de cálculo
    return "alta"  # Exemplo

def identificar_causas(problema, metricas, logs):
    """Identifica possíveis causas do problema."""
    # Implementar lógica de identificação
    return ["sobrecarga", "falha de recurso"]  # Exemplo

def avaliar_impacto(problema, metricas):
    """Avalia o impacto do problema no sistema."""
    # Implementar lógica de avaliação
    return {
        'usuarios_afetados': 100,
        'servicos_afetados': ['api', 'banco_dados']
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) 