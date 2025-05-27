#!/usr/bin/env python3
"""
Script para atualizar a memória compartilhada com a reorganização Docker
"""

from src.core.memoria.gerenciador_memoria import GerenciadorMemoria

def main():
    print("🧠 Atualizando memória compartilhada...")
    
    gm = GerenciadorMemoria()
    
    # Registrar a ação principal
    sucesso = gm.registrar_acao(
        'REORGANIZACAO_DOCKER_COMPLETA',
        'Reorganização completa da infraestrutura Docker: estrutura profissional por ambientes, segurança implementada, containers funcionais, documentação completa, testes 100% validados'
    )
    
    if sucesso:
        print("✅ Memória compartilhada atualizada com sucesso!")
        print("📊 Reorganização Docker registrada no histórico")
    else:
        print("❌ Erro ao atualizar memória compartilhada")

if __name__ == "__main__":
    main() 