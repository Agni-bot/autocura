"""
Testes do guardião cognitivo do sistema.
"""
import pytest
from datetime import datetime
from typing import Dict, Any

from src.guardiao.guardiao_cognitivo import GuardiaoCognitivo

@pytest.fixture
def guardiao():
    """Fixture que fornece uma instância do guardião cognitivo para os testes."""
    return GuardiaoCognitivo()

def test_monitorar_recursos():
    """Testa o monitoramento de recursos."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
    metricas = {
        "cpu_uso": 60,
        "memoria_uso": 65,
        "disco_uso": 50,
        "rede_uso": 40
    }
    
    # Monitorar recursos
    resultado = guardiao.monitorar_recursos(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert len(resultado["alertas"]) == 0

def test_monitorar_recursos_criticos():
    """Testa o monitoramento de recursos críticos."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas críticas
    metricas = {
        "cpu_uso": 95,
        "memoria_uso": 90,
        "disco_uso": 85,
        "rede_uso": 80
    }
    
    # Monitorar recursos
    resultado = guardiao.monitorar_recursos(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert len(resultado["alertas"]) > 0
    assert "cpu" in resultado["alertas"][0].lower()
    assert "memoria" in resultado["alertas"][1].lower()

def test_monitorar_desempenho():
    """Testa o monitoramento de desempenho."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
    metricas = {
        "latencia": 100,
        "throughput": 1000,
        "erros": 0,
        "tempo_resposta": 50
    }
    
    # Monitorar desempenho
    resultado = guardiao.monitorar_desempenho(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert len(resultado["alertas"]) == 0

def test_monitorar_desempenho_critico():
    """Testa o monitoramento de desempenho crítico."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas críticas
    metricas = {
        "latencia": 1000,
        "throughput": 100,
        "erros": 50,
        "tempo_resposta": 500
    }
    
    # Monitorar desempenho
    resultado = guardiao.monitorar_desempenho(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert len(resultado["alertas"]) > 0
    assert "latencia" in resultado["alertas"][0].lower()
    assert "erros" in resultado["alertas"][1].lower()

def test_monitorar_seguranca():
    """Testa o monitoramento de segurança."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
    metricas = {
        "tentativas_acesso": 10,
        "falhas_autenticacao": 2,
        "requisicoes_suspeitas": 1,
        "vulnerabilidades": 0
    }
    
    # Monitorar segurança
    resultado = guardiao.monitorar_seguranca(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert len(resultado["alertas"]) == 0

def test_monitorar_seguranca_critico():
    """Testa o monitoramento de segurança crítico."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas críticas
    metricas = {
        "tentativas_acesso": 1000,
        "falhas_autenticacao": 100,
        "requisicoes_suspeitas": 50,
        "vulnerabilidades": 10
    }
    
    # Monitorar segurança
    resultado = guardiao.monitorar_seguranca(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert len(resultado["alertas"]) > 0
    assert "acesso" in resultado["alertas"][0].lower()
    assert "vulnerabilidades" in resultado["alertas"][1].lower()

def test_monitorar_etica():
    """Testa o monitoramento de ética."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
    metricas = {
        "vies_detectado": 0,
        "discriminacao": 0,
        "privacidade": 0,
        "transparencia": 100
    }
    
    # Monitorar ética
    resultado = guardiao.monitorar_etica(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert len(resultado["alertas"]) == 0

def test_monitorar_etica_critico():
    """Testa o monitoramento de ética crítico."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas críticas
    metricas = {
        "vies_detectado": 50,
        "discriminacao": 30,
        "privacidade": 20,
        "transparencia": 10
    }
    
    # Monitorar ética
    resultado = guardiao.monitorar_etica(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert len(resultado["alertas"]) > 0
    assert "vies" in resultado["alertas"][0].lower()
    assert "discriminacao" in resultado["alertas"][1].lower()

def test_aplicar_salvaguardas_recursos():
    """Testa a aplicação de salvaguardas para recursos."""
    guardiao = GuardiaoCognitivo()
    
    # Simular incidente
    incidente = {
        "id": "test_1",
        "tipo": "critico",
        "componente": "cpu",
        "mensagem": "Uso de CPU acima do limite crítico",
        "valor": 95,
        "timestamp": datetime.now().isoformat()
    }
    
    # Aplicar salvaguardas
    resultado = guardiao.aplicar_salvaguardas(incidente)
    
    # Verificar resultado
    assert resultado["status"] == "emergencia"
    assert resultado["acao"] == "reduzir_carga"
    assert len(resultado["alertas"]) > 0

def test_aplicar_salvaguardas_desempenho():
    """Testa a aplicação de salvaguardas para desempenho."""
    guardiao = GuardiaoCognitivo()
    
    # Simular incidente
    incidente = {
        "id": "test_1",
        "tipo": "critico",
        "componente": "latencia",
        "mensagem": "Latência acima do limite crítico",
        "valor": 1000,
        "timestamp": datetime.now().isoformat()
    }
    
    # Aplicar salvaguardas
    resultado = guardiao.aplicar_salvaguardas(incidente)
    
    # Verificar resultado
    assert resultado["status"] == "emergencia"
    assert resultado["acao"] == "otimizar_performance"
    assert len(resultado["alertas"]) > 0

def test_aplicar_salvaguardas_seguranca():
    """Testa a aplicação de salvaguardas para segurança."""
    guardiao = GuardiaoCognitivo()
    
    # Simular incidente
    incidente = {
        "id": "test_1",
        "tipo": "critico",
        "componente": "seguranca",
        "mensagem": "Tentativas de acesso suspeitas detectadas",
        "valor": 1000,
        "timestamp": datetime.now().isoformat()
    }
    
    # Aplicar salvaguardas
    resultado = guardiao.aplicar_salvaguardas(incidente)
    
    # Verificar resultado
    assert resultado["status"] == "emergencia"
    assert resultado["acao"] == "bloquear_acesso"
    assert len(resultado["alertas"]) > 0

def test_aplicar_salvaguardas_etica():
    """Testa a aplicação de salvaguardas para ética."""
    guardiao = GuardiaoCognitivo()
    
    # Simular incidente
    incidente = {
        "id": "test_1",
        "tipo": "critico",
        "componente": "etica",
        "mensagem": "Vies detectado nas decisões",
        "valor": 50,
        "timestamp": datetime.now().isoformat()
    }
    
    # Aplicar salvaguardas
    resultado = guardiao.aplicar_salvaguardas(incidente)
    
    # Verificar resultado
    assert resultado["status"] == "emergencia"
    assert resultado["acao"] == "revisar_decisoes"
    assert len(resultado["alertas"]) > 0

def test_verificar_autonomia():
    """Testa a verificação de autonomia."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
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
    
    # Verificar autonomia
    resultado = guardiao.verificar_autonomia(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert resultado["pode_avancar"] == True
    assert resultado["nivel_autonomia"] == 1

def test_verificar_autonomia_reduzida():
    """Testa a verificação de autonomia reduzida."""
    guardiao = GuardiaoCognitivo()
    
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
    
    # Verificar autonomia
    resultado = guardiao.verificar_autonomia(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert resultado["pode_avancar"] == False
    assert resultado["nivel_autonomia"] == 0

def test_verificar_aprendizado():
    """Testa a verificação de aprendizado."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
    metricas = {
        "acertos": 90,
        "erros": 10,
        "melhorias": 5,
        "novos_casos": 10
    }
    
    # Verificar aprendizado
    resultado = guardiao.verificar_aprendizado(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert resultado["nivel_aprendizado"] == "avancado"
    assert len(resultado["alertas"]) == 0

def test_verificar_aprendizado_insuficiente():
    """Testa a verificação de aprendizado insuficiente."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas ruins
    metricas = {
        "acertos": 50,
        "erros": 50,
        "melhorias": 0,
        "novos_casos": 0
    }
    
    # Verificar aprendizado
    resultado = guardiao.verificar_aprendizado(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert resultado["nivel_aprendizado"] == "basico"
    assert len(resultado["alertas"]) > 0

def test_verificar_estabilidade():
    """Testa a verificação de estabilidade."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
    metricas = {
        "uptime": 99.9,
        "falhas": 0,
        "recuperacoes": 0,
        "tempo_medio_falha": 0
    }
    
    # Verificar estabilidade
    resultado = guardiao.verificar_estabilidade(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert resultado["nivel_estabilidade"] == "alta"
    assert len(resultado["alertas"]) == 0

def test_verificar_estabilidade_baixa():
    """Testa a verificação de estabilidade baixa."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas ruins
    metricas = {
        "uptime": 90.0,
        "falhas": 10,
        "recuperacoes": 5,
        "tempo_medio_falha": 60
    }
    
    # Verificar estabilidade
    resultado = guardiao.verificar_estabilidade(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert resultado["nivel_estabilidade"] == "baixa"
    assert len(resultado["alertas"]) > 0

def test_verificar_conformidade():
    """Testa a verificação de conformidade."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
    metricas = {
        "lgpd": 100,
        "gdpr": 100,
        "iso27001": 100,
        "nist": 100
    }
    
    # Verificar conformidade
    resultado = guardiao.verificar_conformidade(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert resultado["nivel_conformidade"] == "total"
    assert len(resultado["alertas"]) == 0

def test_verificar_conformidade_parcial():
    """Testa a verificação de conformidade parcial."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas ruins
    metricas = {
        "lgpd": 50,
        "gdpr": 50,
        "iso27001": 50,
        "nist": 50
    }
    
    # Verificar conformidade
    resultado = guardiao.verificar_conformidade(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert resultado["nivel_conformidade"] == "parcial"
    assert len(resultado["alertas"]) > 0

def test_verificar_evolucao():
    """Testa a verificação de evolução."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
    metricas = {
        "novas_funcionalidades": 10,
        "melhorias": 5,
        "correcoes": 2,
        "feedback_positivo": 90
    }
    
    # Verificar evolução
    resultado = guardiao.verificar_evolucao(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert resultado["nivel_evolucao"] == "avancado"
    assert len(resultado["alertas"]) == 0

def test_verificar_evolucao_estagnada():
    """Testa a verificação de evolução estagnada."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas ruins
    metricas = {
        "novas_funcionalidades": 0,
        "melhorias": 0,
        "correcoes": 0,
        "feedback_positivo": 50
    }
    
    # Verificar evolução
    resultado = guardiao.verificar_evolucao(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert resultado["nivel_evolucao"] == "estagnado"
    assert len(resultado["alertas"]) > 0

def test_verificar_resiliencia():
    """Testa a verificação de resiliência."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas
    metricas = {
        "tempo_recuperacao": 0,
        "falhas_recuperadas": 0,
        "degradacao_aceitavel": 0,
        "backup_sucesso": 100
    }
    
    # Verificar resiliência
    resultado = guardiao.verificar_resiliencia(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "normal"
    assert resultado["nivel_resiliencia"] == "alta"
    assert len(resultado["alertas"]) == 0

def test_verificar_resiliencia_baixa():
    """Testa a verificação de resiliência baixa."""
    guardiao = GuardiaoCognitivo()
    
    # Simular métricas ruins
    metricas = {
        "tempo_recuperacao": 60,
        "falhas_recuperadas": 5,
        "degradacao_aceitavel": 50,
        "backup_sucesso": 50
    }
    
    # Verificar resiliência
    resultado = guardiao.verificar_resiliencia(metricas)
    
    # Verificar resultado
    assert resultado["status"] == "critico"
    assert resultado["nivel_resiliencia"] == "baixa"
    assert len(resultado["alertas"]) > 0 