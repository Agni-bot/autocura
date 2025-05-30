#!/usr/bin/env python3
"""
Script unificado para atualizar memória compartilhada do Sistema AutoCura.
Permite registrar progresso de fases, marcos e ações importantes.
"""

import sys
from datetime import datetime
from src.core.memoria.gerenciador_memoria import GerenciadorMemoria


def atualizar_fase_beta(gm: GerenciadorMemoria):
    sucesso = gm.registrar_acao(
        'FASE_BETA_IMPLEMENTADA',
        'Fase Beta implementada com sucesso: SwarmCoordinator, BehaviorEmergence, SafeCodeGenerator, EvolutionSandbox, capacidades BFT, auto-modificação controlada, sandbox multi-tipo, validação ética, testes isolados.'
    )
    if sucesso:
        print("✅ Fase Beta registrada na memória compartilhada!")
    else:
        print("❌ Erro ao registrar Fase Beta")

def atualizar_reorganizacao_docker(gm: GerenciadorMemoria):
    sucesso = gm.registrar_acao(
        'REORGANIZACAO_DOCKER_COMPLETA',
        'Reorganização completa da infraestrutura Docker: estrutura profissional por ambientes, segurança implementada, containers funcionais, documentação completa, testes 100% validados'
    )
    if sucesso:
        print("✅ Reorganização Docker registrada na memória compartilhada!")
    else:
        print("❌ Erro ao registrar reorganização Docker")

def main():
    gm = GerenciadorMemoria()
    if len(sys.argv) < 2:
        print("Uso: python atualizar_memoria.py [fase_beta|docker]")
        sys.exit(1)
    acao = sys.argv[1]
    if acao == "fase_beta":
        atualizar_fase_beta(gm)
    elif acao == "docker":
        atualizar_reorganizacao_docker(gm)
    else:
        print("Ação não reconhecida. Use: fase_beta ou docker.")

if __name__ == "__main__":
    main() 