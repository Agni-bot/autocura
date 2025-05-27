# 🔧 Plano de Correção para Carregamento Completo dos Módulos

## 🎯 **Problemas Identificados**

### **❌ Problema 1: Importações Circulares e Incorretas**
- `diagnostico.py` tenta importar `from ..monitoramento import MetricasSistema`
- `MetricasSistema` existe em múltiplos locais diferentes
- Importações apontam para estrutura antiga (`src.core.logger`)

### **❌ Problema 2: Conflito de Timeseries Prometheus** 
- `Duplicated timeseries in CollectorRegistry: {'metricas_criadas_created', 'metricas_criadas_total', 'metricas_criadas'}`
- Múltiplas instâncias do Prometheus sendo criadas

### **❌ Problema 3: Módulos Dependentes Não Encontrados**
- `src.core.logger` e `src.core.cache` não existem na nova estrutura
- Falta de inicialização adequada dos módulos

### **❌ Problema 4: Estrutura de Imports Desalinhada**
- Novo sistema usa `autocura.` mas imports ainda referenciam `src.`

---

## 🛠️ **Plano de Correção por Etapas**

### **📋 ETAPA 1: Correção das Importações Base (Crítico)**

#### **1.1 Corrigir MetricasSistema centralizada**
```python
# Criar: autocura/core/models/metricas.py
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class MetricasSistema:
    throughput: float
    taxa_erro: float  
    latencia: float
    uso_recursos: Dict[str, float]
    timestamp: datetime = datetime.now()

@dataclass
class Metrica:
    nome: str
    valor: float
    tipo: str
    labels: Dict[str, str]
    timestamp: datetime
```

#### **1.2 Atualizar imports em diagnostico.py**
```python
# DE: from ..monitoramento import MetricasSistema, Metrica, ColetorMetricas
# PARA: from ...core.models.metricas import MetricasSistema, Metrica
#       from ..monitoramento.coletor_metricas import ColetorMetricas
```

#### **1.3 Corrigir imports em coletor_metricas.py**
```python
# DE: from src.core.logger import Logger
#     from src.core.cache import Cache
# PARA: from ...utils.logging.logger import get_logger
#       from ...utils.cache.redis_cache import CacheDistribuido
```

---

### **📋 ETAPA 2: Resolver Conflito Prometheus (Crítico)**

#### **2.1 Singleton para Prometheus Registry**
```python
# Criar: autocura/monitoring/metrics/prometheus_singleton.py
import prometheus_client
from typing import Optional

class PrometheusRegistry:
    _instance: Optional['PrometheusRegistry'] = None
    _registry: Optional[prometheus_client.CollectorRegistry] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._registry = prometheus_client.CollectorRegistry()
        return cls._instance
    
    @property
    def registry(self):
        return self._registry
```

#### **2.2 Atualizar GerenciadorMetricas**
```python
# Usar registry singleton em vez de registry global
from .prometheus_singleton import PrometheusRegistry
registry = PrometheusRegistry().registry
```

---

### **📋 ETAPA 3: Completar Módulos Services (Alto)**

#### **3.1 Corrigir imports em todos os serviços**
- **ia/cliente_ia.py:** Corrigir imports para nova estrutura
- **etica/validador_etico.py:** Atualizar dependências  
- **guardiao/guardiao_cognitivo.py:** Corrigir paths

#### **3.2 Criar __init__.py completos**
```python
# autocura/services/__init__.py
from .ia import ClienteIA, AgenteAdaptativo
from .diagnostico import DiagnosticoSistema, RealSuggestionsDetector
from .monitoramento import ColetorMetricas, AnalisadorMetricas
from .etica import ValidadorEtico, CircuitosMorais
from .guardiao import GuardiaoCognitivo
from .gerador import GeradorAutomatico

__all__ = [
    "ClienteIA", "AgenteAdaptativo",
    "DiagnosticoSistema", "RealSuggestionsDetector", 
    "ColetorMetricas", "AnalisadorMetricas",
    "ValidadorEtico", "CircuitosMorais",
    "GuardiaoCognitivo", "GeradorAutomatico"
]
```

---

### **📋 ETAPA 4: Implementar Security Module (Médio)**

#### **4.1 Completar quantum_safe_crypto.py**
```python
# Implementar criptografia pós-quântica funcional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
# Implementação completa baseada no plano evolutivo
```

#### **4.2 Criar deteccao/anomalias.py**
```python
# Sistema de detecção de anomalias de segurança
class DetectorAnomalias:
    def detectar_intruso(self):
        pass
    def verificar_integridade(self):
        pass
```

---

### **📋 ETAPA 5: Atualizar main_modular.py (Alto)**

#### **5.1 Imports mais robustos**
```python
# Imports com fallbacks específicos para cada módulo
def load_services():
    try:
        from autocura.services import (
            DiagnosticoSistema, RealSuggestionsDetector,
            ColetorMetricas, AnalisadorMetricas
        )
        return True, locals()
    except ImportError as e:
        logger.warning(f"Services module error: {e}")
        return False, {}

services_loaded, services = load_services()
```

#### **5.2 Inicialização condicional**
```python
if services_loaded:
    system_state.diagnostic_service = services['DiagnosticoSistema']()
    system_state.suggestions_detector = services['RealSuggestionsDetector']()
```

---

## ⚡ **Execução Imediata: Correções Críticas**

### **🔥 Correção 1: MetricasSistema centralizada**
```bash
# Criar estrutura de models
mkdir -p autocura/core/models
# Mover definição central de MetricasSistema
```

### **🔥 Correção 2: Prometheus Singleton**
```bash
# Resolver conflito de timeseries imediatamente
# Implementar registry singleton
```

### **🔥 Correção 3: Imports em diagnostico**
```bash
# Corrigir importações que quebram o carregamento
# Atualizar paths de `src.` para `autocura.`
```

---

## 📊 **Cronograma de Implementação**

| Etapa | Prioridade | Tempo Estimado | Status |
|-------|------------|---------------|--------|
| **MetricasSistema central** | 🔥 Crítico | 15 min | Pendente |
| **Prometheus singleton** | 🔥 Crítico | 20 min | Pendente |
| **Imports diagnostico** | 🔥 Crítico | 10 min | Pendente |
| **Services completos** | 🟡 Alto | 45 min | Pendente |
| **Security module** | 🟢 Médio | 30 min | Pendente |

---

## 🎯 **Resultado Esperado**

### **Antes (Atual):**
- Core: ✅ 1/4 módulos funcionais
- Services: ❌ 0/6 serviços carregados
- Monitoring: ❌ Conflito Prometheus
- Security: ❌ Não implementado

### **Depois (Objetivo):**
- Core: ✅ 4/4 módulos funcionais  
- Services: ✅ 6/6 serviços carregados
- Monitoring: ✅ 3/3 sistemas operacionais
- Security: ✅ 2/2 módulos implementados

---

## 🚀 **Comandos para Execução**

```bash
# 1. Criar estrutura de models
mkdir -p autocura/core/models

# 2. Testar após cada correção
curl http://localhost:8001/api/health

# 3. Rebuild Docker após correções
docker-compose -f deployment/docker/docker-compose.modular.yml build

# 4. Validar sistema completo
python validate_modular_system.py
```

---

*Plano criado em: 2025-05-27 15:40:00*  
*Objetivo: Carregamento completo de todos os módulos* 🚀 