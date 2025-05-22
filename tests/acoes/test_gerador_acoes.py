"""
Testes unitários para o módulo de geração de ações.
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
from src.services.diagnostico.rede_neural import Diagnostico

@pytest.mark.asyncio
class TestGeradorAcoes(unittest.TestCase):
    """Testes unitários para o GeradorAcoes."""
    
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
    def test_carregar_configuracoes(self, mock_path):
        """Testa carregamento de configurações."""
        # Configura mock para retornar o caminho do arquivo temporário
        mock_path.return_value = self.config_path
        
        # Carrega configurações
        self.gerador._carregar_configuracoes()
        
        # Verifica se configurações foram carregadas
        self.assertEqual(self.gerador.mapeamento_acoes, self.config_exemplo["mapeamento_acoes"])
        self.assertEqual(self.gerador.tempo_estimado_padrao, self.config_exemplo["tempos_padrao"]["tempo_estimado_padrao"])
        self.assertEqual(self.gerador.probabilidade_sucesso_padrao, self.config_exemplo["tempos_padrao"]["probabilidade_sucesso_padrao"])
    
    @patch('src.acoes.gerador_acoes.Path')
    def test_carregar_configuracoes_arquivo_inexistente(self, mock_path):
        """Testa carregamento de configurações com arquivo inexistente."""
        # Configura mock para retornar caminho inexistente
        mock_path.return_value = Path("/caminho/inexistente/config.json")
        
        # Carrega configurações
        self.gerador._carregar_configuracoes()
        
        # Verifica se configurações padrão foram mantidas
        self.assertEqual(self.gerador.mapeamento_acoes, {})
        self.assertEqual(self.gerador.tempo_estimado_padrao, 30.0)
        self.assertEqual(self.gerador.probabilidade_sucesso_padrao, 0.8)
    
    def test_obter_estatisticas_acoes_vazio(self):
        """Testa obtenção de estatísticas com histórico vazio."""
        estatisticas = self.gerador.obter_estatisticas_acoes()
        self.assertEqual(estatisticas["total_acoes"], 0)
        self.assertEqual(estatisticas["acoes_por_tipo"], {})
        self.assertEqual(estatisticas["taxa_sucesso"], 0.0)
    
    def test_obter_estatisticas_acoes_com_dados(self):
        """Testa obtenção de estatísticas com histórico populado."""
        # Adiciona ações ao histórico
        self.gerador.historico_acoes = [
            {"tipo": "alta_cpu", "sucesso": True},
            {"tipo": "alta_cpu", "sucesso": False},
            {"tipo": "alta_memoria", "sucesso": True}
        ]
        
        estatisticas = self.gerador.obter_estatisticas_acoes()
        self.assertEqual(estatisticas["total_acoes"], 3)
        self.assertEqual(estatisticas["acoes_por_tipo"]["alta_cpu"], 2)
        self.assertEqual(estatisticas["acoes_por_tipo"]["alta_memoria"], 1)
        self.assertAlmostEqual(estatisticas["taxa_sucesso"], 0.67, places=2)
    
    def test_plano_acao_calculo_tempo_estimado(self):
        """Testa cálculo de tempo estimado no plano de ação."""
        plano = PlanoAcao(
            acoes=[
                Acao(
                    id="1",
                    tipo=TipoAcao.CRITICA,
                    descricao="Teste 1",
                    prioridade=PrioridadeAcao.ALTA,
                    timestamp=datetime.now(),
                    diagnostico=self.diagnostico_mock,
                    parametros={},
                    status="pendente"
                ),
                Acao(
                    id="2",
                    tipo=TipoAcao.CRITICA,
                    descricao="Teste 2",
                    prioridade=PrioridadeAcao.ALTA,
                    timestamp=datetime.now(),
                    diagnostico=self.diagnostico_mock,
                    parametros={},
                    status="pendente"
                )
            ]
        )
        
        tempo_estimado = plano.calcular_tempo_estimado()
        self.assertEqual(tempo_estimado, 60.0)  # 2 ações * 30.0 segundos
    
    def test_plano_acao_calculo_probabilidade_sucesso(self):
        """Testa cálculo de probabilidade de sucesso no plano de ação."""
        plano = PlanoAcao(
            acoes=[
                Acao(
                    id="1",
                    tipo=TipoAcao.CRITICA,
                    descricao="Teste 1",
                    prioridade=PrioridadeAcao.ALTA,
                    timestamp=datetime.now(),
                    diagnostico=self.diagnostico_mock,
                    parametros={},
                    status="pendente"
                ),
                Acao(
                    id="2",
                    tipo=TipoAcao.CRITICA,
                    descricao="Teste 2",
                    prioridade=PrioridadeAcao.ALTA,
                    timestamp=datetime.now(),
                    diagnostico=self.diagnostico_mock,
                    parametros={},
                    status="pendente"
                )
            ]
        )
        
        probabilidade = plano.calcular_probabilidade_sucesso()
        self.assertAlmostEqual(probabilidade, 0.64, places=2)  # 0.8 * 0.8
    
    def test_gerar_acao_sem_anomalia(self):
        """Testa geração de ação sem anomalia detectada."""
        self.diagnostico_mock.tipo = None
        acao = self.gerador.gerar_acao(self.diagnostico_mock)
        self.assertIsNone(acao)
    
    def test_gerar_acao_padrao_desconhecido(self):
        """Testa geração de ação com padrão desconhecido."""
        self.diagnostico_mock.tipo = "padrao_desconhecido"
        acao = self.gerador.gerar_acao(self.diagnostico_mock)
        self.assertIsNone(acao)
    
    def test_gerar_acao_sucesso(self):
        """Testa geração de ação com sucesso."""
        acao = self.gerador.gerar_acao(self.diagnostico_mock)
        self.assertIsNotNone(acao)
        self.assertEqual(acao.tipo, TipoAcao.ESCALONAMENTO)
        self.assertEqual(acao.prioridade, PrioridadeAcao.ALTA)
        self.assertEqual(acao.parametros["min_replicas"], 2)
        self.assertEqual(acao.parametros["max_replicas"], 5)
        self.assertEqual(acao.parametros["target_cpu"], 70)
    
    async def test_gerar_acoes_async(self):
        """Testa geração assíncrona de ações."""
        acoes = await self.gerador.gerar_acoes_async([self.diagnostico_mock])
        self.assertEqual(len(acoes), 1)
        self.assertIsNotNone(acoes[0])
        self.assertEqual(acoes[0].tipo, TipoAcao.ESCALONAMENTO)
    
    async def test_gerar_plano_acao_async(self):
        """Testa geração assíncrona de plano de ação."""
        plano = await self.gerador.gerar_plano_acao_async([self.diagnostico_mock])
        self.assertIsNotNone(plano)
        self.assertEqual(len(plano.acoes), 1)
        self.assertEqual(plano.acoes[0].tipo, TipoAcao.ESCALONAMENTO)

if __name__ == '__main__':
    unittest.main() 