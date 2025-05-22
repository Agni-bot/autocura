"""
Testes do orquestrador do sistema.
"""
import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from src.orchestration.orquestrador import Orquestrador
from src.services.memoria.gerenciador_memoria import GerenciadorMemoria
from src.services.etica.validador_etico import ValidadorEtico
from src.services.guardiao.guardiao_cognitivo import GuardiaoCognitivo
from src.acoes.gerador_acoes import GeradorAcoes

@pytest.fixture
def orquestrador():
    """Fixture que fornece uma instância do orquestrador para os testes."""
    gerenciador_memoria = GerenciadorMemoria({
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0
    })
    validador_etico = ValidadorEtico()
    guardiao_cognitivo = GuardiaoCognitivo()
    gerador_acoes = GeradorAcoes()
    
    return Orquestrador(
        gerenciador_memoria=gerenciador_memoria,
        validador_etico=validador_etico,
        guardiao_cognitivo=guardiao_cognitivo,
        gerador_acoes=gerador_acoes
    )

@pytest.mark.asyncio
async def test_inicializar_sistema():
    """Testa a inicialização do sistema."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Verificar estado inicial
    estado = orquestrador.obter_estado()
    assert estado["nivel_autonomia"] == 0
    assert estado["status"] == "inicializado"
    assert estado["ciclo_atual"] == 0

@pytest.mark.asyncio
async def test_executar_ciclo_normal():
    """Testa a execução de um ciclo normal."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["acoes_executadas"] == 0
    assert resultado["incidentes"] == 0

@pytest.mark.asyncio
async def test_executar_ciclo_com_incidente():
    """Testa a execução de um ciclo com incidente."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular incidente
    incidente = {
        "id": "test_1",
        "tipo": "critico",
        "componente": "api",
        "mensagem": "Falha crítica detectada",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar incidente
    orquestrador.gerenciador_memoria.registrar_incidente(incidente)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "incidente"
    assert resultado["ciclo"] == 1
    assert resultado["acoes_executadas"] == 0
    assert resultado["incidentes"] == 1

@pytest.mark.asyncio
async def test_executar_ciclo_com_decisao():
    """Testa a execução de um ciclo com decisão."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular decisão
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "descricao": "Corrigir bug crítico",
        "componente": "api",
        "impacto": "alto",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar decisão
    orquestrador.gerenciador_memoria.registrar_decisao(decisao)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["acoes_executadas"] == 0
    assert resultado["decisoes_processadas"] == 1

