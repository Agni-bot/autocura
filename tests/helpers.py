"""
Helpers para testes do sistema de autocura.
"""
import pytest
import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from datetime import datetime
import logging
from unittest.mock import Mock, AsyncMock

T = TypeVar('T')

def assert_dict_contains(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> None:
    """
    Verifica se dict1 contém todas as chaves e valores de dict2.
    
    Args:
        dict1: Dicionário que deve conter as chaves
        dict2: Dicionário com chaves a serem verificadas
    """
    for key, value in dict2.items():
        assert key in dict1, f"Chave '{key}' não encontrada em dict1"
        assert dict1[key] == value, f"Valor da chave '{key}' diferente: {dict1[key]} != {value}"

def assert_list_contains(list1: List[Any], list2: List[Any]) -> None:
    """
    Verifica se list1 contém todos os elementos de list2.
    
    Args:
        list1: Lista que deve conter os elementos
        list2: Lista com elementos a serem verificados
    """
    for item in list2:
        assert item in list1, f"Item '{item}' não encontrado em list1"

@pytest.mark.asyncio
async def assert_async_raises(
    exception: Type[Exception],
    coro: Any,
    *args: Any,
    **kwargs: Any
) -> None:
    """
    Verifica se uma corotina lança uma exceção específica.
    
    Args:
        exception: Tipo da exceção esperada
        coro: Corotina a ser executada
        *args: Argumentos posicionais para a corotina
        **kwargs: Argumentos nomeados para a corotina
    """
    with pytest.raises(exception):
        await coro(*args, **kwargs)

def assert_log_contains(
    caplog: pytest.LogCaptureFixture,
    message: str,
    level: Optional[int] = None
) -> None:
    """
    Verifica se uma mensagem específica foi registrada no log.
    
    Args:
        caplog: Fixture de captura de logs
        message: Mensagem a ser verificada
        level: Nível do log (opcional)
    """
    if level is not None:
        assert any(
            record.levelno == level and message in record.message
            for record in caplog.records
        ), f"Mensagem '{message}' não encontrada no nível {level}"
    else:
        assert any(
            message in record.message
            for record in caplog.records
        ), f"Mensagem '{message}' não encontrada"

def create_mock_response(
    status_code: int = 200,
    json_data: Optional[Dict[str, Any]] = None,
    text: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None
) -> Mock:
    """
    Cria um mock de resposta HTTP.
    
    Args:
        status_code: Código de status HTTP
        json_data: Dados JSON da resposta
        text: Texto da resposta
        headers: Cabeçalhos da resposta
        
    Returns:
        Mock: Mock da resposta HTTP
    """
    mock = Mock()
    mock.status_code = status_code
    mock.headers = headers or {}
    
    if json_data is not None:
        mock.json = AsyncMock(return_value=json_data)
    
    if text is not None:
        mock.text = text
    
    return mock

def create_mock_entity(
    entity_type: str,
    data: Dict[str, Any],
    id: Optional[str] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um mock de entidade.
    
    Args:
        entity_type: Tipo da entidade
        data: Dados da entidade
        id: ID da entidade (opcional)
        created_at: Data de criação (opcional)
        updated_at: Data de atualização (opcional)
        
    Returns:
        Dict[str, Any]: Mock da entidade
    """
    return {
        "id": id or "mock_id",
        "type": entity_type,
        "data": data,
        "created_at": created_at or datetime.now(),
        "updated_at": updated_at or datetime.now()
    }

def create_mock_event(
    event_type: str,
    data: Dict[str, Any],
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um mock de evento.
    
    Args:
        event_type: Tipo do evento
        data: Dados do evento
        timestamp: Timestamp do evento (opcional)
        
    Returns:
        Dict[str, Any]: Mock do evento
    """
    return {
        "type": event_type,
        "data": data,
        "timestamp": timestamp or datetime.now()
    }

def create_mock_metric(
    name: str,
    value: Union[int, float],
    labels: Optional[Dict[str, str]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um mock de métrica.
    
    Args:
        name: Nome da métrica
        value: Valor da métrica
        labels: Labels da métrica (opcional)
        timestamp: Timestamp da métrica (opcional)
        
    Returns:
        Dict[str, Any]: Mock da métrica
    """
    return {
        "name": name,
        "value": value,
        "labels": labels or {},
        "timestamp": timestamp or datetime.now()
    }

def create_mock_log(
    level: int,
    message: str,
    extra: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um mock de log.
    
    Args:
        level: Nível do log
        message: Mensagem do log
        extra: Dados extras (opcional)
        timestamp: Timestamp do log (opcional)
        
    Returns:
        Dict[str, Any]: Mock do log
    """
    return {
        "level": level,
        "message": message,
        "extra": extra or {},
        "timestamp": timestamp or datetime.now()
    }

def create_mock_config(
    config_type: str,
    data: Dict[str, Any],
    version: Optional[str] = None,
    environment: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cria um mock de configuração.
    
    Args:
        config_type: Tipo da configuração
        data: Dados da configuração
        version: Versão da configuração (opcional)
        environment: Ambiente da configuração (opcional)
        
    Returns:
        Dict[str, Any]: Mock da configuração
    """
    return {
        "type": config_type,
        "data": data,
        "version": version or "1.0.0",
        "environment": environment or "test"
    }

def create_mock_error(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um mock de erro.
    
    Args:
        error_type: Tipo do erro
        message: Mensagem do erro
        details: Detalhes do erro (opcional)
        timestamp: Timestamp do erro (opcional)
        
    Returns:
        Dict[str, Any]: Mock do erro
    """
    return {
        "type": error_type,
        "message": message,
        "details": details or {},
        "timestamp": timestamp or datetime.now()
    }

def create_mock_alert(
    alert_type: str,
    message: str,
    severity: str,
    source: Optional[str] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um mock de alerta.
    
    Args:
        alert_type: Tipo do alerta
        message: Mensagem do alerta
        severity: Severidade do alerta
        source: Fonte do alerta (opcional)
        timestamp: Timestamp do alerta (opcional)
        
    Returns:
        Dict[str, Any]: Mock do alerta
    """
    return {
        "type": alert_type,
        "message": message,
        "severity": severity,
        "source": source or "system",
        "timestamp": timestamp or datetime.now()
    }

def create_mock_validation(
    is_valid: bool,
    errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Cria um mock de validação.
    
    Args:
        is_valid: Se a validação passou
        errors: Lista de erros (opcional)
        warnings: Lista de avisos (opcional)
        timestamp: Timestamp da validação (opcional)
        
    Returns:
        Dict[str, Any]: Mock da validação
    """
    return {
        "is_valid": is_valid,
        "errors": errors or [],
        "warnings": warnings or [],
        "timestamp": timestamp or datetime.now()
    } 