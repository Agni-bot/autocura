import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor
from src.core.sistema_autocura import SistemaAutocura

class TesteAlocacaoRecursos:
    @pytest.fixture
    def sistema(self):
        return SistemaAutocura()
        
    @pytest.mark.asyncio
    async def test_alocacao_massiva(self, sistema):
        """Testa alocação de recursos sob carga pesada"""
        # Simula 500 workers concorrentes
        with ThreadPoolExecutor(max_workers=500) as executor:
            futures = []
            for i in range(500):
                futures.append(executor.submit(
                    lambda: sistema.recursos.update({f'worker_{i}': 1.0})
                ))
                
            # Aguarda todas as alocações
            for future in futures:
                future.result()
                
        # Verifica equidade
        equidade = sistema._calcular_equidade()
        assert equidade >= 0.8, f"Equidade muito baixa: {equidade}"
        
    @pytest.mark.asyncio
    async def test_monitoramento_continuo(self, sistema):
        """Testa monitoramento contínuo por 5 segundos"""
        # Inicia monitoramento em background
        monitor_task = asyncio.create_task(sistema.monitorar_recursos())
        
        # Aguarda 5 segundos
        await asyncio.sleep(5)
        
        # Cancela monitoramento
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
            
        # Verifica histórico
        assert len(sistema.historico) > 0, "Histórico vazio"
        ultimas_metricas = sistema.historico[-1]['metricas']
        assert 'cpu' in ultimas_metricas
        assert 'memoria' in ultimas_metricas
        assert 'equidade' in ultimas_metricas
        
    @pytest.mark.asyncio
    async def test_ajuste_automatico(self, sistema):
        """Testa ajuste automático quando equidade cai"""
        # Simula distribuição desigual
        sistema.recursos = {
            'worker_1': 90.0,
            'worker_2': 10.0
        }
        # Força verificação de limites
        await sistema.verificar_limites()
        # Verifica se ajuste foi acionado
        print(f"[TESTE] recursos: {sistema.recursos}")
        print(f"[TESTE] historico: {sistema.historico}")
        assert len(sistema.historico) > 0
        ultima_equidade = sistema.historico[-1]['metricas']['equidade']
        print(f"[TESTE] ultima_equidade: {ultima_equidade}")
        assert ultima_equidade > 0.85, f"Equidade não melhorou: {ultima_equidade}" 