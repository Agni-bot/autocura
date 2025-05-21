import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import redis
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry
from dataclasses import dataclass
import os
import uuid

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gerenciador_memoria")

@dataclass
class EntidadeMemoria:
    """Representa uma entidade na memória compartilhada."""
    id: str
    tipo: str
    dados: Dict[str, Any]
    timestamp: datetime
    versao: str
    tags: List[str]
    relacionamentos: List[str]

class GerenciadorMemoria:
    """Módulo Gerenciador de Memória para gerenciar a memória compartilhada do sistema."""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        memoria_path: Optional[str] = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        registry: Optional[CollectorRegistry] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Inicializa o gerenciador de memória.
        
        Args:
            config: Configuração do gerenciador (opcional)
            memoria_path: Caminho do arquivo de memória (opcional)
            redis_host: Host do Redis (padrão: localhost)
            redis_port: Porta do Redis (padrão: 6379)
            redis_db: Banco de dados do Redis (padrão: 0)
            registry: Registry do Prometheus (opcional)
            logger: Logger customizado (opcional)
        """
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        
        # Define o caminho do arquivo de memória
        self.caminho_memoria = Path(memoria_path or self.config.get("memoria_path", "data/memoria_compartilhada.json"))
        self.caminho_memoria.parent.mkdir(parents=True, exist_ok=True)
        
        # Cliente Redis
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        
        # Cache local
        self.cache_local: Dict[str, EntidadeMemoria] = {}
        
        # Inicializa métricas Prometheus
        self.registry = registry or CollectorRegistry()
        self.metricas = self._inicializar_metricas()
        
        # Configuração de tipos de entidade
        self.tipos_entidade = {
            "conhecimento": {
                "ttl": timedelta(days=30),
                "max_size": 1024 * 1024  # 1MB
            },
            "evento": {
                "ttl": timedelta(days=7),
                "max_size": 64 * 1024  # 64KB
            },
            "metricas": {
                "ttl": timedelta(hours=24),
                "max_size": 32 * 1024  # 32KB
            },
            "configuracao": {
                "ttl": timedelta(days=365),
                "max_size": 16 * 1024  # 16KB
            }
        }
        
        # Inicializa memória
        self.memoria = self._carregar_memoria()
        if not self.memoria:
            self.memoria = self._criar_memoria_inicial()
            self._salvar_memoria(self.memoria)
        
        self.logger.info("Gerenciador de Memória inicializado")
    
    def _inicializar_metricas(self) -> Dict[str, Any]:
        """Inicializa as métricas do Prometheus."""
        try:
            # Verifica se as métricas já existem no registro
            if hasattr(self.registry, '_names_to_collectors'):
                for name in self.registry._names_to_collectors:
                    if name.startswith('entidades_memoria_'):
                        return self.metricas

            # Inicializa novas métricas
            self.metricas = {
                "entidades_criadas": Counter(
                    "entidades_memoria_criadas",
                    "Número de entidades criadas na memória",
                    ["tipo"],
                    registry=self.registry
                ),
                "entidades_atualizadas": Counter(
                    "entidades_memoria_atualizadas",
                    "Número de entidades atualizadas na memória",
                    ["tipo"],
                    registry=self.registry
                ),
                "entidades_removidas": Counter(
                    "entidades_memoria_removidas",
                    "Número de entidades removidas da memória",
                    ["tipo"],
                    registry=self.registry
                ),
                "operacoes_redis": Counter(
                    "operacoes_redis_total",
                    "Número total de operações no Redis",
                    ["operacao"],
                    registry=self.registry
                ),
                "tempo_operacao": Histogram(
                    "tempo_operacao_segundos",
                    "Tempo de execução das operações",
                    ["operacao"],
                    registry=self.registry
                )
            }
            return self.metricas
        except Exception as e:
            self.logger.error(f"Erro ao inicializar métricas: {str(e)}")
            return {}
    
    async def criar_entidade(self, tipo: str, dados: Dict[str, Any], tags: List[str] = None) -> Optional[EntidadeMemoria]:
        """Cria uma nova entidade na memória."""
        try:
            if "entidades" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["entidades"] = {}
            if tipo not in self.memoria["memoria_operacional"]["entidades"]:
                self.memoria["memoria_operacional"]["entidades"][tipo] = []
            entidade = EntidadeMemoria(
                id=str(uuid.uuid4()),
                tipo=tipo,
                dados=dados,
                tags=tags or [],
                timestamp=datetime.now().isoformat(),
                versao="1.0",
                relacionamentos=[]
            )
            self.memoria["memoria_operacional"]["entidades"][tipo].append(entidade.__dict__)
            self._salvar_memoria(self.memoria)
            if "entidades_criadas" in self.metricas:
                self.metricas["entidades_criadas"].labels(tipo=tipo).inc()
            self.logger.info(f"Nova entidade do tipo {tipo} criada")
            return entidade
        except Exception as e:
            self.logger.error(f"Erro ao criar entidade: {str(e)}")
            return None
    
    async def atualizar_entidade(self, id: str, dados: Dict[str, Any]) -> bool:
        """Atualiza uma entidade na memória."""
        try:
            for tipo in self.memoria["memoria_operacional"]["entidades"]:
                for i, entidade in enumerate(self.memoria["memoria_operacional"]["entidades"][tipo]):
                    if entidade["id"] == id:
                        entidade["dados"].update(dados)
                        entidade["timestamp"] = datetime.now().isoformat()
                        self._salvar_memoria(self.memoria)
                        
                        if "entidades_atualizadas" in self.metricas:
                            self.metricas["entidades_atualizadas"].labels(tipo=tipo).inc()
                        
                        self.logger.info(f"Entidade {id} atualizada")
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao atualizar entidade: {str(e)}")
            return False
    
    async def obter_entidade(self, id: str) -> Optional[EntidadeMemoria]:
        """Obtém uma entidade da memória pelo ID."""
        try:
            for tipo in self.memoria["memoria_operacional"]["entidades"]:
                for entidade in self.memoria["memoria_operacional"]["entidades"][tipo]:
                    if entidade["id"] == id:
                        return EntidadeMemoria(**entidade)
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter entidade: {str(e)}")
            return None
    
    async def buscar_entidades(self, tipo: Optional[str] = None, tags: Optional[List[str]] = None) -> List[EntidadeMemoria]:
        """Busca entidades por tipo e/ou tags.
        
        Args:
            tipo: Tipo da entidade (opcional)
            tags: Tags da entidade (opcional)
            
        Returns:
            Lista de entidades encontradas
        """
        try:
            with self.metricas["tempo_operacao"].labels(operacao="buscar").time():
                entidades = []
                
                # Busca no Redis
                for chave in self.redis.scan_iter("entidade:*"):
                    dados_json = self.redis.get(chave)
                    if not dados_json:
                        continue
                    
                    dados = json.loads(dados_json)
                    entidade = EntidadeMemoria(**dados)
                    
                    # Filtra por tipo
                    if tipo and entidade.tipo != tipo:
                        continue
                    
                    # Filtra por tags
                    if tags and not all(tag in entidade.tags for tag in tags):
                        continue
                    
                    entidades.append(entidade)
                
                return entidades
                
        except Exception as e:
            self.logger.error(f"Erro ao buscar entidades: {e}")
            return []
    
    async def adicionar_relacionamento(self, entidade_id: str, entidade_relacionada_id: str) -> bool:
        """Adiciona um relacionamento entre entidades.
        
        Args:
            entidade_id: ID da entidade
            entidade_relacionada_id: ID da entidade relacionada
            
        Returns:
            True se adicionado com sucesso
        """
        try:
            with self.metricas["tempo_operacao"].labels(operacao="relacionar").time():
                # Obtém entidades
                entidade = await self.obter_entidade(entidade_id)
                entidade_relacionada = await self.obter_entidade(entidade_relacionada_id)
                
                if not entidade or not entidade_relacionada:
                    return False
                
                # Adiciona relacionamento bidirecional
                if entidade_relacionada_id not in entidade.relacionamentos:
                    entidade.relacionamentos.append(entidade_relacionada_id)
                if entidade_id not in entidade_relacionada.relacionamentos:
                    entidade_relacionada.relacionamentos.append(entidade_id)
                
                # Salva no Redis
                self.redis.set(
                    f"entidade:{entidade_id}",
                    json.dumps(entidade.__dict__, default=str),
                    ex=int(self.tipos_entidade[entidade.tipo]["ttl"].total_seconds())
                )
                
                self.redis.set(
                    f"entidade:{entidade_relacionada_id}",
                    json.dumps(entidade_relacionada.__dict__, default=str),
                    ex=int(self.tipos_entidade[entidade_relacionada.tipo]["ttl"].total_seconds())
                )
                
                # Atualiza cache local
                self.cache_local[entidade_id] = entidade
                self.cache_local[entidade_relacionada_id] = entidade_relacionada
                
                self.logger.info(f"Relacionamento adicionado: {entidade_id} <-> {entidade_relacionada_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao adicionar relacionamento: {e}")
            return False
    
    async def obter_relacionamentos(self, entidade_id: str) -> List[EntidadeMemoria]:
        """Obtém as entidades relacionadas.
        
        Args:
            entidade_id: ID da entidade
            
        Returns:
            Lista de entidades relacionadas
        """
        try:
            with self.metricas["tempo_operacao"].labels(operacao="relacionamentos").time():
                entidade = await self.obter_entidade(entidade_id)
                if not entidade:
                    return []
                
                relacionamentos = []
                for rel_id in entidade.relacionamentos:
                    rel = await self.obter_entidade(rel_id)
                    if rel:
                        relacionamentos.append(rel)
                
                return relacionamentos
                
        except Exception as e:
            self.logger.error(f"Erro ao obter relacionamentos: {e}")
            return []
    
    async def limpar_cache(self) -> None:
        """Limpa o cache local."""
        self.cache_local.clear()
        self.logger.info("Cache local limpo")
    
    async def obter_estatisticas(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória."""
        try:
            stats = {
                "total_entidades": sum(
                    len(entidades)
                    for entidades in self.memoria["memoria_operacional"]["entidades"].values()
                ),
                "entidades_por_tipo": {
                    tipo: len(entidades)
                    for tipo, entidades in self.memoria["memoria_operacional"]["entidades"].items()
                },
                "total_acoes": len(self.memoria["memoria_operacional"]["acoes"]),
                "total_validacoes": len(self.memoria["memoria_etica"].get("validacoes", [])),
                "total_violacoes": len(self.memoria["memoria_etica"].get("violacoes", [])),
                "ultima_atualizacao": datetime.now().isoformat()
            }
            return stats
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}

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
                    memoria = json.load(f)
                # Garante que a estrutura de entidades exista
                if "entidades" not in memoria["memoria_operacional"]:
                    memoria["memoria_operacional"]["entidades"] = {}
                return memoria
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
                "anomalias": [],
                "entidades": {}  # Garante que sempre existe
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
        """Registra uma validação ética.
        
        Args:
            validacao: Dados da validação ética
        """
        if "validacoes" not in self.memoria["memoria_etica"]:
            self.memoria["memoria_etica"]["validacoes"] = []
        
        self.memoria["memoria_etica"]["validacoes"].append({
            **validacao,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        self.logger.info("Nova validação ética registrada")

    async def validar_decisao_etica(self, decisao: Dict[str, Any]) -> Dict[str, Any]:
        """Valida uma decisão sob aspectos éticos (async)."""
        principios = self.memoria["memoria_etica"].get("principios", {})
        resultado = {
            "aprovado": True,
            "justificativa": "Decisão validada",
            "nivel_confianca": 1.0,
            "avaliacao_principios": {}
        }
        if "principios_afetados" in decisao:
            for principio in decisao["principios_afetados"]:
                if principio in principios:
                    resultado["avaliacao_principios"][principio] = principios[principio]
                    if principios[principio] < 0.8:
                        resultado["aprovado"] = False
                        resultado["justificativa"] = f"Violou o princípio de {principio}"
                        resultado["nivel_confianca"] = principios[principio]
        self.registrar_validacao_etica({
            "tipo": "decisao",
            "contexto": decisao.get("contexto", "geral"),
            "resultado": "aprovado" if resultado["aprovado"] else "reprovado",
            "justificativa": resultado["justificativa"],
            "nivel_confianca": resultado["nivel_confianca"]
        })
        return resultado

    def registrar_violacao_etica(self, violacao: Dict[str, Any]) -> None:
        """Registra uma violação ética.
        
        Args:
            violacao: Dados da violação ética
        """
        if "violacoes" not in self.memoria["memoria_etica"]:
            self.memoria["memoria_etica"]["violacoes"] = []
        
        self.memoria["memoria_etica"]["violacoes"].append({
            **violacao,
            "timestamp": datetime.now().isoformat()
        })
        self._salvar_memoria(self.memoria)
        self.logger.info("Nova violação ética registrada")

    def obter_validacoes_eticas(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna as validações éticas mais recentes.
        
        Args:
            limite: Número máximo de validações a retornar
            
        Returns:
            Lista de validações éticas
        """
        validacoes = self.memoria["memoria_etica"].get("validacoes", [])
        return validacoes[-limite:]

    def obter_violacoes_eticas(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna as violações éticas mais recentes.
        
        Args:
            limite: Número máximo de violações a retornar
            
        Returns:
            Lista de violações éticas
        """
        violacoes = self.memoria["memoria_etica"].get("violacoes", [])
        return violacoes[-limite:]

    def obter_historico_etico(self) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna o histórico ético completo.
        
        Returns:
            Dicionário com histórico de validações e violações
        """
        return {
            "validacoes": self.memoria["memoria_etica"].get("validacoes", []),
            "violacoes": self.memoria["memoria_etica"].get("violacoes", [])
        }

    def analisar_tendencia_etica(self) -> Dict[str, Any]:
        """Analisa a tendência ética do sistema.
        
        Returns:
            Análise de tendência ética
        """
        validacoes = self.memoria["memoria_etica"].get("validacoes", [])
        violacoes = self.memoria["memoria_etica"].get("violacoes", [])
        
        total_validacoes = len(validacoes)
        total_violacoes = len(violacoes)
        
        if total_validacoes == 0:
            return {
                "taxa_aprovacao": 0.0,
                "taxa_violacao": 0.0,
                "tendencia": "neutra",
                "recomendacoes": ["Iniciar monitoramento ético"]
            }
        
        taxa_aprovacao = sum(1 for v in validacoes if v["resultado"] == "aprovado") / total_validacoes
        taxa_violacao = total_violacoes / (total_validacoes + total_violacoes)
        
        # Determina tendência
        if taxa_aprovacao > 0.9 and taxa_violacao < 0.1:
            tendencia = "positiva"
            recomendacoes = ["Manter práticas atuais"]
        elif taxa_aprovacao < 0.7 or taxa_violacao > 0.3:
            tendencia = "negativa"
            recomendacoes = [
                "Revisar princípios éticos",
                "Implementar controles adicionais",
                "Realizar auditoria ética"
            ]
        else:
            tendencia = "neutra"
            recomendacoes = ["Monitorar evolução"]
        
        return {
            "taxa_aprovacao": taxa_aprovacao,
            "taxa_violacao": taxa_violacao,
            "tendencia": tendencia,
            "recomendacoes": recomendacoes
        }

    def registrar_principios_eticos(self, principios: Dict[str, float]) -> None:
        """Registra princípios éticos do sistema.
        
        Args:
            principios: Dicionário com princípios e seus pesos
        """
        self.memoria["memoria_etica"]["principios"] = principios
        self._salvar_memoria(self.memoria)
        self.logger.info("Princípios éticos atualizados")

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
        data_limite = (datetime.now() - timedelta(days=dias)).isoformat()
        
        # Limpa entidades antigas
        for tipo in self.memoria["memoria_operacional"]["entidades"]:
            self.memoria["memoria_operacional"]["entidades"][tipo] = [
                e for e in self.memoria["memoria_operacional"]["entidades"][tipo]
                if e["timestamp"] > data_limite
            ]
        
        # Limpa ações antigas
        self.memoria["memoria_operacional"]["acoes"] = [
            a for a in self.memoria["memoria_operacional"]["acoes"]
            if a["timestamp"] > data_limite
        ]
        
        # Limpa validações éticas antigas
        if "validacoes" in self.memoria["memoria_etica"]:
            self.memoria["memoria_etica"]["validacoes"] = [
                v for v in self.memoria["memoria_etica"]["validacoes"]
                if v["timestamp"] > data_limite
            ]
        
        if "violacoes" in self.memoria["memoria_etica"]:
            self.memoria["memoria_etica"]["violacoes"] = [
                v for v in self.memoria["memoria_etica"]["violacoes"]
                if v["timestamp"] > data_limite
            ]
        
        self._salvar_memoria(self.memoria)
        self.logger.info(f"Memória antiga limpa (mais antiga que {dias} dias)") 