"""
Testes do fluxo de autonomia do sistema.
"""
import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from src.services.memoria.gerenciador_memoria import GerenciadorMemoria
from src.services.etica.validador_etico import ValidadorEtico
from src.services.guardiao.guardiao_cognitivo import GuardiaoCognitivo
from src.services.gerador.gerador_acoes import GeradorAcoes
from src.core.orquestrador import Orquestrador

@pytest.fixture
async def orquestrador():
    """Fixture que fornece uma instância do orquestrador para os testes."""
    orquestrador = Orquestrador()
    yield orquestrador
    # Limpeza após os testes
    await orquestrador.gerenciador_memoria.limpar_memoria_antiga(dias=0)

@pytest.mark.asyncio
async def test_transicao_autonomia_nivel_1_para_2():
    """Testa a transição de autonomia do nível 1 para o nível 2."""
    orquestrador = Orquestrador()
    
    # Configurar estado inicial
    estado_inicial = {
        "nivel_autonomia": 1,
        "status": "normal",
        "metricas_desempenho": {
            "precisao": 0.98,
            "falsos_negativos": 0,
            "tempo_operacao": 100,  # dias
            "incidentes": 0
        }
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_inicial)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar transição
    estado_final = orquestrador.gerenciador_memoria.obter_estado_sistema()
    assert estado_final["nivel_autonomia"] == 2
    assert resultado["status"] == "sucesso"

@pytest.mark.asyncio
async def test_manter_autonomia_nivel_1_por_baixo_desempenho():
    """Testa que o sistema mantém o nível 1 quando o desempenho está abaixo do esperado."""
    orquestrador = Orquestrador()
    
    # Configurar estado com métricas ruins
    estado_inicial = {
        "nivel_autonomia": 1,
        "status": "normal",
        "metricas_desempenho": {
            "precisao": 0.85,
            "falsos_negativos": 2,
            "tempo_operacao": 30,  # dias
            "incidentes": 1
        }
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_inicial)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar que permanece no nível 1
    estado_final = orquestrador.gerenciador_memoria.obter_estado_sistema()
    assert estado_final["nivel_autonomia"] == 1
    assert resultado["status"] == "sucesso"

@pytest.mark.asyncio
async def test_reducao_autonomia_por_violacao_etica():
    """Testa a redução de autonomia após violação ética."""
    orquestrador = Orquestrador()
    
    # Configurar estado inicial com nível 3
    estado_inicial = {
        "nivel_autonomia": 3,
        "status": "normal",
        "metricas_desempenho": {
            "precisao": 0.98,
            "falsos_negativos": 0,
            "tempo_operacao": 100,
            "incidentes": 0
        }
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_inicial)
    
    # Simular violação ética
    violacao = {
        "tipo": "violacao_etica",
        "componente": "gerador_acoes",
        "mensagem": "Ação violou princípio de transparência",
        "timestamp": datetime.now().isoformat()
    }
    orquestrador.guardiao.aplicar_salvaguardas(violacao)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar redução de autonomia
    estado_final = orquestrador.gerenciador_memoria.obter_estado_sistema()
    assert estado_final["nivel_autonomia"] == 1
    assert estado_final["status"] == "suspenso"

@pytest.mark.asyncio
async def test_reducao_autonomia_por_incidente_critico():
    """Testa a redução de autonomia após incidente crítico."""
    orquestrador = Orquestrador()
    
    # Configurar estado inicial com nível 2
    estado_inicial = {
        "nivel_autonomia": 2,
        "status": "normal",
        "metricas_desempenho": {
            "precisao": 0.98,
            "falsos_negativos": 0,
            "tempo_operacao": 100,
            "incidentes": 0
        }
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_inicial)
    
    # Simular incidente crítico
    incidente = {
        "tipo": "critico",
        "componente": "cpu",
        "mensagem": "Uso de CPU acima do limite crítico",
        "valor": 95,
        "timestamp": datetime.now().isoformat()
    }
    orquestrador.guardiao.aplicar_salvaguardas(incidente)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar redução de autonomia
    estado_final = orquestrador.gerenciador_memoria.obter_estado_sistema()
    assert estado_final["nivel_autonomia"] == 1
    assert estado_final["status"] == "emergencia"

