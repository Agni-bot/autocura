#!/usr/bin/env python3
"""
Implementação do gerador de ações do sistema.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import json
import random

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GeradorAcoes:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.memoria_path = self.base_dir / 'memoria' / 'memoria_compartilhada.json'
        self.estado: Dict[str, Any] = {
            'ciclo_atual': 0,
            'ultima_execucao': None,
            'acoes_geradas': [],
            'historico': []
        }
        self.acoes_disponiveis = {
            'cpu': [
                {
                    'tipo': 'escalonamento',
                    'acao': 'aumentar_replicas',
                    'descricao': 'Aumentar número de réplicas do serviço',
                    'parametros': {'incremento': 1}
                },
                {
                    'tipo': 'otimizacao',
                    'acao': 'reduzir_carga',
                    'descricao': 'Reduzir carga de processamento',
                    'parametros': {'reducao': 0.2}
                }
            ],
            'memoria': [
                {
                    'tipo': 'limpeza',
                    'acao': 'liberar_cache',
                    'descricao': 'Liberar memória cache',
                    'parametros': {'porcentagem': 0.5}
                },
                {
                    'tipo': 'otimizacao',
                    'acao': 'compactar_memoria',
                    'descricao': 'Compactar uso de memória',
                    'parametros': {'agressividade': 'media'}
                }
            ],
            'disco': [
                {
                    'tipo': 'limpeza',
                    'acao': 'remover_logs',
                    'descricao': 'Remover logs antigos',
                    'parametros': {'dias': 7}
                },
                {
                    'tipo': 'otimizacao',
                    'acao': 'compactar_dados',
                    'descricao': 'Compactar dados armazenados',
                    'parametros': {'nivel': 'medio'}
                }
            ],
            'latencia': [
                {
                    'tipo': 'otimizacao',
                    'acao': 'otimizar_queries',
                    'descricao': 'Otimizar consultas ao banco de dados',
                    'parametros': {'modo': 'agressivo'}
                },
                {
                    'tipo': 'cache',
                    'acao': 'aumentar_cache',
                    'descricao': 'Aumentar cache de consultas frequentes',
                    'parametros': {'fator': 1.5}
                }
            ],
            'erros': [
                {
                    'tipo': 'recuperacao',
                    'acao': 'reiniciar_servico',
                    'descricao': 'Reiniciar serviço com problemas',
                    'parametros': {'modo': 'suave'}
                },
                {
                    'tipo': 'fallback',
                    'acao': 'ativar_reserva',
                    'descricao': 'Ativar sistema de reserva',
                    'parametros': {'duracao': 300}
                }
            ]
        }
    
    async def carregar_memoria(self):
        """Carrega o estado atual da memória compartilhada."""
        try:
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
                    self.estado.update(memoria.get('estado_gerador', {}))
            logger.info("Memória do gerador carregada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar memória do gerador: {str(e)}")
            raise
    
    async def analisar_diagnostico(self) -> List[Dict[str, Any]]:
        """Analisa o diagnóstico atual e identifica problemas."""
        try:
            problemas = []
            
            # Carregar diagnóstico atual
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
                    diagnostico = memoria.get('estado_diagnostico', {}).get('diagnosticos', [])[-1]
            
            if not diagnostico:
                logger.warning("Nenhum diagnóstico encontrado")
                return problemas
            
            # Analisar anomalias
            if diagnostico.get('anomalia_detectada', False):
                problemas.append({
                    'tipo': 'anomalia',
                    'severidade': 'alta',
                    'descricao': 'Anomalia detectada no sistema'
                })
            
            # Analisar métricas críticas
            for metrica in diagnostico.get('metricas_criticas', []):
                problemas.append({
                    'tipo': metrica['tipo'],
                    'severidade': 'alta',
                    'descricao': metrica['mensagem'],
                    'valor': metrica['valor'],
                    'limite': metrica['limite']
                })
            
            # Analisar tendências
            for tendencia in diagnostico.get('tendencias', []):
                if tendencia['magnitude'] == 'significativa':
                    problemas.append({
                        'tipo': tendencia['tipo'],
                        'severidade': 'media',
                        'descricao': tendencia['mensagem']
                    })
            
            return problemas
        except Exception as e:
            logger.error(f"Erro ao analisar diagnóstico: {str(e)}")
            raise
    
    async def selecionar_acoes(self, problemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Seleciona ações apropriadas para os problemas identificados."""
        try:
            acoes_selecionadas = []
            
            for problema in problemas:
                tipo = problema['tipo']
                severidade = problema['severidade']
                
                if tipo in self.acoes_disponiveis:
                    # Selecionar ações baseadas na severidade
                    if severidade == 'alta':
                        # Para problemas graves, selecionar múltiplas ações
                        acoes = random.sample(self.acoes_disponiveis[tipo], 
                                           min(2, len(self.acoes_disponiveis[tipo])))
                    else:
                        # Para problemas menos graves, selecionar uma ação
                        acoes = [random.choice(self.acoes_disponiveis[tipo])]
                    
                    for acao in acoes:
                        acao_completa = {
                            'timestamp': datetime.now().isoformat(),
                            'problema': problema,
                            'acao': acao,
                            'prioridade': 'alta' if severidade == 'alta' else 'media',
                            'status': 'pendente'
                        }
                        acoes_selecionadas.append(acao_completa)
            
            return acoes_selecionadas
        except Exception as e:
            logger.error(f"Erro ao selecionar ações: {str(e)}")
            raise
    
    async def validar_acoes(self, acoes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida as ações selecionadas."""
        try:
            acoes_validadas = []
            
            for acao in acoes:
                # TODO: Implementar validação real
                # Por enquanto, apenas simula validação
                acao['validacao'] = {
                    'status': 'aprovada',
                    'timestamp': datetime.now().isoformat(),
                    'observacoes': 'Validação simulada'
                }
                acoes_validadas.append(acao)
            
            return acoes_validadas
        except Exception as e:
            logger.error(f"Erro ao validar ações: {str(e)}")
            raise
    
    async def atualizar_historico(self, acoes: List[Dict[str, Any]]):
        """Atualiza o histórico de ações."""
        try:
            for acao in acoes:
                self.estado['historico'].append(acao)
            
            # Manter apenas as últimas 1000 entradas
            if len(self.estado['historico']) > 1000:
                self.estado['historico'] = self.estado['historico'][-1000:]
            
            logger.info("Histórico de ações atualizado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao atualizar histórico: {str(e)}")
            raise
    
    async def atualizar_memoria(self):
        """Atualiza a memória compartilhada com o novo estado."""
        try:
            self.estado['ultima_execucao'] = datetime.now().isoformat()
            self.estado['ciclo_atual'] += 1
            
            # Carrega memória existente
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
            else:
                memoria = {}
            
            # Atualiza estado do gerador
            memoria['estado_gerador'] = self.estado
            
            # Salva memória atualizada
            with open(self.memoria_path, 'w', encoding='utf-8') as f:
                json.dump(memoria, f, indent=2, ensure_ascii=False)
            
            logger.info("Memória do gerador atualizada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao atualizar memória do gerador: {str(e)}")
            raise
    
    async def ciclo_geracao(self):
        """Executa um ciclo completo de geração de ações."""
        try:
            logger.info("Iniciando ciclo de geração de ações...")
            
            await self.carregar_memoria()
            problemas = await self.analisar_diagnostico()
            acoes = await self.selecionar_acoes(problemas)
            acoes_validadas = await self.validar_acoes(acoes)
            
            self.estado['acoes_geradas'] = acoes_validadas
            await self.atualizar_historico(acoes_validadas)
            await self.atualizar_memoria()
            
            logger.info(f"Ciclo de geração concluído. {len(acoes_validadas)} ações geradas")
            
        except Exception as e:
            logger.error(f"Erro durante o ciclo de geração: {str(e)}")
            raise
    
    async def executar_continuamente(self, intervalo: int = 300):  # 5 minutos
        """Executa ciclos de geração continuamente."""
        while True:
            try:
                await self.ciclo_geracao()
                await asyncio.sleep(intervalo)
            except Exception as e:
                logger.error(f"Erro no ciclo contínuo de geração: {str(e)}")
                await asyncio.sleep(intervalo)  # Aguarda antes de tentar novamente

async def main():
    """Função principal."""
    gerador = GeradorAcoes()
    await gerador.executar_continuamente()

if __name__ == '__main__':
    asyncio.run(main()) 