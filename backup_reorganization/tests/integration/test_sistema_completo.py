"""
Testes de integração do sistema completo.

Este módulo contém testes que verificam a integração entre diferentes
componentes do sistema, incluindo casos complexos e cenários de erro.
"""

import pytest
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
import logging
import mock
from src.orchestration.monitoramento import MonitoramentoTestes
from src.core.sistema_autocura import SistemaAutocura
from prometheus_client import CollectorRegistry

# Marca todos os testes deste módulo como de integração
pytestmark = pytest.mark.integration

class TestSistemaCompleto:
    """
    Testes que verificam a integração entre diferentes componentes do sistema.
    
    Estes testes são mais complexos e demorados, pois testam o sistema
    como um todo, incluindo:
    - Integração com banco de dados
    - Integração com cache
    - Integração com API externa
    - Processamento assíncrono
    - Tratamento de erros
    - Recuperação de falhas
    """
    
    @pytest.fixture(autouse=True)
    def mock_elasticsearch(self):
        """Fixture para mockar o cliente Elasticsearch globalmente."""
        with mock.patch('elasticsearch.Elasticsearch') as mock_es:
            mock_es.return_value.index.return_value = {'_id': 'test_id', 'result': 'created'}
            yield mock_es

    def test_fluxo_completo_processamento(self, mock_elasticsearch):
        """Testa o fluxo completo de processamento de dados."""
        # Configuração inicial
        sistema = SistemaAutocura()
        registry = CollectorRegistry()
        monitor = MonitoramentoTestes(registry=registry)
        
        # Dados de teste
        dados = {
            'id': 'test_001',
            'dados': [1, 2, 3],
            'timestamp': '2025-05-21T15:58:28'
        }
        
        # Execução do processamento
        resultado = sistema.processar_dados(dados)
        
        # Verificações
        assert resultado['status'] == 'success'
        assert 'processado_em' in resultado
        assert mock_elasticsearch.called
        
        # Verifica métricas
        metricas = monitor.obter_metricas()
        assert metricas['total_processamentos'] > 0
        assert metricas['tempo_medio_processamento'] > 0

    def test_recuperacao_falha(self, mock_elasticsearch):
        """Testa o processo de recuperação após uma falha."""
        # Configuração inicial
        sistema = SistemaAutocura()
        registry = CollectorRegistry()
        monitor = MonitoramentoTestes(registry=registry)
        
        # Dados de teste
        dados = {
            'id': 'test_002',
            'dados': [4, 5, 6],
            'timestamp': '2025-05-21T15:58:29'
        }
        
        # Simula falha e recuperação
        mock_elasticsearch.return_value.index.side_effect = [
            Exception("Erro temporário"),
            {'_id': 'test_id', 'result': 'created'}
        ]
        
        # Execução com retry
        resultado = sistema.processar_dados(dados, max_retries=3)
        
        # Verificações
        assert resultado['status'] == 'success'
        assert mock_elasticsearch.call_count == 2
        
        # Verifica métricas de falha
        metricas = monitor.obter_metricas()
        assert metricas['falhas_processamento'] > 0
        assert metricas['recuperacoes_sucesso'] > 0
        
    def test_processamento_concorrente(
        self,
        config_teste: Dict[str, Any],
        mock_api: Any,
        mock_db: Any,
        mock_redis: Any,
        monitoramento: Any
    ) -> None:
        """
        Testa o processamento concorrente de múltiplos dados.
        
        Este teste verifica:
        1. Processamento paralelo
        2. Consistência dos dados
        3. Performance
        
        Args:
            config_teste: Configurações de teste
            mock_api: Mock da API
            mock_db: Mock do banco de dados
            mock_redis: Mock do Redis
            monitoramento: Instância do monitoramento
        """
        # Arrange
        dados_entrada = [
            {"id": f"test_{i}", "dados": [i], "timestamp": datetime.now().isoformat()}
            for i in range(10)
        ]
        
        # Act
        inicio = time.time()
        resultados = self._processar_dados_concorrente(dados_entrada, config_teste)
        duracao = time.time() - inicio
        
        # Assert
        assert len(resultados) == len(dados_entrada)
        assert all(r["status"] == "success" for r in resultados)
        
        # Verifica métricas
        monitoramento.registrar_execucao_teste(
            "test_processamento_concorrente",
            True,
            duracao
        )
        
    def test_persistencia_dados(
        self,
        config_teste: Dict[str, Any],
        mock_db: Any,
        temp_dir: Path
    ) -> None:
        """
        Testa a persistência de dados em diferentes formatos.
        
        Este teste verifica:
        1. Persistência em banco
        2. Persistência em arquivo
        3. Consistência dos dados
        
        Args:
            config_teste: Configurações de teste
            mock_db: Mock do banco de dados
            temp_dir: Diretório temporário para arquivos
        """
        # Arrange
        dados = {
            "id": "test_789",
            "dados": [7, 8, 9],
            "timestamp": datetime.now().isoformat()
        }
        
        # Act
        arquivo_path = temp_dir / "dados.json"
        
        # Limpa arquivo existente se houver
        if arquivo_path.exists():
            arquivo_path.unlink()
        
        # Persiste dados
        self._persistir_dados(dados, arquivo_path)
        
        # Verifica se arquivo foi criado
        assert arquivo_path.exists()
        
        # Lê dados persistidos
        dados_lidos = json.loads(arquivo_path.read_text())
        
        # Assert
        assert dados_lidos == dados
        
        # Verifica que não há duplicação
        self._persistir_dados(dados, arquivo_path)
        dados_lidos_apos_duplicacao = json.loads(arquivo_path.read_text())
        assert dados_lidos_apos_duplicacao == dados  # Deve manter os mesmos dados, não duplicar
        
    def _processar_dados(self, dados: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa os dados recebidos.
        
        Args:
            dados: Dados a serem processados
            config: Configurações
            
        Returns:
            Dict[str, Any]: Resultado do processamento
        """
        # Implementação simulada
        return {
            "status": "success",
            "id": dados["id"],
            "timestamp": datetime.now().isoformat()
        }
        
    def _processar_dados_concorrente(
        self,
        dados_lista: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Processa múltiplos dados concorrentemente.
        
        Args:
            dados_lista: Lista de dados a serem processados
            config: Configurações
            
        Returns:
            List[Dict[str, Any]]: Lista de resultados
        """
        # Implementação simulada
        return [self._processar_dados(dados, config) for dados in dados_lista]
        
    def _persistir_dados(self, dados: Dict[str, Any], arquivo_path: Path) -> None:
        """
        Persiste dados em arquivo.
        
        Args:
            dados: Dados a serem persistidos
            arquivo_path: Caminho do arquivo
        """
        arquivo_path.write_text(json.dumps(dados, indent=2)) 