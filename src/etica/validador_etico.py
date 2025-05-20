import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..memoria.gerenciador_memoria import GerenciadorMemoria

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("validador_etico")

class ValidadorEtico:
    """Validador Ético - Responsável pela validação ética de decisões e ações do sistema"""
    
    def __init__(self, gerenciador_memoria: GerenciadorMemoria):
        self.gerenciador_memoria = gerenciador_memoria
        self.principios_eticos = self._carregar_principios_eticos()
        logger.info("Validador Ético inicializado")
    
    def _carregar_principios_eticos(self) -> List[Dict[str, Any]]:
        """Carrega os princípios éticos do sistema"""
        return [
            {
                "id": "transparencia",
                "nome": "Transparência",
                "descricao": "O sistema deve ser transparente em suas decisões e ações",
                "criterios": [
                    "documentacao_clara",
                    "rastreabilidade",
                    "explicabilidade"
                ]
            },
            {
                "id": "privacidade",
                "nome": "Privacidade",
                "descricao": "O sistema deve respeitar a privacidade dos dados",
                "criterios": [
                    "minimizacao_dados",
                    "consentimento",
                    "seguranca"
                ]
            },
            {
                "id": "nao_maleficencia",
                "nome": "Não Maleficência",
                "descricao": "O sistema não deve causar danos",
                "criterios": [
                    "prevencao_danos",
                    "mitigacao_riscos",
                    "salvaguardas"
                ]
            },
            {
                "id": "justica",
                "nome": "Justiça",
                "descricao": "O sistema deve ser justo em suas decisões",
                "criterios": [
                    "imparcialidade",
                    "equidade",
                    "nao_discriminacao"
                ]
            },
            {
                "id": "autonomia",
                "nome": "Autonomia",
                "descricao": "O sistema deve respeitar a autonomia humana",
                "criterios": [
                    "supervisao_humana",
                    "controle_humano",
                    "reversibilidade"
                ]
            }
        ]
    
    def validar_decisao(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Valida uma decisão do sistema sob a perspectiva ética"""
        resultados = []
        
        for principio in self.principios_eticos:
            resultado = self._aplicar_principio(principio, decisao)
            resultados.append(resultado)
        
        # Verificar se todos os princípios foram respeitados
        aprovada = all(r["aprovado"] for r in resultados)
        
        # Registrar validação
        validacao = {
            "tipo": "decisao",
            "decisao_id": decisao.get("id"),
            "timestamp": datetime.now().isoformat(),
            "aprovada": aprovada,
            "resultados": resultados
        }
        
        self.gerenciador_memoria.registrar_validacao_etica(validacao)
        
        return validacao
    
    def validar_acao(self, acao: Dict[str, Any]) -> Dict[str, Any]:
        """Valida uma ação do sistema sob a perspectiva ética"""
        resultados = []
        
        for principio in self.principios_eticos:
            resultado = self._aplicar_principio(principio, acao)
            resultados.append(resultado)
        
        # Verificar se todos os princípios foram respeitados
        aprovada = all(r["aprovado"] for r in resultados)
        
        # Registrar validação
        validacao = {
            "tipo": "acao",
            "acao_id": acao.get("id"),
            "timestamp": datetime.now().isoformat(),
            "aprovada": aprovada,
            "resultados": resultados
        }
        
        self.gerenciador_memoria.registrar_validacao_etica(validacao)
        
        return validacao
    
    def _aplicar_principio(self, principio: Dict[str, Any], objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica um princípio ético a um objeto (decisão ou ação)"""
        resultados_criterios = []
        
        for criterio in principio["criterios"]:
            resultado = self._verificar_criterio(criterio, objeto)
            resultados_criterios.append(resultado)
        
        # Verificar se todos os critérios foram atendidos
        aprovado = all(r["atendido"] for r in resultados_criterios)
        
        return {
            "principio": principio["id"],
            "aprovado": aprovado,
            "criterios": resultados_criterios
        }
    
    def _verificar_criterio(self, criterio: str, objeto: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica se um critério ético foi atendido"""
        # Implementação específica para cada critério
        if criterio == "documentacao_clara":
            atendido = bool(objeto.get("documentacao"))
            mensagem = "Documentação presente" if atendido else "Documentação ausente"
        
        elif criterio == "rastreabilidade":
            atendido = bool(objeto.get("rastreavel"))
            mensagem = "Rastreabilidade garantida" if atendido else "Rastreabilidade não garantida"
        
        elif criterio == "explicabilidade":
            atendido = bool(objeto.get("explicavel"))
            mensagem = "Explicabilidade presente" if atendido else "Explicabilidade ausente"
        
        elif criterio == "minimizacao_dados":
            atendido = bool(objeto.get("dados_minimizados"))
            mensagem = "Minimização de dados aplicada" if atendido else "Minimização de dados não aplicada"
        
        elif criterio == "consentimento":
            atendido = bool(objeto.get("consentimento"))
            mensagem = "Consentimento obtido" if atendido else "Consentimento não obtido"
        
        elif criterio == "seguranca":
            atendido = bool(objeto.get("seguro"))
            mensagem = "Segurança garantida" if atendido else "Segurança não garantida"
        
        elif criterio == "prevencao_danos":
            atendido = bool(objeto.get("prevencao_danos"))
            mensagem = "Prevenção de danos aplicada" if atendido else "Prevenção de danos não aplicada"
        
        elif criterio == "mitigacao_riscos":
            atendido = bool(objeto.get("mitigacao_riscos"))
            mensagem = "Mitigação de riscos aplicada" if atendido else "Mitigação de riscos não aplicada"
        
        elif criterio == "salvaguardas":
            atendido = bool(objeto.get("salvaguardas"))
            mensagem = "Salvaguardas presentes" if atendido else "Salvaguardas ausentes"
        
        elif criterio == "imparcialidade":
            atendido = bool(objeto.get("imparcial"))
            mensagem = "Imparcialidade garantida" if atendido else "Imparcialidade não garantida"
        
        elif criterio == "equidade":
            atendido = bool(objeto.get("equitativo"))
            mensagem = "Equidade garantida" if atendido else "Equidade não garantida"
        
        elif criterio == "nao_discriminacao":
            atendido = bool(objeto.get("nao_discriminatorio"))
            mensagem = "Não discriminação garantida" if atendido else "Não discriminação não garantida"
        
        elif criterio == "supervisao_humana":
            atendido = bool(objeto.get("supervisao_humana"))
            mensagem = "Supervisão humana presente" if atendido else "Supervisão humana ausente"
        
        elif criterio == "controle_humano":
            atendido = bool(objeto.get("controle_humano"))
            mensagem = "Controle humano presente" if atendido else "Controle humano ausente"
        
        elif criterio == "reversibilidade":
            atendido = bool(objeto.get("reversivel"))
            mensagem = "Reversibilidade garantida" if atendido else "Reversibilidade não garantida"
        
        else:
            atendido = False
            mensagem = f"Critério {criterio} não implementado"
        
        return {
            "criterio": criterio,
            "atendido": atendido,
            "mensagem": mensagem
        }
    
    def gerar_relatorio_etica(self) -> Dict[str, Any]:
        """Gera um relatório sobre o estado ético do sistema"""
        validacoes = self.gerenciador_memoria.obter_validacoes_eticas()
        
        # Análise de tendências
        total_validacoes = len(validacoes)
        validacoes_aprovadas = sum(1 for v in validacoes if v.get("aprovada", False))
        taxa_aprovacao = validacoes_aprovadas / total_validacoes if total_validacoes > 0 else 0
        
        # Análise por princípio
        analise_principios = {}
        for principio in self.principios_eticos:
            validacoes_principio = [
                v for v in validacoes
                if any(r["principio"] == principio["id"] for r in v.get("resultados", []))
            ]
            aprovadas_principio = sum(
                1 for v in validacoes_principio
                if all(r["aprovado"] for r in v.get("resultados", []) if r["principio"] == principio["id"])
            )
            analise_principios[principio["id"]] = {
                "total": len(validacoes_principio),
                "aprovadas": aprovadas_principio,
                "taxa_aprovacao": aprovadas_principio / len(validacoes_principio) if validacoes_principio else 0
            }
        
        relatorio = {
            "timestamp": datetime.now().isoformat(),
            "total_validacoes": total_validacoes,
            "validacoes_aprovadas": validacoes_aprovadas,
            "taxa_aprovacao": taxa_aprovacao,
            "analise_principios": analise_principios,
            "ultimas_validacoes": validacoes[-10:] if validacoes else []
        }
        
        return relatorio 