from flask import Flask, jsonify
from guardiao_cognitivo import GuardiaoCognitivo

app = Flask(__name__)
guardiao = GuardiaoCognitivo()

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/monitorar', methods=['POST'])
def monitorar():
    try:
        resultado = guardiao.monitorar()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006) 