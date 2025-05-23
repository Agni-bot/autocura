import numpy as np # Para cálculo de IRR e NPV se necessário

class ROICalculator:
    def __init__(self):
        """Inicializa a Calculadora de ROI."""
        print("[ROICalculator] Calculadora de ROI inicializada.")

    def _find_payback_period_years(self, initial_investment: float, annual_cash_flows: list[float]) -> float | str:
        """Calcula o período de payback em anos.

        Args:
            initial_investment (float): O investimento inicial (deve ser positivo).
            annual_cash_flows (list[float]): Lista dos fluxos de caixa anuais esperados (positivos).

        Returns:
            float: Período de payback em anos, ou uma string indicando que não há payback.
        """
        if initial_investment <= 0:
            return "Investimento inicial deve ser positivo."
        if not annual_cash_flows or all(cf <= 0 for cf in annual_cash_flows):
            return "Fluxos de caixa anuais devem ser fornecidos e pelo menos um deve ser positivo."

        cumulative_cash_flow = 0.0
        for i, cash_flow in enumerate(annual_cash_flows):
            cumulative_cash_flow += cash_flow
            if cumulative_cash_flow >= initial_investment:
                # Payback ocorre neste ano
                # Se o fluxo de caixa do ano anterior não cobriu, calcula a fração do ano atual
                if i == 0: # Payback no primeiro ano
                    return initial_investment / cash_flow if cash_flow > 0 else float('inf')
                
                # (Investimento - Acumulado até ano anterior) / Fluxo do ano atual
                payback_fraction = (initial_investment - (cumulative_cash_flow - cash_flow)) / cash_flow if cash_flow > 0 else float('inf')
                return i + payback_fraction
        
        return "Payback não ocorre dentro do período dos fluxos de caixa fornecidos."

    def _calculate_npv(self, initial_investment: float, annual_cash_flows: list[float], discount_rate: float) -> float:
        """Calcula o Valor Presente Líquido (NPV).
        
        Args:
            initial_investment (float): O investimento inicial.
            annual_cash_flows (list[float]): Lista dos fluxos de caixa anuais.
            discount_rate (float): Taxa de desconto anual (ex: 0.10 para 10%).

        Returns:
            float: O valor do NPV.
        """
        npv = -initial_investment
        for i, cash_flow in enumerate(annual_cash_flows):
            npv += cash_flow / ((1 + discount_rate) ** (i + 1))
        return npv

    def _calculate_irr(self, initial_investment: float, annual_cash_flows: list[float]) -> float | str:
        """Calcula a Taxa Interna de Retorno (IRR) usando numpy.irr.
        Nota: np.irr pode não convergir ou pode dar resultados inesperados para fluxos de caixa não convencionais.
        
        Args:
            initial_investment (float): O investimento inicial.
            annual_cash_flows (list[float]): Lista dos fluxos de caixa anuais.

        Returns:
            float: A IRR como uma porcentagem (ex: 0.15 para 15%), ou uma string em caso de erro.
        """
        cash_flows_for_irr = [-initial_investment] + annual_cash_flows
        try:
            # np.irr retorna a taxa por período. Multiplicamos por 100 para percentual.
            irr = np.irr(cash_flows_for_irr)
            return irr * 100 if not np.isnan(irr) else "Não foi possível calcular IRR (resultado NaN)."
        except Exception as e:
            # Isso pode acontecer se não houver mudança de sinal nos fluxos de caixa, etc.
            print(f"[ROICalculator] Erro ao calcular IRR com numpy: {e}")
            return f"Erro ao calcular IRR: {e}"

    def calculate_roi_metrics(self, investment_name: str, initial_investment: float, annual_savings_or_gains: list[float], discount_rate: float = 0.10) -> dict:
        """Calcula as principais métricas de ROI para um investimento.

        Args:
            investment_name (str): Nome ou descrição do investimento.
            initial_investment (float): Custo inicial do investimento.
            annual_savings_or_gains (list[float]): Lista de economias ou ganhos anuais esperados.
            discount_rate (float, optional): Taxa de desconto anual para cálculo do NPV. Default 0.10 (10%).

        Returns:
            dict: Um dicionário contendo as métricas de ROI calculadas.
        """
        print(f"[ROICalculator] Calculando métricas de ROI para: {investment_name}")
        print(f"  Investimento Inicial: ${initial_investment:.2f}")
        print(f"  Ganhos/Economias Anuais: {annual_savings_or_gains}")
        print(f"  Taxa de Desconto: {discount_rate*100:.2f}%")

        if initial_investment <= 0:
            return {"error": "Investimento inicial deve ser um valor positivo."}
        if not annual_savings_or_gains:
            return {"error": "Lista de ganhos/economias anuais não pode estar vazia."}

        total_gains = sum(annual_savings_or_gains)
        net_profit = total_gains - initial_investment
        
        # ROI Simples ( (Ganhos Totais - Investimento) / Investimento ) * 100%
        simple_roi_percentage = (net_profit / initial_investment) * 100 if initial_investment != 0 else float('inf')
        
        payback_period = self._find_payback_period_years(initial_investment, annual_savings_or_gains)
        npv = self._calculate_npv(initial_investment, annual_savings_or_gains, discount_rate)
        irr = self._calculate_irr(initial_investment, annual_savings_or_gains)

        results = {
            "investment_name": investment_name,
            "initial_investment_usd": round(initial_investment, 2),
            "total_gains_usd": round(total_gains, 2),
            "net_profit_usd": round(net_profit, 2),
            "simple_roi_percentage": round(simple_roi_percentage, 2) if isinstance(simple_roi_percentage, float) else simple_roi_percentage,
            "payback_period_years": payback_period if isinstance(payback_period, str) else round(payback_period, 2),
            "npv_at_discount_rate_usd": round(npv, 2),
            "discount_rate_for_npv_percentage": round(discount_rate * 100, 2),
            "irr_percentage": irr if isinstance(irr, str) else round(irr, 2) # IRR já vem como %
        }
        print(f"[ROICalculator] Métricas de ROI calculadas: {results}")
        return results

