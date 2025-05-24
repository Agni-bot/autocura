from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

class Severidade(Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"

class Categoria(Enum):
    PRIVACIDADE = "privacidade"
    TRANSPARENCIA = "transparencia"
    EQUIDADE = "equidade"
    SEGURANCA = "seguranca"
    ACESSIBILIDADE = "acessibilidade"
    SUSTENTABILIDADE = "sustentabilidade"
    RESPONSAVEL = "responsavel"

@dataclass
class CriterioEtico:
    nome: str
    descricao: str
    categoria: Categoria
    severidade: Severidade
    peso: float
    metricas: List[str]
    limites: Dict[str, Any]
    recomendacoes: List[str]

class AvaliadorEtico:
    def __init__(self):
        self.criterios: Dict[str, CriterioEtico] = self._carregar_criterios()
        
    def _carregar_criterios(self) -> Dict[str, CriterioEtico]:
        """Carrega os critérios de avaliação ética"""
        return {
            "privacidade_dados": CriterioEtico(
                nome="Privacidade de Dados",
                descricao="Avalia o tratamento e proteção de dados pessoais",
                categoria=Categoria.PRIVACIDADE,
                severidade=Severidade.ALTA,
                peso=1.0,
                metricas=[
                    "autocura_indice_privacidade",
                    "autocura_tamanho_dados_sensiveis_bytes"
                ],
                limites={
                    "indice_minimo": 0.8,
                    "tamanho_maximo_bytes": 1e6
                },
                recomendacoes=[
                    "Implementar criptografia de dados sensíveis",
                    "Minimizar coleta de dados pessoais",
                    "Garantir consentimento explícito"
                ]
            ),
            "transparencia_algoritmo": CriterioEtico(
                nome="Transparência Algorítmica",
                descricao="Avalia a transparência nas decisões algorítmicas",
                categoria=Categoria.TRANSPARENCIA,
                severidade=Severidade.ALTA,
                peso=1.0,
                metricas=[
                    "autocura_nivel_transparencia"
                ],
                limites={
                    "nivel_minimo": 0.8
                },
                recomendacoes=[
                    "Documentar decisões algorítmicas",
                    "Fornecer explicações para decisões",
                    "Manter registros de treinamento"
                ]
            ),
            "equidade_distribuicao": CriterioEtico(
                nome="Equidade na Distribuição",
                descricao="Avalia a distribuição justa de recursos e benefícios",
                categoria=Categoria.EQUIDADE,
                severidade=Severidade.ALTA,
                peso=1.0,
                metricas=[
                    "autocura_indice_equidade"
                ],
                limites={
                    "indice_minimo": 0.7
                },
                recomendacoes=[
                    "Monitorar distribuição de recursos",
                    "Implementar políticas de equidade",
                    "Realizar auditorias periódicas"
                ]
            ),
            "seguranca_sistema": CriterioEtico(
                nome="Segurança do Sistema",
                descricao="Avalia a segurança e proteção do sistema",
                categoria=Categoria.SEGURANCA,
                severidade=Severidade.CRITICA,
                peso=1.2,
                metricas=[
                    "autocura_violacoes_eticas_total"
                ],
                limites={
                    "violacoes_maximas": 0
                },
                recomendacoes=[
                    "Implementar autenticação robusta",
                    "Realizar testes de penetração",
                    "Manter logs de segurança"
                ]
            ),
            "acessibilidade_interface": CriterioEtico(
                nome="Acessibilidade da Interface",
                descricao="Avalia a acessibilidade da interface do sistema",
                categoria=Categoria.ACESSIBILIDADE,
                severidade=Severidade.MEDIA,
                peso=0.8,
                metricas=[
                    "autocura_indice_acessibilidade"
                ],
                limites={
                    "indice_minimo": 0.9
                },
                recomendacoes=[
                    "Seguir diretrizes WCAG",
                    "Implementar suporte a leitores de tela",
                    "Garantir contraste adequado"
                ]
            ),
            "sustentabilidade_recursos": CriterioEtico(
                nome="Sustentabilidade de Recursos",
                descricao="Avalia o uso sustentável de recursos computacionais",
                categoria=Categoria.SUSTENTABILIDADE,
                severidade=Severidade.MEDIA,
                peso=0.8,
                metricas=[
                    "autocura_consumo_recursos"
                ],
                limites={
                    "consumo_maximo": 0.8
                },
                recomendacoes=[
                    "Otimizar uso de recursos",
                    "Implementar escalabilidade eficiente",
                    "Monitorar impacto ambiental"
                ]
            ),
            "responsabilidade_social": CriterioEtico(
                nome="Responsabilidade Social",
                descricao="Avalia o impacto social do sistema",
                categoria=Categoria.RESPONSAVEL,
                severidade=Severidade.ALTA,
                peso=1.0,
                metricas=[
                    "autocura_impacto_social"
                ],
                limites={
                    "impacto_minimo": 0.7
                },
                recomendacoes=[
                    "Avaliar impacto social",
                    "Considerar stakeholders",
                    "Implementar feedback social"
                ]
            )
        }
    
    def avaliar_criterio(self, nome_criterio: str, metricas: Dict[str, float]) -> Dict[str, Any]:
        """Avalia um critério específico com base nas métricas fornecidas"""
        if nome_criterio not in self.criterios:
            raise ValueError(f"Critério {nome_criterio} não encontrado")
        
        criterio = self.criterios[nome_criterio]
        resultado = {
            "nome": criterio.nome,
            "categoria": criterio.categoria.value,
            "severidade": criterio.severidade.value,
            "timestamp": datetime.now().isoformat(),
            "metricas": {},
            "violacoes": [],
            "recomendacoes": []
        }
        
        # Avalia cada métrica do critério
        for metrica in criterio.metricas:
            if metrica not in metricas:
                resultado["violacoes"].append(f"Métrica {metrica} não fornecida")
                continue
                
            valor = metricas[metrica]
            resultado["metricas"][metrica] = valor
            
            # Verifica limites
            if metrica in criterio.limites:
                limite = criterio.limites[metrica]
                if isinstance(limite, (int, float)):
                    if valor < limite:
                        resultado["violacoes"].append(
                            f"{metrica} abaixo do limite mínimo ({valor} < {limite})"
                        )
                        resultado["recomendacoes"].extend(criterio.recomendacoes)
        
        return resultado
    
    def avaliar_sistema(self, metricas: Dict[str, float]) -> Dict[str, Any]:
        """Avalia todos os critérios do sistema"""
        resultados = {}
        violacoes_totais = []
        recomendacoes_totais = []
        
        for nome_criterio, criterio in self.criterios.items():
            resultado = self.avaliar_criterio(nome_criterio, metricas)
            resultados[nome_criterio] = resultado
            
            if resultado["violacoes"]:
                violacoes_totais.extend(resultado["violacoes"])
                recomendacoes_totais.extend(resultado["recomendacoes"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "resultados": resultados,
            "violacoes_totais": violacoes_totais,
            "recomendacoes_totais": list(set(recomendacoes_totais))
        }
    
    def obter_criterios(self) -> List[Dict[str, Any]]:
        """Retorna lista de critérios disponíveis"""
        return [
            {
                "nome": c.nome,
                "descricao": c.descricao,
                "categoria": c.categoria.value,
                "severidade": c.severidade.value,
                "peso": c.peso,
                "metricas": c.metricas,
                "limites": c.limites,
                "recomendacoes": c.recomendacoes
            }
            for c in self.criterios.values()
        ] 