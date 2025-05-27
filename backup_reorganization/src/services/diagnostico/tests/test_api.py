import pytest
from flask import Flask
from ..app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert data['service'] == 'diagnostico'

def test_analisar_problema_sem_dados(client):
    response = client.post('/analisar')
    assert response.status_code == 400
    data = response.get_json()
    assert data['erro'] == 'Dados não fornecidos'

def test_analisar_problema_com_dados(client):
    dados = {
        'problema': {
            'tipo': 'desempenho',
            'descricao': 'Alto uso de CPU'
        },
        'metricas': {
            'cpu_uso': 90.0,
            'memoria_uso': 60.0
        },
        'logs': [
            'CPU usage high',
            'Memory usage normal'
        ]
    }
    
    response = client.post('/analisar', json=dados)
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'tipo' in data
    assert 'severidade' in data
    assert 'causas_provaveis' in data
    assert 'impacto' in data
    assert 'timestamp' in data
    
    assert data['tipo'] == 'desempenho'
    assert data['severidade'] == 'alta'
    assert isinstance(data['causas_provaveis'], list)
    assert isinstance(data['impacto'], dict)

def test_analisar_problema_com_erro(client):
    dados = {
        'problema': None,
        'metricas': None,
        'logs': None
    }
    
    response = client.post('/analisar', json=dados)
    assert response.status_code == 500
    data = response.get_json()
    assert 'erro' in data 