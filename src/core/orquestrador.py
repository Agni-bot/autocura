import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..memoria.gerenciador_memoria import GerenciadorMemoria
from ..etica.validador_etico import ValidadorEtico
from ..guardiao.guardiao_cognitivo import GuardiaoCognitivo
from ..gerador.gerador_acoes import GeradorAcoes

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("orquestrador")

class Orquestrador:
    """Orquestrador - Coordena todos os componentes do sistema"""
    
    def __init__(self):
        # Inicializar componentes
        self.gerenciador_memoria = GerenciadorMemoria({
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_db": 0
        })
        self.validador_etico = ValidadorEtico(self.gerenciador_memoria)
        self.guardiao = GuardiaoCognitivo(self.gerenciador_memoria)
        self.gerador_acoes = GeradorAcoes(self.gerenciador_memoria, self.validador_etico)
        
        # Estado do sistema
        self.estado = {
            "status": "inicializado",
            "ultima_atualizacao": datetime.now().isoformat(),
            "ciclos_executados": 0
        }
        
        logger.info("Orquestrador inicializado")
    
    async def executar_ciclo(self) -> Dict[str, Any]:
        """Executa um ciclo completo do sistema"""
        try:
            # 1. Monitoramento de Saúde
            resultado_saude = self.guardiao.monitorar_saude_sistema()
            if resultado_saude["status"] == "alerta":
                logger.warning("Alertas detectados no monitoramento de saúde")
                for alerta in resultado_saude["alertas"]:
                    self.guardiao.aplicar_salvaguardas(alerta)
            
            # 2. Verificação Ética
            resultado_etica = self.guardiao.verificar_integridade_etica()
            if resultado_etica["status"] == "violacao":
                logger.warning("Violações éticas detectadas")
                for violacao in resultado_etica["violacoes"]:
                    self.guardiao.aplicar_salvaguardas(violacao)
            
            # 3. Verificação de Autonomia
            resultado_autonomia = self.guardiao.verificar_autonomia()
            if resultado_autonomia["transicoes_pendentes"]:
                logger.info("Transições de autonomia pendentes detectadas")
            
            # 4. Verificação de Aprendizado
            resultado_aprendizado = self.guardiao.verificar_aprendizado()
            if resultado_aprendizado["padroes_detectados"] > 0:
                logger.info("Novos padrões de aprendizado detectados")
            
            # 5. Geração de Ações
            if self._pode_gerar_acoes():
                contexto = self._gerar_contexto_acao()
                acao = self.gerador_acoes.gerar_acao(contexto)
                if acao["estado"] != "rejeitada":
                    logger.info(f"Nova ação gerada: {acao['id']}")
            
            # 6. Execução de Ações Pendentes
            acoes_pendentes = self.gerador_acoes.obter_acoes_pendentes()
            for acao in acoes_pendentes:
                if self._pode_executar_acao(acao):
                    resultado = self.gerador_acoes.executar_acao(acao["id"])
                    logger.info(f"Ação {acao['id']} executada: {resultado['estado']}")
            
            # Atualizar estado
            self.estado["ciclos_executados"] += 1
            self.estado["ultima_atualizacao"] = datetime.now().isoformat()
            
            return {
                "status": "sucesso",
                "ciclo": self.estado["ciclos_executados"],
                "resultados": {
                    "saude": resultado_saude,
                    "etica": resultado_etica,
                    "autonomia": resultado_autonomia,
                    "aprendizado": resultado_aprendizado
                }
            }
            
        except Exception as e:
            logger.error(f"Erro no ciclo de execução: {str(e)}")
            return {
                "status": "erro",
                "erro": str(e),
                "ciclo": self.estado["ciclos_executados"]
            }
    
    def _pode_gerar_acoes(self) -> bool:
        """Verifica se o sistema pode gerar novas ações"""
        estado = self.gerenciador_memoria.obter_estado_sistema()
        return (
            estado["status"] not in ["emergencia", "suspenso"] and
            estado["nivel_autonomia"] > 1
        )
    
    def _pode_executar_acao(self, acao: Dict[str, Any]) -> bool:
        """Verifica se uma ação pode ser executada"""
        estado = self.gerenciador_memoria.obter_estado_sistema()
        return (
            estado["status"] not in ["emergencia", "suspenso"] and
            estado["nivel_autonomia"] >= self._obter_nivel_autonomia_requerido(acao)
        )
    
    def _obter_nivel_autonomia_requerido(self, acao: Dict[str, Any]) -> int:
        """Determina o nível de autonomia requerido para uma ação"""
        tipo_acao = acao["tipo"]
        if tipo_acao == "hotfix":
            return 2
        elif tipo_acao == "refatoracao":
            return 3
        elif tipo_acao == "redesign":
            return 4
        else:
            return 1
    
    def _gerar_contexto_acao(self) -> Dict[str, Any]:
        """Gera o contexto para uma nova ação"""
        estado = self.gerenciador_memoria.obter_estado_sistema()
        metricas = estado.get("metricas_desempenho", {})
        
        # Análise de métricas para determinar tipo de ação
        if metricas.get("cpu_uso", 0) > 80:
            return {
                "tipo": "correcao",
                "impacto": 4,
                "urgencia": 5,
                "complexidade": 2,
                "recursos_cpu": 2,
                "recursos_memoria": 1
            }
        elif metricas.get("memoria_uso", 0) > 80:
            return {
                "tipo": "correcao",
                "impacto": 4,
                "urgencia": 5,
                "complexidade": 2,
                "recursos_cpu": 1,
                "recursos_memoria": 2
            }
        else:
            return {
                "tipo": "manutencao",
                "impacto": 2,
                "urgencia": 2,
                "complexidade": 1,
                "recursos_cpu": 1,
                "recursos_memoria": 1
            }
    
    async def executar_continuamente(self, intervalo: int = 60) -> None:
        """Executa o sistema continuamente com um intervalo entre ciclos"""
        logger.info("Iniciando execução contínua do sistema")
        
        while True:
            try:
                resultado = await self.executar_ciclo()
                if resultado["status"] == "erro":
                    logger.error(f"Erro no ciclo {resultado['ciclo']}: {resultado['erro']}")
                    await asyncio.sleep(intervalo * 2)  # Dobra o intervalo em caso de erro
                else:
                    logger.info(f"Ciclo {resultado['ciclo']} executado com sucesso")
                    await asyncio.sleep(intervalo)
            
            except Exception as e:
                logger.error(f"Erro na execução contínua: {str(e)}")
                await asyncio.sleep(intervalo * 2)
    
    def obter_estado_sistema(self) -> Dict[str, Any]:
        """Retorna o estado atual do sistema"""
        return {
            **self.estado,
            "memoria": self.gerenciador_memoria.obter_estado_sistema(),
            "estatisticas_acoes": self.gerador_acoes.obter_estatisticas()
        }
    
    def obter_relatorio_etica(self) -> Dict[str, Any]:
        """Retorna o relatório ético do sistema"""
        return self.validador_etico.gerar_relatorio_etica()

async def main():
    """Função principal"""
    orquestrador = Orquestrador()
    await orquestrador.executar_continuamente()

if __name__ == "__main__":
    asyncio.run(main()) 