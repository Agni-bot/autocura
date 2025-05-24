"""
Serialização Adaptativa - AutoCura
==================================

Sistema de serialização que se adapta ao tipo de dado e tecnologia alvo.
"""

import json
import pickle
import base64
from typing import Any, Dict, Union, Type
from abc import ABC, abstractmethod
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SerializationFormat:
    """Formatos de serialização suportados"""
    JSON = "json"
    PICKLE = "pickle"
    NUMPY = "numpy"
    QUANTUM = "quantum"  # Preparação futura
    NANO = "nano"        # Preparação futura

class BaseSerializer(ABC):
    """Interface base para serializadores"""
    
    @abstractmethod
    def serialize(self, data: Any) -> bytes:
        """Serializa dados"""
        pass
    
    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """Deserializa dados"""
        pass

class JSONSerializer(BaseSerializer):
    """Serializador JSON para dados simples"""
    
    def serialize(self, data: Any) -> bytes:
        """Serializa para JSON"""
        try:
            # Converte tipos especiais
            if isinstance(data, datetime):
                data = data.isoformat()
            elif isinstance(data, np.ndarray):
                data = data.tolist()
            
            json_str = json.dumps(data, ensure_ascii=False)
            return json_str.encode('utf-8')
        except Exception as e:
            logger.error(f"Erro na serialização JSON: {e}")
            raise
    
    def deserialize(self, data: bytes) -> Any:
        """Deserializa de JSON"""
        try:
            json_str = data.decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Erro na deserialização JSON: {e}")
            raise

class PickleSerializer(BaseSerializer):
    """Serializador Pickle para objetos complexos"""
    
    def serialize(self, data: Any) -> bytes:
        """Serializa com Pickle"""
        try:
            return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logger.error(f"Erro na serialização Pickle: {e}")
            raise
    
    def deserialize(self, data: bytes) -> Any:
        """Deserializa de Pickle"""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Erro na deserialização Pickle: {e}")
            raise

class NumpySerializer(BaseSerializer):
    """Serializador otimizado para arrays NumPy"""
    
    def serialize(self, data: np.ndarray) -> bytes:
        """Serializa array NumPy"""
        try:
            # Salva com metadados
            buffer = []
            
            # Metadados
            metadata = {
                "shape": data.shape,
                "dtype": str(data.dtype)
            }
            metadata_bytes = json.dumps(metadata).encode('utf-8')
            
            # Tamanho dos metadados (4 bytes)
            buffer.append(len(metadata_bytes).to_bytes(4, 'little'))
            buffer.append(metadata_bytes)
            
            # Dados
            buffer.append(data.tobytes())
            
            return b''.join(buffer)
        except Exception as e:
            logger.error(f"Erro na serialização NumPy: {e}")
            raise
    
    def deserialize(self, data: bytes) -> np.ndarray:
        """Deserializa array NumPy"""
        try:
            # Lê tamanho dos metadados
            metadata_size = int.from_bytes(data[:4], 'little')
            
            # Lê metadados
            metadata_bytes = data[4:4+metadata_size]
            metadata = json.loads(metadata_bytes.decode('utf-8'))
            
            # Lê dados
            array_bytes = data[4+metadata_size:]
            
            # Reconstrói array
            dtype = np.dtype(metadata['dtype'])
            array = np.frombuffer(array_bytes, dtype=dtype)
            return array.reshape(metadata['shape'])
        except Exception as e:
            logger.error(f"Erro na deserialização NumPy: {e}")
            raise

class QuantumSerializer(BaseSerializer):
    """Preparação para serialização de estados quânticos"""
    
    def serialize(self, data: Any) -> bytes:
        """Serializa estado quântico (simulado)"""
        # Por enquanto, usa serialização clássica
        logger.info("Serialização quântica simulada - usando fallback clássico")
        return PickleSerializer().serialize(data)
    
    def deserialize(self, data: bytes) -> Any:
        """Deserializa estado quântico (simulado)"""
        logger.info("Deserialização quântica simulada - usando fallback clássico")
        return PickleSerializer().deserialize(data)

