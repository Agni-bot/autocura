import pytest
from datetime import datetime
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria

@pytest.fixture
def test_config():
    """Fixture que fornece configuração para testes."""
    return {
        "memoria_path": "memoria_test.json",
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0
    }

@pytest.fixture
def prometheus_registry():
    """Fixture que fornece um registro Prometheus limpo para testes."""
    from prometheus_client import CollectorRegistry
    return CollectorRegistry()

@pytest.fixture
def gerenciador_memoria(test_config, prometheus_registry):
    """Fixture que cria uma instância do GerenciadorMemoria para testes de validação ética."""
    return GerenciadorMemoria(
        config=test_config,
        registry=prometheus_registry
    )

@pytest.mark.asyncio
async def test_registrar_validacao_etica(gerenciador_memoria):
    """Testa o registro de uma validação ética."""
    validacao = {
        "tipo": "decisao",
        "contexto": "teste",
        "resultado": "aprovado",
        "justificativa": "Teste de validação",
        "nivel_confianca": 0.95
    }
    
    gerenciador_memoria.registrar_validacao_etica(validacao)
    
    validacoes = gerenciador_memoria.obter_validacoes_eticas()
    assert len(validacoes) == 1
    assert validacoes[0]["tipo"] == "decisao"
    assert validacoes[0]["resultado"] == "aprovado"

@pytest.mark.asyncio
async def test_validar_decisao_etica(gerenciador_memoria):
    """Testa a validação ética de uma decisão."""
    # Registra princípios éticos
    principios = {
        "privacidade": 0.9,
        "transparencia": 0.85,
        "justica": 0.95
    }
    gerenciador_memoria.registrar_principios_eticos(principios)
    
    # Testa decisão que respeita os princípios
    decisao = {
        "contexto": "processamento_dados",
        "principios_afetados": ["privacidade", "transparencia"],
        "dados": {"tipo": "pessoal", "nivel_sensibilidade": "baixo"}
    }
    
    resultado = await gerenciador_memoria.validar_decisao_etica(decisao)
    assert resultado["aprovado"] is True
    assert resultado["nivel_confianca"] > 0.8
    
    # Testa decisão que viola princípios
    decisao_violacao = {
        "contexto": "processamento_dados",
        "principios_afetados": ["privacidade"],
        "dados": {"tipo": "pessoal", "nivel_sensibilidade": "alto"}
    }
    
    resultado = await gerenciador_memoria.validar_decisao_etica(decisao_violacao)
    assert resultado["aprovado"] is False
    assert "privacidade" in resultado["justificativa"]

@pytest.mark.asyncio
async def test_registrar_violacao_etica(gerenciador_memoria):
    """Testa o registro de uma violação ética."""
    violacao = {
        "tipo": "decisao",
        "contexto": "teste",
        "principio_violado": "privacidade",
        "descricao": "Teste de violação",
        "severidade": "alta"
    }
    
    gerenciador_memoria.registrar_violacao_etica(violacao)
    
    violacoes = gerenciador_memoria.obter_violacoes_eticas()
    assert len(violacoes) == 1
    assert violacoes[0]["tipo"] == "decisao"
    assert violacoes[0]["principio_violado"] == "privacidade"

@pytest.mark.asyncio
async def test_obter_historico_etico(gerenciador_memoria):
    """Testa a obtenção do histórico ético."""
    # Registra algumas validações e violações
    validacao = {
        "tipo": "decisao",
        "contexto": "teste",
        "resultado": "aprovado",
        "justificativa": "Teste de validação"
    }
    gerenciador_memoria.registrar_validacao_etica(validacao)
    
    violacao = {
        "tipo": "decisao",
        "contexto": "teste",
        "principio_violado": "privacidade",
        "descricao": "Teste de violação"
    }
    gerenciador_memoria.registrar_violacao_etica(violacao)
    
    historico = gerenciador_memoria.obter_historico_etico()
    assert len(historico["validacoes"]) == 1
    assert len(historico["violacoes"]) == 1

@pytest.mark.asyncio
async def test_analise_tendencia_etica(gerenciador_memoria):
    """Testa a análise de tendência ética."""
    # Registra várias validações e violações
    for _ in range(5):
        validacao = {
            "tipo": "decisao",
            "contexto": "teste",
            "resultado": "aprovado",
            "justificativa": "Teste de validação"
        }
        gerenciador_memoria.registrar_validacao_etica(validacao)
    
    for _ in range(2):
        violacao = {
            "tipo": "decisao",
            "contexto": "teste",
            "principio_violado": "privacidade",
            "descricao": "Teste de violação"
        }
        gerenciador_memoria.registrar_violacao_etica(violacao)
    
    tendencia = gerenciador_memoria.analisar_tendencia_etica()
    assert tendencia["taxa_aprovacao"] == 1.0
    assert tendencia["taxa_violacao"] == 0.4
    assert tendencia["tendencia"] == "positiva"
    assert len(tendencia["recomendacoes"]) > 0

@pytest.mark.asyncio
async def test_validacao_etica_com_principios(gerenciador_memoria):
    """Testa a validação ética considerando princípios específicos."""
    # Registra princípios éticos
    principios = {
        "privacidade": 0.9,
        "transparencia": 0.85,
        "justica": 0.95,
        "seguranca": 0.88
    }
    gerenciador_memoria.registrar_principios_eticos(principios)
    
    # Testa decisão que afeta múltiplos princípios
    decisao = {
        "contexto": "processamento_dados",
        "principios_afetados": ["privacidade", "seguranca", "transparencia"],
        "dados": {
            "tipo": "pessoal",
            "nivel_sensibilidade": "medio",
            "medidas_seguranca": ["criptografia", "auditoria"]
        }
    }
    
    resultado = await gerenciador_memoria.validar_decisao_etica(decisao)
    assert resultado["aprovado"] is True
    assert len(resultado["avaliacao_principios"]) == 3
    assert all(peso > 0.8 for peso in resultado["avaliacao_principios"].values()) 