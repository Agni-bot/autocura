try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("[ForexEA] Biblioteca MetaTrader5 não encontrada. Funcionalidades de Forex trading estarão desabilitadas ou simuladas.")
import time

class ForexEA:
    def __init__(self, login, password, server, symbol="EURUSD", risk_percentage=2.0):
        """Inicializa o Expert Advisor para Forex trading.

        Args:
            login (int): Número da conta de login no MetaTrader 5.
            password (str): Senha da conta.
            server (str): Nome do servidor da corretora.
            symbol (str): Símbolo do par de moedas a ser negociado (ex: "EURUSD").
            risk_percentage (float): Percentual do saldo a ser arriscado por trade (ex: 2.0 para 2%).
        """
        self.login = login
        self.password = password
        self.server = server
        self.symbol = symbol
        self.risk_percentage = risk_percentage / 100.0  # Converter para decimal
        self.initialized = False
        self.last_tick = None
        print(f"[ForexEA] Expert Advisor inicializado para o símbolo: {self.symbol}")

        if MT5_AVAILABLE:
            self._initialize_mt5()
        else:
            print("[ForexEA] MetaTrader5 não está disponível. As operações de trading serão simuladas.")

    def _initialize_mt5(self):
        """Inicializa a conexão com o terminal MetaTrader 5."""
        if not mt5.initialize(login=self.login, password=self.password, server=self.server):
            print(f"[ForexEA] Falha na inicialização do MetaTrader5: {mt5.last_error()}")
            self.initialized = False
            return
        
        print("[ForexEA] MetaTrader5 inicializado com sucesso.")
        
        # Preparar o símbolo
        selected = mt5.symbol_select(self.symbol, True)
        if not selected:
            print(f"[ForexEA] Falha ao selecionar o símbolo {self.symbol}: {mt5.last_error()}")
            mt5.shutdown()
            self.initialized = False
            return
        print(f"[ForexEA] Símbolo {self.symbol} selecionado e pronto para uso.")
        self.initialized = True

    def get_current_price(self) -> float | None:
        """Obtém o preço de mercado atual (ask) para o símbolo."""
        if not self.initialized and MT5_AVAILABLE:
            print("[ForexEA] MT5 não inicializado. Não é possível obter o preço.")
            return None
        
        if MT5_AVAILABLE:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick:
                self.last_tick = tick
                # print(f"[ForexEA] Tick recebido para {self.symbol}: Ask={tick.ask}, Bid={tick.bid}")
                return tick.ask
            else:
                print(f"[ForexEA] Não foi possível obter o tick para {self.symbol}: {mt5.last_error()}")
                return None
        else:
            # Simulação de preço
            simulated_price = round(1.0850 + random.uniform(-0.0050, 0.0050), 4)
            print(f"[ForexEA] Preço simulado para {self.symbol}: {simulated_price}")
            return simulated_price

    def calculate_stop_loss(self, entry_price: float, order_type: int) -> float:
        """Calcula o preço do Stop Loss com base no risco e no preço de entrada."""
        # Este é um cálculo simplificado. Em um EA real, consideraria o saldo da conta,
        # o valor do pip, e o tamanho do lote para determinar o SL em preço.
        # Aqui, vamos definir um SL fixo percentual abaixo/acima do preço de entrada.
        if order_type == mt5.ORDER_TYPE_BUY:
            sl_price = entry_price * (1 - self.risk_percentage) # SL para compra é abaixo do preço
        elif order_type == mt5.ORDER_TYPE_SELL:
            sl_price = entry_price * (1 + self.risk_percentage) # SL para venda é acima do preço
        else:
            return 0.0
        
        # Arredondar para o número de dígitos do símbolo (geralmente 4 ou 5 para Forex)
        # symbol_info = mt5.symbol_info(self.symbol)
        # digits = symbol_info.digits if symbol_info else 5
        digits = 5 # Assumindo 5 dígitos para simplificar a simulação
        return round(sl_price, digits)

    def execute_trade(self, operation: str, volume: float) -> dict | None:
        """Executa ordens de compra ou venda com gerenciamento de risco (stop loss).

        Args:
            operation (str): "buy" ou "sell".
            volume (float): Volume da ordem em lotes.

        Returns:
            Dicionário com o resultado da ordem ou None em caso de falha.
        """
        if not self.initialized and MT5_AVAILABLE:
            print("[ForexEA] MT5 não inicializado. Não é possível executar trade.")
            return None

        order_type = None
        if operation.lower() == "buy":
            order_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(self.symbol).ask if MT5_AVAILABLE and self.last_tick else self.get_current_price()
        elif operation.lower() == "sell":
            order_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(self.symbol).bid if MT5_AVAILABLE and self.last_tick else self.get_current_price()
        else:
            print(f"[ForexEA] Operação inválida: {operation}. Use 'buy' ou 'sell'.")
            return None

        if price is None:
            print("[ForexEA] Não foi possível obter o preço atual para executar a ordem.")
            return None

        stop_loss_price = self.calculate_stop_loss(price, order_type)
        # Take profit pode ser definido de forma similar, ex: entry_price * (1 + risk_percentage * 2) para compra
        # tp_price = price * (1 + self.risk_percentage * 1.5) if order_type == mt5.ORDER_TYPE_BUY else price * (1 - self.risk_percentage * 1.5)
        # tp_price = round(tp_price, 5)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": stop_loss_price,
            # "tp": tp_price,
            "deviation": 10, # Slippage permitido em pontos
            "magic": 234000, # Magic number para identificar ordens deste EA
            "comment": "Ordem via Python EA",
            "type_time": mt5.ORDER_TIME_GTC, # Good Till Cancelled
            "type_filling": mt5.ORDER_FILLING_IOC, # Immediate Or Cancel
        }
        print(f"[ForexEA] Preparando para enviar ordem: {request}")

        if MT5_AVAILABLE:
            result = mt5.order_send(request)
            if result is None:
                print(f"[ForexEA] Falha ao enviar ordem: mt5.order_send() retornou None. Erro: {mt5.last_error()}")
                return None
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print(f"[ForexEA] Ordem não executada. Retcode: {result.retcode}, Comentário: {result.comment}")
                # Tentar obter mais detalhes do erro
                error_details = mt5.last_error()
                print(f"[ForexEA] Detalhes do erro MT5: {error_details}")
                return {"retcode": result.retcode, "comment": result.comment, "request": request, "mt5_error": error_details}
            else:
                print(f"[ForexEA] Ordem executada com sucesso: {result}")
                return {"retcode": result.retcode, "comment": result.comment, "order_id": result.order, "request": request}
        else:
            # Simulação de execução de ordem
            simulated_order_id = int(time.time() * 1000)
            print(f"[ForexEA] Ordem simulada enviada. ID da Ordem Simulada: {simulated_order_id}")
            return {"retcode": "SIMULATED_DONE", "comment": "Ordem simulada com sucesso", "order_id": simulated_order_id, "request": request}

    def shutdown_mt5(self):
        """Encerra a conexão com o terminal MetaTrader 5."""
        if self.initialized and MT5_AVAILABLE:
            print("[ForexEA] Encerrando conexão com MetaTrader5...")
            mt5.shutdown()
            self.initialized = False
            print("[ForexEA] Conexão com MetaTrader5 encerrada.")
        elif not MT5_AVAILABLE:
            print("[ForexEA] MetaTrader5 não estava disponível, nenhum encerramento necessário.")
        else:
            print("[ForexEA] MetaTrader5 não estava inicializado.")

