"""
Testes de integração para o módulo de ações.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from pathlib import Path
import json
import tempfile
import os
import pytest

from src.acoes.gerador_acoes import (
    GeradorAcoes,
    Acao,
    PlanoAcao,
    TipoAcao,
    PrioridadeAcao
)
from src.core.acoes_correcao import (
    GerenciadorAcoes,
    StatusAcao
)
from src.services.diagnostico.rede_neural import Diagnostico

@pytest.mark.asyncio
class TestIntegracaoAcoes(unittest.TestCase):
    """Testes de integração para o módulo de ações."""
    
    def setUp(self):
        """Configuração inicial dos testes."""
        # Cria um arquivo de configuração temporário
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "acoes_config.json"
        
        # Configuração de exemplo
        self.config_exemplo = {
            "mapeamento_acoes": {
                "alta_cpu": {
                    "tipo": "escalar_horizontal",
                    "descricao": "Escalar horizontalmente para distribuir carga",
                    "prioridade": 2,
                    "parametros": {
                        "min_replicas": 2,
                        "max_replicas": 5,
                        "target_cpu": 70
                    }
                }
            },
            "tempos_padrao": {
                "tempo_estimado_padrao": 30.0,
                "probabilidade_sucesso_padrao": 0.8
            }
        }
        
        # Salva configuração temporária
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config_exemplo, f)
        
        # Inicializa mocks
        self.memoria_mock = AsyncMock()
        self.memoria_mock.salvar_acao = AsyncMock()
        self.memoria_mock.atualizar_acao = AsyncMock()
        self.memoria_mock.obter_acao = AsyncMock()
        
        # Inicializa componentes
        self.gerador = GeradorAcoes()
        self.gerador.memoria = self.memoria_mock
        self.gerador.mapeamento_acoes = self.config_exemplo["mapeamento_acoes"]
        self.gerador.tempo_estimado_padrao = self.config_exemplo["tempos_padrao"]["tempo_estimado_padrao"]
        self.gerador.probabilidade_sucesso_padrao = self.config_exemplo["tempos_padrao"]["probabilidade_sucesso_padrao"]
        
        self.gerenciador = GerenciadorAcoes()
        self.gerenciador.memoria = self.memoria_mock
        
        # Mock do Diagnostico
        self.diagnostico_mock = MagicMock(spec=Diagnostico)
        self.diagnostico_mock.tipo = "alta_cpu"
        self.diagnostico_mock.parametros = {"cpu_usage": 90}
    
    def tearDown(self):
        """Limpeza após os testes."""
        # Remove arquivo temporário
        os.remove(self.config_path)
        os.rmdir(self.temp_dir)
    
    @patch('src.acoes.gerador_acoes.Path')
    async def test_fluxo_completo_acao(self, mock_path):
        """Testa fluxo completo de geração, execução e finalização de ação."""
        # Configura mock para retornar o caminho do arquivo temporário
        mock_path.return_value = self.config_path
        
        # Gera ação
        acao = self.gerador.gerar_acao(self.diagnostico_mock)
        self.assertIsNotNone(acao)
        
        # Cria ação no gerenciador
        acao_id = await self.gerenciador.criar_acao_async(acao)
        self.assertIsNotNone(acao_id)
        
        # Verifica se ação foi salva
        self.memoria_mock.salvar_acao.assert_called_once()
        
        # Executa ação
        sucesso = await self.gerenciador.executar_acao_async(acao_id)
        self.assertTrue(sucesso)
        
        # Verifica se ação foi atualizada
        self.memoria_mock.atualizar_acao.assert_called()
        
        # Finaliza ação
        sucesso = await self.gerenciador.finalizar_acao_async(acao_id, {"resultado": "sucesso"})
        self.assertTrue(sucesso)
        
        # Verifica se ação foi atualizada com resultado
        self.memoria_mock.atualizar_acao.assert_called()
    
    @patch('src.acoes.gerador_acoes.Path')
    async def test_fluxo_acao_nao_encontrada(self, mock_path):
        """Testa fluxo quando ação não é encontrada."""
        # Configura mock para retornar o caminho do arquivo temporário
        mock_path.return_value = self.config_path
        
        # Tenta executar ação inexistente
        sucesso = await self.gerenciador.executar_acao_async("acao_inexistente")
        self.assertFalse(sucesso)
        
        # Tenta finalizar ação inexistente
        sucesso = await self.gerenciador.finalizar_acao_async("acao_inexistente", {})
        self.assertFalse(sucesso)
        
        # Tenta validar ação inexistente
        sucesso = await self.gerenciador.validar_acao_async("acao_inexistente")
        self.assertFalse(sucesso)
    
    @patch('src.acoes.gerador_acoes.Path')
    async def test_fluxo_acao_invalida(self, mock_path):
        """Testa fluxo com ação inválida."""
        # Configura mock para retornar o caminho do arquivo temporário
        mock_path.return_value = self.config_path
        
        # Tenta criar ação com tipo inválido
        acao_invalida = Acao(
            id="1",
            tipo=None,  # Tipo inválido
            descricao="Teste inválido",
            prioridade=PrioridadeAcao.ALTA,
            timestamp=datetime.now(),
            diagnostico=self.diagnostico_mock,
            parametros={},
            status="pendente"
        )
        
        acao_id = await self.gerenciador.criar_acao_async(acao_invalida)
        self.assertIsNone(acao_id)
        
        # Tenta criar ação com descrição vazia
        acao_invalida = Acao(
            id="2",
            tipo=TipoAcao.CRITICA,
            descricao="",  # Descrição vazia
            prioridade=PrioridadeAcao.ALTA,
            timestamp=datetime.now(),
            diagnostico=self.diagnostico_mock,
            parametros={},
            status="pendente"
        )
        
        acao_id = await self.gerenciador.criar_acao_async(acao_invalida)
        self.assertIsNone(acao_id)
    
    @patch('src.acoes.gerador_acoes.Path')
    async def test_fluxo_acao_com_falha(self, mock_path):
        """Testa fluxo de ação que falha."""
        # Configura mock para retornar o caminho do arquivo temporário
        mock_path.return_value = self.config_path
        
        # Gera ação
        acao = self.gerador.gerar_acao(self.diagnostico_mock)
        self.assertIsNotNone(acao)
        
        # Cria ação no gerenciador
        acao_id = await self.gerenciador.criar_acao_async(acao)
        self.assertIsNotNone(acao_id)
        
        # Configura mock para simular falha
        self.memoria_mock.obter_acao.return_value = {
            "id": acao_id,
            "status": StatusAcao.FALHA,
            "resultado": {"erro": "Falha na execução"}
        }
        
        # Finaliza ação com falha
        sucesso = await self.gerenciador.finalizar_acao_async(acao_id, {"erro": "Falha na execução"})
        self.assertTrue(sucesso)
        
        # Verifica se ação foi atualizada com status de falha
        self.memoria_mock.atualizar_acao.assert_called()
        ultima_chamada = self.memoria_mock.atualizar_acao.call_args[0][1]
        self.assertEqual(ultima_chamada["status"], StatusAcao.FALHA)

if __name__ == '__main__':
    unittest.main() 