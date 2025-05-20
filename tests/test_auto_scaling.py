import pytest
from datetime import datetime, timedelta
from src.scaling.auto_scaling import AutoScaling, MetricasScaling

@pytest.fixture
def auto_scaling():
    """Fixture que fornece uma instância do auto-scaling para os testes."""
    return AutoScaling(
        min_instancias=1,
        max_instancias=5,
        cpu_threshold=70.0,
        memoria_threshold=80.0,
        latencia_threshold=200.0,
        cooldown_period=1
    )

def test_inicializacao(auto_scaling):
    """Testa a inicialização do auto-scaling."""
    assert auto_scaling.min_instancias == 1
    assert auto_scaling.max_instancias == 5
    assert auto_scaling.cpu_threshold == 70.0
    assert auto_scaling.memoria_threshold == 80.0
    assert auto_scaling.latencia_threshold == 200.0
    assert auto_scaling.instancias_atuais == 1

def test_registrar_metricas(auto_scaling):
    """Testa o registro de métricas."""
    metricas = MetricasScaling(
        cpu_usage=50.0,
        memoria_usage=60.0,
        latencia=150.0,
        requests_por_segundo=100.0,
        timestamp=datetime.now()
    )
    
    auto_scaling.registrar_metricas(metricas)
    assert len(auto_scaling.metricas_historico) == 1
    assert auto_scaling.metricas_historico[0] == metricas

def test_scaling_up(auto_scaling):
    """Testa o scaling up quando as métricas excedem os limites."""
    # Registra métricas que devem trigger scaling up
    for i in range(10):
        metricas = MetricasScaling(
            cpu_usage=80.0,  # Acima do threshold
            memoria_usage=85.0,  # Acima do threshold
            latencia=250.0,  # Acima do threshold
            requests_por_segundo=150.0,
            timestamp=datetime.now()
        )
        auto_scaling.registrar_metricas(metricas)
    
    # Executa scaling
    novas_instancias = auto_scaling.executar_scaling()
    assert novas_instancias == 2  # Deve aumentar para 2 instâncias

def test_scaling_down(auto_scaling):
    """Testa o scaling down quando as métricas estão baixas."""
    # Primeiro escala up
    auto_scaling.instancias_atuais = 3
    
    # Registra métricas que devem trigger scaling down
    for i in range(10):
        metricas = MetricasScaling(
            cpu_usage=30.0,  # Bem abaixo do threshold
            memoria_usage=35.0,  # Bem abaixo do threshold
            latencia=100.0,  # Bem abaixo do threshold
            requests_por_segundo=50.0,
            timestamp=datetime.now()
        )
        auto_scaling.registrar_metricas(metricas)
    
    # Executa scaling
    novas_instancias = auto_scaling.executar_scaling()
    assert novas_instancias == 2  # Deve diminuir para 2 instâncias

def test_cooldown_period(auto_scaling):
    """Testa o período de cooldown entre operações de scaling."""
    # Registra métricas para scaling up
    for i in range(10):
        metricas = MetricasScaling(
            cpu_usage=80.0,
            memoria_usage=85.0,
            latencia=250.0,
            requests_por_segundo=150.0,
            timestamp=datetime.now()
        )
        auto_scaling.registrar_metricas(metricas)
    
    # Primeiro scaling
    novas_instancias = auto_scaling.executar_scaling()
    assert novas_instancias == 2
    
    # Tenta scaling novamente imediatamente
    novas_instancias = auto_scaling.executar_scaling()
    assert novas_instancias is None  # Deve retornar None devido ao cooldown

def test_limites_instancias(auto_scaling):
    """Testa os limites mínimo e máximo de instâncias."""
    # Tenta scaling down com mínimo de instâncias
    auto_scaling.instancias_atuais = 1
    for i in range(10):
        metricas = MetricasScaling(
            cpu_usage=20.0,
            memoria_usage=25.0,
            latencia=50.0,
            requests_por_segundo=10.0,
            timestamp=datetime.now()
        )
        auto_scaling.registrar_metricas(metricas)
    
    novas_instancias = auto_scaling.executar_scaling()
    assert novas_instancias is None  # Não deve diminuir abaixo do mínimo
    
    # Tenta scaling up com máximo de instâncias
    auto_scaling.instancias_atuais = 5
    for i in range(10):
        metricas = MetricasScaling(
            cpu_usage=90.0,
            memoria_usage=95.0,
            latencia=300.0,
            requests_por_segundo=200.0,
            timestamp=datetime.now()
        )
        auto_scaling.registrar_metricas(metricas)
    
    novas_instancias = auto_scaling.executar_scaling()
    assert novas_instancias is None  # Não deve aumentar acima do máximo

def test_obter_metricas_atual(auto_scaling):
    """Testa a obtenção das métricas atuais."""
    # Sem métricas registradas
    metricas = auto_scaling.obter_metricas_atual()
    assert metricas["instancias"] == 1
    assert metricas["cpu_usage"] == 0.0
    assert metricas["memoria_usage"] == 0.0
    assert metricas["latencia"] == 0.0
    assert metricas["requests_por_segundo"] == 0.0
    
    # Com métricas registradas
    metricas_registro = MetricasScaling(
        cpu_usage=75.0,
        memoria_usage=80.0,
        latencia=180.0,
        requests_por_segundo=120.0,
        timestamp=datetime.now()
    )
    auto_scaling.registrar_metricas(metricas_registro)
    
    metricas = auto_scaling.obter_metricas_atual()
    assert metricas["instancias"] == 1
    assert metricas["cpu_usage"] == 75.0
    assert metricas["memoria_usage"] == 80.0
    assert metricas["latencia"] == 180.0
    assert metricas["requests_por_segundo"] == 120.0 