@pytest.mark.asyncio
async def test_executar_ciclo_com_acao():
    """Testa a execução de um ciclo com ação."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "manutencao",
        "status": "pendente",
        "componente": "api",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar ação
    orquestrador.gerenciador_memoria.registrar_acao(acao)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["acoes_executadas"] == 1
    assert resultado["incidentes"] == 0

@pytest.mark.asyncio
async def test_executar_ciclo_com_aprendizado():
    """Testa a execução de um ciclo com aprendizado."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular aprendizado
    aprendizado = {
        "id": "test_1",
        "tipo": "otimizacao",
        "descricao": "Melhorar performance da API",
        "componente": "api",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar aprendizado
    orquestrador.gerenciador_memoria.registrar_aprendizado(aprendizado)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["acoes_executadas"] == 0
    assert resultado["aprendizados_aplicados"] == 1

@pytest.mark.asyncio
async def test_executar_ciclo_com_autonomia():
    """Testa a execução de um ciclo com autonomia."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular métricas boas
    metricas = {
        "cpu_uso": 30,
        "memoria_uso": 35,
        "disco_uso": 40,
        "rede_uso": 25,
        "latencia": 100,
        "throughput": 1000,
        "erros": 0,
        "tempo_resposta": 50
    }
    
    # Atualizar métricas
    orquestrador.gerenciador_memoria.atualizar_metricas(metricas)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["nivel_autonomia"] == 1
    assert resultado["pode_avancar"] == True

@pytest.mark.asyncio
async def test_executar_ciclo_com_autonomia_reduzida():
    """Testa a execução de um ciclo com autonomia reduzida."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular métricas ruins
    metricas = {
        "cpu_uso": 90,
        "memoria_uso": 85,
        "disco_uso": 80,
        "rede_uso": 75,
        "latencia": 1000,
        "throughput": 100,
        "erros": 50,
        "tempo_resposta": 500
    }
    
    # Atualizar métricas
    orquestrador.gerenciador_memoria.atualizar_metricas(metricas)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert resultado["ciclo"] == 1
    assert resultado["nivel_autonomia"] == 0
    assert resultado["pode_avancar"] == False

@pytest.mark.asyncio
async def test_executar_ciclo_com_validacao_etica():
    """Testa a execução de um ciclo com validação ética."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular decisão com validação ética
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "descricao": "Corrigir bug crítico",
        "componente": "api",
        "impacto": "alto",
        "documentacao": True,
        "rastreavel": True,
        "explicavel": True,
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar decisão
    orquestrador.gerenciador_memoria.registrar_decisao(decisao)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["decisoes_processadas"] == 1
    assert resultado["validacoes_eticas"] == 1

@pytest.mark.asyncio
async def test_executar_ciclo_com_validacao_etica_rejeitada():
    """Testa a execução de um ciclo com validação ética rejeitada."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular decisão sem validação ética
    decisao = {
        "id": "test_1",
        "tipo": "manutencao",
        "descricao": "Corrigir bug crítico",
        "componente": "api",
        "impacto": "alto",
        "documentacao": False,
        "rastreavel": False,
        "explicavel": False,
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar decisão
    orquestrador.gerenciador_memoria.registrar_decisao(decisao)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "rejeitado"
    assert resultado["ciclo"] == 1
    assert resultado["decisoes_processadas"] == 1
    assert resultado["validacoes_eticas"] == 1
    assert resultado["validacoes_rejeitadas"] == 1

@pytest.mark.asyncio
async def test_executar_ciclo_com_salvaguardas():
    """Testa a execução de um ciclo com salvaguardas."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular incidente crítico
    incidente = {
        "id": "test_1",
        "tipo": "critico",
        "componente": "cpu",
        "mensagem": "Uso de CPU acima do limite crítico",
        "valor": 95,
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar incidente
    orquestrador.gerenciador_memoria.registrar_incidente(incidente)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "emergencia"
    assert resultado["ciclo"] == 1
    assert resultado["incidentes"] == 1
    assert resultado["salvaguardas_aplicadas"] == 1

@pytest.mark.asyncio
async def test_executar_ciclo_com_acoes_geradas():
    """Testa a execução de um ciclo com ações geradas."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular contexto para ação
    contexto = {
        "tipo": "manutencao",
        "prioridade": "alta",
        "descricao": "Corrigir bug crítico",
        "componente": "api",
        "impacto": "alto"
    }
    
    # Gerar ação
    acao = orquestrador.gerador_acoes.gerar_acao(contexto)
    
    # Registrar ação
    orquestrador.gerenciador_memoria.registrar_acao(acao)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["acoes_geradas"] == 1
    assert resultado["acoes_executadas"] == 1

@pytest.mark.asyncio
async def test_executar_ciclo_com_acoes_executadas():
    """Testa a execução de um ciclo com ações executadas."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular ação
    acao = {
        "id": "test_1",
        "tipo": "manutencao",
        "status": "pendente",
        "componente": "api",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar ação
    orquestrador.gerenciador_memoria.registrar_acao(acao)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["acoes_executadas"] == 1
    assert resultado["acoes_concluidas"] == 1

@pytest.mark.asyncio
async def test_executar_ciclo_com_aprendizado_aplicado():
    """Testa a execução de um ciclo com aprendizado aplicado."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular aprendizado
    aprendizado = {
        "id": "test_1",
        "tipo": "otimizacao",
        "descricao": "Melhorar performance da API",
        "componente": "api",
        "timestamp": datetime.now().isoformat()
    }
    
    # Registrar aprendizado
    orquestrador.gerenciador_memoria.registrar_aprendizado(aprendizado)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["aprendizados_aplicados"] == 1
    assert resultado["aprendizados_concluidos"] == 1

@pytest.mark.asyncio
async def test_executar_ciclo_com_estado_atualizado():
    """Testa a execução de um ciclo com estado atualizado."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular estado
    estado = {
        "nivel_autonomia": 1,
        "status": "normal",
        "timestamp": datetime.now().isoformat()
    }
    
    # Atualizar estado
    orquestrador.gerenciador_memoria.atualizar_estado_sistema(estado)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["nivel_autonomia"] == 1
    assert resultado["estado_atualizado"] == True

@pytest.mark.asyncio
async def test_executar_ciclo_com_metricas_atualizadas():
    """Testa a execução de um ciclo com métricas atualizadas."""
    orquestrador = Orquestrador(
        GerenciadorMemoria(),
        ValidadorEtico(),
        GuardiaoCognitivo(),
        GeradorAcoes()
    )
    
    # Inicializar sistema
    await orquestrador.inicializar()
    
    # Simular métricas
    metricas = {
        "cpu_uso": 60,
        "memoria_uso": 65,
        "disco_uso": 50,
        "rede_uso": 40,
        "timestamp": datetime.now().isoformat()
    }
    
    # Atualizar métricas
    orquestrador.gerenciador_memoria.atualizar_metricas(metricas)
    
    # Executar ciclo
    resultado = await orquestrador.executar_ciclo()
    
    # Verificar resultado
    assert resultado["status"] == "sucesso"
    assert resultado["ciclo"] == 1
    assert resultado["metricas_atualizadas"] == True
    assert resultado["metricas"]["cpu_uso"] == 60
    assert resultado["metricas"]["memoria_uso"] == 65 