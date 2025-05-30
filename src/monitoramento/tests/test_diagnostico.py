"""
Testes para o sistema de diagnóstico.
"""

import unittest
from datetime import datetime
from ..diagnostico import (
    SistemaDiagnostico,
    Problema,
    StatusDiagnostico,
    Severidade
)

class TestSistemaDiagnostico(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para os testes."""
        self.sistema = SistemaDiagnostico()
        self.metricas_teste = {
            'cpu_uso': 95,
            'memoria_uso': 90,
            'latencia_media': 1500
        }

    def test_analise_metricas(self):
        """Testa a análise de métricas."""
        problemas = self.sistema.analisar_metricas(self.metricas_teste)
        
        self.assertIsInstance(problemas, list)
        self.assertTrue(len(problemas) > 0)
        
        for problema in problemas:
            self.assertIsInstance(problema, Problema)
            self.assertIsInstance(problema.id, str)
            self.assertIsInstance(problema.titulo, str)
            self.assertIsInstance(problema.descricao, str)
            self.assertIsInstance(problema.causa_raiz, str)
            self.assertIsInstance(problema.recomendacoes, list)
            self.assertIsInstance(problema.timestamp, datetime)
            self.assertIsInstance(problema.status, StatusDiagnostico)
            self.assertIsInstance(problema.severidade, Severidade)
            self.assertIsInstance(problema.componentes_afetados, list)
            self.assertIsInstance(problema.metricas, dict)
            self.assertIsInstance(problema.logs, list)
            self.assertIsInstance(problema.metadata, dict)

    def test_registro_problema(self):
        """Testa o registro de problemas."""
        problemas = self.sistema.analisar_metricas(self.metricas_teste)
        
        for problema in problemas:
            self.sistema.registrar_problema(problema)
            problema_registrado = self.sistema.obter_problema(problema.id)
            
            self.assertIsNotNone(problema_registrado)
            self.assertEqual(problema_registrado.id, problema.id)
            self.assertEqual(problema_registrado.titulo, problema.titulo)

    def test_listar_problemas(self):
        """Testa a listagem de problemas com filtros."""
        problemas = self.sistema.analisar_metricas(self.metricas_teste)
        
        for problema in problemas:
            self.sistema.registrar_problema(problema)
            
        # Teste sem filtros
        todos_problemas = self.sistema.listar_problemas()
        self.assertEqual(len(todos_problemas), len(problemas))
        
        # Teste com filtro de status
        problemas_ativos = self.sistema.listar_problemas(status=StatusDiagnostico.ATIVO)
        self.assertTrue(all(p.status == StatusDiagnostico.ATIVO for p in problemas_ativos))
        
        # Teste com filtro de severidade
        problemas_alta = self.sistema.listar_problemas(severidade=Severidade.ALTA)
        self.assertTrue(all(p.severidade == Severidade.ALTA for p in problemas_alta))

    def test_historico(self):
        """Testa o histórico de problemas."""
        problemas = self.sistema.analisar_metricas(self.metricas_teste)
        
        for problema in problemas:
            self.sistema.registrar_problema(problema)
            
        historico = self.sistema.obter_historico()
        self.assertEqual(len(historico), len(problemas))
        
        for registro in historico:
            self.assertIn('id', registro)
            self.assertIn('timestamp', registro)
            self.assertIn('tipo', registro)
            self.assertIn('severidade', registro)
            self.assertIn('status', registro)

    def test_atualizar_status(self):
        """Testa a atualização de status de problemas."""
        problemas = self.sistema.analisar_metricas(self.metricas_teste)
        
        for problema in problemas:
            self.sistema.registrar_problema(problema)
            self.sistema.atualizar_status(problema.id, StatusDiagnostico.RESOLVIDO)
            
            problema_atualizado = self.sistema.obter_problema(problema.id)
            self.assertEqual(problema_atualizado.status, StatusDiagnostico.RESOLVIDO)

    def test_adicionar_recomendacao(self):
        """Testa a adição de recomendações."""
        problemas = self.sistema.analisar_metricas(self.metricas_teste)
        
        for problema in problemas:
            self.sistema.registrar_problema(problema)
            recomendacao_original = len(problema.recomendacoes)
            
            self.sistema.adicionar_recomendacao(problema.id, "Nova recomendação de teste")
            
            problema_atualizado = self.sistema.obter_problema(problema.id)
            self.assertEqual(len(problema_atualizado.recomendacoes), recomendacao_original + 1)
            self.assertIn("Nova recomendação de teste", problema_atualizado.recomendacoes)

    def test_adicionar_log(self):
        """Testa a adição de logs."""
        problemas = self.sistema.analisar_metricas(self.metricas_teste)
        
        for problema in problemas:
            self.sistema.registrar_problema(problema)
            logs_originais = len(problema.logs)
            
            self.sistema.adicionar_log(problema.id, "Novo log de teste")
            
            problema_atualizado = self.sistema.obter_problema(problema.id)
            self.assertEqual(len(problema_atualizado.logs), logs_originais + 1)
            self.assertIn("Novo log de teste", problema_atualizado.logs)

if __name__ == '__main__':
    unittest.main() 