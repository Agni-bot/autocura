"""
Módulo Guardião Cognitivo

Este módulo é responsável por monitorar a saúde cognitiva do sistema e implementar
mecanismos de proteção contra degeneração cognitiva. Ele opera de forma independente
dos outros módulos para garantir que possa intervir mesmo em caso de falhas severas.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import os

@dataclass
class EstadoCognitivo:
    """Representa o estado cognitivo atual do sistema"""
    timestamp: datetime
    nivel_coerencia: float  # 0-1, onde 1 é totalmente coerente
    nivel_estabilidade: float  # 0-1, onde 1 é totalmente estável
    nivel_eficacia: float  # 0-1, onde 1 é totalmente eficaz
    alertas: List[str]
    metricas: Dict[str, float]

@dataclass
class ProtocoloEmergencia:
    """Define um protocolo de emergência para diferentes níveis de alerta"""
    nivel: int  # 1-5, onde 5 é o mais severo
    nome: str
    acoes: List[str]
    requisitos_aprovacao: List[str]
    tempo_maximo_resposta: str

class GuardiaoCognitivo:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.historico_estados: List[EstadoCognitivo] = []
        self.protocolos = self._carregar_protocolos()
        self.nivel_alerta_atual = 0
        
    def _carregar_protocolos(self) -> Dict[int, ProtocoloEmergencia]:
        """Carrega os protocolos de emergência do arquivo de configuração"""
        protocolos = {
            1: ProtocoloEmergencia(
                nivel=1,
                nome="Monitoramento Intensificado",
                acoes=[
                    "Aumentar frequência de coleta de métricas",
                    "Ativar logging detalhado",
                    "Notificar equipe de suporte"
                ],
                requisitos_aprovacao=["supervisor"],
                tempo_maximo_resposta="5min"
            ),
            2: ProtocoloEmergencia(
                nivel=2,
                nome="Intervenção Preventiva",
                acoes=[
                    "Reduzir autonomia do sistema",
                    "Ativar modo de segurança",
                    "Iniciar backup de dados críticos"
                ],
                requisitos_aprovacao=["supervisor", "especialista"],
                tempo_maximo_resposta="15min"
            ),
            3: ProtocoloEmergencia(
                nivel=3,
                nome="Contenção Ativa",
                acoes=[
                    "Suspender operações não críticas",
                    "Ativar redundância completa",
                    "Preparar rollback"
                ],
                requisitos_aprovacao=["supervisor", "especialista", "gerente"],
                tempo_maximo_resposta="30min"
            ),
            4: ProtocoloEmergencia(
                nivel=4,
                nome="Emergência Crítica",
                acoes=[
                    "Executar rollback completo",
                    "Isolar componentes afetados",
                    "Ativar plano de contingência"
                ],
                requisitos_aprovacao=["supervisor", "especialista", "gerente", "diretor"],
                tempo_maximo_resposta="1h"
            ),
            5: ProtocoloEmergencia(
                nivel=5,
                nome="Falha Catastrófica",
                acoes=[
                    "Desligar sistema principal",
                    "Ativar sistema de backup",
                    "Iniciar procedimento de recuperação"
                ],
                requisitos_aprovacao=["supervisor", "especialista", "gerente", "diretor", "CEO"],
                tempo_maximo_resposta="imediato"
            )
        }
        return protocolos
    
    def monitorar_coerencia(self, metricas: Dict[str, float]) -> float:
        """Monitora a coerência das decisões e operações do sistema"""
        # Implementa lógica para avaliar coerência
        # Por exemplo, verifica consistência entre decisões relacionadas
        return 0.8  # Valor exemplo
    
    def monitorar_estabilidade(self, historico: List[EstadoCognitivo]) -> float:
        """Monitora a estabilidade do sistema ao longo do tempo"""
        if not historico:
            return 1.0
            
        # Analisa variações nos últimos estados
        ultimos_estados = historico[-5:]
        variacoes = []
        
        for i in range(1, len(ultimos_estados)):
            variacao = abs(ultimos_estados[i].nivel_coerencia - 
                         ultimos_estados[i-1].nivel_coerencia)
            variacoes.append(variacao)
            
        # Calcula estabilidade baseada nas variações
        if not variacoes:
            return 1.0
            
        media_variacao = sum(variacoes) / len(variacoes)
        estabilidade = 1.0 - min(media_variacao, 1.0)
        
        return estabilidade
    
    def monitorar_eficacia(self, metricas: Dict[str, float]) -> float:
        """Monitora a eficácia das ações corretivas"""
        # Implementa lógica para avaliar eficácia
        # Por exemplo, verifica se problemas foram resolvidos
        return 0.9  # Valor exemplo
    
    def avaliar_estado_cognitivo(self, metricas: Dict[str, float]) -> EstadoCognitivo:
        """Avalia o estado cognitivo atual do sistema"""
        # Calcula métricas de saúde cognitiva
        coerencia = self.monitorar_coerencia(metricas)
        estabilidade = self.monitorar_estabilidade(self.historico_estados)
        eficacia = self.monitorar_eficacia(metricas)
        
        # Gera alertas baseados nas métricas
        alertas = []
        if coerencia < 0.7:
            alertas.append("Baixa coerência detectada")
        if estabilidade < 0.7:
            alertas.append("Instabilidade detectada")
        if eficacia < 0.7:
            alertas.append("Baixa eficácia detectada")
            
        # Cria estado atual
        estado = EstadoCognitivo(
            timestamp=datetime.now(),
            nivel_coerencia=coerencia,
            nivel_estabilidade=estabilidade,
            nivel_eficacia=eficacia,
            alertas=alertas,
            metricas=metricas
        )
        
        # Atualiza histórico
        self.historico_estados.append(estado)
        
        return estado
    
    def determinar_nivel_alerta(self, estado: EstadoCognitivo) -> int:
        """Determina o nível de alerta baseado no estado cognitivo"""
        # Lógica para determinar nível de alerta
        if (estado.nivel_coerencia < 0.3 or 
            estado.nivel_estabilidade < 0.3 or 
            estado.nivel_eficacia < 0.3):
            return 5
        elif (estado.nivel_coerencia < 0.5 or 
              estado.nivel_estabilidade < 0.5 or 
              estado.nivel_eficacia < 0.5):
            return 4
        elif (estado.nivel_coerencia < 0.6 or 
              estado.nivel_estabilidade < 0.6 or 
              estado.nivel_eficacia < 0.6):
            return 3
        elif (estado.nivel_coerencia < 0.7 or 
              estado.nivel_estabilidade < 0.7 or 
              estado.nivel_eficacia < 0.7):
            return 2
        elif (estado.nivel_coerencia < 0.8 or 
              estado.nivel_estabilidade < 0.8 or 
              estado.nivel_eficacia < 0.8):
            return 1
        return 0
    
    def ativar_protocolo_emergencia(self, nivel: int) -> Optional[ProtocoloEmergencia]:
        """Ativa o protocolo de emergência para o nível especificado"""
        if nivel not in self.protocolos:
            self.logger.error(f"Nível de protocolo inválido: {nivel}")
            return None
            
        protocolo = self.protocolos[nivel]
        self.logger.warning(f"Ativando protocolo de emergência nível {nivel}: {protocolo.nome}")
        
        # Registra ativação do protocolo
        self._registrar_ativacao_protocolo(protocolo)
        
        return protocolo
    
    def _registrar_ativacao_protocolo(self, protocolo: ProtocoloEmergencia):
        """Registra a ativação de um protocolo de emergência"""
        registro = {
            "timestamp": datetime.now().isoformat(),
            "protocolo": protocolo.nome,
            "nivel": protocolo.nivel,
            "acoes": protocolo.acoes,
            "requisitos_aprovacao": protocolo.requisitos_aprovacao
        }
        
        # Salva registro em arquivo
        log_dir = "logs/guardiao"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "protocolos_emergencia.json")
        try:
            if os.path.exists(log_file):
                with open(log_file, "r") as f:
                    registros = json.load(f)
            else:
                registros = []
                
            registros.append(registro)
            
            with open(log_file, "w") as f:
                json.dump(registros, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Erro ao registrar ativação de protocolo: {str(e)}")

# Exemplo de uso
if __name__ == "__main__":
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    
    # Cria instância do guardião
    guardiao = GuardiaoCognitivo()
    
    # Simula métricas do sistema
    metricas = {
        "throughput": 800,
        "latencia": 150,
        "taxa_erro": 2.5,
        "uso_cpu": 75,
        "uso_memoria": 60
    }
    
    # Avalia estado cognitivo
    estado = guardiao.avaliar_estado_cognitivo(metricas)
    
    # Determina nível de alerta
    nivel_alerta = guardiao.determinar_nivel_alerta(estado)
    
    print("\nEstado Cognitivo do Sistema:")
    print(f"Coerência: {estado.nivel_coerencia:.2f}")
    print(f"Estabilidade: {estado.nivel_estabilidade:.2f}")
    print(f"Eficácia: {estado.nivel_eficacia:.2f}")
    print(f"\nAlertas: {', '.join(estado.alertas) if estado.alertas else 'Nenhum'}")
    print(f"\nNível de Alerta: {nivel_alerta}")
    
    if nivel_alerta > 0:
        protocolo = guardiao.ativar_protocolo_emergencia(nivel_alerta)
        if protocolo:
            print(f"\nProtocolo de Emergência Ativado: {protocolo.nome}")
            print("Ações:")
            for acao in protocolo.acoes:
                print(f"- {acao}") 