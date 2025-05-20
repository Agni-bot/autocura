from datetime import datetime, timedelta
import random

class HardwareEvolutionSimulator:
    def _gpu_cost_model(self, years_from_now: int) -> float:
        """Simula o custo de uma GPU ao longo do tempo.
        Assume uma queda de preço inicial e depois estabilização com pequenas flutuações.
        Este é um modelo muito simplificado.
        """
        base_cost = 700  # Custo base de uma GPU de referência hoje
        if years_from_now == 0:
            return base_cost
        elif years_from_now == 1:
            return base_cost * 0.8  # Queda no primeiro ano com novos modelos
        elif years_from_now <= 5:
            # Estabilização com leve tendência de queda
            return base_cost * (0.8 - (years_from_now - 1) * 0.05) * random.uniform(0.95, 1.05)
        else:
            # Aumento gradual devido à inflação ou escassez de modelos mais antigos
            return base_cost * (0.8 - 4 * 0.05 + (years_from_now - 5) * 0.02) * random.uniform(0.98, 1.02)

    def _moores_law(self, years_from_now: int, initial_performance: float = 1.0) -> float:
        """Simula o aumento de performance baseado na Lei de Moore (dobrando a cada 2 anos).
        Retorna um multiplicador de performance em relação ao inicial.
        """
        # A Lei de Moore tradicionalmente se refere a transistores, mas aplicamos aqui para performance.
        doubling_period_years = 2
        performance_multiplier = 2 ** (years_from_now / doubling_period_years)
        return initial_performance * performance_multiplier * random.uniform(0.9, 1.1) # Adiciona alguma variabilidade

    def simulate_hardware_scenario(self, years: int):
        """Projeta custo/desempenho de hardware (ex: GPUs NVIDIA)"""
        current_year = datetime.now().year
        projected_year = current_year + years
        
        projected_cost = self._gpu_cost_model(years)
        projected_performance_multiplier = self._moores_law(years)
        
        print(f"[HardwareEvolutionSimulator] Simulando cenário para o ano: {projected_year}")
        print(f"[HardwareEvolutionSimulator] Custo projetado da GPU: ${projected_cost:.2f}")
        print(f"[HardwareEvolutionSimulator] Multiplicador de performance projetado: {projected_performance_multiplier:.2f}x")
        
        return {
            'ano': projected_year,
            'custo_projetado_gpu_usd': round(projected_cost, 2),
            'performance_multiplicador': round(projected_performance_multiplier, 2)
        }

# Exemplo de uso (pode ser removido ou comentado em produção)
if __name__ == '__main__':
    simulator = HardwareEvolutionSimulator()
    
    print("--- Simulação para 1 ano no futuro ---")
    scenario_1_ano = simulator.simulate_hardware_scenario(years=1)
    print(scenario_1_ano)
    
    print("\n--- Simulação para 3 anos no futuro ---")
    scenario_3_anos = simulator.simulate_hardware_scenario(years=3)
    print(scenario_3_anos)

    print("\n--- Simulação para 5 anos no futuro ---")
    scenario_5_anos = simulator.simulate_hardware_scenario(years=5)
    print(scenario_5_anos)

    print("\n--- Simulação para 10 anos no futuro ---")
    scenario_10_anos = simulator.simulate_hardware_scenario(years=10)
    print(scenario_10_anos)
