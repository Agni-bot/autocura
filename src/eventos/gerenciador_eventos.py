import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import json
from prometheus_client import Counter, Gauge, Histogram

@dataclass
class Evento:
    """Representa um evento do sistema."""
    id: str
    tipo: str
    dados: Dict[str, Any]
    timestamp: datetime
    origem: str
    prioridade: int
    tags: List[str]
    status: str

class GerenciadorEventos:
    """Módulo Gerenciador de Eventos para gerenciar eventos do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o gerenciador de eventos.
        
        Args:
            config: Configuração do gerenciador
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Cache de eventos
        self.eventos: Dict[str, Evento] = {}
        
        # Handlers de eventos
        self.handlers: Dict[str, List[Callable]] = {}
        
        # Métricas Prometheus
        self.metricas = {
            "eventos_criados": Counter(
                "eventos_criados_total",
                "Total de eventos criados",
                ["tipo", "origem"]
            ),
            "eventos_processados": Counter(
                "eventos_processados_total",
                "Total de eventos processados",
                ["tipo", "status"]
            ),
            "eventos_pendentes": Gauge(
                "eventos_pendentes_total",
                "Total de eventos pendentes",
                ["tipo"]
            ),
            "tempo_processamento": Histogram(
                "tempo_processamento_evento_seconds",
                "Tempo de processamento de eventos",
                ["tipo"]
            )
        }
        
        # Configuração de tipos de evento
        self.tipos_evento = {
            "sistema": {
                "prioridade": 1,
                "ttl": timedelta(days=7)
            },
            "aplicacao": {
                "prioridade": 2,
                "ttl": timedelta(days=3)
            },
            "seguranca": {
                "prioridade": 0,
                "ttl": timedelta(days=30)
            },
            "monitoramento": {
                "prioridade": 3,
                "ttl": timedelta(days=1)
            }
        }
        
        self.logger.info("Gerenciador de Eventos inicializado")
    
    async def registrar_evento(self, tipo: str, dados: Dict[str, Any], origem: str, tags: List[str] = None) -> Optional[Evento]:
        """Registra um novo evento.
        
        Args:
            tipo: Tipo do evento
            dados: Dados do evento
            origem: Origem do evento
            tags: Tags do evento
            
        Returns:
            Evento registrado ou None em caso de erro
        """
        if tipo not in self.tipos_evento:
            self.logger.error(f"Tipo de evento desconhecido: {tipo}")
            return None
        
        try:
            # Gera ID único
            evento_id = f"{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Cria evento
            evento = Evento(
                id=evento_id,
                tipo=tipo,
                dados=dados,
                timestamp=datetime.now(),
                origem=origem,
                prioridade=self.tipos_evento[tipo]["prioridade"],
                tags=tags or [],
                status="pendente"
            )
            
            # Adiciona ao cache
            self.eventos[evento_id] = evento
            
            # Atualiza métricas
            self.metricas["eventos_criados"].labels(tipo=tipo, origem=origem).inc()
            self.metricas["eventos_pendentes"].labels(tipo=tipo).inc()
            
            # Agenda processamento
            asyncio.create_task(self._processar_evento(evento))
            
            self.logger.info(f"Evento registrado: {evento_id}")
            return evento
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar evento: {e}")
            return None
    
    async def _processar_evento(self, evento: Evento) -> None:
        """Processa um evento.
        
        Args:
            evento: Evento a ser processado
        """
        try:
            with self.metricas["tempo_processamento"].labels(tipo=evento.tipo).time():
                # Verifica se há handlers para o tipo
                if evento.tipo not in self.handlers:
                    self.logger.warning(f"Nenhum handler registrado para evento: {evento.tipo}")
                    return
                
                # Processa com cada handler
                for handler in self.handlers[evento.tipo]:
                    try:
                        await handler(evento)
                    except Exception as e:
                        self.logger.error(f"Erro no handler {handler.__name__}: {e}")
                
                # Atualiza status
                evento.status = "processado"
                
                # Atualiza métricas
                self.metricas["eventos_processados"].labels(
                    tipo=evento.tipo,
                    status=evento.status
                ).inc()
                self.metricas["eventos_pendentes"].labels(tipo=evento.tipo).dec()
                
                self.logger.info(f"Evento processado: {evento.id}")
                
        except Exception as e:
            self.logger.error(f"Erro ao processar evento: {e}")
            evento.status = "erro"
            
            # Atualiza métricas
            self.metricas["eventos_processados"].labels(
                tipo=evento.tipo,
                status=evento.status
            ).inc()
            self.metricas["eventos_pendentes"].labels(tipo=evento.tipo).dec()
    
    def registrar_handler(self, tipo: str, handler: Callable) -> None:
        """Registra um handler para um tipo de evento.
        
        Args:
            tipo: Tipo do evento
            handler: Função handler
        """
        if tipo not in self.handlers:
            self.handlers[tipo] = []
        
        self.handlers[tipo].append(handler)
        self.logger.info(f"Handler registrado para evento: {tipo}")
    
    async def obter_evento(self, evento_id: str) -> Optional[Evento]:
        """Obtém um evento pelo ID.
        
        Args:
            evento_id: ID do evento
            
        Returns:
            Evento ou None se não encontrado
        """
        return self.eventos.get(evento_id)
    
    async def buscar_eventos(self, tipo: Optional[str] = None, status: Optional[str] = None, 
                           origem: Optional[str] = None, tags: Optional[List[str]] = None,
                           inicio: Optional[datetime] = None, fim: Optional[datetime] = None) -> List[Evento]:
        """Busca eventos por critérios.
        
        Args:
            tipo: Tipo do evento (opcional)
            status: Status do evento (opcional)
            origem: Origem do evento (opcional)
            tags: Tags do evento (opcional)
            inicio: Data inicial (opcional)
            fim: Data final (opcional)
            
        Returns:
            Lista de eventos encontrados
        """
        eventos = []
        
        for evento in self.eventos.values():
            # Filtra por tipo
            if tipo and evento.tipo != tipo:
                continue
            
            # Filtra por status
            if status and evento.status != status:
                continue
            
            # Filtra por origem
            if origem and evento.origem != origem:
                continue
            
            # Filtra por tags
            if tags and not all(tag in evento.tags for tag in tags):
                continue
            
            # Filtra por período
            if inicio and evento.timestamp < inicio:
                continue
            if fim and evento.timestamp > fim:
                continue
            
            eventos.append(evento)
        
        return eventos
    
    async def limpar_eventos_antigos(self) -> None:
        """Limpa eventos antigos baseado no TTL configurado."""
        agora = datetime.now()
        eventos_remover = []
        
        for evento in self.eventos.values():
            ttl = self.tipos_evento[evento.tipo]["ttl"]
            if agora - evento.timestamp > ttl:
                eventos_remover.append(evento.id)
        
        for evento_id in eventos_remover:
            del self.eventos[evento_id]
        
        if eventos_remover:
            self.logger.info(f"Eventos antigos removidos: {len(eventos_remover)}")
    
    async def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas dos eventos.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            "timestamp": datetime.now(),
            "total_eventos": len(self.eventos),
            "por_tipo": {},
            "por_status": {},
            "por_origem": {},
            "por_tag": {}
        }
        
        # Conta eventos por tipo, status, origem e tag
        for evento in self.eventos.values():
            if evento.tipo not in stats["por_tipo"]:
                stats["por_tipo"][evento.tipo] = 0
            stats["por_tipo"][evento.tipo] += 1
            
            if evento.status not in stats["por_status"]:
                stats["por_status"][evento.status] = 0
            stats["por_status"][evento.status] += 1
            
            if evento.origem not in stats["por_origem"]:
                stats["por_origem"][evento.origem] = 0
            stats["por_origem"][evento.origem] += 1
            
            for tag in evento.tags:
                if tag not in stats["por_tag"]:
                    stats["por_tag"][tag] = 0
                stats["por_tag"][tag] += 1
        
        return stats 