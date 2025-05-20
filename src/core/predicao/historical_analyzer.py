import numpy as np
import pandas as pd # Para manipulação de séries temporais, se necessário

class HistoricalPatternEngine:
    """Identifica padrões e ciclos em dados históricos usando técnicas como FFT."""
    def __init__(self):
        print("[HistoricalPatternEngine] Inicializado.")

    def _preprocess_data(self, dataset: list, column_name: str = None) -> np.ndarray:
        """Prepara os dados para análise FFT. Espera uma lista de valores numéricos
           ou um DataFrame do Pandas com uma coluna especificada.
        """
        print(f"[HistoricalPatternEngine] Pré-processando dados...")
        if isinstance(dataset, pd.DataFrame):
            if column_name and column_name in dataset.columns:
                series = dataset[column_name].values
            else:
                # Tenta usar a primeira coluna numérica se nenhuma for especificada
                numeric_cols = dataset.select_dtypes(include=np.number).columns
                if not numeric_cols.empty:
                    series = dataset[numeric_cols[0]].values
                    print(f"[HistoricalPatternEngine] Usando a primeira coluna numérica encontrada: {numeric_cols[0]}")
                else:
                    raise ValueError("DataFrame não contém colunas numéricas ou nome da coluna não especificado/inválido.")
        elif isinstance(dataset, list):
            series = np.array(dataset)
        elif isinstance(dataset, np.ndarray):
            series = dataset
        else:
            raise TypeError("Formato do dataset não suportado. Use lista, np.ndarray ou pd.DataFrame.")

        if not np.issubdtype(series.dtype, np.number):
            raise ValueError("Os dados da série devem ser numéricos para análise FFT.")
        
        # Remover a média (detrending simples) pode ajudar a destacar ciclos
        series_detrended = series - np.mean(series)
        print(f"[HistoricalPatternEngine] Dados pré-processados. Comprimento da série: {len(series_detrended)}")
        return series_detrended

    def find_cycles_fft(self, dataset: list, data_column: str = None, top_n_cycles: int = 3) -> dict:
        """Identifica os ciclos dominantes em um dataset usando a Transformada Rápida de Fourier (FFT).

        Args:
            dataset (list or pd.DataFrame or np.ndarray): A série temporal de dados a ser analisada.
            data_column (str, optional): Se o dataset for um DataFrame, especifica a coluna a ser usada.
            top_n_cycles (int): O número dos ciclos mais proeminentes (por amplitude) a serem retornados.

        Returns:
            dict: Um dicionário contendo os ciclos identificados (frequência, período, amplitude).
                  Ex: {"dominant_cycles": [{"frequency": 0.1, "period": 10, "amplitude": 50.0}, ...]}
        """
        try:
            series = self._preprocess_data(dataset, data_column)
        except (TypeError, ValueError) as e:
            print(f"[HistoricalPatternEngine] Erro no pré-processamento dos dados: {e}")
            return {"error": str(e), "dominant_cycles": []}

        if len(series) < 2:
            print("[HistoricalPatternEngine] Série de dados muito curta para análise FFT.")
            return {"error": "Série de dados muito curta", "dominant_cycles": []}

        print(f"[HistoricalPatternEngine] Calculando FFT para série de {len(series)} pontos...")
        fft_result = np.fft.fft(series)
        frequencies = np.fft.fftfreq(len(series))
        
        # Considerar apenas a parte positiva do espectro (frequências positivas)
        positive_mask = frequencies > 0
        positive_frequencies = frequencies[positive_mask]
        positive_fft_amplitudes = np.abs(fft_result[positive_mask])

        if len(positive_frequencies) == 0:
            print("[HistoricalPatternEngine] Nenhuma frequência positiva encontrada após FFT.")
            return {"dominant_cycles": []}

        print(f"[HistoricalPatternEngine] Encontradas {len(positive_frequencies)} frequências positivas.")

        # Identificar os picos (ciclos dominantes) por amplitude
        # Ordenar por amplitude decrescente e pegar os top N
        sorted_indices = np.argsort(positive_fft_amplitudes)[::-1]
        
        dominant_cycles = []
        for i in range(min(top_n_cycles, len(sorted_indices))):
            idx = sorted_indices[i]
            freq = positive_frequencies[idx]
            amplitude = positive_fft_amplitudes[idx]
            period = 1 / freq # Período em unidades de tempo da amostragem original
            
            dominant_cycles.append({
                "frequency": round(freq, 6),
                "period": round(period, 2),
                "amplitude": round(amplitude, 2)
            })
        
        print(f"[HistoricalPatternEngine] Ciclos dominantes identificados: {dominant_cycles}")
        return {"dominant_cycles": dominant_cycles}

# Exemplo de uso (simulado)
if __name__ == "__main__":
    engine = HistoricalPatternEngine()

    print("\n--- Testando com Dados Sintéticos (Senoide) ---")
    # Dados com um ciclo claro de período 10 e outro de período 50
    time_steps = np.arange(0, 200, 1)
    signal_10 = 5 * np.sin(2 * np.pi * time_steps / 10)
    signal_50 = 2 * np.sin(2 * np.pi * time_steps / 50)
    noise = np.random.normal(0, 0.5, len(time_steps))
    synthetic_data = signal_10 + signal_50 + noise
    
    cycles_synthetic = engine.find_cycles_fft(dataset=synthetic_data.tolist(), top_n_cycles=3)
    print(f"Ciclos encontrados nos dados sintéticos: {cycles_synthetic}")
    # Esperado: períodos próximos de 10 e 50 devem aparecer com altas amplitudes.

    print("\n--- Testando com Dados de Exemplo (Lista Simples) ---")
    simple_data = [10, 12, 15, 10, 8, 10, 13, 16, 11, 9] # Padrão curto
    cycles_simple = engine.find_cycles_fft(dataset=simple_data, top_n_cycles=2)
    print(f"Ciclos encontrados nos dados simples: {cycles_simple}")

    print("\n--- Testando com DataFrame Pandas ---")
    data_dict = {
        'tempo': np.arange(100),
        'vendas': 100 + 20 * np.sin(2 * np.pi * np.arange(100) / 20) + 5 * np.random.randn(100)
    }
    df_data = pd.DataFrame(data_dict)
    cycles_df = engine.find_cycles_fft(dataset=df_data, data_column='vendas', top_n_cycles=2)
    print(f"Ciclos encontrados no DataFrame: {cycles_df}")
    # Esperado: um ciclo com período próximo de 20.

    print("\n--- Testando com Dados Curtos ---")
    short_data = [1, 2]
    cycles_short = engine.find_cycles_fft(dataset=short_data)
    print(f"Ciclos encontrados em dados curtos: {cycles_short}")

    print("\n--- Testando com Dados Não Numéricos (Deve falhar) ---")
    non_numeric_data = ['a', 'b', 'c']
    try:
        cycles_non_numeric = engine.find_cycles_fft(dataset=non_numeric_data)
        print(f"Ciclos encontrados em dados não numéricos: {cycles_non_numeric}")
    except Exception as e:
        print(f"Erro esperado ao processar dados não numéricos: {e}")

