"""
Testes para o módulo de visualização 4D.
"""

import unittest
from datetime import datetime, timedelta
from ..visualizacao_4d import Visualizacao4D, Dimensao4D

class TestVisualizacao4D(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para os testes."""
        self.visualizador = Visualizacao4D({})
        self.dados_teste = {
            "performance": [
                Dimensao4D("performance", 0.8, datetime.now(), {"host": "server1"}),
                Dimensao4D("performance", 0.9, datetime.now(), {"host": "server1"}),
                Dimensao4D("performance", 0.7, datetime.now(), {"host": "server1"})
            ],
            "saude": [
                Dimensao4D("saude", 0.95, datetime.now(), {"host": "server1"}),
                Dimensao4D("saude", 0.98, datetime.now(), {"host": "server1"}),
                Dimensao4D("saude", 0.92, datetime.now(), {"host": "server1"})
            ]
        }
        
        # Adiciona dados de teste
        for dimensao in self.dados_teste["performance"]:
            self.visualizador.atualizar_dimensao(
                dimensao.nome,
                dimensao.valor,
                dimensao.contexto
            )
        
        for dimensao in self.dados_teste["saude"]:
            self.visualizador.atualizar_dimensao(
                dimensao.nome,
                dimensao.valor,
                dimensao.contexto
            )

    def test_atualizar_dimensao(self):
        """Testa a atualização de dimensões."""
        nome = "teste"
        valor = 0.5
        contexto = {"test": True}
        
        self.visualizador.atualizar_dimensao(nome, valor, contexto)
        dimensoes = self.visualizador.obter_dimensao(nome)
        
        self.assertEqual(len(dimensoes), 1)
        self.assertEqual(dimensoes[0].nome, nome)
        self.assertEqual(dimensoes[0].valor, valor)
        self.assertEqual(dimensoes[0].contexto, contexto)

    def test_obter_dimensao(self):
        """Testa a obtenção de dimensões."""
        dimensoes = self.visualizador.obter_dimensao("performance")
        
        self.assertEqual(len(dimensoes), 3)
        self.assertTrue(all(d.nome == "performance" for d in dimensoes))
        
        # Teste com período
        periodo = timedelta(minutes=1)
        dimensoes = self.visualizador.obter_dimensao("performance", periodo)
        self.assertEqual(len(dimensoes), 3)

    def test_calcular_estatisticas(self):
        """Testa o cálculo de estatísticas."""
        estatisticas = self.visualizador.calcular_estatisticas("performance")
        
        self.assertIn("media", estatisticas)
        self.assertIn("mediana", estatisticas)
        self.assertIn("desvio_padrao", estatisticas)
        self.assertIn("min", estatisticas)
        self.assertIn("max", estatisticas)
        
        self.assertEqual(estatisticas["min"], 0.7)
        self.assertEqual(estatisticas["max"], 0.9)

    def test_detectar_anomalias(self):
        """Testa a detecção de anomalias."""
        # Adiciona uma anomalia
        self.visualizador.atualizar_dimensao(
            "performance",
            2.0,  # Valor anormalmente alto
            {"host": "server1"}
        )
        
        anomalias = self.visualizador.detectar_anomalias("performance")
        
        self.assertTrue(len(anomalias) > 0)
        self.assertIn("timestamp", anomalias[0])
        self.assertIn("valor", anomalias[0])
        self.assertIn("z_score", anomalias[0])
        self.assertIn("contexto", anomalias[0])

    def test_calcular_correlacoes(self):
        """Testa o cálculo de correlações."""
        correlacao = self.visualizador.calcular_correlacoes("performance", "saude")
        
        self.assertIsInstance(correlacao, float)
        self.assertTrue(-1 <= correlacao <= 1)

    def test_gerar_matriz_correlacao(self):
        """Testa a geração da matriz de correlação."""
        matriz = self.visualizador.gerar_matriz_correlacao()
        
        self.assertIn("performance", matriz)
        self.assertIn("saude", matriz)
        self.assertIn("performance", matriz["performance"])
        self.assertIn("saude", matriz["performance"])
        
        # Correlação de uma dimensão com ela mesma deve ser 1
        self.assertEqual(matriz["performance"]["performance"], 1.0)
        self.assertEqual(matriz["saude"]["saude"], 1.0)

    def test_detectar_tendencias(self):
        """Testa a detecção de tendências."""
        # Adiciona dados com tendência crescente
        for i in range(10):
            self.visualizador.atualizar_dimensao(
                "tendencia",
                i * 0.1,
                {"test": True}
            )
        
        tendencias = self.visualizador.detectar_tendencias("tendencia")
        
        self.assertIn("inclinacao", tendencias)
        self.assertIn("intercepto", tendencias)
        self.assertIn("r2", tendencias)
        self.assertIn("tendencia", tendencias)
        
        self.assertGreater(tendencias["inclinacao"], 0)
        self.assertEqual(tendencias["tendencia"], "crescente")

    def test_gerar_relatorio(self):
        """Testa a geração de relatório."""
        relatorio = self.visualizador.gerar_relatorio()
        
        self.assertIn("timestamp", relatorio)
        self.assertIn("dimensoes", relatorio)
        self.assertIn("metricas", relatorio)
        self.assertIn("anomalias", relatorio)
        
        self.assertIn("performance", relatorio["dimensoes"])
        self.assertIn("saude", relatorio["dimensoes"])

    def test_limpar_dados_antigos(self):
        """Testa a limpeza de dados antigos."""
        # Adiciona dados antigos
        self.visualizador.atualizar_dimensao(
            "teste",
            0.5,
            {"test": True}
        )
        
        # Força timestamp antigo
        self.visualizador.dimensoes["teste"][-1].timestamp = datetime.now() - timedelta(days=1)
        
        # Limpa dados mais antigos que 12 horas
        self.visualizador.limpar_dados_antigos(timedelta(hours=12))
        
        dimensoes = self.visualizador.obter_dimensao("teste")
        self.assertEqual(len(dimensoes), 0)

if __name__ == '__main__':
    unittest.main() 