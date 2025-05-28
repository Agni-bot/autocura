# Arquivo criado em 2025-05-28T18:22:05.184617
# Primeira sugestão: perf-io-001 - Alto I/O de Disco Detectado
# Código otimizado por IA

import asyncio
from collections import deque
import aiofiles

class BufferedIOManager:
    """
    Classe para gerenciar operações de I/O com buffer e cache.
    """
    def __init__(self, buffer_size=1000):
        self.write_buffer = deque(maxlen=buffer_size)
        self.read_cache = {}
        self.flush_interval = 5  # segundos
        self._running = False

    async def start(self):
        """
        Inicia o gerenciador de I/O.
        """
        self._running = True
        asyncio.create_task(self._flush_periodically())

    async def write_buffered(self, filename, data):
        """
        Escreve dados no buffer. Se o buffer estiver cheio, realiza um flush.
        """
        self.write_buffer.append((filename, data))
        
        if len(self.write_buffer) >= self.write_buffer.maxlen:
            await self._flush_buffer()

    async def read_cached(self, filename):
        """
        Lê dados com cache. Se os dados não estiverem no cache, lê do arquivo e armazena no cache.
        """
        if filename in self.read_cache:
            return self.read_cache[filename]
        
        try:
            async with aiofiles.open(filename, 'r') as f:
                data = await f.read()
                self.read_cache[filename] = data
                return data
        except FileNotFoundError:
            print(f"Arquivo {filename} não encontrado.")
            return None

    async def _flush_buffer(self):
        """
        Realiza um flush do buffer, escrevendo os dados em lote.
        """
        batch = list(self.write_buffer)
        self.write_buffer.clear()
        
        for filename, data in batch:
            try:
                async with aiofiles.open(filename, 'a') as f:
                    await f.write(data)
            except Exception as e:
                print(f"Erro ao escrever no arquivo {filename}: {str(e)}")

    async def _flush_periodically(self):
        """
        Realiza um flush do buffer periodicamente.
        """
        while self._running:
            await asyncio.sleep(self.flush_interval)
            if self.write_buffer:
                await self._flush_buffer()

# Aplicar globalmente
io_manager = BufferedIOManager()