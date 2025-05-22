from typing import List, Dict
from dataclasses import dataclass
from src.diagnostico import Diagnostico
from src.monitoramento import MetricasSistema
from enum import Enum

@dataclass
class MetricaDimensional:
    nome: str
    valor: float
    unidade: str = ""

@dataclass
class PadraoAnomalia:
    nome: str
    descricao: str
    severidade: int

class TipoAcao(Enum):
    HOTFIX = "hotfix"
    REFATORACAO = "refatoracao"
    REDESIGN = "redesign"

@dataclass
class Acao:
    tipo: str  # hotfix, refatoracao, redesign
    descricao: str
    prioridade: int
    tempo_estimado: str
    recursos_necessarios: List[str]

@dataclass
class AcaoCorretiva:
    id: str
    tipo: TipoAcao
    descricao: str
    comandos: List[str]
    impacto_estimado: Dict[str, float]
    tempo_estimado: int
    recursos_necessarios: Dict[str, str]
    risco: float = 0.0

    def __post_init__(self):
        if not 0 <= self.risco <= 1:
            raise ValueError("Risco deve estar entre 0 e 1")
        if self.tempo_estimado < 0:
            raise ValueError("Tempo estimado não pode ser negativo")

@dataclass
class PlanoAcao:
    id: str
    acoes: List[AcaoCorretiva]
    prioridade: int
    descricao: str

    def __post_init__(self):
        if not self.acoes:
            raise ValueError("Plano de ação deve conter pelo menos uma ação")
        if self.prioridade < 1 or self.prioridade > 5:
            raise ValueError("Prioridade deve estar entre 1 e 5")

@dataclass
class GeradorHotfix:
    id: str
    descricao: str
    comandos: List[str]
    impacto_estimado: Dict[str, float]
    tempo_estimado: int
    recursos_necessarios: Dict[str, str]
    risco: float = 0.0

    def __post_init__(self):
        if not 0 <= self.risco <= 1:
            raise ValueError("Risco deve estar entre 0 e 1")
        if self.tempo_estimado < 0:
            raise ValueError("Tempo estimado não pode ser negativo")

@dataclass
class MotorRefatoracao:
    id: str
    descricao: str
    comandos: List[str]
    impacto_estimado: Dict[str, float]
    tempo_estimado: int
    recursos_necessarios: Dict[str, str]
    risco: float = 0.0

    def __post_init__(self):
        if not 0 <= self.risco <= 1:
            raise ValueError("Risco deve estar entre 0 e 1")
        if self.tempo_estimado < 0:
            raise ValueError("Tempo estimado não pode ser negativo")

@dataclass
class ProjetorRedesign:
    id: str
    descricao: str
    comandos: List[str]
    impacto_estimado: Dict[str, float]
    tempo_estimado: int
    recursos_necessarios: Dict[str, str]
    risco: float = 0.0

    def __post_init__(self):
        if not 0 <= self.risco <= 1:
            raise ValueError("Risco deve estar entre 0 e 1")
        if self.tempo_estimado < 0:
            raise ValueError("Tempo estimado não pode ser negativo")

@dataclass
class OrquestradorAcoes:
    id: str
    descricao: str
    comandos: List[str]
    impacto_estimado: Dict[str, float]
    tempo_estimado: int
    recursos_necessarios: Dict[str, str]
    risco: float = 0.0

    def __post_init__(self):
        if not 0 <= self.risco <= 1:
            raise ValueError("Risco deve estar entre 0 e 1")
        if self.tempo_estimado < 0:
            raise ValueError("Tempo estimado não pode ser negativo")