# Exemplo de uso (requer MetaTrader 5 instalado, conta demo e dados de login)
if __name__ == '__main__':
    # ATENÇÃO: Substitua com suas credenciais de uma conta DEMO para testes.
    # NÃO USE CREDENCIAIS DE CONTA REAL DIRETAMENTE NO CÓDIGO EM PRODUÇÃO.
    # Considere usar variáveis de ambiente ou um arquivo de configuração seguro.
    try:
        from mt5_credentials import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER # Arquivo local não versionado
    except ImportError:
        print("Arquivo mt5_credentials.py não encontrado. Usando credenciais dummy ou pulando testes MT5.")
        # Use credenciais dummy se o arquivo não existir, para que o código não quebre
        # mas as operações MT5 reais falharão ou serão simuladas.
        MT5_LOGIN = 12345678 
        MT5_PASSWORD = "password"
        MT5_SERVER = "YourBroker-Demo"

    ea = ForexEA(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER, symbol="EURUSD")

    if ea.initialized or not MT5_AVAILABLE: # Prosseguir se MT5 inicializado ou se estiver em modo de simulação
        print("\n--- Obtendo Preço Atual ---")
        current_price = ea.get_current_price()
        if current_price:
            print(f"Preço atual (Ask) para {ea.symbol}: {current_price}")
        else:
            print(f"Não foi possível obter o preço para {ea.symbol}.")

        print("\n--- Executando Trade de Compra (0.01 lotes) ---")
        buy_result = ea.execute_trade(operation="buy", volume=0.01)
        if buy_result:
            print(f"Resultado da Compra: {buy_result}")
        
        time.sleep(2) # Pausa entre trades

        print("\n--- Executando Trade de Venda (0.01 lotes) ---")
        sell_result = ea.execute_trade(operation="sell", volume=0.01)
        if sell_result:
            print(f"Resultado da Venda: {sell_result}")
    else:
        print("\nMetaTrader5 não pôde ser inicializado. Verifique suas credenciais, servidor e se o terminal MT5 está em execução.")

    ea.shutdown_mt5()

