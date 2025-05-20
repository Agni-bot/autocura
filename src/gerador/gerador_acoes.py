#!/usr/bin/env python3
"""
Implementação do gerador de ações do sistema.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import random

from ..memoria.gerenciador_memoria import GerenciadorMemoria
from ..etica.validador_etico import ValidadorEtico

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gerador_acoes")

class GeradorAcoes:
    """Gerador de Ações - Responsável pela geração e execução de ações do sistema"""
    
    def __init__(self, gerenciador_memoria: GerenciadorMemoria, validador_etico: ValidadorEtico):
        self.gerenciador_memoria = gerenciador_memoria
        self.validador_etico = validador_etico
        self.acoes_pendentes = []
        self.acoes_executadas = []
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
        logger.info("Gerador de Ações inicializado")
    
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
    
    def gerar_acao(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Gera uma nova ação baseada no contexto"""
        # Analisar contexto
        tipo_acao = self._determinar_tipo_acao(contexto)
        prioridade = self._calcular_prioridade(contexto)
        
        # Criar ação
        acao = {
            "id": f"acao_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "tipo": tipo_acao,
            "prioridade": prioridade,
            "contexto": contexto,
            "estado": "pendente",
            "timestamp_criacao": datetime.now().isoformat(),
            "dependencias": self._identificar_dependencias(contexto),
            "recursos_necessarios": self._calcular_recursos(contexto),
            "estimativa_duracao": self._estimar_duracao(contexto),
            "riscos": self._avaliar_riscos(contexto)
        }
        
        # Validar ação
        validacao = self.validador_etico.validar_acao(acao)
        if not validacao["aprovada"]:
            logger.warning(f"Ação {acao['id']} não aprovada pela validação ética")
            acao["estado"] = "rejeitada"
            acao["motivo_rejeicao"] = "falha_validacao_etica"
        else:
            self.acoes_pendentes.append(acao)
            logger.info(f"Nova ação gerada: {acao['id']}")
        
        # Registrar ação
        self.gerenciador_memoria.registrar_acao(acao)
        
        return acao
    
    def _determinar_tipo_acao(self, contexto: Dict[str, Any]) -> str:
        """Determina o tipo de ação baseado no contexto"""
        if contexto.get("tipo") == "correcao":
            return "hotfix"
        elif contexto.get("tipo") == "melhoria":
            return "refatoracao"
        elif contexto.get("tipo") == "evolucao":
            return "redesign"
        else:
            return "manutencao"
    
    def _calcular_prioridade(self, contexto: Dict[str, Any]) -> int:
        """Calcula a prioridade da ação (1-5)"""
        fatores = {
            "impacto": contexto.get("impacto", 1),
            "urgencia": contexto.get("urgencia", 1),
            "complexidade": contexto.get("complexidade", 1)
        }
        
        # Fórmula de prioridade: (impacto * urgencia) / complexidade
        prioridade = (fatores["impacto"] * fatores["urgencia"]) / fatores["complexidade"]
        
        # Normalizar para escala 1-5
        return min(max(round(prioridade), 1), 5)
    
    def _identificar_dependencias(self, contexto: Dict[str, Any]) -> List[str]:
        """Identifica dependências da ação"""
        return contexto.get("dependencias", [])
    
    def _calcular_recursos(self, contexto: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula recursos necessários para a ação"""
        return {
            "cpu": contexto.get("recursos_cpu", 1),
            "memoria": contexto.get("recursos_memoria", 1),
            "armazenamento": contexto.get("recursos_armazenamento", 1),
            "rede": contexto.get("recursos_rede", 1)
        }
    
    def _estimar_duracao(self, contexto: Dict[str, Any]) -> int:
        """Estima a duração da ação em minutos"""
        complexidade = contexto.get("complexidade", 1)
        return complexidade * 30  # 30 minutos por nível de complexidade
    
    def _avaliar_riscos(self, contexto: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Avalia os riscos associados à ação"""
        riscos = []
        
        # Risco de falha
        if contexto.get("complexidade", 1) > 3:
            riscos.append({
                "tipo": "falha",
                "nivel": "alto",
                "descricao": "Alta complexidade pode levar a falhas"
            })
        
        # Risco de impacto
        if contexto.get("impacto", 1) > 3:
            riscos.append({
                "tipo": "impacto",
                "nivel": "alto",
                "descricao": "Alto impacto em caso de falha"
            })
        
        # Risco de dependência
        if len(contexto.get("dependencias", [])) > 2:
            riscos.append({
                "tipo": "dependencia",
                "nivel": "medio",
                "descricao": "Múltiplas dependências podem causar atrasos"
            })
        
        return riscos
    
    def executar_acao(self, acao_id: str) -> Dict[str, Any]:
        """Executa uma ação pendente"""
        # Encontrar ação
        acao = next((a for a in self.acoes_pendentes if a["id"] == acao_id), None)
        if not acao:
            raise ValueError(f"Ação {acao_id} não encontrada")
        
        # Verificar dependências
        if not self._verificar_dependencias(acao):
            logger.warning(f"Ação {acao_id} não pode ser executada: dependências não atendidas")
            return acao
        
        # Atualizar estado
        acao["estado"] = "em_execucao"
        acao["timestamp_inicio"] = datetime.now().isoformat()
        
        try:
            # Executar ação
            resultado = self._executar_acao_especifica(acao)
            
            # Atualizar estado
            acao["estado"] = "concluida"
            acao["timestamp_fim"] = datetime.now().isoformat()
            acao["resultado"] = resultado
            
            # Registrar sucesso
            logger.info(f"Ação {acao_id} executada com sucesso")
            
        except Exception as e:
            # Registrar falha
            acao["estado"] = "falha"
            acao["timestamp_fim"] = datetime.now().isoformat()
            acao["erro"] = str(e)
            logger.error(f"Falha na execução da ação {acao_id}: {str(e)}")
        
        # Atualizar memória
        self.gerenciador_memoria.registrar_acao(acao)
        
        # Remover da lista de pendentes
        self.acoes_pendentes.remove(acao)
        self.acoes_executadas.append(acao)
        
        return acao
    
    def _verificar_dependencias(self, acao: Dict[str, Any]) -> bool:
        """Verifica se todas as dependências da ação foram atendidas"""
        for dep_id in acao["dependencias"]:
            dep = next((a for a in self.acoes_executadas if a["id"] == dep_id), None)
            if not dep or dep["estado"] != "concluida":
                return False
        return True
    
    def _executar_acao_especifica(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ação específica baseada em seu tipo"""
        tipo_acao = acao["tipo"]
        
        if tipo_acao == "hotfix":
            return self._executar_hotfix(acao)
        elif tipo_acao == "refatoracao":
            return self._executar_refatoracao(acao)
        elif tipo_acao == "redesign":
            return self._executar_redesign(acao)
        else:
            return self._executar_manutencao(acao)
    
    def _executar_hotfix(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ação do tipo hotfix"""
        # Implementação específica para hotfix
        return {
            "tipo": "hotfix",
            "status": "sucesso",
            "alteracoes": acao["contexto"].get("alteracoes", [])
        }
    
    def _executar_refatoracao(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ação do tipo refatoração"""
        # Implementação específica para refatoração
        return {
            "tipo": "refatoracao",
            "status": "sucesso",
            "melhorias": acao["contexto"].get("melhorias", [])
        }
    
    def _executar_redesign(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ação do tipo redesign"""
        # Implementação específica para redesign
        return {
            "tipo": "redesign",
            "status": "sucesso",
            "evolucoes": acao["contexto"].get("evolucoes", [])
        }
    
    def _executar_manutencao(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma ação do tipo manutenção"""
        # Implementação específica para manutenção
        return {
            "tipo": "manutencao",
            "status": "sucesso",
            "tarefas": acao["contexto"].get("tarefas", [])
        }
    
    def obter_acoes_pendentes(self) -> List[Dict[str, Any]]:
        """Retorna a lista de ações pendentes"""
        return self.acoes_pendentes
    
    def obter_acoes_executadas(self) -> List[Dict[str, Any]]:
        """Retorna a lista de ações executadas"""
        return self.acoes_executadas
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre as ações"""
        total_acoes = len(self.acoes_executadas)
        acoes_sucesso = sum(1 for a in self.acoes_executadas if a["estado"] == "concluida")
        acoes_falha = sum(1 for a in self.acoes_executadas if a["estado"] == "falha")
        
        return {
            "total_acoes": total_acoes,
            "acoes_sucesso": acoes_sucesso,
            "acoes_falha": acoes_falha,
            "taxa_sucesso": acoes_sucesso / total_acoes if total_acoes > 0 else 0,
            "acoes_pendentes": len(self.acoes_pendentes)
        }

async def main():
    """Função principal."""
    gerenciador_memoria = GerenciadorMemoria()
    validador_etico = ValidadorEtico()
    gerador = GeradorAcoes(gerenciador_memoria, validador_etico)
    await gerador.executar_continuamente()

if __name__ == '__main__':
    asyncio.run(main()) 