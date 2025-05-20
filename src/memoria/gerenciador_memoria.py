import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import redis
from prometheus_client import Counter, Gauge, Histogram
from dataclasses import dataclass

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
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o gerenciador de memória.
        
        Args:
            config: Configuração do gerenciador
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Cliente Redis
        self.redis = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        
        # Cache local
        self.cache_local: Dict[str, EntidadeMemoria] = {}
        
        # Métricas Prometheus
        self.metricas = {
            "entidades_criadas": Counter(
                "entidades_memoria_criadas_total",
                "Total de entidades criadas",
                ["tipo"]
            ),
            "entidades_atualizadas": Counter(
                "entidades_memoria_atualizadas_total",
                "Total de entidades atualizadas",
                ["tipo"]
            ),
            "tamanho_memoria": Gauge(
                "tamanho_memoria_bytes",
                "Tamanho total da memória em bytes"
            ),
            "tempo_operacao": Histogram(
                "tempo_operacao_memoria_seconds",
                "Tempo de operações na memória",
                ["operacao"]
            )
        }
        
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
        
        self.logger.info("Gerenciador de Memória inicializado")
    
    async def criar_entidade(self, tipo: str, dados: Dict[str, Any], tags: List[str] = None) -> Optional[EntidadeMemoria]:
        """Cria uma nova entidade na memória.
        
        Args:
            tipo: Tipo da entidade
            dados: Dados da entidade
            tags: Tags da entidade
            
        Returns:
            Entidade criada ou None em caso de erro
        """
        if tipo not in self.tipos_entidade:
            self.logger.error(f"Tipo de entidade desconhecido: {tipo}")
            return None
        
        try:
            with self.metricas["tempo_operacao"].labels(operacao="criar").time():
                # Gera ID único
                entidade_id = f"{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Cria entidade
                entidade = EntidadeMemoria(
                    id=entidade_id,
                    tipo=tipo,
                    dados=dados,
                    timestamp=datetime.now(),
                    versao="1.0",
                    tags=tags or [],
                    relacionamentos=[]
                )
                
                # Verifica tamanho
                dados_json = json.dumps(entidade.__dict__, default=str)
                if len(dados_json) > self.tipos_entidade[tipo]["max_size"]:
                    self.logger.error(f"Entidade excede tamanho máximo: {len(dados_json)} bytes")
                    return None
                
                # Salva no Redis
                self.redis.set(
                    f"entidade:{entidade_id}",
                    dados_json,
                    ex=int(self.tipos_entidade[tipo]["ttl"].total_seconds())
                )
                
                # Atualiza cache local
                self.cache_local[entidade_id] = entidade
                
                # Atualiza métricas
                self.metricas["entidades_criadas"].labels(tipo=tipo).inc()
                self.metricas["tamanho_memoria"].inc(len(dados_json))
                
                self.logger.info(f"Entidade criada: {entidade_id}")
                return entidade
                
        except Exception as e:
            self.logger.error(f"Erro ao criar entidade: {e}")
            return None
    
    async def atualizar_entidade(self, entidade_id: str, dados: Dict[str, Any]) -> bool:
        """Atualiza uma entidade existente.
        
        Args:
            entidade_id: ID da entidade
            dados: Novos dados
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            with self.metricas["tempo_operacao"].labels(operacao="atualizar").time():
                # Obtém entidade
                entidade = await self.obter_entidade(entidade_id)
                if not entidade:
                    return False
                
                # Incrementa versão
                versao_atual = float(entidade.versao)
                nova_versao = f"{versao_atual + 0.1:.1f}"
                
                # Atualiza entidade
                entidade.dados = dados
                entidade.timestamp = datetime.now()
                entidade.versao = nova_versao
                
                # Verifica tamanho
                dados_json = json.dumps(entidade.__dict__, default=str)
                if len(dados_json) > self.tipos_entidade[entidade.tipo]["max_size"]:
                    self.logger.error(f"Entidade excede tamanho máximo: {len(dados_json)} bytes")
                    return False
                
                # Salva no Redis
                self.redis.set(
                    f"entidade:{entidade_id}",
                    dados_json,
                    ex=int(self.tipos_entidade[entidade.tipo]["ttl"].total_seconds())
                )
                
                # Atualiza cache local
                self.cache_local[entidade_id] = entidade
                
                # Atualiza métricas
                self.metricas["entidades_atualizadas"].labels(tipo=entidade.tipo).inc()
                
                self.logger.info(f"Entidade atualizada: {entidade_id} (versão {nova_versao})")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar entidade: {e}")
            return False
    
    async def obter_entidade(self, entidade_id: str) -> Optional[EntidadeMemoria]:
        """Obtém uma entidade pelo ID.
        
        Args:
            entidade_id: ID da entidade
            
        Returns:
            Entidade ou None se não encontrada
        """
        try:
            with self.metricas["tempo_operacao"].labels(operacao="obter").time():
                # Verifica cache local
                if entidade_id in self.cache_local:
                    return self.cache_local[entidade_id]
                
                # Tenta obter do Redis
                dados_json = self.redis.get(f"entidade:{entidade_id}")
                if not dados_json:
                    return None
                
                # Converte para entidade
                dados = json.loads(dados_json)
                entidade = EntidadeMemoria(**dados)
                
                # Atualiza cache local
                self.cache_local[entidade_id] = entidade
                
                return entidade
                
        except Exception as e:
            self.logger.error(f"Erro ao obter entidade: {e}")
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
        """Obtém estatísticas da memória.
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            with self.metricas["tempo_operacao"].labels(operacao="estatisticas").time():
                stats = {
                    "timestamp": datetime.now(),
                    "total_entidades": len(self.cache_local),
                    "por_tipo": {},
                    "por_tag": {},
                    "tamanho_total": 0
                }
                
                # Conta entidades por tipo e tag
                for entidade in self.cache_local.values():
                    if entidade.tipo not in stats["por_tipo"]:
                        stats["por_tipo"][entidade.tipo] = 0
                    stats["por_tipo"][entidade.tipo] += 1
                    
                    for tag in entidade.tags:
                        if tag not in stats["por_tag"]:
                            stats["por_tag"][tag] = 0
                        stats["por_tag"][tag] += 1
                    
                    # Calcula tamanho total
                    dados_json = json.dumps(entidade.__dict__, default=str)
                    stats["tamanho_total"] += len(dados_json)
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
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