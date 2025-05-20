import pytest
from app import app
import json
from validators.forex_validator import ForexValidator

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_status_endpoint(client):
    """Test the /api/will/status endpoint"""
    response = client.get('/api/will/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'status' in data
    assert data['status'] == 'OPERATIONAL'
    assert 'active_models' in data
    assert 'data_feed_status' in data
    assert 'system_health_metrics' in data
    assert 'trading_status' in data
    assert 'active_pairs' in data['trading_status']
    assert 'major_pairs' in data['trading_status']
    assert 'minor_pairs' in data['trading_status']

def test_decision_endpoint(client):
    """Test the /api/will/decision endpoint"""
    test_data = {
        "asset": "EUR/USD",
        "volume": 10000
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'trade_signal' in data
    assert 'confidence_score' in data
    assert 'target_asset' in data
    assert data['target_asset'] == test_data['asset']
    assert 'recommended_volume' in data
    assert 'risk_assessment' in data
    assert 'supporting_factors' in data
    assert 'gemini_analysis_summary' in data
    assert 'market_analysis' in data
    assert 'input_parameters' in data
    assert 'pair_info' in data['input_parameters']

def test_decision_endpoint_invalid_input(client):
    """Test the /api/will/decision endpoint with invalid input"""
    # Test with missing required fields
    test_data = {
        "asset": "EUR/USD"
        # Missing volume
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    
    # Test with invalid asset
    test_data = {
        "asset": "INVALID/PAIR",
        "volume": 10000
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'par' in data['error'].lower()

def test_decision_endpoint_invalid_json(client):
    """Test the /api/will/decision endpoint with invalid JSON"""
    response = client.post(
        '/api/will/decision',
        data="invalid json",
        content_type='application/json'
    )
    assert response.status_code == 400

def test_decision_endpoint_negative_volume(client):
    """Test the /api/will/decision endpoint with negative volume"""
    test_data = {
        "asset": "EUR/USD",
        "volume": -10000
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'volume' in data['error'].lower()

def test_decision_endpoint_zero_volume(client):
    """Test the /api/will/decision endpoint with zero volume"""
    test_data = {
        "asset": "EUR/USD",
        "volume": 0
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'volume' in data['error'].lower()

def test_decision_endpoint_missing_content_type(client):
    """Test the /api/will/decision endpoint without content-type header"""
    test_data = {
        "asset": "EUR/USD",
        "volume": 10000
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data)
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'content-type' in data['error'].lower()

def test_decision_endpoint_empty_json(client):
    """Test the /api/will/decision endpoint with empty JSON object"""
    test_data = {}
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'required' in data['error'].lower()

def test_decision_endpoint_additional_fields(client):
    """Test the /api/will/decision endpoint with additional fields"""
    test_data = {
        "asset": "EUR/USD",
        "volume": 10000,
        "extra_field": "should be ignored"
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'trade_signal' in data
    assert 'target_asset' in data
    assert data['target_asset'] == test_data['asset']

def test_status_endpoint_headers(client):
    """Test the /api/will/status endpoint response headers"""
    response = client.get('/api/will/status')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert 'Access-Control-Allow-Origin' in response.headers

def test_decision_endpoint_headers(client):
    """Test the /api/will/decision endpoint response headers"""
    test_data = {
        "asset": "EUR/USD",
        "volume": 10000
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert 'Access-Control-Allow-Origin' in response.headers

def test_pairs_endpoint(client):
    """Test the /api/will/pairs endpoint"""
    response = client.get('/api/will/pairs')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'major_pairs' in data
    assert 'minor_pairs' in data
    assert 'all_pairs' in data
    assert 'last_update' in data
    
    # Verify content
    validator = ForexValidator()
    assert data['major_pairs'] == validator.get_major_pairs()
    assert data['minor_pairs'] == validator.get_minor_pairs()
    assert data['all_pairs'] == validator.get_all_valid_pairs()

def test_pair_info_endpoint_valid(client):
    """Test the /api/will/pairs/<pair> endpoint with valid pair"""
    response = client.get('/api/will/pairs/EUR/USD')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'pair' in data
    assert 'base_currency' in data
    assert 'quote_currency' in data
    assert 'type' in data
    assert 'typical_spread' in data
    assert 'min_trade_size' in data
    assert 'max_trade_size' in data
    
    # Verify content
    assert data['pair'] == 'EUR/USD'
    assert data['base_currency']['code'] == 'EUR'
    assert data['quote_currency']['code'] == 'USD'
    assert data['type'] == 'MAJOR'

def test_pair_info_endpoint_invalid(client):
    """Test the /api/will/pairs/<pair> endpoint with invalid pair"""
    response = client.get('/api/will/pairs/INVALID/PAIR')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'não encontrado' in data['error'].lower()

def test_decision_endpoint_minor_pair(client):
    """Test the /api/will/decision endpoint with minor pair"""
    test_data = {
        "asset": "EUR/GBP",
        "volume": 10000
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['target_asset'] == 'EUR/GBP'
    assert 'pair_info' in data['input_parameters']
    assert data['input_parameters']['pair_info']['type'] == 'MINOR'

def test_decision_endpoint_volume_limits(client):
    """Test the /api/will/decision endpoint with volume limits"""
    # Test minimum volume
    test_data = {
        "asset": "EUR/USD",
        "volume": 500  # Below minimum
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'mínimo' in data['error'].lower()
    
    # Test maximum volume
    test_data = {
        "asset": "EUR/USD",
        "volume": 2000000  # Above maximum
    }
    
    response = client.post(
        '/api/will/decision',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'máximo' in data['error'].lower() 