class GeradorAcoes:
    def __init__(self):
        self.acoes_base = {
            "erro_sistema": {
                "hotfix": [
                    ("Reiniciar serviço afetado", 1, "5min", ["servidor"]),
                    ("Reverter última atualização", 2, "15min", ["servidor", "banco_dados"]),
                    ("Ativar modo de segurança", 3, "2min", ["servidor"])
                ],
                "refatoracao": [
                    ("Implementar tratamento de erros robusto", 2, "2h", ["desenvolvedor"]),
                    ("Adicionar logging detalhado", 1, "1h", ["desenvolvedor"]),
                    ("Melhorar validação de dados", 2, "3h", ["desenvolvedor", "qa"])
                ],
                "redesign": [
                    ("Redesenhar arquitetura de tratamento de erros", 3, "2sprints", ["arquiteto", "desenvolvedor"]),
                    ("Implementar sistema de fallback distribuído", 2, "1sprint", ["arquiteto", "devops"])
                ]
            },
            "latencia_alta": {
                "hotfix": [
                    ("Aumentar recursos de CPU", 1, "5min", ["infraestrutura"]),
                    ("Limpar cache", 2, "2min", ["servidor"]),
                    ("Reduzir nível de log", 3, "1min", ["servidor"])
                ],
                "refatoracao": [
                    ("Otimizar consultas ao banco", 1, "4h", ["desenvolvedor", "dba"]),
                    ("Implementar cache distribuído", 2, "8h", ["desenvolvedor", "devops"]),
                    ("Melhorar algoritmos de processamento", 2, "6h", ["desenvolvedor"])
                ],
                "redesign": [
                    ("Implementar arquitetura de microserviços", 3, "3sprints", ["arquiteto", "devops"]),
                    ("Redesenhar modelo de dados", 2, "2sprints", ["arquiteto", "dba"])
                ]
            }
        }
    
    def gerar_acoes(self, diagnostico: Diagnostico, metricas: MetricasSistema) -> List[Acao]:
        """Gera ações baseadas no diagnóstico e métricas"""
        acoes = []
        
        # Determina o tipo de anomalia
        tipo_anomalia = diagnostico.tipo_anomalia
        
        # Gera ações para cada horizonte temporal
        if tipo_anomalia in self.acoes_base:
            for horizonte in ["hotfix", "refatoracao", "redesign"]:
                if horizonte in self.acoes_base[tipo_anomalia]:
                    for descricao, prioridade, tempo, recursos in self.acoes_base[tipo_anomalia][horizonte]:
                        acoes.append(Acao(
                            tipo=horizonte,
                            descricao=descricao,
                            prioridade=prioridade,
                            tempo_estimado=tempo,
                            recursos_necessarios=recursos
                        ))
        
        # Ajusta prioridades baseado na gravidade
        for acao in acoes:
            if diagnostico.nivel_gravidade > 0.8:
                acao.prioridade = min(acao.prioridade + 1, 3)
        
        return acoes
    
    def priorizar_acoes(self, acoes: List[Acao]) -> List[Acao]:
        """Prioriza as ações baseado em múltiplos critérios"""
        # Ordena por prioridade (menor primeiro) e tipo (hotfix primeiro)
        tipo_ordem = {"hotfix": 0, "refatoracao": 1, "redesign": 2}
        return sorted(acoes, key=lambda x: (x.prioridade, tipo_ordem[x.tipo]))

# Exemplo de uso
if __name__ == "__main__":
    from src.monitoramento import MonitoramentoMultidimensional
    from src.diagnostico import RedeNeuralDiagnostico
    
    # Simula o fluxo completo
    monitor = MonitoramentoMultidimensional()
    diagnostico = RedeNeuralDiagnostico()
    gerador = GeradorAcoes()
    
    # Coleta métricas
    metricas = monitor.coletar_metricas()
    
    # Gera diagnóstico
    resultado_diagnostico = diagnostico.gerar_diagnostico(metricas)
    
    # Gera e prioriza ações
    acoes = gerador.gerar_acoes(resultado_diagnostico, metricas)
    acoes_priorizadas = gerador.priorizar_acoes(acoes)
    
    # Exibe resultados
    print("\nDiagnóstico:")
    print(f"Tipo de anomalia: {resultado_diagnostico.tipo_anomalia}")
    print(f"Nível de gravidade: {resultado_diagnostico.nivel_gravidade:.2f}")
    
    print("\nAções Priorizadas:")
    for acao in acoes_priorizadas:
        print(f"\nTipo: {acao.tipo}")
        print(f"Descrição: {acao.descricao}")
        print(f"Prioridade: {acao.prioridade}")
        print(f"Tempo estimado: {acao.tempo_estimado}")
        print(f"Recursos necessários: {', '.join(acao.recursos_necessarios)}") 