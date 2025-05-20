# src/conscienciaSituacional/web/rate_limiter.py
import time
from threading import Lock

class RateLimitExceeded(Exception):
    """Exceção para quando o limite de taxa é excedido."""
    def __init__(self, message="Limite de taxa da API excedido", retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after

class TokenBucket:
    """Implementação simples de um Token Bucket para rate limiting."""
    def __init__(self, capacity: int, refill_rate: float):
        """
        capacity: Número máximo de tokens que o balde pode conter.
        refill_rate: Taxa na qual os tokens são adicionados ao balde (tokens por segundo).
        """
        self.capacity = float(capacity)
        self._tokens = float(capacity) # Começa cheio
        self.refill_rate = float(refill_rate)
        self.last_refill_time = time.monotonic()
        self._lock = Lock()

    def _refill(self):
        now = time.monotonic()
        time_passed = now - self.last_refill_time
        tokens_to_add = time_passed * self.refill_rate
        self._tokens = min(self.capacity, self._tokens + tokens_to_add)
        self.last_refill_time = now

    def consume(self, tokens_to_consume: int = 1) -> bool:
        """Tenta consumir um número de tokens. Retorna True se bem-sucedido, False caso contrário."""
        with self._lock:
            self._refill()
            if self._tokens >= tokens_to_consume:
                self._tokens -= tokens_to_consume
                return True
            return False

    def wait_for_token(self, tokens_to_consume: int = 1, timeout: float = None) -> bool:
        """Espera até que tokens suficientes estejam disponíveis ou o timeout seja atingido."""
        start_time = time.monotonic()
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens_to_consume:
                    self._tokens -= tokens_to_consume
                    return True
            
            if timeout is not None and (time.monotonic() - start_time) > timeout:
                return False # Timeout atingido
            
            # Calcula o tempo de espera estimado para o próximo token (ou tokens)
            # Esta é uma estimativa, pode precisar de ajuste para múltiplos tokens
            wait_time = 0.1 # Pequeno delay para evitar busy-waiting excessivo
            if self.refill_rate > 0:
                needed = tokens_to_consume - self._tokens
                if needed > 0:
                    wait_time = max(wait_time, needed / self.refill_rate)
            
            time.sleep(min(wait_time, 0.5)) # Limita o sleep máximo para reavaliação

class APIRateLimiter:
    """Gerenciador de Rate Limiting para chamadas de API usando TokenBucket."""
    def __init__(self, calls_per_interval: int, interval_seconds: int = 60):
        """
        calls_per_interval: Número de chamadas permitidas dentro do intervalo.
        interval_seconds: Duração do intervalo em segundos (padrão: 60 segundos para chamadas por minuto).
        """
        if interval_seconds <= 0:
            raise ValueError("O intervalo deve ser positivo.")
        # A capacidade é o número de chamadas, a taxa de recarga é normalizada por segundo.
        self.bucket = TokenBucket(capacity=calls_per_interval, refill_rate=calls_per_interval / interval_seconds)
        self.calls_per_interval = calls_per_interval
        self.interval_seconds = interval_seconds

    def call_api(self, func_to_call, *args, **kwargs):
        """
        Tenta executar a função `func_to_call`.
        Levanta RateLimitExceeded se o limite for atingido e não puder ser satisfeito imediatamente.
        A função `func_to_call` deve ser uma função que realiza a chamada à API.
        """
        if self.bucket.consume(1):
            return func_to_call(*args, **kwargs)
        else:
            # Calcula retry_after (simplificado)
            retry_after_seconds = self.interval_seconds / self.calls_per_interval 
            print(f"Rate limit excedido. Tente novamente após aproximadamente {retry_after_seconds:.2f} segundos.")
            raise RateLimitExceeded(retry_after=retry_after_seconds)

    def call_api_blocking(self, func_to_call, *args, timeout_wait: float = None, **kwargs):
        """
        Tenta executar a função `func_to_call`, esperando se necessário.
        Levanta RateLimitExceeded se o timeout for atingido antes que o token esteja disponível.
        """
        if self.bucket.wait_for_token(1, timeout=timeout_wait):
            return func_to_call(*args, **kwargs)
        else:
            raise RateLimitExceeded("Rate limit excedido e timeout de espera atingido.")

# Exemplo de uso (não será executado diretamente aqui):
# if __name__ == "__main__":
#     # Limita a 5 chamadas por minuto
#     limiter = APIRateLimiter(calls_per_interval=5, interval_seconds=60)

#     def minha_api_call(param):
#         print(f"Fazendo chamada à API com {param} às {time.strftime('%X')}")
#         return f"Resultado para {param}"

#     for i in range(10):
#         try:
#             # Usando a versão não bloqueante
#             # resultado = limiter.call_api(minha_api_call, f"chamada {i+1}")
#             # print(resultado)
            
#             # Usando a versão bloqueante (espera até 15s por um token)
#             resultado = limiter.call_api_blocking(minha_api_call, f"chamada {i+1}", timeout_wait=15)
#             print(resultado)

#         except RateLimitExceeded as e:
#             print(f"Erro: {e}. Tentando novamente em {e.retry_after if e.retry_after else 'breve'}...")
#             if e.retry_after:
#                 time.sleep(e.retry_after + 0.1) # Espera um pouco mais
#             else:
#                 time.sleep(5) # Espera genérica
#         time.sleep(1) # Pequeno delay entre tentativas de chamada

