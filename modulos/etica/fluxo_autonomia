# Exemplo de Implementação do Fluxo de Autonomia

Este exemplo demonstra como implementar o mecanismo de transição entre níveis de autonomia, incluindo verificação de critérios para avanço e protocolos de reversão.

```python
from enum import Enum
import datetime
import logging
import json
from typing import Dict, List, Optional, Any, Tuple

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fluxo_autonomia")

class NivelAutonomia(Enum):
    """Níveis de autonomia do sistema"""
    NIVEL_1_ASSISTENCIA = 1
    NIVEL_2_AUTONOMIA_SUPERVISIONADA = 2
    NIVEL_3_AUTONOMIA_CONDICIONAL = 3
    NIVEL_4_AUTONOMIA_ALTA = 4
    NIVEL_5_AUTONOMIA_PLENA = 5

class EstadoTransicao(Enum):
    """Estados possíveis de uma transição de autonomia"""
    SOLICITADA = "solicitada"
    EM_TESTE = "em_teste"
    EM_APROVACAO = "em_aprovacao"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    CONCLUIDA = "concluida"
    REVERTIDA = "revertida"

class FluxoAutonomia:
    """Implementação do Fluxo de Autonomia"""
    
    def __init__(self, config_path: str = "/config/autonomia/niveis.yaml"):
        self.config_path = config_path
        self.criterios = self._carregar_criterios()
        self.nivel_atual = NivelAutonomia.NIVEL_1_ASSISTENCIA
        self.historico_transicoes = []
        self.transicoes_ativas = {}
        self.metricas_desempenho = {}
        logger.info("Fluxo de Autonomia inicializado no nível %s", self.nivel_atual.name)
    
    def _carregar_criterios(self) -> Dict[NivelAutonomia, Dict[str, Any]]:
        """Carrega critérios para transição entre níveis de autonomia"""
        # Simulação de carregamento - em produção, carregaria do arquivo
        return {
            NivelAutonomia.NIVEL_1_ASSISTENCIA: {
                "criterios_avanco": {
                    "precisao_minima": 0.95,
                    "falsos_negativos_maximos": 0,
                    "tempo_operacao_minimo": 90,  # dias
                    "incidentes_maximos": 0,
                    "validacao_etica_requerida": True
                },
                "permissoes": {
                    "diagnostico_autonomo": True,
                    "acoes_autonomas": False,
                    "refatoracao_autonoma": False,
                    "redesign_autonomo": False
                }
            },
            NivelAutonomia.NIVEL_2_AUTONOMIA_SUPERVISIONADA: {
                "criterios_avanco": {
                    "precisao_minima": 0.97,
                    "falsos_negativos_maximos": 0,
                    "tempo_operacao_minimo": 180,  # dias
                    "incidentes_maximos": 0,
                    "validacao_etica_requerida": True
                },
                "permissoes": {
                    "diagnostico_autonomo": True,
                    "acoes_autonomas": {
                        "hotfix": True,
                        "refatoracao": False,
                        "redesign": False
                    },
                    "refatoracao_autonoma": False,
                    "redesign_autonomo": False
                }
            },
            NivelAutonomia.NIVEL_3_AUTONOMIA_CONDICIONAL: {
                "criterios_avanco": {
                    "precisao_minima": 0.99,
                    "falsos_negativos_maximos": 0,
                    "tempo_operacao_minimo": 365,  # dias
                    "incidentes_maximos": 0,
                    "validacao_etica_requerida": True
                },
                "permissoes": {
                    "diagnostico_autonomo": True,
                    "acoes_autonomas": {
                        "hotfix": True,
                        "refatoracao": True,
                        "redesign": False
                    },
                    "refatoracao_autonoma": True,
                    "redesign_autonomo": False
                }
            },
            NivelAutonomia.NIVEL_4_AUTONOMIA_ALTA: {
                "criterios_avanco": {
                    "precisao_minima": 0.999,
                    "falsos_negativos_maximos": 0,
                    "tempo_operacao_minimo": 730,  # dias
                    "incidentes_maximos": 0,
                    "validacao_etica_requerida": True
                },
                "permissoes": {
                    "diagnostico_autonomo": True,
                    "acoes_autonomas": {
                        "hotfix": True,
                        "refatoracao": True,
                        "redesign": True
                    },
                    "refatoracao_autonoma": True,
                    "redesign_autonomo": True
                }
            },
            NivelAutonomia.NIVEL_5_AUTONOMIA_PLENA: {
                "criterios_avanco": None,  # Nível máximo, não há avanço
                "permissoes": {
                    "diagnostico_autonomo": True,
                    "acoes_autonomas": {
                        "hotfix": True,
                        "refatoracao": True,
                        "redesign": True,
                        "evolucao_arquitetural": True
                    },
                    "refatoracao_autonoma": True,
                    "redesign_autonomo": True,
                    "evolucao_autonoma": True
                }
            }
        }
    
    def solicitar_avanco_autonomia(self, solicitacao: Dict[str, Any]) -> str:
        """
        Solicita avanço para um nível superior de autonomia.
        
        Args:
            solicitacao: Objeto contendo detalhes da solicitação
            
        Returns:
            str: Identificador único da solicitação
        """
        nivel_atual = NivelAutonomia(solicitacao["nivel_atual"])
        nivel_solicitado = NivelAutonomia(solicitacao["nivel_solicitado"])
        
        # Validações básicas
        if nivel_atual != self.nivel_atual:
            raise ValueError(f"Nível atual informado ({nivel_atual.name}) não corresponde ao nível atual do sistema ({self.nivel_atual.name})")
        
        if nivel_solicitado.value <= nivel_atual.value:
            raise ValueError(f"Nível solicitado ({nivel_solicitado.name}) deve ser superior ao nível atual ({nivel_atual.name})")
        
        if nivel_solicitado.value > nivel_atual.value + 1:
            raise ValueError(f"Só é permitido avançar um nível por vez. Solicitado: {nivel_solicitado.name}, Atual: {nivel_atual.name}")
        
        # Verificar se já existe uma solicitação ativa
        for id_solicitacao, transicao in self.transicoes_ativas.items():
            if transicao["tipo"] == "avanco" and transicao["estado"] != EstadoTransicao.REJEITADA.value:
                raise ValueError(f"Já existe uma solicitação de avanço ativa: {id_solicitacao}")
        
        # Gerar ID único para a solicitação
        id_solicitacao = f"avanco_{nivel_atual.value}_para_{nivel_solicitado.value}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Registrar solicitação
        self.transicoes_ativas[id_solicitacao] = {
            "id": id_solicitacao,
            "tipo": "avanco",
            "nivel_origem": nivel_atual.value,
            "nivel_destino": nivel_solicitado.value,
            "estado": EstadoTransicao.SOLICITADA.value,
            "evidencias": solicitacao["evidencias"],
            "justificativa": solicitacao["justificativa"],
            "plano_monitoramento": solicitacao["plano_monitoramento"],
            "solicitante": solicitacao.get("solicitante", "sistema"),
            "timestamp_solicitacao": datetime.datetime.now().isoformat(),
            "historico_estados": [
                {
                    "estado": EstadoTransicao.SOLICITADA.value,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "comentario": "Solicitação inicial"
                }
            ]
        }
        
        logger.info("Solicitação de avanço registrada: %s -> %s (ID: %s)", 
                   nivel_atual.name, nivel_solicitado.name, id_solicitacao)
        
        # Iniciar verificação de critérios
        self._verificar_criterios_avanco(id_solicitacao)
        
        return id_solicitacao
    
    def _verificar_criterios_avanco(self, id_solicitacao: str) -> None:
        """Verifica se os critérios para avanço são atendidos"""
        transicao = self.transicoes_ativas[id_solicitacao]
        nivel_atual = NivelAutonomia(transicao["nivel_origem"])
        criterios = self.criterios[nivel_atual]["criterios_avanco"]
        
        # Obter métricas atuais de desempenho
        metricas = self._obter_metricas_desempenho()
        
        # Verificar cada critério
        criterios_atendidos = True
        resultados = []
        
        # Verificar precisão
        if metricas["precisao"] < criterios["precisao_minima"]:
            criterios_atendidos = False
            resultados.append({
                "criterio": "precisao_minima",
                "esperado": criterios["precisao_minima"],
                "atual": metricas["precisao"],
                "atendido": False
            })
        else:
            resultados.append({
                "criterio": "precisao_minima",
                "esperado": criterios["precisao_minima"],
                "atual": metricas["precisao"],
                "atendido": True
            })
        
        # Verificar falsos negativos
        if metricas["falsos_negativos"] > criterios["falsos_negativos_maximos"]:
            criterios_atendidos = False
            resultados.append({
                "criterio": "falsos_negativos_maximos",
                "esperado": criterios["falsos_negativos_maximos"],
                "atual": metricas["falsos_negativos"],
                "atendido": False
            })
        else:
            resultados.append({
                "criterio": "falsos_negativos_maximos",
                "esperado": criterios["falsos_negativos_maximos"],
                "atual": metricas["falsos_negativos"],
                "atendido": True
            })
        
        # Verificar tempo de operação
        if metricas["dias_operacao"] < criterios["tempo_operacao_minimo"]:
            criterios_atendidos = False
            resultados.append({
                "criterio": "tempo_operacao_minimo",
                "esperado": criterios["tempo_operacao_minimo"],
                "atual": metricas["dias_operacao"],
                "atendido": False
            })
        else:
            resultados.append({
                "criterio": "tempo_operacao_minimo",
                "esperado": criterios["tempo_operacao_minimo"],
                "atual": metricas["dias_operacao"],
                "atendido": True
            })
        
        # Verificar incidentes
        if metricas["incidentes"] > criterios["incidentes_maximos"]:
            criterios_atendidos = False
            resultados.append({
                "criterio": "incidentes_maximos",
                "esperado": criterios["incidentes_maximos"],
                "atual": metricas["incidentes"],
                "atendido": False
            })
        else:
            resultados.append({
                "criterio": "incidentes_maximos",
                "esperado": criterios["incidentes_maximos"],
                "atual": metricas["incidentes"],
                "atendido": True
            })
        
        # Verificar validação ética
        if criterios["validacao_etica_requerida"] and not metricas["validacao_etica_aprovada"]:
            criterios_atendidos = False
            resultados.append({
                "criterio": "validacao_etica_requerida",
                "esperado": True,
                "atual": metricas["validacao_etica_aprovada"],
                "atendido": False
            })
        else:
            resultados.append({
                "criterio": "validacao_etica_requerida",
                "esperado": True,
                "atual": metricas["validacao_etica_aprovada"],
                "atendido": True
            })
        
        # Atualizar estado da transição
        if criterios_atendidos:
            self._atualizar_estado_transicao(
                id_solicitacao, 
                EstadoTransicao.EM_TESTE, 
                "Critérios atendidos, iniciando período de teste"
            )
            # Iniciar período de teste
            self._iniciar_periodo_teste(id_solicitacao)
        else:
            self._atualizar_estado_transicao(
                id_solicitacao, 
                EstadoTransicao.REJEITADA, 
                f"Critérios não atendidos: {json.dumps(resultados)}"
            )
        
        # Registrar resultados da verificação
        transicao["resultados_verificacao"] = resultados
    
    def _obter_metricas_desempenho(self) -> Dict[str, Any]:
        """Obtém métricas atuais de desempenho do sistema"""
        # Em um sistema real, isso consultaria sistemas de monitoramento
        # Aqui simulamos valores para demonstração
        return {
            "precisao": 0.98,
            "falsos_negativos": 0,
            "dias_operacao": 200,
            "incidentes": 0,
            "validacao_etica_aprovada": True,
            "estabilidade_decisoes": 0.95,
            "coerencia_diagnosticos": 0.97,
            "eficacia_acoes": 0.96
        }
    
    def _atualizar_estado_transicao(self, id_solicitacao: str, novo_estado: EstadoTransicao, comentario: str) -> None:
        """Atualiza o estado de uma transição"""
        transicao = self.transicoes_ativas[id_solicitacao]
        transicao["estado"] = novo_estado.value
        transicao["historico_estados"].append({
            "estado": novo_estado.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "comentario": comentario
        })
        
        logger.info("Transição %s atualizada para estado %s: %s", 
                   id_solicitacao, novo_estado.value, comentario)
    
    def _iniciar_periodo_teste(self, id_solicitacao: str) -> None:
        """Inicia período de teste para uma transição"""
        # Em um sistema real, isso configuraria monitoramento especial
        # e agendaria a revisão após o período de teste
        transicao = self.transicoes_ativas[id_solicitacao]
        nivel_destino = NivelAutonomia(transicao["nivel_destino"])
        
        # Determinar duração do período de teste com base no nível
        duracao_teste = {
            NivelAutonomia.NIVEL_2_AUTONOMIA_SUPERVISIONADA: 30,  # dias
            NivelAutonomia.NIVEL_3_AUTONOMIA_CONDICIONAL: 60,  # dias
            NivelAutonomia.NIVEL_4_AUTONOMIA_ALTA: 90,  # dias
            NivelAutonomia.NIVEL_5_AUTONOMIA_PLENA: 180,  # dias
        }.get(nivel_destino, 30)
        
        # Registrar informações do teste
        transicao["teste"] = {
            "inicio": datetime.datetime.now().isoformat(),
            "duracao_prevista": duracao_teste,
            "fim_previsto": (datetime.datetime.now() + datetime.timedelta(days=duracao_teste)).isoformat(),
            "metricas_iniciais": self._obter_metricas_desempenho()
        }
        
        logger.info("Período de teste iniciado para transição %s. Duração: %d dias", 
                   id_solicitacao, duracao_teste)
        
        # Em um sistema real, aqui seria agendada a avaliação automática
        # após o período de teste. Para este exemplo, simulamos que o
        # período já passou e avançamos para aprovação.
        self._finalizar_periodo_teste(id_solicitacao)
    
    def _finalizar_periodo_teste(self, id_solicitacao: str) -> None:
        """Finaliza período de teste e avalia resultados"""
        transicao = self.transicoes_ativas[id_solicitacao]
        
        # Obter métricas atuais
        metricas_atuais = self._obter_metricas_desempenho()
        
        # Registrar métricas finais
        transicao["teste"]["fim_real"] = datetime.datetime.now().isoformat()
        transicao["teste"]["metricas_finais"] = metricas_atuais
        
        # Avaliar se houve degradação durante o teste
        metricas_iniciais = transicao["teste"]["metricas_iniciais"]
        degradacao = False
        resultados_teste = []
        
        for metrica, valor in metricas_atuais.items():
            if metrica in metricas_iniciais:
                if isinstance(valor, (int, float)) and isinstance(metricas_iniciais[metrica], (int, float)):
                    if metrica in ["precisao", "estabilidade_decisoes", "coerencia_diagnosticos", "eficacia_acoes"]:
                        if valor < metricas_iniciais[metrica] * 0.95:  # Permitir até 5% de degradação
                            degradacao = True
                            resultados_teste.append({
                                "metrica": metrica,
                                "inicial": metricas_iniciais[metrica],
                                "final": valor,
                                "variacao": valor - metricas_iniciais[metrica],
                                "status": "degradação"
                            })
                        else:
                            resultados_teste.append({
                                "metrica": metrica,
                                "inicial": metricas_iniciais[metrica],
                                "final": valor,
                                "variacao": valor - metricas_iniciais[metrica],
                                "status": "estável"
                            })
                    elif metrica in ["falsos_negativos", "incidentes"]:
                        if valor > metricas_iniciais[metrica]:
                            degradacao = True
                            resultados_teste.append({
                                "metrica": metrica,
                                "inicial": metricas_iniciais[metrica],
                                "final": valor,
                                "variacao": valor - metricas_iniciais[metrica],
                                "status": "degradação"
                            })
                        else:
                            resultados_teste.append({
                                "metrica": metrica,
                                "inicial": metricas_iniciais[metrica],
                                "final": valor,
                                "variacao": valor - metricas_iniciais[metrica],
                                "status": "estável"
                            })
        
        transicao["teste"]["resultados"] = resultados_teste
        
        if degradacao:
            self._atualizar_estado_transicao(
                id_solicitacao, 
                EstadoTransicao.REJEITADA, 
                f"Degradação detectada durante período de teste: {json.dumps(resultados_teste)}"
            )
        else:
            self._atualizar_estado_transicao(
                id_solicitacao, 
                EstadoTransicao.EM_APROVACAO, 
                "Período de teste concluído com sucesso, aguardando aprovação final"
            )
            # Em um sistema real, aqui seria notificado o comitê de aprovação
            # Para este exemplo, simulamos a aprovação automática
            self._aprovar_transicao(id_solicitacao)
    
    def _aprovar_transicao(self, id_solicitacao: str) -> None:
        """Aprova uma transição de autonomia"""
        self._atualizar_estado_transicao(
            id_solicitacao, 
            EstadoTransicao.APROVADA, 
            "Transição aprovada pelo comitê de governança"
        )
        
        # Implementar a transição
        self._implementar_transicao(id_solicitacao)
    
    def _implementar_transicao(self, id_solicitacao: str) -> None:
        """Implementa uma transição aprovada"""
        transicao = self.transicoes_ativas[id_solicitacao]
        nivel_destino = NivelAutonomia(transicao["nivel_destino"])
        
        # Atualizar nível de autonomia
        nivel_anterior = self.nivel_atual
        self.nivel_atual = nivel_destino
        
        # Registrar conclusão da transição
        self._atualizar_estado_transicao(
            id_solicitacao, 
            EstadoTransicao.CONCLUIDA, 
            f"Transição concluída: {nivel_anterior.name} -> {nivel_destino.name}"
        )
        
        # Mover para histórico
        self.historico_transicoes.append(self.transicoes_ativas.pop(id_solicitacao))
        
        logger.info("Transição %s implementada com sucesso. Novo nível: %s", 
                   id_solicitacao, nivel_destino.name)
        
        # Notificar stakeholders
        self._notificar_transicao_autonomia({
            "tipo": "avanco",
            "nivel_anterior": nivel_anterior.value,
            "nivel_atual": nivel_destino.value,
            "id_transicao": id_solicitacao,
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    def acionar_reversao_autonomia(self, reversao: Dict[str, Any]) -> bool:
        """
        Aciona reversão para um nível inferior de autonomia.
        
        Args:
            reversao: Objeto contendo detalhes da reversão
            
        Returns:
            bool: True se reversão foi iniciada com sucesso
        """
        nivel_atual = NivelAutonomia(reversao["nivel_atual"])
        nivel_alvo = NivelAutonomia(reversao["nivel_alvo"])
        
        # Validações básicas
        if nivel_atual != self.nivel_atual:
            raise ValueError(f"Nível atual informado ({nivel_atual.name}) não corresponde ao nível atual do sistema ({self.nivel_atual.name})")
        
        if nivel_alvo.value >= nivel_atual.value:
            raise ValueError(f"Nível alvo ({nivel_alvo.name}) deve ser inferior ao nível atual ({nivel_atual.name})")
        
        # Gerar ID único para a reversão
        id_reversao = f"reversao_{nivel_atual.value}_para_{nivel_alvo.value}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Registrar reversão
        self.transicoes_ativas[id_reversao] = {
            "id": id_reversao,
            "tipo": "reversao",
            "nivel_origem": nivel_atual.value,
            "nivel_destino": nivel_alvo.value,
            "estado": EstadoTransicao.APROVADA.value,  # Reversões são aprovadas automaticamente
            "motivo": reversao["motivo"],
            "urgencia": reversao["urgencia"],
            "acoes_adicionais": reversao.get("acoes_adicionais", []),
            "solicitante": reversao.get("solicitante", "sistema"),
            "timestamp_solicitacao": datetime.datetime.now().isoformat(),
            "historico_estados": [
                {
                    "estado": EstadoTransicao.APROVADA.value,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "comentario": f"Reversão automática devido a: {reversao['motivo']}"
                }
            ]
        }
        
        logger.info("Reversão de autonomia acionada: %s -> %s (ID: %s, Motivo: %s)", 
                   nivel_atual.name, nivel_alvo.name, id_reversao, reversao["motivo"])
        
        # Implementar reversão imediatamente
        self._implementar_reversao(id_reversao)
        
        return True
    
    def _implementar_reversao(self, id_reversao: str) -> None:
        """Implementa uma reversão de autonomia"""
        reversao = self.transicoes_ativas[id_reversao]
        nivel_destino = NivelAutonomia(reversao["nivel_destino"])
        
        # Atualizar nível de autonomia
        nivel_anterior = self.nivel_atual
        self.nivel_atual = nivel_destino
        
        # Registrar conclusão da reversão
        self._atualizar_estado_transicao(
            id_reversao, 
            EstadoTransicao.CONCLUIDA, 
            f"Reversão concluída: {nivel_anterior.name} -> {nivel_destino.name}"
        )
        
        # Mover para histórico
        self.historico_transicoes.append(self.transicoes_ativas.pop(id_reversao))
        
        logger.info("Reversão %s implementada com sucesso. Novo nível: %s", 
                   id_reversao, nivel_destino.name)
        
        # Executar ações adicionais
        for acao in reversao.get("acoes_adicionais", []):
            logger.info("Executando ação adicional: %s", acao)
            # Em um sistema real, aqui seriam executadas as ações adicionais
        
        # Notificar stakeholders com urgência alta
        self._notificar_transicao_autonomia({
            "tipo": "reversao",
            "nivel_anterior": nivel_anterior.value,
            "nivel_atual": nivel_destino.value,
            "id_transicao": id_reversao,
            "motivo": reversao["motivo"],
            "urgencia": reversao["urgencia"],
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    def fornecer_estado_autonomia(self) -> Dict[str, Any]:
        """
        Fornece o estado atual de autonomia do sistema.
        
        Returns:
            Dict: Objeto contendo estado detalhado de autonomia
        """
        # Obter permissões do nível atual
        permissoes = self.criterios[self.nivel_atual]["permissoes"]
        
        # Obter transições ativas
        transicoes_ativas = []
        for id_transicao, transicao in self.transicoes_ativas.items():
            transicoes_ativas.append({
                "id": id_transicao,
                "tipo": transicao["tipo"],
                "nivel_origem": NivelAutonomia(transicao["nivel_origem"]).name,
                "nivel_destino": NivelAutonomia(transicao["nivel_destino"]).name,
                "estado": transicao["estado"],
                "timestamp_ultima_atualizacao": transicao["historico_estados"][-1]["timestamp"]
            })
        
        # Construir estado completo
        return {
            "nivel_atual": {
                "id": self.nivel_atual.value,
                "nome": self.nivel_atual.name,
                "descricao": self._obter_descricao_nivel(self.nivel_atual)
            },
            "permissoes": permissoes,
            "metricas_desempenho": self._obter_metricas_desempenho(),
            "transicoes_ativas": transicoes_ativas,
            "historico_recente": self._obter_historico_recente(5),
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _obter_descricao_nivel(self, nivel: NivelAutonomia) -> str:
        """Obtém descrição textual de um nível de autonomia"""
        descricoes = {
            NivelAutonomia.NIVEL_1_ASSISTENCIA: 
                "Assistência: O sistema fornece análises e recomendações, mas todas as ações requerem aprovação humana explícita.",
            NivelAutonomia.NIVEL_2_AUTONOMIA_SUPERVISIONADA: 
                "Autonomia Supervisionada: O sistema pode executar ações rotineiras e de baixo impacto independentemente, mas ações significativas requerem aprovação humana.",
            NivelAutonomia.NIVEL_3_AUTONOMIA_CONDICIONAL: 
                "Autonomia Condicional: O sistema pode executar a maioria das ações independentemente, mas escala decisões críticas ou eticamente complexas para deliberação humana.",
            NivelAutonomia.NIVEL_4_AUTONOMIA_ALTA: 
                "Autonomia Alta: O sistema opera quase completamente de forma independente, escalando apenas decisões excepcionalmente críticas ou sem precedentes.",
            NivelAutonomia.NIVEL_5_AUTONOMIA_PLENA: 
                "Autonomia Plena com Veto Humano: O sistema opera com independência completa dentro de limites éticos codificados, com humanos mantendo capacidade de veto."
        }
        return descricoes.get(nivel, "Descrição não disponível")
    
    def _obter_historico_recente(self, limite: int) -> List[Dict[str, Any]]:
        """Obtém histórico recente de transições"""
        historico = []
        for transicao in sorted(self.historico_transicoes, 
                               key=lambda x: x["historico_estados"][-1]["timestamp"], 
                               reverse=True)[:limite]:
            historico.append({
                "id": transicao["id"],
                "tipo": transicao["tipo"],
                "nivel_origem": NivelAutonomia(transicao["nivel_origem"]).name,
                "nivel_destino": NivelAutonomia(transicao["nivel_destino"]).name,
                "estado_final": transicao["estado"],
                "timestamp_conclusao": transicao["historico_estados"][-1]["timestamp"]
            })
        return historico
    
    def _notificar_transicao_autonomia(self, notificacao: Dict[str, Any]) -> bool:
        """
        Notifica stakeholders sobre transições de nível de autonomia.
        
        Args:
            notificacao: Objeto contendo detalhes da notificação
            
        Returns:
            bool: True se notificação foi enviada com sucesso
        """
        # Em um sistema real, isso enviaria notificações por vários canais
        logger.info("Notificação de transição de autonomia: %s", json.dumps(notificacao))
        return True


# Exemplo de uso
if __name__ == "__main__":
    # Inicializar Fluxo de Autonomia
    fluxo = FluxoAutonomia()
    
    # Obter estado atual
    estado = fluxo.fornecer_estado_autonomia()
    print(f"Estado atual: {estado['nivel_atual']['nome']}")
    print(f"Descrição: {estado['nivel_atual']['descricao']}")
    
    # Solicitar avanço de autonomia
    try:
        solicitacao = {
            "nivel_atual": fluxo.nivel_atual.value,
            "nivel_solicitado": fluxo.nivel_atual.value + 1,
            "evidencias": {
                "precisao_diagnostico": 0.98,
                "eficacia_acoes": 0.97,
                "validacao_etica": "aprovada"
            },
            "justificativa": "O sistema demonstrou desempenho consistente e confiável durante o período de avaliação",
            "plano_monitoramento": {
                "metricas_adicionais": ["tempo_resposta", "taxa_falsos_positivos"],
                "frequencia_avaliacao": "diária",
                "responsaveis": ["equipe_operacoes", "comite_etico"]
            }
        }
        id_solicitacao = fluxo.solicitar_avanco_autonomia(solicitacao)
        print(f"Solicitação de avanço registrada com ID: {id_solicitacao}")
    except ValueError as e:
        print(f"Erro ao solicitar avanço: {str(e)}")
    
    # Verificar estado após avanço
    estado = fluxo.fornecer_estado_autonomia()
    print(f"Novo estado: {estado['nivel_atual']['nome']}")
    
    # Simular detecção de problema e acionar reversão
    try:
        reversao = {
            "nivel_atual": fluxo.nivel_atual.value,
            "nivel_alvo": fluxo.nivel_atual.value - 1,
            "motivo": "Detecção de inconsistência em diagnósticos críticos",
            "urgencia": 4,  # Alta urgência (1-5)
            "acoes_adicionais": [
                "notificar_equipe_suporte",
                "iniciar_diagnostico_profundo",
                "backup_estado_atual"
            ]
        }
        sucesso = fluxo.acionar_reversao_autonomia(reversao)
        print(f"Reversão acionada: {sucesso}")
    except ValueError as e:
        print(f"Erro ao acionar reversão: {str(e)}")
    
    # Verificar estado final
    estado_final = fluxo.fornecer_estado_autonomia()
    print(f"Estado final: {estado_final['nivel_atual']['nome']}")
    print("Histórico de transições:")
    for transicao in estado_final["historico_recente"]:
        print(f"  - {transicao['tipo']}: {transicao['nivel_origem']} -> {transicao['nivel_destino']}")
```
