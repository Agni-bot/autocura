"""Testes do sistema de logging."""

import json
import os
import pytest
from ..src.logging import StructuredLogger, JsonFormatter

@pytest.fixture
def log_file(tmp_path):
    """Fixture que retorna um arquivo de log temporário."""
    return str(tmp_path / "test.log")

@pytest.fixture
def logger(log_file):
    """Fixture que retorna uma instância do StructuredLogger."""
    return StructuredLogger(log_file=log_file)

@pytest.mark.asyncio
async def test_log_message(logger, log_file):
    """Testa registro de mensagem de log."""
    # Registra uma mensagem
    await logger.log(
        level="info",
        message="Test message",
        extra_field="extra"
    )
    
    # Verifica se o arquivo foi criado
    assert os.path.exists(log_file)
    
    # Lê o conteúdo do arquivo
    with open(log_file, 'r') as f:
        log_entry = json.loads(f.read())
    
    # Verifica campos
    assert log_entry['level'] == 'INFO'
    assert log_entry['message'] == 'Test message'
    assert log_entry['extra_field'] == 'extra'
    assert 'timestamp' in log_entry

@pytest.mark.asyncio
async def test_log_levels(logger, log_file):
    """Testa diferentes níveis de log."""
    levels = ['debug', 'info', 'warning', 'error', 'critical']
    
    for level in levels:
        await logger.log(level=level, message=f"{level} message")
    
    # Lê o conteúdo do arquivo
    with open(log_file, 'r') as f:
        log_entries = [json.loads(line) for line in f.readlines()]
    
    # Verifica se todos os níveis foram registrados
    assert len(log_entries) == len(levels)
    for entry, level in zip(log_entries, levels):
        assert entry['level'] == level.upper()

@pytest.mark.asyncio
async def test_get_logs(logger):
    """Testa recuperação de logs."""
    # Registra alguns logs
    await logger.log(level="info", message="Info message")
    await logger.log(level="error", message="Error message")
    await logger.log(level="info", message="Another info message")
    
    # Recupera todos os logs
    all_logs = await logger.get_logs()
    assert len(all_logs) == 3
    
    # Filtra por nível
    info_logs = await logger.get_logs(level="info")
    assert len(info_logs) == 2
    
    error_logs = await logger.get_logs(level="error")
    assert len(error_logs) == 1

@pytest.mark.asyncio
async def test_log_formatting(logger, log_file):
    """Testa formatação de logs."""
    # Registra log com campos extras
    await logger.log(
        level="info",
        message="Test message",
        user_id="123",
        action="test",
        metadata={"key": "value"}
    )
    
    # Lê o conteúdo do arquivo
    with open(log_file, 'r') as f:
        log_entry = json.loads(f.read())
    
    # Verifica formatação
    assert log_entry['level'] == 'INFO'
    assert log_entry['message'] == 'Test message'
    assert log_entry['user_id'] == '123'
    assert log_entry['action'] == 'test'
    assert log_entry['metadata'] == {"key": "value"}

@pytest.mark.asyncio
async def test_clear_logs(logger):
    """Testa limpeza de logs."""
    # Registra alguns logs
    await logger.log(level="info", message="Info message")
    await logger.log(level="error", message="Error message")
    
    # Limpa logs
    logger.clear_logs()
    
    # Verifica se foram limpos
    logs = await logger.get_logs()
    assert len(logs) == 0

@pytest.mark.asyncio
async def test_json_formatter():
    """Testa o formatador JSON."""
    formatter = JsonFormatter()
    
    # Cria um registro de log mock
    class MockRecord:
        def __init__(self):
            self.levelname = "INFO"
            self.getMessage = lambda: "Test message"
            self.module = "test_module"
            self.funcName = "test_function"
            self.lineno = 123
            self.extra = {"key": "value"}
    
    # Formata o registro
    formatted = formatter.format(MockRecord())
    log_entry = json.loads(formatted)
    
    # Verifica campos
    assert log_entry['level'] == 'INFO'
    assert log_entry['message'] == 'Test message'
    assert log_entry['module'] == 'test_module'
    assert log_entry['function'] == 'test_function'
    assert log_entry['line'] == 123
    assert log_entry['key'] == 'value' 