class AdaptiveSerializer:
    """
    Serializador adaptativo que escolhe o melhor formato
    baseado no tipo de dado e destino.
    """
    
    def __init__(self):
        self.serializers = {
            SerializationFormat.JSON: JSONSerializer(),
            SerializationFormat.PICKLE: PickleSerializer(),
            SerializationFormat.NUMPY: NumpySerializer(),
            SerializationFormat.QUANTUM: QuantumSerializer(),
        }
        
        # Mapeamento de tipos para formatos preferidos
        self.type_mapping = {
            dict: SerializationFormat.JSON,
            list: SerializationFormat.JSON,
            str: SerializationFormat.JSON,
            int: SerializationFormat.JSON,
            float: SerializationFormat.JSON,
            bool: SerializationFormat.JSON,
            np.ndarray: SerializationFormat.NUMPY,
        }
    
    def serialize(self, data: Any, target: str = "classical") -> bytes:
        """
        Serializa dados adaptando ao tipo e destino.
        
        Args:
            data: Dados a serializar
            target: Destino (classical, quantum, nano)
            
        Returns:
            bytes: Dados serializados
        """
        try:
            # Determina formato baseado no destino
            if target == "quantum":
                format_type = SerializationFormat.QUANTUM
            elif target == "nano":
                # Por enquanto usa pickle para nano
                format_type = SerializationFormat.PICKLE
            else:
                # Determina formato baseado no tipo de dado
                format_type = self._detect_format(data)
            
            # Serializa
            serializer = self.serializers.get(format_type)
            if not serializer:
                logger.warning(f"Formato {format_type} não disponível, usando pickle")
                serializer = self.serializers[SerializationFormat.PICKLE]
            
            # Adiciona metadados
            serialized = serializer.serialize(data)
            
            # Envelope com formato
            envelope = {
                "format": format_type,
                "data": base64.b64encode(serialized).decode('ascii'),
                "timestamp": datetime.now().isoformat()
            }
            
            return json.dumps(envelope).encode('utf-8')
            
        except Exception as e:
            logger.error(f"Erro na serialização adaptativa: {e}")
            raise
    
    def deserialize(self, data: bytes) -> Any:
        """
        Deserializa dados detectando formato automaticamente.
        
        Args:
            data: Dados serializados
            
        Returns:
            Any: Dados deserializados
        """
        try:
            # Decodifica envelope
            envelope = json.loads(data.decode('utf-8'))
            
            # Obtém formato
            format_type = envelope.get("format", SerializationFormat.PICKLE)
            serialized = base64.b64decode(envelope["data"].encode('ascii'))
            
            # Deserializa
            serializer = self.serializers.get(format_type)
            if not serializer:
                logger.warning(f"Formato {format_type} não disponível, usando pickle")
                serializer = self.serializers[SerializationFormat.PICKLE]
            
            return serializer.deserialize(serialized)
            
        except Exception as e:
            logger.error(f"Erro na deserialização adaptativa: {e}")
            raise
    
    def _detect_format(self, data: Any) -> str:
        """Detecta melhor formato para o tipo de dado"""
        data_type = type(data)
        
        # Verifica mapeamento direto
        if data_type in self.type_mapping:
            return self.type_mapping[data_type]
        
        # Verifica se é serializável em JSON
        try:
            json.dumps(data)
            return SerializationFormat.JSON
        except:
            pass
        
        # Fallback para pickle
        return SerializationFormat.PICKLE
    
    def register_format(self, format_name: str, serializer: BaseSerializer):
        """Registra novo formato de serialização"""
        self.serializers[format_name] = serializer
        logger.info(f"Formato {format_name} registrado")
    
    def get_supported_formats(self) -> list:
        """Retorna formatos suportados"""
        return list(self.serializers.keys()) 