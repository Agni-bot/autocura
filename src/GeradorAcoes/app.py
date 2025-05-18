from flask import Flask, jsonify, request
from gerador import GeradorAcoes

app = Flask(__name__)
gerador = GeradorAcoes()

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/gerar_acao', methods=['POST'])
def gerar_acao():
    try:
        diagnostico = request.json
        acao = gerador.gerar_acao(diagnostico)
        return jsonify(acao)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002) 