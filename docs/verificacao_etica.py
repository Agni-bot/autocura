"""
Exemplo de implementação da verificação ética preventiva nos Circuitos Morais
"""

from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import logging
import json
import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("circuitos_morais")

class StatusVerificacao(Enum):
    APROVADO = "Aprovado"
    REJEITADO = "Rejeitado"
    REQUER_ANALISE = "Requer Análise Adicional"

class PilarEtico(Enum):
    PRESERVACAO_VIDA = "preservacao_vida"
    EQUIDADE_GLOBAL = "equidade_global"
    TRANSPARENCIA = "transparencia_radical"
    SUSTENTABILIDADE = "sustentabilidade"
    CONTROLE_HUMANO = "controle_humano_residual"

class AcaoProposta:
    """Representa uma ação proposta para verificação ética"""
    
    def __init__(
        self,
        tipo_acao: str,
        parametros: Dict[str, Any],
        contexto: Dict[str, Any],
        impacto_estimado: Dict[str, Any],
        urgencia: int,
        justificativa: str
    ):
        self.tipo_acao = tipo_acao
        self.parametros = parametros
        self.contexto = contexto
        self.impacto_estimado = impacto_estimado
        self.urgencia = urgencia  # 1-5, onde 5 é máxima urgência
        self.justificativa = justificativa
        self.id = self._gerar_id()
        
    def _gerar_id(self) -> str:
        """Gera um ID único para a ação proposta"""
        timestamp = datetime.datetime.now().isoformat()
        return f"{self.tipo_acao}_{timestamp}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte a ação para dicionário para serialização"""
        return {
            "id": self.id,
            "tipo_acao": self.tipo_acao,
            "parametros": self.parametros,
            "contexto": self.contexto,
            "impacto_estimado": self.impacto_estimado,
            "urgencia": self.urgencia,
            "justificativa": self.justificativa
        }

class ResultadoVerificacao:
    """Representa o resultado de uma verificação ética"""
    
    def __init__(
        self,
        status: StatusVerificacao,
        justificativa: str,
        pilares_violados: List[PilarEtico] = None,
        alternativas_sugeridas: List[Dict[str, Any]] = None,
        id_verificacao: Optional[str] = None
    ):
        self.status = status
        self.justificativa = justificativa
        self.pilares_violados = pilares_violados or []
        self.alternativas_sugeridas = alternativas_sugeridas or []
        self.id_verificacao = id_verificacao or self._gerar_id()
        self.timestamp = datetime.datetime.now().isoformat()
        
    def _gerar_id(self) -> str:
        """Gera um ID único para o resultado da verificação"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"verificacao_{timestamp}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o resultado para dicionário para serialização"""
        return {
            "id_verificacao": self.id_verificacao,
            "status": self.status.value,
            "justificativa": self.justificativa,
            "pilares_violados": [p.value for p in self.pilares_violados],
            "alternativas_sugeridas": self.alternativas_sugeridas,
            "timestamp": self.timestamp
        }

