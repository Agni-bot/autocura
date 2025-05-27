"""
Módulo de Consciência Situacional do Sistema de Autocura.
Responsável por integrar e contextualizar informações do ambiente.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import logging
import os
import json
from .core import AnalisadorSituacional, GeradorContexto, ProjetorConsequencias

# Configuração do Flask
app = Flask(__name__)

# Configuração do logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'logs/consciencia_situacional.log')
)
logger = logging.getLogger(__name__)

# Inicializa componentes
analisador = AnalisadorSituacional()
gerador = GeradorContexto()
projetor = ProjetorConsequencias()

@app.route('/health')
def health_check():
    """Verifica a saúde do serviço."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'consciencia_situacional'
    })

@app.route('/api/v1/analisar-situacao', methods=['POST'])
def analisar_situacao():
    """
    Analisa a situação atual do ambiente com base em métricas, logs e eventos.
    
    Returns:
        dict: Análise situacional do ambiente
    """
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        # Analisa a situação
        situacao = analisador.analisar(
            metricas=dados.get('metricas', {}),
            logs=dados.get('logs', []),
            eventos=dados.get('eventos', []),
            contexto=dados.get('contexto', {})
        )

        # Gera contexto
        contexto = gerador.gerar_contexto(situacao)

        # Projeta consequências
        projecao = projetor.projetar(contexto)

        return jsonify({
            'situacao': situacao,
            'contexto': contexto,
            'projecao': projecao,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Erro ao analisar situação: {str(e)}")
        return jsonify({'erro': str(e)}), 500

@app.route('/api/v1/atualizar-contexto', methods=['POST'])
def atualizar_contexto():
    """
    Atualiza o contexto do sistema com novas informações.
    
    Returns:
        dict: Status da atualização
    """
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({'erro': 'Dados não fornecidos'}), 400

        # Atualiza o contexto
        gerador.atualizar_contexto(dados)

        return jsonify({
            'status': 'sucesso',
            'mensagem': 'Contexto atualizado com sucesso',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Erro ao atualizar contexto: {str(e)}")
        return jsonify({'erro': str(e)}), 500

@app.route('/api/v1/obter-contexto', methods=['GET'])
def obter_contexto():
    """
    Obtém o contexto atual do sistema.
    
    Returns:
        dict: Contexto atual
    """
    try:
        contexto = gerador.obter_contexto()
        return jsonify({
            'contexto': contexto,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Erro ao obter contexto: {str(e)}")
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002) 