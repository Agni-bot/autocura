from flask import Flask, render_template, jsonify, send_from_directory
import os

app = Flask(__name__, template_folder=".", static_folder="static")

# Define o diretório base para os templates e arquivos estáticos
# Isso é relativo à localização de frontend_server.py
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.template_folder = TEMPLATES_DIR
app.static_folder = STATIC_DIR

@app.route("/")
def index():
    """Serve a página principal do frontend."""
    return render_template("index.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    """Serve arquivos estáticos (CSS, JS, imagens)."""
    return send_from_directory(app.static_folder, filename)


@app.route("/api/services")
def get_services():
    """Fornece uma lista de serviços (mocked)."""
    services = [
        {
            "id": "diagnostico_cognitivo",
            "name": "Diagnóstico Cognitivo",
            "description": "Módulo para identificar e analisar falhas cognitivas no sistema.",
            "link": "#/services/diagnostico"
        },
        {
            "id": "autocorrecao_avancada",
            "name": "Autocorreção Avançada",
            "description": "Implementa mecanismos de correção autônoma para falhas detectadas.",
            "link": "#/services/autocorrecao"
        },
        {
            "id": "adaptacao_autonoma",
            "name": "Adaptação Autônoma",
            "description": "Permite que o sistema se adapte a novas situações e ambientes.",
            "link": "#/services/adaptacao"
        },
        {
            "id": "previsao_cenarios",
            "name": "Previsão de Cenários",
            "description": "Analisa dados para prever cenários econômicos, políticos e históricos.",
            "link": "#/services/previsao"
        },
        {
            "id": "consciencia_situacional",
            "name": "Consciência Situacional",
            "description": "Monitora e analisa o ambiente operacional em tempo real.",
            "link": "#/services/consciencia"
        },
        {
            "id": "financas_autocura",
            "name": "Finanças Autocura",
            "description": "Microsserviço para gestão financeira, trading e crowdfunding.",
            "link": "#/services/financas"
        }
    ]
    return jsonify(services)

if __name__ == "__main__":
    # Garante que o Flask escute em todas as interfaces de rede e na porta 8080
    # O modo debug não é recomendado para produção, mas útil para desenvolvimento.
    app.run(host="0.0.0.0", port=8080, debug=True)

