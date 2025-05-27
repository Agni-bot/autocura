"""
Sistema de Mensageria Universal - AutoCura
=========================================

Sistema de comunicação multi-protocolo que suporta mensagens clássicas
e prepara para comunicação quântica futura.
"""

import asyncio
import json
import redis
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from enum import Enum
import logging
from abc import ABC, abstractmethod
import os

logger = logging.getLogger(__name__)

class MessageProtocol(Enum):
    """Protocolos de comunicação suportados"""
    CLASSICAL = "classical"
    QUANTUM = "quantum"  # Preparação futura
    HYBRID = "hybrid"    # Híbrido clássico-quântico

class MessagePriority(Enum):
    """Prioridades de mensagens"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class Message:
    """Estrutura de mensagem universal"""
    def __init__(self, 
                 topic: str,
                 payload: Dict[str, Any],
                 protocol: MessageProtocol = MessageProtocol.CLASSICAL,
                 priority: MessagePriority = MessagePriority.NORMAL,
                 sender: Optional[str] = None):
        self.id = f"{datetime.now().isoformat()}_{topic}"
        self.topic = topic
        self.payload = payload
        self.protocol = protocol
        self.priority = priority
        self.sender = sender
        self.timestamp = datetime.now()
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte mensagem para dicionário"""
        return {
            "id": self.id,
            "topic": self.topic,
            "payload": self.payload,
            "protocol": self.protocol.value,
            "priority": self.priority.value,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Cria mensagem a partir de dicionário"""
        msg = cls(
            topic=data["topic"],
            payload=data["payload"],
            protocol=MessageProtocol(data["protocol"]),
            priority=MessagePriority(data["priority"]),
            sender=data.get("sender")
        )
        msg.id = data["id"]
        msg.timestamp = datetime.fromisoformat(data["timestamp"])
        msg.metadata = data.get("metadata", {})
        return msg

class UniversalEventBus:
    """
    Bus de eventos universal com suporte multi-protocolo.
    Preparado para evolução tecnológica.
    """
    
    def __init__(self, redis_host: Optional[str] = None, redis_port: int = 6379):
        # Detecta automaticamente se está rodando em Docker
        if redis_host is None:
            # Verifica se está em container Docker
            if os.path.exists('/.dockerenv') or os.environ.get('ENVIRONMENT') == 'alpha':
                redis_host = "autocura-redis"  # Nome do serviço Docker
                logger.info("Detectado ambiente Docker - usando autocura-redis")
            else:
                redis_host = "localhost"  # Desenvolvimento local
                logger.info("Detectado ambiente local - usando localhost")
        
        self.redis_host = redis_host
        self.redis_port = redis_port
        
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Testa conexão
            self.redis_client.ping()
            logger.info(f"Conectado ao Redis em {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.error(f"Erro ao conectar Redis {self.redis_host}:{self.redis_port}: {e}")
            # Fallback para modo sem Redis
            self.redis_client = None
        
        self.subscribers: Dict[str, List[Callable]] = {}
        self.running = False
        self.quantum_ready = False
        self.protocol_handlers = {
            MessageProtocol.CLASSICAL: self._handle_classical,
            MessageProtocol.QUANTUM: self._handle_quantum,
            MessageProtocol.HYBRID: self._handle_hybrid
        }
        
    async def start(self):
        """Inicia o event bus"""
        self.running = True
        logger.info("Universal Event Bus iniciado")
        if self.redis_client:
            asyncio.create_task(self._message_processor())
        else:
            logger.warning("Event Bus iniciado em modo fallback (sem Redis)")
    
    async def stop(self):
        """Para o event bus"""
        self.running = False
        logger.info("Universal Event Bus parado")
    
    async def send(self, message: Message) -> bool:
        """
        Envia mensagem através do protocolo apropriado.
        
        Args:
            message: Mensagem a enviar
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            handler = self.protocol_handlers.get(message.protocol)
            if handler:
                return await handler(message)
            else:
                logger.error(f"Protocolo não suportado: {message.protocol}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False
    
    async def send_classical(self, topic: str, payload: Dict[str, Any], 
                           priority: MessagePriority = MessagePriority.NORMAL) -> bool:
        """Envia mensagem clássica via Redis"""
        message = Message(topic, payload, MessageProtocol.CLASSICAL, priority)
        return await self.send(message)
    
    async def subscribe(self, topic: str, handler: Callable) -> bool:
        """
        Inscreve handler para receber mensagens de um tópico.
        
        Args:
            topic: Tópico a inscrever
            handler: Função callback
            
        Returns:
            bool: True se inscrito com sucesso
        """
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        
        self.subscribers[topic].append(handler)
        logger.info(f"Handler inscrito no tópico: {topic}")
        return True
    
    async def unsubscribe(self, topic: str, handler: Callable) -> bool:
        """Remove inscrição de handler"""
        if topic in self.subscribers and handler in self.subscribers[topic]:
            self.subscribers[topic].remove(handler)
            return True
        return False
    
    async def _handle_classical(self, message: Message) -> bool:
        """Processa mensagem clássica"""
        try:
            if not self.redis_client:
                # Modo fallback - processa diretamente
                logger.debug(f"Processando mensagem em modo fallback: {message.id}")
                await self._process_message_direct(message)
                return True
            
            # Serializa e envia via Redis
            serialized = json.dumps(message.to_dict())
            
            # Usa lista com prioridade
            queue_name = f"queue:{message.topic}:{message.priority.value}"
            self.redis_client.lpush(queue_name, serialized)
            
            logger.debug(f"Mensagem clássica enviada: {message.id}")
            return True
        except Exception as e:
            logger.error(f"Erro ao processar mensagem clássica: {e}")
            # Fallback direto em caso de erro
            try:
                await self._process_message_direct(message)
                return True
            except Exception as fallback_error:
                logger.error(f"Erro no fallback: {fallback_error}")
                return False
    
    async def _process_message_direct(self, message: Message):
        """Processa mensagem diretamente (modo fallback)"""
        topic = message.topic
        if topic in self.subscribers:
            for handler in self.subscribers[topic]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Erro no handler direto: {e}")
    
    async def _handle_quantum(self, message: Message) -> bool:
        """Prepara para processamento quântico futuro"""
        if not self.quantum_ready:
            logger.warning("Quantum não disponível, usando fallback clássico")
            message.protocol = MessageProtocol.CLASSICAL
            return await self._handle_classical(message)
        
        # TODO: Implementar quando quantum estiver disponível
        logger.info("Processamento quântico simulado")
        return True
    
    async def _handle_hybrid(self, message: Message) -> bool:
        """Processa mensagem híbrida"""
        # Por enquanto, usa processamento clássico
        return await self._handle_classical(message)
    
    async def _message_processor(self):
        """Processa mensagens recebidas"""
        while self.running:
            try:
                if not self.redis_client:
                    await asyncio.sleep(1)
                    continue
                
                # Processa mensagens por prioridade
                for priority in sorted([p.value for p in MessagePriority], reverse=True):
                    for topic in self.subscribers:
                        queue_name = f"queue:{topic}:{priority}"
                        
                        # Busca mensagem
                        msg_data = self.redis_client.rpop(queue_name)
                        if msg_data:
                            message = Message.from_dict(json.loads(msg_data))
                            
                            # Notifica subscribers
                            for handler in self.subscribers.get(topic, []):
                                try:
                                    await handler(message)
                                except Exception as e:
                                    logger.error(f"Erro no handler: {e}")
                
                await asyncio.sleep(0.01)  # Evita busy waiting
                
            except Exception as e:
                logger.error(f"Erro no processador de mensagens: {e}")
                await asyncio.sleep(1)
    
    def prepare_quantum_channel(self) -> None:
        """Preparação para comunicação quântica futura"""
        logger.info("Preparando canal quântico (simulado)")
        # TODO: Integrar com qiskit/cirq quando disponível
        self.quantum_ready = False  # Será True quando hardware estiver disponível
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do bus"""
        metrics = {
            "total_topics": len(self.subscribers),
            "total_handlers": sum(len(handlers) for handlers in self.subscribers.values()),
            "quantum_ready": self.quantum_ready,
            "supported_protocols": [p.value for p in MessageProtocol],
            "redis_connected": self.redis_client is not None,
            "redis_host": self.redis_host,
            "redis_port": self.redis_port
        }
        
        # Métricas de fila por tópico (apenas se Redis estiver disponível)
        if self.redis_client:
            try:
                for topic in self.subscribers:
                    for priority in MessagePriority:
                        queue_name = f"queue:{topic}:{priority.value}"
                        queue_size = self.redis_client.llen(queue_name)
                        metrics[f"queue_{topic}_{priority.name}"] = queue_size
            except Exception as e:
                logger.error(f"Erro ao obter métricas de fila: {e}")
        
        return metrics 