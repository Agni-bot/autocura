@echo off
echo ===== VERIFICANDO CONTAINERS DOCKER =====
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ===== PARANDO CONTAINERS ANTIGOS =====
docker stop autocura-dashboard 2>nul
docker stop autocura-api 2>nul
docker rm autocura-dashboard 2>nul
docker rm autocura-api 2>nul

echo.
echo ===== CONSTRUINDO NOVA IMAGEM DO DASHBOARD =====
docker build -t autocura-dashboard .

echo.
echo ===== INICIANDO CONTAINERS ATUALIZADOS =====
docker run -d --name autocura-dashboard -p 8080:80 autocura-dashboard
docker run -d --name autocura-api -p 8001:8001 python:3.11 python -c "
import http.server
import socketserver
import json
from datetime import datetime

class SuggestionsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/evolution/suggestions':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'success': True,
                'suggestions': [
                    {
                        'id': 'perf-opt-001',
                        'type': 'performance',
                        'priority': 'high',
                        'title': 'Otimização de Cache Redis',
                        'detection_description': 'Cache subutilizado',
                        'improvement_description': 'Cache inteligente',
                        'benefits_description': 'Melhoria de performance',
                        'metrics': {'impact': '+40%', 'risk': 'Baixo'}
                    }
                ]
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/evolution/apply':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'success': True, 'message': 'Aplicado com sucesso'}
            self.wfile.write(json.dumps(response).encode())

with socketserver.TCPServer(('', 8001), SuggestionsHandler) as httpd:
    httpd.serve_forever()
"

echo.
echo ===== CONTAINERS ATUALIZADOS =====
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo Dashboard: http://localhost:8080
echo API: http://localhost:8001
echo.
echo Navegue para a aba "Aprovacoes" no dashboard!
pause 