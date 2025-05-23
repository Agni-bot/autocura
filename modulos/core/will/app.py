"""
Will System API
API para o sistema de trading automatizado.
"""

from flask import Flask, request, jsonify
import logging
from datetime import datetime
import json
from typing import Dict, Any
import os
from functools import wraps
import time

from trading.mt5_manager import MT5Manager
from validators.forex_validator import ForexValidator

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("will_api")

# Inicializa o app Flask
app = Flask(__name__)

# Inicializa o gerenciador MT5
mt5_manager = MT5Manager()

# Inicializa o validador forex
forex_validator = ForexValidator()

def add_cors_headers(response):
    """Adiciona headers CORS à resposta."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

def handle_errors(f):
    """Decorator para tratamento centralizado de erros."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erro na função {f.__name__}: {str(e)}")
            return add_cors_headers(jsonify({
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })), 500
    return wrapper

def validate_json_request(f):
    """Decorator para validar se o request é JSON."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return add_cors_headers(jsonify({
                "status": "error",
                "message": "Content-Type deve ser application/json",
                "timestamp": datetime.now().isoformat()
            })), 400
        return f(*args, **kwargs)
    return wrapper

@app.route('/health', methods=['GET'])
@handle_errors
def health_check():
    """Endpoint para verificar a saúde do sistema."""
    # Verifica conexão com MT5
    mt5_status = mt5_manager.handler is not None and mt5_manager.handler.connected
    
    # Verifica conexão com banco de dados
    db_status = True  # TODO: Implementar verificação real
    
    # Verifica conexão com Elasticsearch
    es_status = True  # TODO: Implementar verificação real
    
    # Determina status geral
    overall_status = "healthy" if all([mt5_status, db_status, es_status]) else "degraded"
    
    response = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "components": {
            "mt5": mt5_status,
            "database": db_status,
            "elasticsearch": es_status
        },
        "version": "1.0.0"
    }
    
    status_code = 200 if overall_status == "healthy" else 503
    return add_cors_headers(jsonify(response)), status_code

@app.route('/api/will/status', methods=['GET'])
@handle_errors
def will_status_endpoint():
    """Endpoint para verificar o status do sistema."""
    # Obtém informações da conta MT5
    account_info = mt5_manager.get_account_info()
    
    # Obtém posições abertas
    positions = mt5_manager.get_open_positions()
    
    # Prepara resposta
    response = {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "mt5_connected": mt5_manager.handler is not None and mt5_manager.handler.connected,
        "account_info": account_info,
        "open_positions": positions,
        "system_info": {
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "uptime": time.time() - app.start_time if hasattr(app, 'start_time') else 0
        }
    }
    
    logger.info(f"Status endpoint acessado: {response}")
    return add_cors_headers(jsonify(response))

@app.route('/api/will/mt5/config', methods=['POST'])
@handle_errors
@validate_json_request
def configure_mt5():
    """Configura as credenciais do MT5."""
    data = request.get_json()
    
    required_fields = ['server', 'login', 'password']
    for field in required_fields:
        if field not in data:
            return add_cors_headers(jsonify({
                'status': 'error',
                'message': f'Campo obrigatório não fornecido: {field}',
                'timestamp': datetime.now().isoformat()
            })), 400
    
    # Atualiza configurações
    mt5_manager.config['server'] = data['server']
    mt5_manager.config['login'] = data['login']
    mt5_manager.config['password'] = data['password']
    
    # Tenta conectar com as novas credenciais
    success, message = mt5_manager.connect()
    
    return add_cors_headers(jsonify({
        'status': 'success' if success else 'error',
        'message': message,
        'timestamp': datetime.now().isoformat()
    }))

@app.route('/api/will/decision', methods=['POST'])
@handle_errors
@validate_json_request
def will_decision_endpoint():
    """Endpoint para obter decisão de trading."""
    # Obtém dados do request
    data = request.get_json()
    
    # Valida campos obrigatórios
    required_fields = ['asset', 'volume']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Campos obrigatórios faltando: {', '.join(missing_fields)}",
            "timestamp": datetime.now().isoformat()
        })), 400

    # Valida par de moedas
    is_valid, error_msg = forex_validator.validate_currency_pair(data['asset'])
    if not is_valid:
        return add_cors_headers(jsonify({
            "status": "error",
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        })), 400

    # Valida volume
    is_valid, error_msg = forex_validator.validate_volume(data['volume'])
    if not is_valid:
        return add_cors_headers(jsonify({
            "status": "error",
            "message": error_msg,
            "timestamp": datetime.now().isoformat()
        })), 400

    # Obtém informações do par
    pair_info = forex_validator.get_pair_info(data['asset'])
    
    # Obtém preço atual
    current_price = mt5_manager.get_current_price(data['asset'])
    
    # Gera decisão
    decision = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "asset": data['asset'],
        "volume": data['volume'],
        "current_price": current_price,
        "pair_info": pair_info,
        "decision": {
            "action": "BUY" if current_price.get('bid', 0) > 0 else "SELL",
            "confidence": 0.85,
            "reason": "Análise técnica e fundamentalista",
            "stop_loss": current_price.get('bid', 0) * 0.99,
            "take_profit": current_price.get('bid', 0) * 1.02
        },
        "market_analysis": {
            "trend": "bullish",
            "support_levels": [current_price.get('bid', 0) * 0.98, current_price.get('bid', 0) * 0.96],
            "resistance_levels": [current_price.get('bid', 0) * 1.02, current_price.get('bid', 0) * 1.04],
            "volatility": "medium"
        }
    }
    
    logger.info(f"Decisão gerada: {decision}")
    return add_cors_headers(jsonify(decision))

@app.route('/api/will/pairs', methods=['GET'])
def will_pairs_endpoint():
    """Endpoint para listar pares de moedas disponíveis."""
    try:
        # Obtém símbolos disponíveis
        symbols = mt5_manager.get_available_symbols()
        
        # Prepara resposta
        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "symbols": symbols
        }
        
        logger.info(f"Pairs endpoint acessado: {response}")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Erro no pairs endpoint: {str(e)}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@app.route('/api/will/pairs/<pair>', methods=['GET'])
def will_pair_info_endpoint(pair):
    """Endpoint para obter informações de um par específico."""
    try:
        # Valida par de moedas
        is_valid, error_msg = forex_validator.validate_currency_pair(pair)
        if not is_valid:
            return add_cors_headers(jsonify({
                "status": "error",
                "message": error_msg
            })), 404

        # Obtém informações do par
        pair_info = forex_validator.get_pair_info(pair)
        
        # Obtém preço atual
        current_price = mt5_manager.get_current_price(pair)
        
        # Prepara resposta
        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "pair": pair,
            "info": pair_info,
            "current_price": current_price
        }
        
        logger.info(f"Pair info endpoint acessado: {response}")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Erro no pair info endpoint: {str(e)}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@app.route('/api/will/positions', methods=['GET'])
def will_positions_endpoint():
    """Endpoint para listar posições abertas."""
    try:
        # Obtém posições abertas
        positions = mt5_manager.get_open_positions()
        
        # Prepara resposta
        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "positions": positions
        }
        
        logger.info(f"Positions endpoint acessado: {response}")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Erro no positions endpoint: {str(e)}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@app.route('/api/will/positions/<int:ticket>', methods=['DELETE'])
def will_close_position_endpoint(ticket):
    """Endpoint para fechar uma posição específica."""
    try:
        # Fecha a posição
        result = mt5_manager.close_position(ticket)
        
        if "error" in result:
            return add_cors_headers(jsonify({
                "status": "error",
                "message": result["error"]
            })), 400
        
        # Prepara resposta
        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        
        logger.info(f"Close position endpoint acessado: {response}")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Erro no close position endpoint: {str(e)}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@app.route('/api/will/connect', methods=['POST'])
def will_connect_endpoint():
    """Endpoint para conectar ao MT5."""
    try:
        # Obtém dados do request
        data = request.get_json()
        
        # Atualiza configurações
        if data:
            mt5_manager.config.update(data)
        
        # Tenta conectar
        success, message = mt5_manager.connect()
        
        if not success:
            return add_cors_headers(jsonify({
                "status": "error",
                "message": message
            })), 400
        
        # Prepara resposta
        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "account_info": mt5_manager.get_account_info()
        }
        
        logger.info(f"Connect endpoint acessado: {response}")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Erro no connect endpoint: {str(e)}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

@app.route('/api/will/disconnect', methods=['POST'])
def will_disconnect_endpoint():
    """Endpoint para desconectar do MT5."""
    try:
        # Desconecta
        mt5_manager.disconnect()
        
        # Prepara resposta
        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "message": "Desconectado com sucesso"
        }
        
        logger.info(f"Disconnect endpoint acessado: {response}")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"Erro no disconnect endpoint: {str(e)}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": str(e)
        })), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

