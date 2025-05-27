#!/usr/bin/env python3
"""
Demo Dashboard Integrado - Sistema AutoCura
==========================================

Demonstração do dashboard totalmente integrado com a Interface de Aprovação Manual.
"""

import webbrowser
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

def start_dashboard_server():
    """Inicia o servidor do dashboard"""
    
    class DashboardHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            super().end_headers()
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    httpd = HTTPServer(('localhost', 8080), DashboardHandler)
    print("🌐 Dashboard rodando em http://localhost:8080")
    httpd.serve_forever()

def print_instructions():
    """Mostra instruções de uso"""
    
    print("""
🤖 SISTEMA AUTOCURA - DASHBOARD INTEGRADO
========================================

🚀 COMO TESTAR A INTERFACE DE APROVAÇÃO MANUAL:

1. 📱 Acesse o Dashboard: http://localhost:8080
2. 🔘 Clique na aba "🤖 Aprovações" 
3. 🔄 Clique em "Buscar Novas Sugestões"
4. 👁️  Veja as 4 sugestões carregadas da API
5. ✅ Teste aplicar uma melhoria
6. 👁️  Use "Ver Código" para preview
7. 📊 Observe as estatísticas atualizando

🎯 SUGESTÕES DISPONÍVEIS:
• 🚀 Otimização de Cache Redis (Alta Prioridade)
• 🐛 Correção de Vazamento de Memória (Média)
• ✨ Auto-Backup Inteligente (Baixa) 
• 🛡️ Fortalecimento 2FA (Crítica)

🔥 FUNCIONALIDADES DEMONSTRADAS:
• Auto-modificação em linguagem natural
• Preview de código em tempo real
• Aplicação com feedback visual
• Estatísticas dinâmicas
• API totalmente funcional

⚡ SERVIÇOS RODANDO:
• Dashboard: http://localhost:8080
• API Sugestões: http://localhost:8001

🎮 Para parar: Ctrl+C
""")

def main():
    """Função principal"""
    
    print_instructions()
    
    try:
        # Inicia servidor em thread separada
        server_thread = threading.Thread(target=start_dashboard_server, daemon=True)
        server_thread.start()
        
        # Aguarda um pouco e abre o browser
        time.sleep(2)
        print("🌐 Abrindo navegador...")
        webbrowser.open('http://localhost:8080')
        
        print("\n✅ Sistema totalmente integrado e funcionando!")
        print("📱 Navegue para a aba '🤖 Aprovações' para testar")
        print("⏸️  Pressione Ctrl+C para parar...")
        
        # Mantém o script rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⏹️  Dashboard encerrado pelo usuário.")
            
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main() 