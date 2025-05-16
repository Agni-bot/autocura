from prometheus_client import start_http_server, Gauge, Counter, Summary
import random
import time

# --- Definição das Métricas --- 
# Usaremos Gauge para valores que podem aumentar ou diminuir, Counter para valores que só aumentam,
# e Summary para observar durações de eventos ou tamanhos de payloads.

# Métricas de Previsão de Demanda (do módulo futuro/predictive_engine)
PREDICTED_FAILURE_PROBABILITY = Gauge(
    "autocura_predicted_failure_probability",
    "Probabilidade de falha prevista pelo DemandPredictor",
    ["horizon"] # Label para distinguir curto, médio, longo prazo
)

# Métricas de Simulação de Cenários (do módulo futuro/scenario_simulator)
HARDWARE_PROJECTED_COST_GPU_USD = Gauge(
    "autocura_hardware_projected_cost_gpu_usd",
    "Custo projetado de GPU em USD pelo HardwareEvolutionSimulator",
    ["projected_year"]
)
HARDWARE_PROJECTED_PERFORMANCE_MULTIPLIER = Gauge(
    "autocura_hardware_projected_performance_multiplier",
    "Multiplicador de performance projetado pelo HardwareEvolutionSimulator",
    ["projected_year"]
)

# Métricas de Tecnologias Emergentes (ex: sandbox_manager)
ACTIVE_SANDBOXES_COUNT = Gauge(
    "autocura_active_sandboxes_count",
    "Número de sandboxes de tecnologias emergentes ativos"
)
SANDBOX_CREATION_TIME_SECONDS = Summary(
    "autocura_sandbox_creation_time_seconds",
    "Tempo gasto para criar um sandbox de tecnologia emergente"
)
SANDBOX_ERRORS_TOTAL = Counter(
    "autocura_sandbox_errors_total",
    "Contador de erros durante operações de sandbox",
    ["operation"] # Labels: create, execute, destroy
)

# Métricas de Finanças (ex: forex_trader, crowdfunding_integrator, risk_manager)
FOREX_TRADES_EXECUTED_TOTAL = Counter(
    "autocura_forex_trades_executed_total",
    "Número total de trades de Forex executados",
    ["symbol", "operation_type", "status"] # Labels: EURUSD, buy/sell, success/failure
)
FOREX_CURRENT_PRICE = Gauge(
    "autocura_forex_current_price",
    "Preço atual de um par de moedas no Forex",
    ["symbol"]
)
CROWDFUNDING_PROJECTS_FOUND_TOTAL = Gauge(
    "autocura_crowdfunding_projects_found_total",
    "Número de projetos de crowdfunding encontrados por uma busca",
    ["query"]
)
RISK_MANAGER_PORTFOLIO_VALUE_USD = Gauge(
    "autocura_risk_manager_portfolio_value_usd",
    "Valor atual do portfólio gerenciado pelo RiskManager"
)
RISK_MANAGER_OPEN_RISK_USD = Gauge(
    "autocura_risk_manager_open_risk_usd",
    "Risco total em aberto no portfólio gerenciado pelo RiskManager"
)

# Métricas de ROI (do módulo planejamento/roi_calculator)
ROI_CALCULATION_COUNT_TOTAL = Counter(
    "autocura_roi_calculation_count_total",
    "Número total de cálculos de ROI realizados",
    ["investment_name"]
)
INVESTMENT_NPV_USD = Gauge(
    "autocura_investment_npv_usd",
    "Valor Presente Líquido (NPV) calculado para um investimento",
    ["investment_name"]
)
INVESTMENT_IRR_PERCENTAGE = Gauge(
    "autocura_investment_irr_percentage",
    "Taxa Interna de Retorno (IRR) calculada para um investimento",
    ["investment_name"]
)

# --- Funções para Atualizar Métricas (Exemplos) ---
# Estas funções seriam chamadas pelos respectivos módulos quando eventos ocorressem.

def update_predicted_failure_probability(horizon: str, probability: float):
    PREDICTED_FAILURE_PROBABILITY.labels(horizon=horizon).set(probability)
    print(f"[MetricsExporter] Métrica PREDICTED_FAILURE_PROBABILITY atualizada: horizon={horizon}, value={probability}")

def update_hardware_projection(year: int, cost: float, performance_multiplier: float):
    HARDWARE_PROJECTED_COST_GPU_USD.labels(projected_year=str(year)).set(cost)
    HARDWARE_PROJECTED_PERFORMANCE_MULTIPLIER.labels(projected_year=str(year)).set(performance_multiplier)
    print(f"[MetricsExporter] Métricas HARDWARE_PROJECTION atualizadas para o ano {year}")

def increment_active_sandboxes():
    ACTIVE_SANDBOXES_COUNT.inc()
    print(f"[MetricsExporter] Métrica ACTIVE_SANDBOXES_COUNT incrementada.")

def decrement_active_sandboxes():
    ACTIVE_SANDBOXES_COUNT.dec()
    print(f"[MetricsExporter] Métrica ACTIVE_SANDBOXES_COUNT decrementada.")

