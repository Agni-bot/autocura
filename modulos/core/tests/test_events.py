"""Testes do sistema de eventos."""

import asyncio
import pytest
from ..src.events import Event, EventBus

@pytest.fixture
def event_bus():
    """Fixture que retorna uma instância do EventBus."""
    return EventBus()

@pytest.mark.asyncio
async def test_publish_and_subscribe(event_bus):
    """Testa publicação e inscrição em eventos."""
    received_events = []
    
    async def handler(event):
        received_events.append(event)
    
    # Inscreve o handler
    await event_bus.subscribe("test_topic", handler)
    
    # Publica um evento
    test_data = {"test": "data"}
    await event_bus.publish(test_data, "test_topic")
    
    # Aguarda processamento assíncrono
    await asyncio.sleep(0.1)
    
    assert len(received_events) == 1
    assert received_events[0].type == "test_topic"
    assert received_events[0].data == test_data

@pytest.mark.asyncio
async def test_multiple_subscribers(event_bus):
    """Testa múltiplos subscribers para um tópico."""
    received_events_1 = []
    received_events_2 = []
    
    async def handler1(event):
        received_events_1.append(event)
    
    async def handler2(event):
        received_events_2.append(event)
    
    # Inscreve os handlers
    await event_bus.subscribe("test_topic", handler1)
    await event_bus.subscribe("test_topic", handler2)
    
    # Publica um evento
    test_data = {"test": "data"}
    await event_bus.publish(test_data, "test_topic")
    
    # Aguarda processamento assíncrono
    await asyncio.sleep(0.1)
    
    assert len(received_events_1) == 1
    assert len(received_events_2) == 1
    assert received_events_1[0].data == test_data
    assert received_events_2[0].data == test_data

@pytest.mark.asyncio
async def test_unsubscribe(event_bus):
    """Testa remoção de inscrição."""
    received_events = []
    
    async def handler(event):
        received_events.append(event)
    
    # Inscreve o handler
    await event_bus.subscribe("test_topic", handler)
    
    # Publica um evento
    test_data = {"test": "data"}
    await event_bus.publish(test_data, "test_topic")
    
    # Remove inscrição
    await event_bus.unsubscribe("test_topic", handler)
    
    # Publica outro evento
    await event_bus.publish({"test": "data2"}, "test_topic")
    
    # Aguarda processamento assíncrono
    await asyncio.sleep(0.1)
    
    assert len(received_events) == 1
    assert received_events[0].data == test_data

@pytest.mark.asyncio
async def test_event_history(event_bus):
    """Testa histórico de eventos."""
    test_data = {"test": "data"}
    
    # Publica alguns eventos
    await event_bus.publish(test_data, "test_topic")
    await event_bus.publish({"test": "data2"}, "test_topic")
    await event_bus.publish({"test": "data3"}, "other_topic")
    
    # Verifica histórico
    history = event_bus.get_event_history()
    assert len(history) == 3
    
    # Verifica filtro por tópico
    topic_history = event_bus.get_event_history(topic="test_topic")
    assert len(topic_history) == 2
    
    # Verifica limite
    limited_history = event_bus.get_event_history(limit=1)
    assert len(limited_history) == 1

@pytest.mark.asyncio
async def test_clear_history(event_bus):
    """Testa limpeza do histórico."""
    # Publica alguns eventos
    await event_bus.publish({"test": "data"}, "test_topic")
    await event_bus.publish({"test": "data2"}, "test_topic")
    
    # Limpa histórico
    event_bus.clear_history()
    
    # Verifica se está vazio
    assert len(event_bus.get_event_history()) == 0

@pytest.mark.asyncio
async def test_error_handling(event_bus):
    """Testa tratamento de erros nos handlers."""
    error_events = []
    
    async def error_handler(event):
        raise Exception("Test error")
    
    async def error_logger(event):
        error_events.append(event)
    
    # Inscreve handlers
    await event_bus.subscribe("error_topic", error_handler)
    await event_bus.subscribe("error_topic", error_logger)
    
    # Publica evento que causará erro
    await event_bus.publish({"test": "data"}, "error_topic")
    
    # Aguarda processamento assíncrono
    await asyncio.sleep(0.1)
    
    # Verifica se o segundo handler ainda foi executado
    assert len(error_events) == 1 