@pytest.mark.asyncio
async def test_estabilidade_autonomia_nivel_2():
    """Testa a estabilidade do sistema no nível 2 de autonomia."""
    orquestrador = Orquestrador()
    
    # Configurar estado inicial
    estado_inicial = {
        "nivel_autonomia": 2,
        "status": "normal",
        "metricas_desempenho": {
            "precisao": 0.96,
            "falsos_negativos": 0,
            "tempo_operacao": 90,
            "incidentes": 0
        }
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_inicial)
    
    # Executar múltiplos ciclos
    for _ in range(5):
        resultado = await orquestrador.executar_ciclo()
        assert resultado["status"] == "sucesso"
    
    # Verificar estabilidade
    estado_final = orquestrador.gerenciador_memoria.obter_estado_sistema()
    assert estado_final["nivel_autonomia"] == 2
    assert estado_final["status"] == "normal"

@pytest.mark.asyncio
async def test_geracao_acoes_por_nivel_autonomia():
    """Testa a geração de ações de acordo com o nível de autonomia."""
    orquestrador = Orquestrador()
    
    # Testar nível 1 (apenas manutenção)
    estado_nivel_1 = {
        "nivel_autonomia": 1,
        "status": "normal",
        "metricas_desempenho": {
            "cpu_uso": 60,
            "memoria_uso": 65
        }
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_nivel_1)
    resultado_nivel_1 = await orquestrador.executar_ciclo()
    acoes_nivel_1 = orquestrador.gerador_acoes.obter_acoes_pendentes()
    assert all(acao["tipo"] == "manutencao" for acao in acoes_nivel_1)
    
    # Testar nível 2 (hotfix permitido)
    estado_nivel_2 = {
        "nivel_autonomia": 2,
        "status": "normal",
        "metricas_desempenho": {
            "cpu_uso": 85,
            "memoria_uso": 75
        }
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_nivel_2)
    resultado_nivel_2 = await orquestrador.executar_ciclo()
    acoes_nivel_2 = orquestrador.gerador_acoes.obter_acoes_pendentes()
    assert any(acao["tipo"] == "hotfix" for acao in acoes_nivel_2)

@pytest.mark.asyncio
async def test_validacao_etica_por_nivel_autonomia():
    """Testa a validação ética de acordo com o nível de autonomia."""
    orquestrador = Orquestrador()
    
    # Testar nível 1 (validação obrigatória)
    estado_nivel_1 = {
        "nivel_autonomia": 1,
        "status": "normal"
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_nivel_1)
    
    # Simular decisão
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "contexto": {
            "documentacao": True,
            "rastreavel": True,
            "explicavel": True
        }
    }
    
    # Validar decisão
    validacao = orquestrador.validador_etico.validar_decisao(decisao)
    assert validacao["aprovada"] == True
    
    # Testar nível 2 (validação mais rigorosa)
    estado_nivel_2 = {
        "nivel_autonomia": 2,
        "status": "normal"
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_nivel_2)
    
    # Simular decisão com falha ética
    decisao_falha = {
        "id": "test_2",
        "tipo": "hotfix",
        "contexto": {
            "documentacao": False,
            "rastreavel": False,
            "explicavel": False
        }
    }
    
    # Validar decisão
    validacao_falha = orquestrador.validador_etico.validar_decisao(decisao_falha)
    assert validacao_falha["aprovada"] == False

@pytest.mark.asyncio
async def test_salvaguardas_por_nivel_autonomia():
    """Testa as salvaguardas de acordo com o nível de autonomia."""
    orquestrador = Orquestrador()
    
    # Testar nível 1 (salvaguardas básicas)
    estado_nivel_1 = {
        "nivel_autonomia": 1,
        "status": "normal"
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_nivel_1)
    
    # Simular incidente
    incidente = {
        "tipo": "critico",
        "componente": "memoria",
        "mensagem": "Uso de memória acima do limite",
        "valor": 90
    }
    
    # Aplicar salvaguarda
    orquestrador.guardiao.aplicar_salvaguardas(incidente)
    estado_final_1 = orquestrador.gerenciador_memoria.obter_estado_sistema()
    assert estado_final_1["status"] == "emergencia"
    
    # Testar nível 2 (salvaguardas mais graduais)
    estado_nivel_2 = {
        "nivel_autonomia": 2,
        "status": "normal"
    }
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado_nivel_2)
    
    # Simular incidente menos crítico
    incidente_2 = {
        "tipo": "alerta",
        "componente": "cpu",
        "mensagem": "Uso de CPU acima do limite de alerta",
        "valor": 75
    }
    
    # Aplicar salvaguarda
    orquestrador.guardiao.aplicar_salvaguardas(incidente_2)
    estado_final_2 = orquestrador.gerenciador_memoria.obter_estado_sistema()
    assert estado_final_2["status"] == "alerta" 