@SANDBOX_CREATION_TIME_SECONDS.time()
def record_sandbox_creation_time():
    # Esta função seria envolvida por um decorador ou chamada com start/end time
    # Exemplo: com SANDBOX_CREATION_TIME_SECONDS.time():
    #            time.sleep(random.random()) # Simula tempo de criação
    print(f"[MetricsExporter] Tempo de criação de sandbox registrado (simulado).")
    time.sleep(random.uniform(0.1, 0.5)) # Simula o tempo que a operação levou

def increment_sandbox_error(operation_type: str):
    SANDBOX_ERRORS_TOTAL.labels(operation=operation_type).inc()
    print(f"[MetricsExporter] Métrica SANDBOX_ERRORS_TOTAL incrementada para operação: {operation_type}")

def record_forex_trade(symbol: str, operation: str, status: str):
    FOREX_TRADES_EXECUTED_TOTAL.labels(symbol=symbol, operation_type=operation, status=status).inc()
    print(f"[MetricsExporter] Métrica FOREX_TRADES_EXECUTED_TOTAL incrementada: {symbol}, {operation}, {status}")

def update_forex_price(symbol: str, price: float):
    FOREX_CURRENT_PRICE.labels(symbol=symbol).set(price)
    print(f"[MetricsExporter] Métrica FOREX_CURRENT_PRICE atualizada: {symbol}, {price}")

# ... e assim por diante para as outras métricas ...

class MetricsExporter:
    def __init__(self, prometheus_port=9090):
        """Inicializa o exportador de métricas para Prometheus."""
        self.port = prometheus_port
        print(f"[MetricsExporter] Exportador de Métricas inicializado. Tentando iniciar servidor na porta {self.port}")
        try:
            start_http_server(self.port)
            print(f"[MetricsExporter] Servidor HTTP do Prometheus iniciado na porta {self.port}")
            self.running = True
        except Exception as e:
            print(f"[MetricsExporter] Falha ao iniciar o servidor HTTP do Prometheus na porta {self.port}: {e}")
            print("[MetricsExporter] As métricas podem não estar acessíveis via HTTP.")
            self.running = False

    def simulate_metrics_updates(self):
        """Simula a atualização de várias métricas para demonstração."""
        if not self.running:
            print("[MetricsExporter] Servidor Prometheus não está rodando. Simulação de atualização de métricas pulada.")
            return
            
        print("\n[MetricsExporter] Iniciando simulação de atualização de métricas...")
        horizons = ["curto_prazo", "medio_prazo", "longo_prazo"]
        for h in horizons:
            update_predicted_failure_probability(h, random.uniform(0.05, 0.75))
        
        update_hardware_projection(2025, random.uniform(500, 800), random.uniform(1.5, 2.5))
        update_hardware_projection(2030, random.uniform(300, 600), random.uniform(8.0, 12.0))

        increment_active_sandboxes()
        record_sandbox_creation_time()
        if random.random() < 0.1: # Simula um erro ocasional
            increment_sandbox_error("create")
        
        record_forex_trade("EURUSD", "buy", "success")
        update_forex_price("EURUSD", round(1.0850 + random.uniform(-0.0050, 0.0050), 5))
        if random.random() < 0.2:
            record_forex_trade("USDJPY", "sell", "failure")
            increment_sandbox_error("execute") # Reutilizando métrica de erro para exemplo

        # Atualizar métricas de Crowdfunding e RiskManager (simulação)
        CROWDFUNDING_PROJECTS_FOUND_TOTAL.labels(query="IA Verde").set(random.randint(0,10))
        RISK_MANAGER_PORTFOLIO_VALUE_USD.set(random.uniform(90000, 110000))
        RISK_MANAGER_OPEN_RISK_USD.set(random.uniform(1000, 5000))

        # Atualizar métricas de ROI (simulação)
        ROI_CALCULATION_COUNT_TOTAL.labels(investment_name="NovaTecnologiaX").inc()
        INVESTMENT_NPV_USD.labels(investment_name="NovaTecnologiaX").set(random.uniform(10000, 50000))
        INVESTMENT_IRR_PERCENTAGE.labels(investment_name="NovaTecnologiaX").set(random.uniform(12, 25))
        
        print("[MetricsExporter] Simulação de atualização de métricas concluída.")

# Exemplo de uso: Iniciar o servidor e simular algumas atualizações
if __name__ == "__main__":
    exporter = MetricsExporter(prometheus_port=9091) # Usando porta diferente para exemplo
    
    if exporter.running:
        print("Servidor de métricas Prometheus rodando em http://localhost:9091/metrics")
        print("Pressione Ctrl+C para parar.")
        try:
            count = 0
            while True:
                count +=1
                print(f"\n--- Ciclo de Simulação de Métricas #{count} ---")
                exporter.simulate_metrics_updates()
                time.sleep(10) # Atualiza a cada 10 segundos
        except KeyboardInterrupt:
            print("\nServidor de métricas interrompido pelo usuário.")
        finally:
            print("Encerrando o exportador de métricas.")
    else:
        print("Não foi possível iniciar o servidor de métricas. Verifique os logs.")