# Exemplo de uso
if __name__ == "__main__":
    calculator = ROICalculator()

    print("\n--- Exemplo 1: Adoção de Nova Tecnologia de Software ---")
    investment_cost_sw = 50000  # $50,000
    annual_savings_sw = [15000, 20000, 25000, 25000, 30000] # Economias anuais por 5 anos
    roi_results_sw = calculator.calculate_roi_metrics(
        investment_name="Nova Tecnologia de Software",
        initial_investment=investment_cost_sw,
        annual_savings_or_gains=annual_savings_sw,
        discount_rate=0.08 # Taxa de desconto de 8%
    )
    print("Resultados do ROI para Software:")
    for key, value in roi_results_sw.items():
        print(f"  {key.replace('_', ' ').capitalize()}: {value}")

    print("\n--- Exemplo 2: Campanha de Marketing Digital ---")
    investment_cost_mkt = 20000 # $20,000
    # Ganhos podem ser mais variáveis e de curto prazo
    monthly_gains_mkt = [1000, 1500, 3000, 5000, 6000, 4000, 3000, 2000] # Ganhos por 8 meses
    # Para fins de cálculo anualizado simples, vamos somar e usar como se fosse um ganho anual
    # Em um cenário real, o NPV/IRR seria calculado com fluxos mensais e taxa mensal.
    # Aqui, simplificamos para usar a estrutura anual.
    annual_equivalent_gain_mkt = [sum(monthly_gains_mkt)] # Tratando como um único ganho no primeiro ano
    
    roi_results_mkt = calculator.calculate_roi_metrics(
        investment_name="Campanha de Marketing Digital (Simplificado)",
        initial_investment=investment_cost_mkt,
        annual_savings_or_gains=annual_equivalent_gain_mkt,
        discount_rate=0.12 # Taxa de desconto de 12%
    )
    print("Resultados do ROI para Marketing (Simplificado):")
    for key, value in roi_results_mkt.items():
        print(f"  {key.replace('_', ' ').capitalize()}: {value}")

    print("\n--- Exemplo 3: Investimento sem Payback Claro ---")
    investment_cost_bad = 100000
    annual_savings_bad = [5000, 5000, 5000] # Baixo retorno
    roi_results_bad = calculator.calculate_roi_metrics(
        investment_name="Investimento de Baixo Retorno",
        initial_investment=investment_cost_bad,
        annual_savings_or_gains=annual_savings_bad,
        discount_rate=0.10
    )
    print("Resultados do ROI para Investimento Ruim:")
    for key, value in roi_results_bad.items():
        print(f"  {key.replace('_', ' ').capitalize()}: {value}")
