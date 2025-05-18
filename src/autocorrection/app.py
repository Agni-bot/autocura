"""
Aplicação principal do serviço de autocorreção.
"""

from flask import Flask, jsonify, request
from autocura import SistemaAutocura
import logging
import os
import json

# Configuração do Flask
app = Flask(__name__)

# Configuração do logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'logs/autocorrection.log')
)

logger = logging.getLogger(__name__)

# Inicializa o sistema de autocura
sistema = SistemaAutocura()

@app.route('/health')
def health_check():
    """Endpoint para verificação de saúde do serviço."""
    return jsonify({
        'status': 'healthy',
        'versao': '1.0.0'
    })

@app.route('/api/v1/detectar-problemas', methods=['POST'])
def detectar_problemas():
    """Endpoint para detecção de problemas."""
    try:
        problemas = sistema.detectar_problemas()
        return jsonify({
            'status': 'sucesso',
            'problemas': problemas
        })
    except Exception as e:
        logger.error(f"Erro ao detectar problemas: {str(e)}")
        return jsonify({
            'status': 'erro',
            'mensagem': str(e)
        }), 500

@app.route('/api/v1/diagnosticar', methods=['POST'])
def diagnosticar():
    """Endpoint para diagnóstico de problemas."""
    try:
        dados = request.get_json()
        if not dados or 'problema' not in dados:
            return jsonify({
                'status': 'erro',
                'mensagem': 'Dados do problema não fornecidos'
            }), 400

        diagnostico = sistema.diagnosticar_problema(dados['problema'])
        return jsonify({
            'status': 'sucesso',
            'diagnostico': diagnostico
        })
    except Exception as e:
        logger.error(f"Erro ao diagnosticar problema: {str(e)}")
        return jsonify({
            'status': 'erro',
            'mensagem': str(e)
        }), 500

@app.route('/api/v1/gerar-acao', methods=['POST'])
def gerar_acao():
    """Endpoint para geração de ações corretivas."""
    try:
        dados = request.get_json()
        if not dados or 'diagnostico' not in dados:
            return jsonify({
                'status': 'erro',
                'mensagem': 'Diagnóstico não fornecido'
            }), 400

        acao = sistema.gerar_acao_correcao(dados['diagnostico'])
        return jsonify({
            'status': 'sucesso',
            'acao': acao
        })
    except Exception as e:
        logger.error(f"Erro ao gerar ação: {str(e)}")
        return jsonify({
            'status': 'erro',
            'mensagem': str(e)
        }), 500

@app.route('/api/v1/executar-correcao', methods=['POST'])
def executar_correcao():
    """Endpoint para execução de ações corretivas."""
    try:
        dados = request.get_json()
        if not dados or 'acao' not in dados:
            return jsonify({
                'status': 'erro',
                'mensagem': 'Ação não fornecida'
            }), 400

        sucesso = sistema.executar_correcao(dados['acao'])
        return jsonify({
            'status': 'sucesso',
            'resultado': 'sucesso' if sucesso else 'falha'
        })
    except Exception as e:
        logger.error(f"Erro ao executar correção: {str(e)}")
        return jsonify({
            'status': 'erro',
            'mensagem': str(e)
        }), 500

@app.route('/api/v1/verificar-efetividade', methods=['POST'])
def verificar_efetividade():
    """Endpoint para verificação de efetividade de ações."""
    try:
        dados = request.get_json()
        if not dados or 'acao' not in dados:
            return jsonify({
                'status': 'erro',
                'mensagem': 'Ação não fornecida'
            }), 400

        efetividade = sistema.verificar_efetividade(dados['acao'])
        return jsonify({
            'status': 'sucesso',
            'efetividade': efetividade
        })
    except Exception as e:
        logger.error(f"Erro ao verificar efetividade: {str(e)}")
        return jsonify({
            'status': 'erro',
            'mensagem': str(e)
        }), 500

@app.route('/api/v1/executar-ciclo', methods=['POST'])
def executar_ciclo():
    """Endpoint para execução de um ciclo completo de autocura."""
    try:
        relatorio = sistema.executar_ciclo_autocura()
        return jsonify({
            'status': 'sucesso',
            'relatorio': relatorio
        })
    except Exception as e:
        logger.error(f"Erro ao executar ciclo: {str(e)}")
        return jsonify({
            'status': 'erro',
            'mensagem': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 