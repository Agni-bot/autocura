"""
Testes de exemplo para demonstrar o uso de fixtures e documentação.

Este módulo contém exemplos de testes unitários e de integração
para demonstrar as melhores práticas de teste no sistema.
"""

import pytest
from datetime import datetime
from typing import Dict, Any, Generator
from unittest.mock import Mock, patch

# Fixtures
@pytest.fixture
def config_teste() -> Dict[str, Any]:
    """
    Fixture que fornece configurações de teste.
    
    Returns:
        Dict[str, Any]: Configurações de teste
    """
    return {
        "timeout": 30,
        "retry_count": 3,
        "api_url": "http://localhost:8000"
    }

@pytest.fixture
def mock_api() -> Generator[Mock, None, None]:
    """
    Fixture que fornece um mock da API.
    
    Yields:
        Mock: Mock da API
    """
    with patch("requests.Session") as mock:
        yield mock

@pytest.fixture
def dados_teste() -> Dict[str, Any]:
    """
    Fixture que fornece dados de teste.
    
    Returns:
        Dict[str, Any]: Dados de teste
    """
    return {
        "id": "test_123",
        "nome": "Teste",
        "data": datetime.now().isoformat(),
        "status": "ativo"
    }

# Testes Unitários
class TestProcessadorDados:
    """Testes para o processador de dados."""
    
    def test_processar_dados_sucesso(self, dados_teste: Dict[str, Any]) -> None:
        """
        Testa o processamento bem-sucedido de dados.
        
        Args:
            dados_teste: Fixture com dados de teste
        """
        # Arrange
        processador = ProcessadorDados()
        
        # Act
        resultado = processador.processar(dados_teste)
        
        # Assert
        assert resultado["status"] == "processado"
        assert "timestamp" in resultado
        assert resultado["id"] == dados_teste["id"]
    
    def test_processar_dados_invalidos(self) -> None:
        """Testa o processamento de dados inválidos."""
        # Arrange
        processador = ProcessadorDados()
        dados_invalidos = {"id": "test_123"}  # Dados incompletos
        
        # Act & Assert
        with pytest.raises(ValueError, match="Dados incompletos"):
            processador.processar(dados_invalidos)

# Testes de Integração
class TestIntegracaoAPI:
    """Testes de integração com a API."""
    
    def test_obter_dados(self, config_teste: Dict[str, Any], mock_api: Mock) -> None:
        """
        Testa a obtenção de dados da API.
        
        Args:
            config_teste: Fixture com configurações
            mock_api: Fixture com mock da API
        """
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"status": "success", "data": []}
        mock_api.return_value.get.return_value = mock_response
        
        # Act
        cliente = APIClient(config_teste)
        resultado = cliente.obter_dados()
        
        # Assert
        assert resultado["status"] == "success"
        mock_api.return_value.get.assert_called_once_with(
            f"{config_teste['api_url']}/dados"
        )
    
    @pytest.mark.timeout(5)  # Timeout de 5 segundos
    def test_timeout_api(self, config_teste: Dict[str, Any], mock_api: Mock) -> None:
        """
        Testa o timeout da API.
        
        Args:
            config_teste: Fixture com configurações
            mock_api: Fixture com mock da API
        """
        # Arrange
        mock_api.return_value.get.side_effect = TimeoutError()
        
        # Act & Assert
        cliente = APIClient(config_teste)
        with pytest.raises(TimeoutError):
            cliente.obter_dados()

# Classes auxiliares para os testes
class ProcessadorDados:
    """Classe auxiliar para processamento de dados."""
    
    def processar(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa os dados recebidos.
        
        Args:
            dados: Dados a serem processados
            
        Returns:
            Dict[str, Any]: Dados processados
            
        Raises:
            ValueError: Se os dados estiverem incompletos
        """
        if not all(k in dados for k in ["id", "nome", "data", "status"]):
            raise ValueError("Dados incompletos")
            
        return {
            **dados,
            "status": "processado",
            "timestamp": datetime.now().isoformat()
        }

class APIClient:
    """Cliente para integração com API."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o cliente.
        
        Args:
            config: Configurações do cliente
        """
        self.config = config
        self.session = requests.Session()
    
    def obter_dados(self) -> Dict[str, Any]:
        """
        Obtém dados da API.
        
        Returns:
            Dict[str, Any]: Dados obtidos
            
        Raises:
            TimeoutError: Se a requisição exceder o timeout
        """
        response = self.session.get(f"{self.config['api_url']}/dados")
        return response.json() 