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
        """Valida uma decisão contra os princípios éticos registrados."""
        try:
            if "principios_eticos" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["principios_eticos"] = {}
            
            # Calcula score ético
            score = 0.0
            total_peso = 0.0
            
            for principio, peso in self.memoria["memoria_operacional"]["principios_eticos"].items():
                if principio in decisao.get("principios", {}):
                    score += peso * decisao["principios"][principio]
                    total_peso += peso
            
            # Normaliza score
            score_normalizado = score / total_peso if total_peso > 0 else 0.0
            
            # Define threshold para aprovação
            aprovado = score_normalizado >= 0.7
            
            resultado = {
                "aprovado": aprovado,
                "score": score_normalizado,
                "justificativa": "Decisão alinhada com princípios éticos" if aprovado else "Decisão não atende aos critérios éticos mínimos"
            }
            
            # Registra validação
            self.registrar_validacao_etica({
                "decisao_id": decisao.get("id"),
                "score": score_normalizado,
                "aprovado": aprovado,
                "timestamp": datetime.now().isoformat()
            })
            
            return resultado
        except Exception as e:
            self.logger.error(f"Erro ao validar decisão ética: {str(e)}")
            return {
                "aprovado": False,
                "score": 0.0,
                "justificativa": f"Erro na validação: {str(e)}"
            }

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
        """Analisa tendências nas validações éticas."""
        try:
            if "validacoes_eticas" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["validacoes_eticas"] = []
            
            validacoes = self.memoria["memoria_operacional"]["validacoes_eticas"]
            total_validacoes = len(validacoes)
            
            if total_validacoes == 0:
                return {
                    "total_validacoes": 0,
                    "taxa_aprovacao": 0.0,
                    "tendencia": "neutra",
                    "recomendacoes": []
                }
            
            # Calcula taxa de aprovação
            aprovacoes = sum(1 for v in validacoes if v.get("aprovado", False))
            taxa_aprovacao = aprovacoes / total_validacoes
            
            # Determina tendência
            if taxa_aprovacao >= 0.8:
                tendencia = "positiva"
                recomendacoes = ["Manter práticas atuais", "Documentar casos de sucesso"]
            elif taxa_aprovacao >= 0.6:
                tendencia = "neutra"
                recomendacoes = ["Revisar princípios éticos", "Monitorar decisões críticas"]
            else:
                tendencia = "negativa"
                recomendacoes = ["Revisar critérios éticos", "Implementar treinamento adicional"]
            
            return {
                "total_validacoes": total_validacoes,
                "taxa_aprovacao": taxa_aprovacao,
                "tendencia": tendencia,
                "recomendacoes": recomendacoes
            }
        except Exception as e:
            self.logger.error(f"Erro ao analisar tendência ética: {str(e)}")
            return {
                "total_validacoes": 0,
                "taxa_aprovacao": 0.0,
                "tendencia": "neutra",
                "recomendacoes": []
            }

    def registrar_principios_eticos(self, principios: Dict[str, float]) -> None:
        """Registra princípios éticos do sistema.
        
        Args:
            principios: Dicionário com princípios e seus pesos
        """
        self.memoria["memoria_etica"]["principios"] = principios
        self._salvar_memoria(self.memoria)
        self.logger.info("Princípios éticos atualizados")

    def registrar_incidente(self, incidente: Dict[str, Any]) -> None:
        """Registra um incidente no sistema."""
        try:
            if "incidentes" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["incidentes"] = []
            
            # Adiciona timestamp se não existir
            if "timestamp" not in incidente:
                incidente["timestamp"] = datetime.now().isoformat()
            
            # Adiciona ID se não existir
            if "id" not in incidente:
                incidente["id"] = f"inc_{len(self.memoria['memoria_operacional']['incidentes']) + 1}"
            
            # Registra incidente
            self.memoria["memoria_operacional"]["incidentes"].append(incidente)
            
            # Se for incidente crítico, registra alerta
            if incidente.get("severidade") in ["alta", "critica"]:
                self.registrar_alerta({
                    "tipo": "incidente_critico",
                    "descricao": f"Incidente crítico detectado: {incidente.get('descricao', 'Sem descrição')}",
                    "severidade": incidente.get("severidade"),
                    "componente": incidente.get("componente"),
                    "timestamp": datetime.now().isoformat()
                })
            
            self._salvar_memoria(self.memoria)
            self.logger.info(f"Incidente registrado: {incidente['id']}")
        except Exception as e:
            self.logger.error(f"Erro ao registrar incidente: {str(e)}")

    def registrar_aprendizado(self, aprendizado: Dict[str, Any]) -> None:
        """Registra um evento de aprendizado."""
        try:
            if "aprendizados" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["aprendizados"] = []
            
            # Adiciona timestamp se não existir
            if "timestamp" not in aprendizado:
                aprendizado["timestamp"] = datetime.now().isoformat()
            
            # Adiciona ID se não existir
            if "id" not in aprendizado:
                aprendizado["id"] = f"apr_{len(self.memoria['memoria_operacional']['aprendizados']) + 1}"
            
            # Registra aprendizado
            self.memoria["memoria_operacional"]["aprendizados"].append(aprendizado)
            
            # Se for aprendizado de alto impacto, registra transição de autonomia
            if aprendizado.get("impacto") == "alto":
                self.registrar_transicao_autonomia({
                    "tipo": "aprendizado",
                    "descricao": f"Transição baseada em aprendizado: {aprendizado.get('descricao', 'Sem descrição')}",
                    "nivel_anterior": self.memoria["memoria_operacional"].get("nivel_autonomia", "baixo"),
                    "nivel_novo": "medio",
                    "timestamp": datetime.now().isoformat()
                })
            
            self._salvar_memoria(self.memoria)
            self.logger.info(f"Aprendizado registrado: {aprendizado['id']}")
        except Exception as e:
            self.logger.error(f"Erro ao registrar aprendizado: {str(e)}")

    def registrar_transicao_autonomia(self, transicao: Dict[str, Any]) -> None:
        """Registra uma transição no nível de autonomia do sistema."""
        try:
            if "transicoes_autonomia" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["transicoes_autonomia"] = []
            
            # Adiciona timestamp se não existir
            if "timestamp" not in transicao:
                transicao["timestamp"] = datetime.now().isoformat()
            
            # Adiciona ID se não existir
            if "id" not in transicao:
                transicao["id"] = f"tr_{len(self.memoria['memoria_operacional']['transicoes_autonomia']) + 1}"
            
            # Registra transição
            self.memoria["memoria_operacional"]["transicoes_autonomia"].append(transicao)
            
            # Atualiza nível atual de autonomia
            self.memoria["memoria_operacional"]["nivel_autonomia"] = transicao.get("nivel_novo", "baixo")
            
            self._salvar_memoria(self.memoria)
            self.logger.info(f"Transição de autonomia registrada: {transicao['id']}")
        except Exception as e:
            self.logger.error(f"Erro ao registrar transição de autonomia: {str(e)}")

    def registrar_diagnostico(self, diagnostico: Dict[str, Any]) -> None:
        """Registra um diagnóstico do sistema."""
        try:
            if "diagnosticos" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["diagnosticos"] = []
            
            # Adiciona timestamp se não existir
            if "timestamp" not in diagnostico:
                diagnostico["timestamp"] = datetime.now().isoformat()
            
            # Registra diagnóstico
            self.memoria["memoria_operacional"]["diagnosticos"].append(diagnostico)
            
            # Se for diagnóstico crítico, registra alerta
            if diagnostico.get("severidade") in ["alta", "critica"]:
                self.registrar_alerta({
                    "tipo": "diagnostico_critico",
                    "descricao": f"Diagnóstico crítico: {diagnostico.get('descricao', 'Sem descrição')}",
                    "severidade": diagnostico.get("severidade"),
                    "componente": diagnostico.get("componente"),
                    "timestamp": datetime.now().isoformat()
                })
            
            self._salvar_memoria(self.memoria)
            self.logger.info(f"Diagnóstico registrado para componente {diagnostico.get('componente')}")
        except Exception as e:
            self.logger.error(f"Erro ao registrar diagnóstico: {str(e)}")

    def registrar_correcao(self, correcao: Dict[str, Any]) -> None:
        """Registra uma correção aplicada no sistema."""
        try:
            if "correcoes" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["correcoes"] = []
            
            # Adiciona timestamp se não existir
            if "timestamp" not in correcao:
                correcao["timestamp"] = datetime.now().isoformat()
            
            # Registra correção
            self.memoria["memoria_operacional"]["correcoes"].append(correcao)
            
            # Atualiza métricas se fornecidas
            if "metricas_depois" in correcao:
                self.atualizar_metricas(correcao["metricas_depois"])
            
            self._salvar_memoria(self.memoria)
            self.logger.info(f"Correção registrada para componente {correcao.get('componente')}")
        except Exception as e:
            self.logger.error(f"Erro ao registrar correção: {str(e)}")

    def registrar_anomalia(self, anomalia: Dict[str, Any]) -> None:
        """Registra uma anomalia detectada no sistema."""
        try:
            if "anomalias" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["anomalias"] = []
            
            # Adiciona timestamp se não existir
            if "timestamp" not in anomalia:
                anomalia["timestamp"] = datetime.now().isoformat()
            
            # Registra anomalia
            self.memoria["memoria_operacional"]["anomalias"].append(anomalia)
            
            # Se for anomalia crítica, registra alerta
            if anomalia.get("severidade") in ["alta", "critica"]:
                self.registrar_alerta({
                    "tipo": "anomalia_critica",
                    "descricao": f"Anomalia crítica detectada: {anomalia.get('descricao', 'Sem descrição')}",
                    "severidade": anomalia.get("severidade"),
                    "componente": anomalia.get("componente"),
                    "timestamp": datetime.now().isoformat()
                })
            
            self._salvar_memoria(self.memoria)
            self.logger.info(f"Anomalia registrada para componente {anomalia.get('componente')}")
        except Exception as e:
            self.logger.error(f"Erro ao registrar anomalia: {str(e)}")

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
        """Registra um incidente no sistema.
        
        Args:
            incidente: Dicionário com os dados do incidente
        """
        try:
            if "incidentes" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["incidentes"] = []
            
            incidente["id"] = str(uuid.uuid4())
            incidente["timestamp"] = datetime.now().isoformat()
            
            self.memoria["memoria_operacional"]["incidentes"].append(incidente)
            self._salvar_memoria(self.memoria)
            
            # Registra alerta se necessário
            if incidente.get("severidade") in ["alta", "critica"]:
                self.registrar_alerta({
                    "tipo": "incidente",
                    "severidade": incidente["severidade"],
                    "mensagem": f"Incidente crítico detectado: {incidente.get('descricao', 'Sem descrição')}",
                    "componente": incidente.get("componente", "sistema"),
                    "timestamp": datetime.now().isoformat()
                })
            
            self.logger.info(f"Incidente registrado: {incidente['id']}")
        except Exception as e:
            self.logger.error(f"Erro ao registrar incidente: {str(e)}")

    def registrar_aprendizado(self, aprendizado: Dict[str, Any]) -> None:
        """Registra um evento de aprendizado do sistema.
        
        Args:
            aprendizado: Dicionário com os dados do aprendizado
        """
        try:
            if "aprendizados" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["aprendizados"] = []
            
            aprendizado["id"] = str(uuid.uuid4())
            aprendizado["timestamp"] = datetime.now().isoformat()
            
            self.memoria["memoria_operacional"]["aprendizados"].append(aprendizado)
            self._salvar_memoria(self.memoria)
            
            # Registra transição de autonomia se necessário
            if aprendizado.get("impacto") == "alto":
                self.registrar_transicao_autonomia({
                    "tipo": "aprendizado",
                    "contexto": aprendizado.get("contexto", "geral"),
                    "descricao": f"Transição de autonomia baseada em aprendizado: {aprendizado.get('descricao', 'Sem descrição')}",
                    "impacto": "alto",
                    "detalhes": aprendizado.get("detalhes", {}),
                    "timestamp": datetime.now().isoformat()
                })
            
            self.logger.info(f"Aprendizado registrado: {aprendizado['id']}")
        except Exception as e:
            self.logger.error(f"Erro ao registrar aprendizado: {str(e)}")

    def registrar_transicao_autonomia(self, transicao: Dict[str, Any]) -> None:
        """Registra uma transição no nível de autonomia do sistema.
        
        Args:
            transicao: Dicionário com os dados da transição
        """
        try:
            if "transicoes_autonomia" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["transicoes_autonomia"] = []
            
            transicao["id"] = str(uuid.uuid4())
            transicao["timestamp"] = datetime.now().isoformat()
            
            self.memoria["memoria_operacional"]["transicoes_autonomia"].append(transicao)
            self._salvar_memoria(self.memoria)
            
            self.logger.info(f"Transição de autonomia registrada: {transicao['id']}")
        except Exception as e:
            self.logger.error(f"Erro ao registrar transição de autonomia: {str(e)}")

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

    def salvar_memoria(self) -> None:
        """Salva o estado atual da memória."""
        try:
            with open(self.caminho_memoria, 'w') as f:
                json.dump(self.memoria, f, default=str)
            self.logger.info("Memória salva com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao salvar memória: {str(e)}")

    def carregar_memoria(self) -> None:
        """Carrega o estado da memória do arquivo."""
        try:
            if self.caminho_memoria.exists():
                with open(self.caminho_memoria, 'r') as f:
                    self.memoria = json.load(f)
                self.logger.info("Memória carregada com sucesso")
            else:
                self.memoria = self._criar_memoria_inicial()
                self._salvar_memoria(self.memoria)
        except Exception as e:
            self.logger.error(f"Erro ao carregar memória: {str(e)}")
            self.memoria = self._criar_memoria_inicial()

    def atualizar_metricas(self, metricas: Dict[str, Any]) -> None:
        """Atualiza as métricas do sistema."""
        try:
            if "metricas" not in self.memoria["memoria_operacional"]:
                self.memoria["memoria_operacional"]["metricas"] = {}
            
            self.memoria["memoria_operacional"]["metricas"].update(metricas)
            self._salvar_memoria(self.memoria)
            self.logger.info("Métricas atualizadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao atualizar métricas: {str(e)}")

    def obter_historico(self) -> List[Dict[str, Any]]:
        """Obtém o histórico completo do sistema."""
        try:
            historico = []
            for tipo in self.memoria["memoria_operacional"]["entidades"]:
                for entidade in self.memoria["memoria_operacional"]["entidades"][tipo]:
                    historico.append(entidade)
            return sorted(historico, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {str(e)}")
            return []

    def obter_historico_por_tipo(self, tipo: str) -> List[Dict[str, Any]]:
        """Obtém o histórico de entidades de um tipo específico."""
        try:
            if tipo not in self.memoria["memoria_operacional"]["entidades"]:
                return []
            return sorted(
                self.memoria["memoria_operacional"]["entidades"][tipo],
                key=lambda x: x["timestamp"],
                reverse=True
            )
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico por tipo: {str(e)}")
            return []

    def obter_historico_por_periodo(self, inicio: datetime, fim: datetime) -> List[Dict[str, Any]]:
        """Obtém o histórico de entidades em um período específico."""
        try:
            historico = []
            for tipo in self.memoria["memoria_operacional"]["entidades"]:
                for entidade in self.memoria["memoria_operacional"]["entidades"][tipo]:
                    timestamp = datetime.fromisoformat(entidade["timestamp"])
                    if inicio <= timestamp <= fim:
                        historico.append(entidade)
            return sorted(historico, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico por período: {str(e)}")
            return [] 