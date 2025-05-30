class RiskManager:
    def __init__(self, max_portfolio_risk_percentage: float = 5.0, max_trade_risk_percentage: float = 1.0):
        """Inicializa o Gerenciador de Risco.

        Args:
            max_portfolio_risk_percentage (float): Percentual máximo do portfólio total que pode ser arriscado.
            max_trade_risk_percentage (float): Percentual máximo do portfólio que pode ser arriscado em um único trade.
        """
        self.max_portfolio_risk_percentage = max_portfolio_risk_percentage / 100.0
        self.max_trade_risk_percentage = max_trade_risk_percentage / 100.0
        self.current_portfolio_value = 0.0  # Deve ser atualizado externamente
        self.current_open_risk = 0.0      # Risco total de todas as posições abertas
        print(f"[RiskManager] Gerenciador de Risco inicializado. Risco Máx. Portfólio: {self.max_portfolio_risk_percentage*100}%, Risco Máx. Trade: {self.max_trade_risk_percentage*100}%")

    def update_portfolio_value(self, new_value: float):
        """Atualiza o valor total do portfólio."""
        if new_value < 0:
            print("[RiskManager] Valor do portfólio não pode ser negativo.")
            return
        self.current_portfolio_value = new_value
        print(f"[RiskManager] Valor do portfólio atualizado para: ${self.current_portfolio_value:.2f}")

    def can_open_new_trade(self, trade_potential_loss: float) -> bool:
        """Verifica se um novo trade pode ser aberto com base nos limites de risco.

        Args:
            trade_potential_loss (float): Perda potencial máxima estimada para o novo trade.

        Returns:
            bool: True se o trade puder ser aberto, False caso contrário.
        """
        if self.current_portfolio_value <= 0:
            print("[RiskManager] Valor do portfólio é zero ou negativo. Não é possível abrir novos trades.")
            return False

        # Verifica o risco do trade individual
        if trade_potential_loss > (self.current_portfolio_value * self.max_trade_risk_percentage):
            print(f"[RiskManager] Risco do trade (${trade_potential_loss:.2f}) excede o máximo permitido por trade (${self.current_portfolio_value * self.max_trade_risk_percentage:.2f}).")
            return False

        # Verifica o risco total do portfólio
        if (self.current_open_risk + trade_potential_loss) > (self.current_portfolio_value * self.max_portfolio_risk_percentage):
            print(f"[RiskManager] Risco total do portfólio com novo trade (${self.current_open_risk + trade_potential_loss:.2f}) excederia o máximo permitido (${self.current_portfolio_value * self.max_portfolio_risk_percentage:.2f}).")
            return False
        
        print(f"[RiskManager] Verificação de risco aprovada para novo trade com perda potencial de ${trade_potential_loss:.2f}.")
        return True

    def add_trade_risk(self, trade_loss_amount: float):
        """Adiciona o risco de um novo trade aberto ao risco total."""
        self.current_open_risk += trade_loss_amount
        print(f"[RiskManager] Risco de ${trade_loss_amount:.2f} adicionado. Risco total atual: ${self.current_open_risk:.2f}")

    def remove_trade_risk(self, trade_loss_amount: float):
        """Remove o risco de um trade fechado do risco total."""
        self.current_open_risk -= trade_loss_amount
        if self.current_open_risk < 0:
            self.current_open_risk = 0 # Evitar risco negativo
        print(f"[RiskManager] Risco de ${trade_loss_amount:.2f} removido. Risco total atual: ${self.current_open_risk:.2f}")

    def get_current_risk_status(self) -> dict:
        """Retorna o status atual de risco do portfólio."""
        if self.current_portfolio_value > 0:
            current_risk_percentage = (self.current_open_risk / self.current_portfolio_value) * 100
        else:
            current_risk_percentage = 0.0
            
        status = {
            "portfolio_value": self.current_portfolio_value,
            "max_portfolio_risk_usd": self.current_portfolio_value * self.max_portfolio_risk_percentage,
            "max_trade_risk_usd": self.current_portfolio_value * self.max_trade_risk_percentage,
            "current_total_open_risk_usd": self.current_open_risk,
            "current_total_open_risk_percentage": round(current_risk_percentage, 2)
        }
        print(f"[RiskManager] Status de Risco: {status}")
        return status

    def calculate_position_size(self, entry_price: float, stop_loss_price: float, account_balance: float) -> float | None:
        """Calcula o tamanho da posição com base no risco por trade.

        Args:
            entry_price (float): Preço de entrada do trade.
            stop_loss_price (float): Preço do stop-loss.
            account_balance (float): Saldo atual da conta.

        Returns:
            float: Tamanho da posição (ex: em lotes para Forex, ou número de ações), ou None se inválido.
        """
        if entry_price <= 0 or stop_loss_price <= 0 or account_balance <= 0:
            print("[RiskManager] Preços de entrada/stop-loss e saldo da conta devem ser positivos.")
            return None
        
        risk_per_unit = abs(entry_price - stop_loss_price)
        if risk_per_unit == 0:
            print("[RiskManager] Risco por unidade é zero (preço de entrada igual ao stop-loss). Não é possível calcular o tamanho da posição.")
            return None
            
        amount_to_risk = account_balance * self.max_trade_risk_percentage
        position_size = amount_to_risk / risk_per_unit
        
        # Em um cenário real, você arredondaria para o mínimo negociável (ex: 0.01 lotes)
        # e consideraria o valor do pip/ponto para o ativo específico.
        # Para simplificar, retornamos o valor calculado.
        print(f"[RiskManager] Cálculo do Tamanho da Posição: Entrada={entry_price}, SL={stop_loss_price}, Saldo=${account_balance:.2f}")
        print(f"[RiskManager] Risco por Unidade=${risk_per_unit:.5f}, Valor a Arriscar=${amount_to_risk:.2f}, Tamanho da Posição Calculado={position_size:.4f}")
        return round(position_size, 4) # Arredondando para 4 casas decimais como exemplo

