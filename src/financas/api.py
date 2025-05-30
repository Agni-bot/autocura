from flask import Flask, jsonify, request
from .forex_trader import ForexEA
from .crowdfunding_integrator import CrowdfundingIntegrator
from .risk_manager import RiskManager
import os

app = Flask(__name__)

# --- Configuração Inicial (Exemplo - Idealmente viria de config files ou env vars) ---
# Para ForexEA - ATENÇÃO: Use credenciais de DEMO para testes.
# Em produção, use variáveis de ambiente ou um sistema de gerenciamento de segredos.
MT5_LOGIN = int(os.environ.get("MT5_LOGIN", 12345678))
MT5_PASSWORD = os.environ.get("MT5_PASSWORD", "password")
MT5_SERVER = os.environ.get("MT5_SERVER", "YourBroker-Demo")

# Inicialização dos componentes (pode ser melhorada com injeção de dependência)
# Idealmente, a inicialização do MT5 seria feita sob demanda ou em um worker separado
# para não bloquear a API na inicialização se o MT5 não estiver disponível.
forex_ea = ForexEA(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
crowdfunding_integrator = CrowdfundingIntegrator() # API Key opcional para dados públicos
risk_manager = RiskManager()
risk_manager.update_portfolio_value(100000) # Valor inicial de exemplo para o portfólio

@app.route("/financas/status", methods=["GET"])
def get_financas_status():
    """Retorna o status geral do módulo de finanças."""
    # forex_status = "MT5 Inicializado" if forex_ea.initialized else "MT5 Não Inicializado ou Falhou"
    # if not forex_ea.MT5_AVAILABLE:
    #     forex_status = "MT5 Biblioteca Não Disponível (Simulado)"
    
    # Simplificando para não depender do estado de inicialização do MT5 na API de status
    forex_lib_status = "Disponível" if forex_ea.MT5_AVAILABLE else "Não Disponível (Simulado)"

    return jsonify({
        "message": "Status do Módulo de Finanças",
        "forex_expert_advisor": {
            "mt5_library_status": forex_lib_status,
            "symbol": forex_ea.symbol
        },
        "crowdfunding_integrator": {
            "platform_url": crowdfunding_integrator.platform_base_url
        },
        "risk_manager": risk_manager.get_current_risk_status()
    }), 200

# --- Endpoints para Forex Trading ---
@app.route("/financas/forex/price/<symbol>", methods=["GET"])
def get_forex_price(symbol):
    """Obtém o preço atual para um símbolo Forex."""
    # Temporariamente, vamos usar o símbolo padrão do EA, mas idealmente o EA seria instanciado por símbolo
    if symbol.upper() != forex_ea.symbol:
        # Poderíamos ter um pool de EAs ou instanciar um novo aqui, mas simplificamos
        return jsonify({"error": f"Símbolo {symbol} não é o símbolo principal configurado ({forex_ea.symbol}). Esta API de exemplo só suporta o símbolo principal."}), 400
    
    price = forex_ea.get_current_price()
    if price:
        return jsonify({"symbol": symbol, "ask_price": price}), 200
    else:
        return jsonify({"error": f"Não foi possível obter o preço para {symbol}"}), 500

@app.route("/financas/forex/trade", methods=["POST"])
def execute_forex_trade():
    """Executa uma ordem de trade no Forex."""
    data = request.get_json()
    if not data or "operation" not in data or "volume" not in data or "symbol" not in data:
        return jsonify({"error": "Dados inválidos. Forneça 'symbol', 'operation' (buy/sell) e 'volume'."}), 400

    symbol = data["symbol"]
    operation = data["operation"]
    volume = float(data["volume"])

    if symbol.upper() != forex_ea.symbol:
         return jsonify({"error": f"Símbolo {symbol} não é o símbolo principal configurado ({forex_ea.symbol})."}), 400

    # Gerenciamento de Risco Básico (exemplo)
    # Supondo que o risco do trade é o volume * um valor nocional * um stop loss percentual
    # Este é um cálculo muito simplificado. O RiskManager deveria ser mais integrado.
    # current_price = forex_ea.get_current_price()
    # if not current_price: 
    #     return jsonify({"error": "Não foi possível obter preço para cálculo de risco"}), 500
    # potential_loss_example = volume * 100000 * 0.01 # Ex: 1% de 1 lote de EURUSD
    # if not risk_manager.can_open_new_trade(potential_loss_example):
    #     return jsonify({"error": "Trade excede limites de risco definidos."}), 403

    result = forex_ea.execute_trade(operation=operation, volume=volume)
    if result:
        # if result.get("retcode") == forex_ea.mt5.TRADE_RETCODE_DONE or result.get("retcode") == "SIMULATED_DONE":
        #     risk_manager.add_trade_risk(potential_loss_example) # Adicionar risco se o trade for bem sucedido
        return jsonify(result), 200
    else:
        return jsonify({"error": "Falha ao executar trade."}), 500

# --- Endpoints para Crowdfunding ---
@app.route("/financas/crowdfunding/search", methods=["GET"])
def search_crowdfunding_projects():
    """Busca projetos de crowdfunding."""
    query = request.args.get("query")
    category = request.args.get("category")
    limit = int(request.args.get("limit", 5))

    if not query:
        return jsonify({"error": "Parâmetro 'query' é obrigatório."}), 400

    projects = crowdfunding_integrator.search_projects(query=query, category=category, limit=limit)
    return jsonify({"query": query, "projects_found": len(projects), "projects": projects}), 200

@app.route("/financas/crowdfunding/project/<project_id>", methods=["GET"])
def get_crowdfunding_project_details(project_id):
    """Obtém detalhes de um projeto de crowdfunding específico."""
    details = crowdfunding_integrator.get_project_details(project_id)
    if details:
        return jsonify(details), 200
    else:
        return jsonify({"error": f"Projeto com ID {project_id} não encontrado ou falha ao buscar detalhes."}), 404

# --- Endpoints para Risk Management ---
@app.route("/financas/risk/status", methods=["GET"])
def get_risk_status_api():
    """Retorna o status atual de risco do portfólio."""
    return jsonify(risk_manager.get_current_risk_status()), 200

@app.route("/financas/risk/portfolio_value", methods=["POST"])
def update_portfolio_value_api():
    """Atualiza o valor do portfólio para o gerenciador de risco."""
    data = request.get_json()
    if not data or "value" not in data:
        return jsonify({"error": "Dados inválidos. Forneça 'value' para o portfólio."}), 400
    
    try:
        value = float(data["value"])
        risk_manager.update_portfolio_value(value)
        return jsonify({"message": "Valor do portfólio atualizado com sucesso.", "new_status": risk_manager.get_current_risk_status()}), 200
    except ValueError:
        return jsonify({"error": "Valor inválido para o portfólio. Deve ser um número."}), 400


if __name__ == "__main__":
    # Para rodar localmente: flask run --port 5001 (ou o nome do arquivo: flask --app api run --port 5001)
    # É importante que as dependências (Flask, MetaTrader5, requests) estejam instaladas.
    print("Para iniciar a API Flask do módulo de Finanças, execute:")
    print("  export FLASK_APP=api.py")
    print("  flask run --host=0.0.0.0 --port=5001")
    app.run(host="0.0.0.0", port=5001, debug=True)