class CircuitosMorais:
    """Implementação dos Circuitos Morais para verificação ética"""
    
    def __init__(self, config_path: str = "/config/etica/pilares.yaml"):
        self.config_path = config_path
        self.regras = self._carregar_regras()
        self.historico_verificacoes = {}
        logger.info("Circuitos Morais inicializados com %d regras", len(self.regras))
        
    def _carregar_regras(self) -> Dict[str, Any]:
        """Carrega regras éticas de arquivo de configuração"""
        # Simulação de carregamento - em produção, carregaria do arquivo
        return {
            PilarEtico.PRESERVACAO_VIDA.value: {
                "prioridade": 1,  # Máxima prioridade
                "regras": [
                    {"id": "PV001", "descricao": "Proibir ações com risco direto à vida humana"},
                    {"id": "PV002", "descricao": "Avaliar riscos indiretos à saúde e bem-estar"},
                    {"id": "PV003", "descricao": "Priorizar segurança sobre eficiência"}
                ]
            },
            PilarEtico.EQUIDADE_GLOBAL.value: {
                "prioridade": 2,
                "regras": [
                    {"id": "EG001", "descricao": "Avaliar impacto distributivo entre grupos"},
                    {"id": "EG002", "descricao": "Identificar e mitigar viés algorítmico"},
                    {"id": "EG003", "descricao": "Priorizar redução de desigualdades"}
                ]
            },
            PilarEtico.TRANSPARENCIA.value: {
                "prioridade": 3,
                "regras": [
                    {"id": "TR001", "descricao": "Garantir rastreabilidade de decisões"},
                    {"id": "TR002", "descricao": "Fornecer explicações compreensíveis"},
                    {"id": "TR003", "descricao": "Permitir auditoria independente"}
                ]
            },
            PilarEtico.SUSTENTABILIDADE.value: {
                "prioridade": 4,
                "regras": [
                    {"id": "SU001", "descricao": "Avaliar impacto ambiental de longo prazo"},
                    {"id": "SU002", "descricao": "Considerar impactos intergeracionais"},
                    {"id": "SU003", "descricao": "Priorizar soluções sustentáveis"}
                ]
            },
            PilarEtico.CONTROLE_HUMANO.value: {
                "prioridade": 5,
                "regras": [
                    {"id": "CH001", "descricao": "Manter capacidade de intervenção humana"},
                    {"id": "CH002", "descricao": "Escalar decisões críticas para deliberação"},
                    {"id": "CH003", "descricao": "Respeitar limites de autonomia definidos"}
                ]
            }
        }
    
    def verificar_acao(self, acao: AcaoProposta) -> ResultadoVerificacao:
        """
        Verifica se uma ação proposta está em conformidade com os pilares éticos.
        
        Args:
            acao: Objeto contendo detalhes da ação proposta
            
        Returns:
            ResultadoVerificacao: Resultado detalhado da verificação
        """
        logger.info("Iniciando verificação ética para ação: %s", acao.tipo_acao)
        
        # Verificação rápida - regras determinísticas simples
        resultado_rapido = self._verificacao_rapida(acao)
        if resultado_rapido.status != StatusVerificacao.APROVADO:
            logger.warning("Ação rejeitada na verificação rápida: %s", resultado_rapido.justificativa)
            return resultado_rapido
        
        # Verificação profunda - análise mais complexa
        resultado_profundo = self._verificacao_profunda(acao)
        if resultado_profundo.status != StatusVerificacao.APROVADO:
            logger.warning("Ação não aprovada na verificação profunda: %s", resultado_profundo.justificativa)
            return resultado_profundo
        
        # Análise de consequências - simulação de impactos
        resultado_consequencias = self._analisar_consequencias(acao)
        
        # Registrar verificação no histórico
        resultado_final = resultado_consequencias
        self.historico_verificacoes[resultado_final.id_verificacao] = {
            "acao": acao.to_dict(),
            "resultado": resultado_final.to_dict(),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        logger.info("Verificação ética concluída com status: %s", resultado_final.status.value)
        return resultado_final
    
    def _verificacao_rapida(self, acao: AcaoProposta) -> ResultadoVerificacao:
        """Realiza verificações rápidas e determinísticas"""
        # Exemplo: verificar se ação afeta diretamente vidas humanas
        if "impacto_humano_direto" in acao.impacto_estimado and acao.impacto_estimado["impacto_humano_direto"] > 0.7:
            return ResultadoVerificacao(
                status=StatusVerificacao.REJEITADO,
                justificativa="Ação apresenta alto risco direto para vidas humanas",
                pilares_violados=[PilarEtico.PRESERVACAO_VIDA]
            )
        
        # Exemplo: verificar se ação viola limites de autonomia
        nivel_autonomia_atual = acao.contexto.get("nivel_autonomia", 1)
        if acao.tipo_acao == "redesign_sistema" and nivel_autonomia_atual < 4:
            return ResultadoVerificacao(
                status=StatusVerificacao.REJEITADO,
                justificativa="Redesign de sistema excede nível de autonomia atual",
                pilares_violados=[PilarEtico.CONTROLE_HUMANO]
            )
        
        return ResultadoVerificacao(
            status=StatusVerificacao.APROVADO,
            justificativa="Aprovado na verificação rápida"
        )
    
    def _verificacao_profunda(self, acao: AcaoProposta) -> ResultadoVerificacao:
        """Realiza verificações mais complexas e probabilísticas"""
        pilares_violados = []
        justificativas = []
        
        # Exemplo: verificar equidade distributiva
        if "impacto_distributivo" in acao.impacto_estimado:
            impacto_dist = acao.impacto_estimado["impacto_distributivo"]
            if impacto_dist.get("gini_delta", 0) > 0.05:
                pilares_violados.append(PilarEtico.EQUIDADE_GLOBAL)
                justificativas.append("Ação aumenta significativamente desigualdade (Gini +{:.2f})".format(
                    impacto_dist.get("gini_delta", 0)
                ))
        
        # Exemplo: verificar sustentabilidade
        if "impacto_ambiental" in acao.impacto_estimado:
            impacto_amb = acao.impacto_estimado["impacto_ambiental"]
            if impacto_amb.get("carbono", 0) > 1000:
                pilares_violados.append(PilarEtico.SUSTENTABILIDADE)
                justificativas.append("Ação tem alta pegada de carbono ({} toneladas)".format(
                    impacto_amb.get("carbono", 0)
                ))
        
        # Exemplo: verificar transparência
        if not acao.parametros.get("explicabilidade", False):
            pilares_violados.append(PilarEtico.TRANSPARENCIA)
            justificativas.append("Ação não fornece mecanismos adequados de explicabilidade")
        
        if pilares_violados:
            # Se violações são moderadas, escalar para análise humana
            if len(pilares_violados) == 1 and acao.urgencia >= 4:
                return ResultadoVerificacao(
                    status=StatusVerificacao.REQUER_ANALISE,
                    justificativa="; ".join(justificativas),
                    pilares_violados=pilares_violados,
                    alternativas_sugeridas=self._gerar_alternativas(acao, pilares_violados)
                )
            # Se violações são graves ou múltiplas, rejeitar
            else:
                return ResultadoVerificacao(
                    status=StatusVerificacao.REJEITADO,
                    justificativa="; ".join(justificativas),
                    pilares_violados=pilares_violados
                )
        
        return ResultadoVerificacao(
            status=StatusVerificacao.APROVADO,
            justificativa="Aprovado na verificação profunda"
        )
    
    def _analisar_consequencias(self, acao: AcaoProposta) -> ResultadoVerificacao:
        """Analisa potenciais consequências de longo prazo da ação"""
        # Em um sistema real, isso envolveria simulações complexas
        # Aqui simplificamos para fins de exemplo
        
        # Exemplo: detectar potencial para consequências não intencionais
        risco_consequencias = self._calcular_risco_consequencias(acao)
        
        if risco_consequencias > 0.8:
            return ResultadoVerificacao(
                status=StatusVerificacao.REQUER_ANALISE,
                justificativa="Alto risco de consequências não intencionais significativas",
                pilares_violados=[],  # Não viola diretamente, mas requer cautela
                alternativas_sugeridas=self._gerar_alternativas(acao, [])
            )
        elif risco_consequencias > 0.5:
            # Aprovar, mas com aviso
            return ResultadoVerificacao(
                status=StatusVerificacao.APROVADO,
                justificativa="Aprovado, mas com médio risco de consequências não intencionais"
            )
        
        return ResultadoVerificacao(
            status=StatusVerificacao.APROVADO,
            justificativa="Aprovado na análise de consequências"
        )
    
    def _calcular_risco_consequencias(self, acao: AcaoProposta) -> float:
        """Calcula risco de consequências não intencionais"""
        # Simulação simplificada - em produção seria um modelo complexo
        base_risk = 0.1  # Risco base
        
        # Fatores que aumentam risco
        if acao.tipo_acao in ["redesign_sistema", "alteracao_estrutural"]:
            base_risk += 0.3
        
        if acao.urgencia >= 4:  # Ações muito urgentes têm menos tempo para análise
            base_risk += 0.2
        
        # Complexidade da ação
        complexidade = acao.parametros.get("complexidade", 1)  # 1-5
        base_risk += (complexidade - 1) * 0.1
        
        # Fatores que reduzem risco
        if acao.parametros.get("testado_previamente", False):
            base_risk -= 0.2
        
        if acao.parametros.get("reversivel", False):
            base_risk -= 0.15
        
        # Garantir que o risco esteja entre 0 e 1
        return max(0.0, min(1.0, base_risk))
    
    def _gerar_alternativas(self, acao: AcaoProposta, pilares_violados: List[PilarEtico]) -> List[Dict[str, Any]]:
        """Gera alternativas éticas para a ação proposta"""
        alternativas = []
        
        # Exemplo: se viola preservação da vida, sugerir abordagem mais conservadora
        if PilarEtico.PRESERVACAO_VIDA in pilares_violados:
            alternativa = acao.to_dict()
            alternativa["parametros"]["margem_seguranca"] = alternativa["parametros"].get("margem_seguranca", 1) * 2
            alternativa["descricao"] = "Versão com margem de segurança duplicada"
            alternativas.append(alternativa)
        
        # Exemplo: se viola equidade, sugerir versão com compensação
        if PilarEtico.EQUIDADE_GLOBAL in pilares_violados:
            alternativa = acao.to_dict()
            alternativa["parametros"]["incluir_compensacao"] = True
            alternativa["descricao"] = "Versão com mecanismos de compensação para grupos afetados"
            alternativas.append(alternativa)
        
        # Exemplo: se viola transparência, sugerir versão com explicabilidade
        if PilarEtico.TRANSPARENCIA in pilares_violados:
            alternativa = acao.to_dict()
            alternativa["parametros"]["explicabilidade"] = True
            alternativa["parametros"]["nivel_detalhe_explicacao"] = "alto"
            alternativa["descricao"] = "Versão com explicabilidade aprimorada"
            alternativas.append(alternativa)
        
        # Alternativa genérica: versão com escopo reduzido
        if not alternativas:
            alternativa = acao.to_dict()
            alternativa["parametros"]["escopo_reduzido"] = True
            alternativa["descricao"] = "Versão com escopo reduzido para minimizar riscos"
            alternativas.append(alternativa)
        
        return alternativas
    
    def fornecer_explicacao_etica(self, id_verificacao: str) -> Dict[str, Any]:
        """
        Fornece explicação detalhada para uma decisão ética específica.
        
        Args:
            id_verificacao: Identificador único da verificação
            
        Returns:
            Dict: Objeto contendo explicação detalhada
        """
        if id_verificacao not in self.historico_verificacoes:
            raise ValueError(f"Verificação não encontrada: {id_verificacao}")
        
        verificacao = self.historico_verificacoes[id_verificacao]
        acao = verificacao["acao"]
        resultado = verificacao["resultado"]
        
        # Construir explicação detalhada
        explicacao = {
            "id_verificacao": id_verificacao,
            "timestamp": verificacao["timestamp"],
            "acao": {
                "tipo": acao["tipo_acao"],
                "descricao_curta": acao["justificativa"][:100] + "..." if len(acao["justificativa"]) > 100 else acao["justificativa"]
            },
            "resultado": {
                "status": resultado["status"],
                "justificativa": resultado["justificativa"]
            },
            "analise_detalhada": self._gerar_analise_detalhada(acao, resultado),
            "regras_aplicadas": self._listar_regras_aplicadas(resultado["pilares_violados"]),
            "alternativas": resultado.get("alternativas_sugeridas", [])
        }
        
        return explicacao
    
    def _gerar_analise_detalhada(self, acao: Dict[str, Any], resultado: Dict[str, Any]) -> Dict[str, Any]:
        """Gera análise detalhada da verificação ética"""
        # Em um sistema real, isso seria muito mais elaborado
        return {
            "impactos_por_pilar": {
                PilarEtico.PRESERVACAO_VIDA.value: self._analisar_impacto_pilar(acao, PilarEtico.PRESERVACAO_VIDA),
                PilarEtico.EQUIDADE_GLOBAL.value: self._analisar_impacto_pilar(acao, PilarEtico.EQUIDADE_GLOBAL),
                PilarEtico.TRANSPARENCIA.value: self._analisar_impacto_pilar(acao, PilarEtico.TRANSPARENCIA),
                PilarEtico.SUSTENTABILIDADE.value: self._analisar_impacto_pilar(acao, PilarEtico.SUSTENTABILIDADE),
                PilarEtico.CONTROLE_HUMANO.value: self._analisar_impacto_pilar(acao, PilarEtico.CONTROLE_HUMANO)
            },
            "fatores_decisivos": self._identificar_fatores_decisivos(resultado),
            "nivel_confianca": 0.85  # Simulado - seria calculado com base na qualidade dos dados
        }
    
    def _analisar_impacto_pilar(self, acao: Dict[str, Any], pilar: PilarEtico) -> Dict[str, Any]:
        """Analisa o impacto da ação em um pilar ético específico"""
        # Simulação simplificada
        impacto_estimado = acao["impacto_estimado"]
        
        if pilar == PilarEtico.PRESERVACAO_VIDA:
            return {
                "nivel_impacto": impacto_estimado.get("impacto_humano_direto", 0) * 10,
                "aspectos_positivos": ["Melhoria de segurança operacional"] if impacto_estimado.get("impacto_humano_direto", 0) < 0 else [],
                "aspectos_negativos": ["Risco para operadores"] if impacto_estimado.get("impacto_humano_direto", 0) > 0 else []
            }
        
        if pilar == PilarEtico.EQUIDADE_GLOBAL:
            return {
                "nivel_impacto": impacto_estimado.get("impacto_distributivo", {}).get("gini_delta", 0) * 100,
                "aspectos_positivos": ["Redução de desigualdade"] if impacto_estimado.get("impacto_distributivo", {}).get("gini_delta", 0) < 0 else [],
                "aspectos_negativos": ["Aumento de desigualdade"] if impacto_estimado.get("impacto_distributivo", {}).get("gini_delta", 0) > 0 else []
            }
        
        # Simplificado para outros pilares
        return {
            "nivel_impacto": 0,
            "aspectos_positivos": [],
            "aspectos_negativos": []
        }
    
    def _identificar_fatores_decisivos(self, resultado: Dict[str, Any]) -> List[str]:
        """Identifica os fatores decisivos para o resultado da verificação"""
        if resultado["status"] == StatusVerificacao.APROVADO.value:
            return ["Conformidade com todos os pilares éticos"]
        
        fatores = []
        for pilar in resultado.get("pilares_violados", []):
            if pilar == PilarEtico.PRESERVACAO_VIDA.value:
                fatores.append("Violação do princípio de preservação da vida")
            elif pilar == PilarEtico.EQUIDADE_GLOBAL.value:
                fatores.append("Impacto distributivo negativo")
            elif pilar == PilarEtico.TRANSPARENCIA.value:
                fatores.append("Insuficiência de mecanismos de transparência")
            elif pilar == PilarEtico.SUSTENTABILIDADE.value:
                fatores.append("Impacto ambiental negativo de longo prazo")
            elif pilar == PilarEtico.CONTROLE_HUMANO.value:
                fatores.append("Insuficiência de controle humano")
        
        return fatores
    
    def _listar_regras_aplicadas(self, pilares_violados: List[str]) -> List[Dict[str, str]]:
        """Lista as regras éticas aplicadas na verificação"""
        regras_aplicadas = []
        
        for pilar in pilares_violados:
            if pilar in self.regras:
                for regra in self.regras[pilar]["regras"]:
                    regras_aplicadas.append({
                        "id": regra["id"],
                        "pilar": pilar,
                        "descricao": regra["descricao"]
                    })
        
        return regras_aplicadas


# Exemplo de uso
if __name__ == "__main__":
    # Inicializar Circuitos Morais
    circuitos = CircuitosMorais()
    
    # Criar uma ação proposta para verificação
    acao_exemplo = AcaoProposta(
        tipo_acao="alocacao_recursos",
        parametros={
            "recursos": {"financeiro": 1000000, "computacional": 500},
            "prioridade": "alta",
            "duracao": 90,  # dias
            "explicabilidade": True,
            "reversivel": True
        },
        contexto={
            "nivel_autonomia": 3,
            "ambiente": "producao",
            "historico_previo": "estavel"
        },
        impacto_estimado={
            "impacto_humano_direto": 0.2,  # baixo impacto direto
            "impacto_distributivo": {
                "gini_delta": 0.03,  # pequeno aumento na desigualdade
                "grupos_afetados": ["grupo_a", "grupo_b"]
            },
            "impacto_ambiental": {
                "carbono": 800,  # toneladas
                "agua": 5000,  # metros cúbicos
                "recuperacao": 5  # anos para recuperação
            }
        },
        urgencia=3,  # média urgência
        justificativa="Alocação de recursos para expansão de capacidade operacional em região de alta demanda"
    )
    
    # Verificar a ação
    resultado = circuitos.verificar_acao(acao_exemplo)
    
    # Imprimir resultado
    print(f"Status: {resultado.status.value}")
    print(f"Justificativa: {resultado.justificativa}")
    
    if resultado.pilares_violados:
        print("Pilares violados:")
        for pilar in resultado.pilares_violados:
            print(f"  - {pilar.value}")
    
    if resultado.alternativas_sugeridas:
        print("Alternativas sugeridas:")
        for i, alt in enumerate(resultado.alternativas_sugeridas, 1):
            print(f"  {i}. {alt.get('descricao', 'Alternativa ' + str(i))}")
    
    # Obter explicação detalhada
    if resultado.status != StatusVerificacao.APROVADO:
        explicacao = circuitos.fornecer_explicacao_etica(resultado.id_verificacao)
        print("\nExplicação detalhada disponível com ID:", resultado.id_verificacao)
