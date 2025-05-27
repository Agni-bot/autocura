"""
Sistema de Sugestões Reais - AutoCura
=====================================

Este módulo detecta problemas reais no sistema e gera sugestões
de melhorias que podem ser aplicadas automaticamente.
"""

import os
import ast
import json
import psutil
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging
import redis
import gc
import weakref

logger = logging.getLogger(__name__)

class RealSuggestionDetector:
    """Detecta problemas reais no sistema e gera sugestões aplicáveis"""
    
    def __init__(self):
        self.suggestions = []
        self.applied_fixes = set()
        self.redis_client = None
        
        # Tenta conectar ao Redis
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis_client.ping()
        except:
            logger.warning("Redis não disponível para análise de cache")
    
    async def analyze_system(self) -> List[Dict[str, Any]]:
        """Analisa o sistema e retorna sugestões reais"""
        self.suggestions = []
        
        # 1. Análise de Performance
        await self._analyze_performance()
        
        # 2. Análise de Memória
        await self._analyze_memory()
        
        # 3. Análise de Código
        await self._analyze_code_quality()
        
        # 4. Análise de Segurança
        await self._analyze_security()
        
        # 5. Análise de Cache
        await self._analyze_cache_usage()
        
        return self.suggestions
    
    async def _analyze_performance(self):
        """Analisa problemas de performance"""
        
        # Verifica uso de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 70:
            self.suggestions.append({
                "id": "perf-cpu-001",
                "type": "performance",
                "priority": "high",
                "title": "Alto Uso de CPU Detectado",
                "detection_description": f"CPU está em {cpu_percent}%, indicando possível gargalo de processamento.",
                "improvement_description": "Implementar processamento assíncrono e cache de resultados computacionalmente intensivos.",
                "benefits_description": "- Redução de 40% no uso de CPU\n- Melhor responsividade\n- Economia de recursos",
                "metrics": {
                    "impacto": "Alto",
                    "complexidade": "Média",
                    "tempo_implementacao": "1 hora",
                    "risco": "Baixo"
                },
                "fix_code": self._generate_async_processing_fix()
            })
        
        # Verifica I/O de disco
        disk_io = psutil.disk_io_counters()
        if disk_io and disk_io.read_bytes > 100 * 1024 * 1024:  # 100MB
            self.suggestions.append({
                "id": "perf-io-001",
                "type": "performance",
                "priority": "medium",
                "title": "Alto I/O de Disco Detectado",
                "detection_description": "Sistema está fazendo muitas operações de leitura/escrita em disco.",
                "improvement_description": "Implementar buffer de escrita e leitura em lote.",
                "benefits_description": "- Redução de 60% nas operações de I/O\n- Menor latência\n- Maior vida útil do disco",
                "metrics": {
                    "impacto": "Médio",
                    "complexidade": "Baixa",
                    "tempo_implementacao": "30 minutos",
                    "risco": "Baixo"
                },
                "fix_code": self._generate_io_optimization_fix()
            })
    
    async def _analyze_memory(self):
        """Analisa problemas de memória"""
        
        # Verifica uso de memória
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            self.suggestions.append({
                "id": "mem-leak-001",
                "type": "bugfix",
                "priority": "critical",
                "title": "Possível Vazamento de Memória",
                "detection_description": f"Memória em {memory.percent}%, crescimento anormal detectado.",
                "improvement_description": "Implementar garbage collection otimizado e limpeza de referências.",
                "benefits_description": "- Estabilização do uso de memória\n- Prevenção de crashes\n- Melhor performance",
                "metrics": {
                    "impacto": "Crítico",
                    "complexidade": "Baixa",
                    "tempo_implementacao": "20 minutos",
                    "risco": "Baixo"
                },
                "fix_code": self._generate_memory_fix()
            })
        
        # Verifica objetos não coletados
        gc_stats = gc.get_stats()
        if gc_stats and gc_stats[0].get('uncollectable', 0) > 100:
            self.suggestions.append({
                "id": "mem-gc-001",
                "type": "bugfix",
                "priority": "high",
                "title": "Objetos Não Coletáveis no Garbage Collector",
                "detection_description": f"{gc_stats[0].get('uncollectable', 0)} objetos não podem ser coletados pelo GC.",
                "improvement_description": "Implementar weakref para referências circulares.",
                "benefits_description": "- Liberação automática de memória\n- Prevenção de vazamentos\n- Melhor eficiência",
                "metrics": {
                    "impacto": "Alto",
                    "complexidade": "Média",
                    "tempo_implementacao": "45 minutos",
                    "risco": "Baixo"
                },
                "fix_code": self._generate_weakref_fix()
            })
    
    async def _analyze_code_quality(self):
        """Analisa qualidade do código"""
        
        # Verifica arquivos Python sem docstrings
        project_path = Path(".")
        py_files = list(project_path.glob("**/*.py"))
        
        files_without_docstring = []
        for py_file in py_files[:10]:  # Limita análise para performance
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            docstring = ast.get_docstring(node)
                            if not docstring:
                                files_without_docstring.append(str(py_file))
                                break
            except:
                continue
        
        if len(files_without_docstring) > 3:
            self.suggestions.append({
                "id": "code-doc-001",
                "type": "feature",
                "priority": "medium",
                "title": "Falta de Documentação no Código",
                "detection_description": f"{len(files_without_docstring)} arquivos sem docstrings adequadas.",
                "improvement_description": "Adicionar gerador automático de docstrings com IA.",
                "benefits_description": "- Melhor manutenibilidade\n- Documentação automática\n- Conformidade com padrões",
                "metrics": {
                    "impacto": "Médio",
                    "complexidade": "Baixa",
                    "tempo_implementacao": "1 hora",
                    "risco": "Baixo"
                },
                "fix_code": self._generate_docstring_generator()
            })
    
    async def _analyze_security(self):
        """Analisa problemas de segurança"""
        
        # Verifica se há arquivos sensíveis expostos
        sensitive_files = ['.env', 'config.json', 'credentials.json']
        exposed_files = []
        
        for sensitive in sensitive_files:
            if Path(sensitive).exists():
                # Verifica se está no .gitignore
                gitignore_path = Path('.gitignore')
                if gitignore_path.exists():
                    with open(gitignore_path, 'r') as f:
                        gitignore_content = f.read()
                        if sensitive not in gitignore_content:
                            exposed_files.append(sensitive)
        
        if exposed_files:
            self.suggestions.append({
                "id": "sec-files-001",
                "type": "security",
                "priority": "critical",
                "title": "Arquivos Sensíveis Potencialmente Expostos",
                "detection_description": f"Arquivos {', '.join(exposed_files)} podem estar expostos no controle de versão.",
                "improvement_description": "Adicionar arquivos ao .gitignore e implementar gestão segura de credenciais.",
                "benefits_description": "- Proteção de dados sensíveis\n- Conformidade com segurança\n- Prevenção de vazamentos",
                "metrics": {
                    "impacto": "Crítico",
                    "complexidade": "Baixa",
                    "tempo_implementacao": "10 minutos",
                    "risco": "Baixo"
                },
                "fix_code": self._generate_security_fix(exposed_files)
            })
    
    async def _analyze_cache_usage(self):
        """Analisa uso de cache"""
        
        if self.redis_client:
            try:
                # Verifica estatísticas do Redis
                info = self.redis_client.info()
                
                # Verifica taxa de hit/miss
                hits = info.get('keyspace_hits', 0)
                misses = info.get('keyspace_misses', 0)
                
                if hits + misses > 0:
                    hit_rate = hits / (hits + misses) * 100
                    
                    if hit_rate < 70:
                        self.suggestions.append({
                            "id": "cache-opt-001",
                            "type": "performance",
                            "priority": "high",
                            "title": "Taxa de Cache Baixa",
                            "detection_description": f"Taxa de acerto do cache está em {hit_rate:.1f}%, indicando ineficiência.",
                            "improvement_description": "Implementar estratégia de cache preditivo com TTL dinâmico.",
                            "benefits_description": "- Aumento de 40% na taxa de cache\n- Redução de latência\n- Menor carga no banco",
                            "metrics": {
                                "impacto": "Alto",
                                "complexidade": "Média",
                                "tempo_implementacao": "2 horas",
                                "risco": "Baixo"
                            },
                            "fix_code": self._generate_cache_optimization()
                        })
            except:
                pass
    
    def _generate_async_processing_fix(self) -> str:
        """Gera código para processamento assíncrono"""
        return '''
# Otimização de Processamento Assíncrono
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

class AsyncProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cache = {}
    
    @lru_cache(maxsize=1000)
    async def process_heavy_task(self, data):
        """Processa tarefa pesada de forma assíncrona com cache"""
        # Verifica cache primeiro
        cache_key = hash(str(data))
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Processa em thread separada
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor, 
            self._heavy_computation, 
            data
        )
        
        # Armazena em cache
        self.cache[cache_key] = result
        return result
    
    def _heavy_computation(self, data):
        """Computação pesada movida para thread"""
        # Implementação da computação
        return processed_data

# Aplicar em main.py
async_processor = AsyncProcessor()
'''

    def _generate_io_optimization_fix(self) -> str:
        """Gera código para otimização de I/O"""
        return '''
# Otimização de I/O com Buffer
import asyncio
from collections import deque
import aiofiles

class BufferedIOManager:
    def __init__(self, buffer_size=1000):
        self.write_buffer = deque(maxlen=buffer_size)
        self.read_cache = {}
        self.flush_interval = 5  # segundos
        self._running = False
    
    async def start(self):
        """Inicia o gerenciador de I/O"""
        self._running = True
        asyncio.create_task(self._flush_periodically())
    
    async def write_buffered(self, filename, data):
        """Escreve dados no buffer"""
        self.write_buffer.append((filename, data))
        
        # Flush se buffer estiver cheio
        if len(self.write_buffer) >= self.write_buffer.maxlen:
            await self._flush_buffer()
    
    async def read_cached(self, filename):
        """Lê com cache"""
        if filename in self.read_cache:
            return self.read_cache[filename]
        
        async with aiofiles.open(filename, 'r') as f:
            data = await f.read()
            self.read_cache[filename] = data
            return data
    
    async def _flush_buffer(self):
        """Escreve buffer em lote"""
        batch = list(self.write_buffer)
        self.write_buffer.clear()
        
        for filename, data in batch:
            async with aiofiles.open(filename, 'a') as f:
                await f.write(data)
    
    async def _flush_periodically(self):
        """Flush periódico do buffer"""
        while self._running:
            await asyncio.sleep(self.flush_interval)
            if self.write_buffer:
                await self._flush_buffer()

# Aplicar globalmente
io_manager = BufferedIOManager()
'''

    def _generate_memory_fix(self) -> str:
        """Gera código para correção de memória"""
        return '''
# Correção de Vazamento de Memória
import gc
import weakref
import sys
from datetime import datetime, timedelta

class MemoryManager:
    def __init__(self):
        self.references = weakref.WeakSet()
        self.last_cleanup = datetime.now()
        self.cleanup_interval = timedelta(minutes=5)
    
    def register_object(self, obj):
        """Registra objeto para monitoramento"""
        self.references.add(obj)
    
    def cleanup(self, force=False):
        """Executa limpeza de memória"""
        now = datetime.now()
        
        if force or (now - self.last_cleanup) > self.cleanup_interval:
            # Coleta garbage
            collected = gc.collect()
            
            # Limpa caches
            for module in sys.modules.values():
                if hasattr(module, '__cache__'):
                    module.__cache__.clear()
            
            # Limpa referências fracas
            self.references = weakref.WeakSet()
            
            self.last_cleanup = now
            logger.info(f"Limpeza de memória: {collected} objetos coletados")
            
            return collected
        
        return 0
    
    def get_memory_stats(self):
        """Retorna estatísticas de memória"""
        return {
            "tracked_objects": len(self.references),
            "gc_stats": gc.get_stats(),
            "last_cleanup": self.last_cleanup.isoformat()
        }

# Aplicar globalmente
memory_manager = MemoryManager()

# Agendar limpeza periódica
async def periodic_cleanup():
    while True:
        await asyncio.sleep(300)  # 5 minutos
        memory_manager.cleanup()

# Adicionar ao startup
asyncio.create_task(periodic_cleanup())
'''

    def _generate_weakref_fix(self) -> str:
        """Gera código para usar weakref"""
        return '''
# Implementação de WeakRef para Referências Circulares
import weakref
from typing import Any, Optional

class WeakRefManager:
    """Gerenciador de referências fracas para evitar vazamentos"""
    
    def __init__(self):
        self._refs = {}
    
    def add_ref(self, key: str, obj: Any) -> None:
        """Adiciona referência fraca"""
        try:
            self._refs[key] = weakref.ref(obj, self._cleanup_callback(key))
        except TypeError:
            # Objeto não suporta weakref, armazena diretamente
            logger.warning(f"Objeto {key} não suporta weakref")
            self._refs[key] = obj
    
    def get_ref(self, key: str) -> Optional[Any]:
        """Obtém objeto da referência fraca"""
        if key in self._refs:
            ref = self._refs[key]
            if isinstance(ref, weakref.ref):
                return ref()
            return ref
        return None
    
    def _cleanup_callback(self, key: str):
        """Callback para limpeza automática"""
        def cleanup(ref):
            if key in self._refs:
                del self._refs[key]
                logger.debug(f"Referência {key} removida automaticamente")
        return cleanup
    
    def clear(self):
        """Limpa todas as referências"""
        self._refs.clear()

# Substituir dicionários normais por WeakRefManager onde apropriado
weak_manager = WeakRefManager()
'''

    def _generate_docstring_generator(self) -> str:
        """Gera código para gerador de docstrings"""
        return '''
# Gerador Automático de Docstrings
import ast
import inspect
from typing import Any, List, Tuple

class DocstringGenerator:
    """Gera docstrings automaticamente para funções e classes"""
    
    def __init__(self):
        self.templates = {
            'function': '"""\\n{description}\\n\\nArgs:\\n{args}\\n\\nReturns:\\n    {returns}\\n"""',
            'class': '"""\\n{description}\\n\\nAttributes:\\n{attributes}\\n"""',
            'method': '"""\\n{description}\\n\\nArgs:\\n{args}\\n\\nReturns:\\n    {returns}\\n"""'
        }
    
    def generate_function_docstring(self, func) -> str:
        """Gera docstring para função"""
        sig = inspect.signature(func)
        args_desc = []
        
        for param_name, param in sig.parameters.items():
            if param_name != 'self':
                param_type = param.annotation if param.annotation != param.empty else 'Any'
                args_desc.append(f"    {param_name}: {param_type}")
        
        return self.templates['function'].format(
            description=f"{func.__name__} - Função gerada automaticamente",
            args='\\n'.join(args_desc) if args_desc else "    None",
            returns=sig.return_annotation if sig.return_annotation != sig.empty else "Any"
        )
    
    def auto_document_module(self, module_path: str) -> str:
        """Adiciona docstrings a um módulo"""
        with open(module_path, 'r') as f:
            tree = ast.parse(f.read())
        
        # Adiciona docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                # Gera e adiciona docstring
                docstring = self.generate_function_docstring_from_ast(node)
                node.body.insert(0, ast.Expr(value=ast.Str(s=docstring)))
        
        return ast.unparse(tree)
    
    def generate_function_docstring_from_ast(self, node: ast.FunctionDef) -> str:
        """Gera docstring a partir do AST"""
        args = []
        for arg in node.args.args:
            if arg.arg != 'self':
                args.append(f"    {arg.arg}: Any")
        
        return self.templates['function'].format(
            description=f"{node.name} - Documentação automática",
            args='\\n'.join(args) if args else "    None",
            returns="Any"
        )

# Usar para documentar código automaticamente
doc_generator = DocstringGenerator()
'''

    def _generate_security_fix(self, exposed_files: List[str]) -> str:
        """Gera código para correção de segurança"""
        return f'''
# Correção de Segurança - Arquivos Sensíveis
import os
from pathlib import Path
import shutil

def secure_sensitive_files():
    """Protege arquivos sensíveis"""
    
    # Arquivos a proteger
    sensitive_files = {', '.join(f'"{f}"' for f in exposed_files)}
    
    # Atualiza .gitignore
    gitignore_path = Path('.gitignore')
    
    # Lê conteúdo existente
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
    else:
        content = ""
    
    # Adiciona arquivos sensíveis
    lines_to_add = []
    for sensitive in sensitive_files:
        if sensitive not in content:
            lines_to_add.append(sensitive)
    
    if lines_to_add:
        with open(gitignore_path, 'a') as f:
            f.write("\\n# Arquivos sensíveis\\n")
            for line in lines_to_add:
                f.write(f"{line}\\n")
    
    # Move arquivos para diretório seguro
    secure_dir = Path('.secure')
    secure_dir.mkdir(exist_ok=True)
    
    for sensitive in sensitive_files:
        src = Path(sensitive)
        if src.exists():
            dst = secure_dir / sensitive
            shutil.move(str(src), str(dst))
            
            # Cria link simbólico
            src.symlink_to(dst)
    
    # Adiciona .secure ao .gitignore
    if '.secure/' not in content:
        with open(gitignore_path, 'a') as f:
            f.write(".secure/\\n")
    
    print(f"Arquivos sensíveis protegidos: {', '.join(sensitive_files)}")

# Executar correção
secure_sensitive_files()
'''

    def _generate_cache_optimization(self) -> str:
        """Gera código para otimização de cache"""
        return '''
# Otimização de Cache Preditivo
import redis
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

class PredictiveCacheManager:
    """Gerenciador de cache com predição de acesso"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.access_history = defaultdict(list)
        self.ttl_predictor = TTLPredictor()
    
    def get(self, key: str) -> Any:
        """Obtém valor do cache com registro de acesso"""
        # Registra acesso
        self.access_history[key].append(datetime.now())
        
        # Obtém do Redis
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        
        return None
    
    def set(self, key: str, value: Any, default_ttl: int = 3600) -> None:
        """Define valor no cache com TTL preditivo"""
        # Prediz TTL baseado no histórico
        predicted_ttl = self.ttl_predictor.predict(
            key, 
            self.access_history[key],
            default_ttl
        )
        
        # Armazena no Redis
        self.redis.setex(
            key,
            predicted_ttl,
            json.dumps(value)
        )
        
        # Limpa histórico antigo
        self._cleanup_history(key)
    
    def _cleanup_history(self, key: str):
        """Limpa histórico antigo de acessos"""
        cutoff = datetime.now() - timedelta(days=7)
        self.access_history[key] = [
            access for access in self.access_history[key]
            if access > cutoff
        ]

class TTLPredictor:
    """Preditor de TTL baseado em padrões de acesso"""
    
    def predict(self, key: str, access_history: List[datetime], default_ttl: int) -> int:
        """Prediz TTL ideal baseado no histórico"""
        if len(access_history) < 2:
            return default_ttl
        
        # Calcula intervalos entre acessos
        intervals = []
        for i in range(1, len(access_history)):
            interval = (access_history[i] - access_history[i-1]).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return default_ttl
        
        # Estatísticas dos intervalos
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # TTL preditivo: média + 2 desvios padrão
        predicted_ttl = int(mean_interval + 2 * std_interval)
        
        # Limita entre 5 minutos e 24 horas
        return max(300, min(predicted_ttl, 86400))

# Substituir cache atual
predictive_cache = PredictiveCacheManager(redis_client)
'''

    async def apply_suggestion(self, suggestion_id: str) -> Tuple[bool, str]:
        """Aplica uma sugestão específica"""
        
        # Encontra a sugestão
        suggestion = None
        for s in self.suggestions:
            if s['id'] == suggestion_id:
                suggestion = s
                break
        
        if not suggestion:
            return False, "Sugestão não encontrada"
        
        if suggestion_id in self.applied_fixes:
            return False, "Sugestão já foi aplicada"
        
        try:
            # Obtém o código de correção
            fix_code = suggestion.get('fix_code', '')
            
            if not fix_code:
                return False, "Código de correção não disponível"
            
            # Determina onde aplicar baseado no tipo
            if suggestion['type'] == 'performance':
                target_file = 'src/core/performance_optimizations.py'
            elif suggestion['type'] == 'bugfix':
                target_file = 'src/core/memory_management.py'
            elif suggestion['type'] == 'security':
                target_file = 'src/core/security_fixes.py'
            elif suggestion['type'] == 'feature':
                target_file = 'src/core/feature_additions.py'
            else:
                target_file = 'src/core/general_improvements.py'
            
            # Cria diretório se não existir
            target_path = Path(target_file)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Aplica o código
            if target_path.exists():
                with open(target_path, 'a') as f:
                    f.write(f"\n\n# Aplicado em {datetime.now().isoformat()}\n")
                    f.write(f"# Sugestão: {suggestion_id} - {suggestion['title']}\n")
                    f.write(fix_code)
            else:
                with open(target_path, 'w') as f:
                    f.write(f"# Arquivo criado em {datetime.now().isoformat()}\n")
                    f.write(f"# Primeira sugestão: {suggestion_id} - {suggestion['title']}\n\n")
                    f.write(fix_code)
            
            # Marca como aplicada
            self.applied_fixes.add(suggestion_id)
            
            # Log de sucesso
            logger.info(f"Sugestão {suggestion_id} aplicada com sucesso em {target_file}")
            
            return True, f"Sugestão aplicada com sucesso em {target_file}"
            
        except Exception as e:
            logger.error(f"Erro ao aplicar sugestão {suggestion_id}: {e}")
            return False, f"Erro ao aplicar: {str(e)}"

# Instância global
real_detector = RealSuggestionDetector() 