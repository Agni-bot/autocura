#!/usr/bin/env python3
"""
Script Modular para Executar o Dashboard AutoCura
=================================================

Este script executa o sistema de forma modular e configurável,
permitindo fácil customização de porta e outras configurações.
"""

import os
import sys
import subprocess
import time
import webbrowser
import argparse
from pathlib import Path
from typing import Dict, Optional

# Adiciona o diretório raiz ao path para imports corretos
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Configurações padrão
DEFAULT_CONFIG = {
    'host': '0.0.0.0',
    'port': 8080,  # Mudando para 8080 como padrão
    'reload': False,
    'environment': 'development',
    'debug': True,
    'log_level': 'INFO'
}

class Colors:
    """Cores para output no terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class DashboardRunner:
    """Classe principal para executar o dashboard de forma modular"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializa o runner com configurações
        
        Args:
            config: Dicionário de configurações (opcional)
        """
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        self.root_dir = ROOT_DIR
        
    def print_status(self, message: str, status: str = "info") -> None:
        """Imprime mensagem com cor apropriada"""
        colors = {
            "success": Colors.OKGREEN,
            "error": Colors.FAIL,
            "warning": Colors.WARNING,
            "info": Colors.OKBLUE,
            "header": Colors.HEADER
        }
        
        if status == "header":
            print(f"\n{colors[status]}{Colors.BOLD}{'='*60}{Colors.ENDC}")
            print(f"{colors[status]}{Colors.BOLD}{message}{Colors.ENDC}")
            print(f"{colors[status]}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        else:
            icon = {
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️"
            }.get(status, "")
            print(f"{colors.get(status, '')}{icon} {message}{Colors.ENDC}")
    
    def check_python(self) -> bool:
        """Verifica se Python está instalado corretamente"""
        try:
            result = subprocess.run(
                [sys.executable, '--version'], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                self.print_status(f"Python encontrado: {result.stdout.strip()}", "success")
                return True
            return False
        except:
            return False
    
    def check_requirements(self) -> bool:
        """Verifica se os requirements estão instalados"""
        required_modules = ['fastapi', 'uvicorn', 'psutil']
        missing = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing.append(module)
        
        if missing:
            self.print_status(f"Dependências faltando: {', '.join(missing)}", "error")
            return False
        
        self.print_status("Todas as dependências encontradas", "success")
        return True
    
    def install_requirements(self) -> bool:
        """Instala os requirements"""
        self.print_status("Instalando dependências...", "info")
        requirements_path = self.root_dir / 'requirements.txt'
        
        if not requirements_path.exists():
            self.print_status("requirements.txt não encontrado", "error")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)],
                capture_output=True,
                text=True,
                cwd=str(self.root_dir)
            )
            if result.returncode == 0:
                self.print_status("Dependências instaladas com sucesso", "success")
                return True
            else:
                self.print_status(f"Erro ao instalar: {result.stderr}", "error")
                return False
        except Exception as e:
            self.print_status(f"Erro ao executar pip: {e}", "error")
            return False
    
    def check_files(self) -> bool:
        """Verifica se os arquivos necessários existem"""
        required_files = [
            'main.py',
            'dashboard.html',
            'memoria_compartilhada.json'
        ]
        
        all_exist = True
        for file in required_files:
            file_path = self.root_dir / file
            if file_path.exists():
                self.print_status(f"Arquivo {file} encontrado", "success")
            else:
                self.print_status(f"Arquivo {file} não encontrado em {self.root_dir}", "error")
                all_exist = False
        
        return all_exist
    
    def create_data_dirs(self) -> None:
        """Cria diretórios necessários"""
        dirs = ['data', 'data/metricas', 'logs']
        for dir_name in dirs:
            dir_path = self.root_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
        self.print_status("Diretórios criados/verificados", "success")
    
    def check_port_available(self) -> bool:
        """Verifica se a porta está disponível"""
        import socket
        
        port = self.config['port']
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                self.print_status(f"Porta {port} está disponível", "success")
                return True
        except OSError:
            self.print_status(f"Porta {port} já está em uso", "error")
            return False
    
    def run_server(self) -> None:
        """Executa o servidor"""
        self.print_status("INICIANDO SERVIDOR AUTOCURA", "header")
        
        # Verifica se a porta está disponível
        if not self.check_port_available():
            self.print_status("Tentando porta alternativa...", "warning")
            # Tenta portas alternativas
            for alt_port in [8000, 8001, 8081, 8082]:
                self.config['port'] = alt_port
                if self.check_port_available():
                    break
            else:
                self.print_status("Nenhuma porta disponível encontrada", "error")
                return
        
        # Define variáveis de ambiente
        env = os.environ.copy()
        env.update({
            'HOST': str(self.config['host']),
            'PORT': str(self.config['port']),
            'RELOAD': str(self.config['reload']).lower(),
            'ENVIRONMENT': self.config['environment'],
            'DEBUG': str(self.config['debug']).lower(),
            'LOG_LEVEL': self.config['log_level']
        })
        
        # Mostra configurações
        self.print_status("Configurações:", "info")
        for key, value in self.config.items():
            print(f"  {key}: {value}")
        
        # URLs de acesso
        port = self.config['port']
        self.print_status("\nACESSO AOS SERVIÇOS:", "header")
        print(f"{Colors.OKBLUE}Dashboard HTML:{Colors.ENDC} http://localhost:{port}/")
        print(f"{Colors.OKBLUE}API Docs:{Colors.ENDC} http://localhost:{port}/docs")
        print(f"{Colors.OKBLUE}API Root:{Colors.ENDC} http://localhost:{port}/api")
        print(f"{Colors.OKBLUE}Health Check:{Colors.ENDC} http://localhost:{port}/api/health")
        
        self.print_status("\nPressione Ctrl+C para parar o servidor", "warning")
        
        # Aguarda um pouco antes de abrir o navegador
        time.sleep(2)
        
        # Tenta abrir o navegador
        try:
            webbrowser.open(f'http://localhost:{port}/')
        except:
            pass
        
        # Executa o servidor
        main_py = self.root_dir / 'main.py'
        try:
            subprocess.run(
                [sys.executable, str(main_py)], 
                env=env,
                cwd=str(self.root_dir)
            )
        except KeyboardInterrupt:
            self.print_status("\nServidor parado pelo usuário", "info")
        except Exception as e:
            self.print_status(f"Erro ao executar servidor: {e}", "error")
    
    def run(self) -> None:
        """Executa o processo completo"""
        self.print_status("DASHBOARD AUTOCURA - EXECUÇÃO MODULAR", "header")
        
        # 1. Verifica Python
        if not self.check_python():
            self.print_status("Python não encontrado corretamente", "error")
            sys.exit(1)
        
        # 2. Muda para o diretório raiz
        os.chdir(str(self.root_dir))
        self.print_status(f"Diretório de trabalho: {self.root_dir}", "info")
        
        # 3. Verifica arquivos necessários
        if not self.check_files():
            self.print_status("Arquivos necessários não encontrados", "error")
            sys.exit(1)
        
        # 4. Cria diretórios
        self.create_data_dirs()
        
        # 5. Verifica/instala dependências
        if not self.check_requirements():
            self.print_status("Instalando dependências necessárias...", "info")
            if not self.install_requirements():
                self.print_status("Falha ao instalar dependências", "error")
                sys.exit(1)
        
        # 6. Executa o servidor
        self.run_server()

def main():
    """Função principal com parsing de argumentos"""
    parser = argparse.ArgumentParser(
        description='Executa o Dashboard AutoCura de forma modular'
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=DEFAULT_CONFIG['port'],
        help=f'Porta do servidor (padrão: {DEFAULT_CONFIG["port"]})'
    )
    parser.add_argument(
        '--host',
        default=DEFAULT_CONFIG['host'],
        help=f'Host do servidor (padrão: {DEFAULT_CONFIG["host"]})'
    )
    parser.add_argument(
        '--reload', '-r',
        action='store_true',
        help='Ativa auto-reload para desenvolvimento'
    )
    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Não abre o navegador automaticamente'
    )
    
    args = parser.parse_args()
    
    # Configura baseado nos argumentos
    config = DEFAULT_CONFIG.copy()
    config['port'] = args.port
    config['host'] = args.host
    config['reload'] = args.reload
    
    # Cria e executa o runner
    runner = DashboardRunner(config)
    
    # Desativa abertura do navegador se solicitado
    if args.no_browser:
        runner.open_browser = False
    
    runner.run()

if __name__ == "__main__":
    main() 