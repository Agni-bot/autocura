#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

def criar_diretorio(path):
    """Cria diretório se não existir."""
    os.makedirs(path, exist_ok=True)

def mover_arquivo(origem, destino):
    """Move arquivo para novo local."""
    if os.path.exists(origem):
        shutil.move(origem, destino)

def reorganizar_scripts():
    """Reorganiza scripts em suas respectivas pastas."""
    # Criar diretórios
    criar_diretorio("deployment/scripts")
    criar_diretorio("deployment/build")
    criar_diretorio("modulos/diagnostico/scripts")
    
    # Mover scripts de diagnóstico
    for script in Path("scripts").glob("*_diagnostico_*.sh"):
        mover_arquivo(script, f"modulos/diagnostico/scripts/{script.name}")
    
    # Mover scripts de instalação
    for script in Path("scripts").glob("0*_*.sh"):
        mover_arquivo(script, f"deployment/scripts/{script.name}")
    
    # Mover scripts de build
    for script in Path("scripts").glob("build*.sh"):
        mover_arquivo(script, f"deployment/build/{script.name}")

def reorganizar_tests():
    """Reorganiza testes em seus respectivos módulos."""
    # Criar diretórios de teste em cada módulo
    for modulo in Path("modulos").iterdir():
        if modulo.is_dir():
            criar_diretorio(f"{modulo}/tests")
    
    # Mover testes específicos para seus módulos
    for modulo in Path("modulos").iterdir():
        if modulo.is_dir():
            for test_file in Path("tests/unit").glob(f"test_{modulo.name}_*.py"):
                mover_arquivo(test_file, f"{modulo}/tests/{test_file.name}")

def limpar_test_results():
    """Limpa resultados antigos de testes."""
    for file in Path("test-results").glob("*"):
        if file.is_file() and not file.name in ["report.html", "junit.xml"]:
            file.unlink()

def main():
    """Função principal."""
    print("Iniciando reorganização...")
    
    # Reorganizar scripts
    print("Reorganizando scripts...")
    reorganizar_scripts()
    
    # Reorganizar testes
    print("Reorganizando testes...")
    reorganizar_tests()
    
    # Limpar resultados de teste
    print("Limpando resultados de teste...")
    limpar_test_results()
    
    print("Reorganização concluída!")

if __name__ == "__main__":
    main() 