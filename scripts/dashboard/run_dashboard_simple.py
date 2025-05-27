#!/usr/bin/env python3
"""
Script simples para executar o Dashboard AutoCura
=================================================

Este script executa o sistema diretamente sem Docker,
útil para desenvolvimento e testes rápidos.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

# Cores para output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="info"):
    """Imprime mensagem com cor apropriada"""
    if status == "success":
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    elif status == "error":
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
    elif status == "warning":
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
    elif status == "info":
        print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")
    elif status == "header":
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def check_python():
    """Verifica se Python está instalado corretamente"""
    try:
        result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_status(f"Python encontrado: {result.stdout.strip()}", "success")
            return True
        return False
    except:
        return False

def check_requirements():
    """Verifica se os requirements estão instalados"""
    try:
        import fastapi
        import uvicorn
        import psutil
        print_status("Dependências principais encontradas", "success")
        return True
    except ImportError as e:
        print_status(f"Dependência faltando: {e}", "error")
        return False

def install_requirements():
    """Instala os requirements"""
    print_status("Instalando dependências...", "info")
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_status("Dependências instaladas com sucesso", "success")
            return True
        else:
            print_status(f"Erro ao instalar dependências: {result.stderr}", "error")
            return False
    except Exception as e:
        print_status(f"Erro ao executar pip: {e}", "error")
        return False

def check_files():
    """Verifica se os arquivos necessários existem"""
    required_files = [
        'main.py',
        'dashboard.html',
        'memoria_compartilhada.json'
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print_status(f"Arquivo {file} encontrado", "success")
        else:
            print_status(f"Arquivo {file} não encontrado", "error")
            all_exist = False
    
    return all_exist

def create_data_dirs():
    """Cria diretórios necessários"""
    dirs = ['data', 'data/metricas', 'logs']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print_status("Diretórios criados", "success")

def run_server():
    """Executa o servidor"""
    print_status("\nIniciando servidor AutoCura...", "header")
    
    # Define variáveis de ambiente
    env = os.environ.copy()
    env['HOST'] = '0.0.0.0'
    env['PORT'] = '8000'
    env['RELOAD'] = 'false'
    env['ENVIRONMENT'] = 'development'
    env['DEBUG'] = 'true'
    
    print_status("Configurações:", "info")
    print(f"  Host: 0.0.0.0")
    print(f"  Port: 8000")
    print(f"  Debug: true")
    
    # URLs de acesso
    print_status("\nACESSO AOS SERVIÇOS:", "header")
    print(f"{Colors.OKBLUE}Dashboard HTML:{Colors.ENDC} http://localhost:8000/")
    print(f"{Colors.OKBLUE}API Docs:{Colors.ENDC} http://localhost:8000/docs")
    print(f"{Colors.OKBLUE}API Root:{Colors.ENDC} http://localhost:8000/api")
    
    print_status("\nPressione Ctrl+C para parar o servidor", "warning")
    
    # Aguarda um pouco antes de abrir o navegador
    time.sleep(2)
    
    # Tenta abrir o navegador
    try:
        webbrowser.open('http://localhost:8000/')
    except:
        pass
    
    # Executa o servidor
    try:
        subprocess.run([sys.executable, 'main.py'], env=env)
    except KeyboardInterrupt:
        print_status("\nServidor parado pelo usuário", "info")
    except Exception as e:
        print_status(f"Erro ao executar servidor: {e}", "error")

def main():
    """Função principal"""
    print_status("EXECUÇÃO SIMPLES DO DASHBOARD AUTOCURA", "header")
    
    # 1. Verifica Python
    if not check_python():
        print_status("Python não encontrado corretamente", "error")
        sys.exit(1)
    
    # 2. Verifica arquivos necessários
    if not check_files():
        print_status("Arquivos necessários não encontrados", "error")
        sys.exit(1)
    
    # 3. Cria diretórios
    create_data_dirs()
    
    # 4. Verifica/instala dependências
    if not check_requirements():
        print_status("Instalando dependências necessárias...", "info")
        if not install_requirements():
            print_status("Falha ao instalar dependências", "error")
            sys.exit(1)
    
    # 5. Executa o servidor
    run_server()

if __name__ == "__main__":
    main() 