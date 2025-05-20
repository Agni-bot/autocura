import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gerenciador_memoria")

class GerenciadorMemoria:
    """Gerenciador da memória compartilhada do sistema"""
    
    def __init__(self, caminho_memoria: str = "memoria_compartilhada.json"):
        self.caminho_memoria = Path(caminho_memoria)
        self.memoria = self._carregar_memoria()
        logger.info("Gerenciador de Memória inicializado")
    
    def initialize(self) -> None:
        """Inicializa o gerenciador de memória"""
        try:
            self.memoria = self._carregar_memoria()
            logger.info("Gerenciador de Memória inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar gerenciador de memória: {str(e)}")
            raise
    
    def _carregar_memoria(self) -> Dict[str, Any]:
        """Carrega a memória compartilhada do arquivo"""
        try:
            if self.caminho_memoria.exists():
                with open(self.caminho_memoria, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Arquivo de memória não encontrado. Criando novo.")
                return self._criar_memoria_inicial()
        except Exception as e:
            logger.error(f"Erro ao carregar memória: {str(e)}")
            raise
    
    def _criar_memoria_inicial(self) -> Dict[str, Any]:
        """Cria uma nova memória compartilhada com estrutura inicial"""
        memoria = {
            "estado_sistema": {
                "nivel_autonomia": 1,
                "status": "inicializado",
                "ultima_atualizacao": datetime.now().isoformat(),
                "metricas_desempenho": {},
                "alertas_ativos": [],
                "incidentes": []
            },
            "memoria_operacional": {
                "decisoes": [],
                "acoes": [],
                "validacoes": [],
                "auditorias": [],
                "diagnosticos": [],
                "correcoes": [],
                "anomalias": []
            },
            "memoria_etica": {
                "principios": [],
                "violacoes": [],
                "ajustes": [],
                "relatorios": []
            },
            "memoria_tecnica": {
                "configuracoes": {},
                "dependencias": {},
                "logs": [],
                "metricas": {}
            },
            "memoria_cognitiva": {
                "aprendizados": [],
                "padroes": [],
                "heuristicas": [],
                "adaptacoes": []
            },
            "memoria_autonomia": {
                "transicoes": [],
                "niveis": {},
                "criterios": {},
                "validacoes": []
            }
        }
        self._salvar_memoria(memoria)
        return memoria
    
    def _salvar_memoria(self, memoria: Dict[str, Any]) -> None:
        """Salva a memória compartilhada no arquivo"""
        try:
            with open(self.caminho_memoria, 'w', encoding='utf-8') as f:
                json.dump(memoria, f, indent=2, ensure_ascii=False)
            logger.info("Memória salva com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {str(e)}")
            raise
    
    def atualizar_estado_sistema(self, atualizacao: Dict[str, Any]) -> None:
        """Atualiza o estado do sistema"""
        self.memoria["estado_sistema"].update(atualizacao)
        self.memoria["estado_sistema"]["ultima_atualizacao"] = datetime.now().isoformat()
        self._salvar_memoria(self.memoria)
        logger.info("Estado do sistema atualizado")
    
    def registrar_decisao(self, decisao: Dict[str, Any]) -> None:
        """Registra uma nova decisão na memória operacional"""
        self.memoria["memoria_operacional"]["decisoes"].append({
            **decisao,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Nova decisão registrada")
    
    def registrar_acao(self, acao: Dict[str, Any]) -> None:
        """Registra uma nova ação na memória operacional"""
        self.memoria["memoria_operacional"]["acoes"].append({
            **acao,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Nova ação registrada")
    
    def registrar_validacao_etica(self, validacao: Dict[str, Any]) -> None:
        """Registra uma nova validação ética"""
        self.memoria["memoria_etica"]["validacoes"].append({
            **validacao,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Nova validação ética registrada")
    
    def registrar_aprendizado(self, aprendizado: Dict[str, Any]) -> None:
        """Registra um novo aprendizado na memória cognitiva"""
        self.memoria["memoria_cognitiva"]["aprendizados"].append({
            **aprendizado,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Novo aprendizado registrado")
    
    def registrar_transicao_autonomia(self, transicao: Dict[str, Any]) -> None:
        """Registra uma nova transição de autonomia"""
        self.memoria["memoria_autonomia"]["transicoes"].append({
            **transicao,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Nova transição de autonomia registrada")
    
    def registrar_diagnostico(self, diagnostico: Dict[str, Any]) -> None:
        """Registra um novo diagnóstico do sistema"""
        if "diagnosticos" not in self.memoria["memoria_operacional"]:
            self.memoria["memoria_operacional"]["diagnosticos"] = []
        
        self.memoria["memoria_operacional"]["diagnosticos"].append({
            **diagnostico,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Novo diagnóstico registrado")

    def registrar_correcao(self, correcao: Dict[str, Any]) -> None:
        """Registra uma nova correção automática"""
        if "correcoes" not in self.memoria["memoria_operacional"]:
            self.memoria["memoria_operacional"]["correcoes"] = []
        
        self.memoria["memoria_operacional"]["correcoes"].append({
            **correcao,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Nova correção registrada")

    def registrar_anomalia(self, anomalia: Dict[str, Any]) -> None:
        """Registra uma nova anomalia detectada"""
        if "anomalias" not in self.memoria["memoria_operacional"]:
            self.memoria["memoria_operacional"]["anomalias"] = []
        
        self.memoria["memoria_operacional"]["anomalias"].append({
            **anomalia,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Nova anomalia registrada")

    def obter_estado_sistema(self) -> Dict[str, Any]:
        """Retorna o estado atual do sistema"""
        return self.memoria["estado_sistema"]
    
    def obter_decisoes_recentes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna as decisões mais recentes"""
        return self.memoria["memoria_operacional"]["decisoes"][-limite:]
    
    def obter_acoes_recentes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna as ações mais recentes"""
        return self.memoria["memoria_operacional"]["acoes"][-limite:]
    
    def obter_validacoes_eticas(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna as validações éticas mais recentes"""
        return self.memoria["memoria_etica"]["validacoes"][-limite:]
    
    def obter_aprendizados_recentes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna os aprendizados mais recentes"""
        return self.memoria["memoria_cognitiva"]["aprendizados"][-limite:]
    
    def obter_transicoes_autonomia(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna as transições de autonomia mais recentes"""
        return self.memoria["memoria_autonomia"]["transicoes"][-limite:]
    
    def obter_diagnosticos_recentes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna os diagnósticos mais recentes"""
        return self.memoria["memoria_operacional"]["diagnosticos"][-limite:]
    
    def obter_correcoes_recentes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna as correções mais recentes"""
        return self.memoria["memoria_operacional"]["correcoes"][-limite:]
    
    def obter_anomalias_recentes(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna as anomalias mais recentes"""
        return self.memoria["memoria_operacional"]["anomalias"][-limite:]
    
    def registrar_metricas_desempenho(self, metricas: Dict[str, Any]) -> None:
        """Registra novas métricas de desempenho"""
        self.memoria["estado_sistema"]["metricas_desempenho"].update(metricas)
        self.memoria["estado_sistema"]["ultima_atualizacao"] = datetime.now().isoformat()
        self._salvar_memoria(self.memoria)
        logger.info("Métricas de desempenho atualizadas")

    def registrar_alerta(self, alerta: Dict[str, Any]) -> None:
        """Registra um novo alerta"""
        self.memoria["estado_sistema"]["alertas_ativos"].append({
            **alerta,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Novo alerta registrado")

    def registrar_incidente(self, incidente: Dict[str, Any]) -> None:
        """Registra um novo incidente"""
        self.memoria["estado_sistema"]["incidentes"].append({
            **incidente,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        logger.info("Novo incidente registrado")
    
    def limpar_memoria_antiga(self, dias: int = 30) -> None:
        """Limpa registros antigos da memória"""
        data_limite = (datetime.now() - datetime.timedelta(days=dias)).isoformat()
        
        for categoria in ["decisoes", "acoes", "validacoes", "auditorias"]:
            self.memoria["memoria_operacional"][categoria] = [
                item for item in self.memoria["memoria_operacional"][categoria]
                if item["timestamp"] > data_limite
            ]
        
        for categoria in ["aprendizados", "padroes", "heuristicas", "adaptacoes"]:
            self.memoria["memoria_cognitiva"][categoria] = [
                item for item in self.memoria["memoria_cognitiva"][categoria]
                if item["timestamp"] > data_limite
            ]
        
        self._salvar_memoria(self.memoria)
        logger.info(f"Memória antiga limpa (mais de {dias} dias)") 