# Exemplo de uso
if __name__ == "__main__":
    manager = RiskManager(max_portfolio_risk_percentage=10.0, max_trade_risk_percentage=2.0)
    
    print("\n--- Atualizando Valor do Portfólio ---")
    manager.update_portfolio_value(100000) # Portfólio de $100,000
    manager.get_current_risk_status()

    print("\n--- Verificando Trade 1 (Perda Potencial: $1500) ---")
    trade1_loss = 1500.00
    if manager.can_open_new_trade(trade1_loss):
        print(f"Pode abrir Trade 1. Adicionando risco...")
        manager.add_trade_risk(trade1_loss)
    else:
        print(f"Não pode abrir Trade 1.")
    manager.get_current_risk_status()

    print("\n--- Verificando Trade 2 (Perda Potencial: $2500) ---")
    trade2_loss = 2500.00 # Excede o risco por trade (2% de 100k = 2000)
    if manager.can_open_new_trade(trade2_loss):
        print(f"Pode abrir Trade 2. Adicionando risco...")
        manager.add_trade_risk(trade2_loss)
    else:
        print(f"Não pode abrir Trade 2.")
    manager.get_current_risk_status()
    
    print("\n--- Verificando Trade 3 (Perda Potencial: $1000) ---")
    trade3_loss = 1000.00
    if manager.can_open_new_trade(trade3_loss):
        print(f"Pode abrir Trade 3. Adicionando risco...")
        manager.add_trade_risk(trade3_loss)
    else:
        print(f"Não pode abrir Trade 3.") # Risco total com trade1 (1500) + trade3 (1000) = 2500. OK.
    manager.get_current_risk_status()

    print("\n--- Fechando Trade 1 (Removendo Risco de $1500) ---")
    manager.remove_trade_risk(trade1_loss)
    manager.get_current_risk_status()

    print("\n--- Calculando Tamanho da Posição --- (Exemplo Forex)")
    # Exemplo: EURUSD, Saldo $10,000, Risco por trade 1% ($100)
    # Entrada: 1.08500, Stop-Loss: 1.08000 (50 pips de risco)
    # Risco por unidade (pip) = 0.00500
    # Tamanho da Posição = $100 / 0.00500 = 20,000 unidades (ou 0.2 lotes se 1 lote = 100,000)
    # (Este cálculo simplifica o valor do pip, que depende do par e do tamanho do contrato)
    pos_size_calc_manager = RiskManager(max_trade_risk_percentage=1.0) # 1% de risco por trade
    calculated_size = pos_size_calc_manager.calculate_position_size(
        entry_price=1.08500, 
        stop_loss_price=1.08000, 
        account_balance=10000.00
    )
    if calculated_size is not None:
        print(f"Tamanho da posição sugerido (simplificado): {calculated_size} unidades/lotes")

