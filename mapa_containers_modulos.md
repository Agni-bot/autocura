# 🐳 Mapa de Containers e Módulos - Sistema AutoCura

## 📋 **Containers Ativos e Localização dos Módulos**

### **🏗️ Arquitetura de Containers**

```
Sistema AutoCura - Dual Deployment
├── autocura-api-modular (porta 8001) 🆕 NOVO
├── autocura-api (porta 8000)         📁 ORIGINAL  
├── autocura-redis (porta 6379)       💾 CACHE
└── autocura-postgres (porta 5432)    🗄️ DATABASE
```

---

## 🆕 **Container: `autocura-api-modular` (Nova Estrutura)**

### **📍 Localização:** `docker-autocura-api-modular:latest`
### **🌐 Porta:** 8001
### **📁 Estrutura Interna:**

```
/app/
├── autocura/                    🏗️ NOVA ESTRUTURA MODULAR
│   ├── core/                   ✅ CARREGADO (1/4 módulos funcionais)
│   │   ├── memoria/            ✅ gerenciador_memoria.py, registrador_contexto.py
│   │   ├── messaging/          ✅ universal_bus.py  
│   │   ├── interfaces/         ✅ universal_interface.py
│   │   ├── self_modify/        ✅ safe_code_generator.py, evolution_sandbox.py
│   │   ├── plugins/            ✅ plugin_manager.py
│   │   └── registry/           ✅ capability_registry.py
│   │
│   ├── services/               ⚠️ PARCIALMENTE CARREGADO
│   │   ├── ia/                 ❌ não carregado (cliente_ia.py, agente_adaptativo.py)
│   │   ├── diagnostico/        ❌ não carregado (diagnostico.py, real_suggestions.py)
│   │   ├── monitoramento/      ❌ não carregado (coletor_metricas.py, analisador_metricas.py)
│   │   ├── etica/              ❌ não carregado (validador_etico.py, circuitos_morais.py)
│   │   ├── guardiao/           ❌ não carregado (guardiao_cognitivo.py)
│   │   └── gerador/            ❌ não carregado (gerador_automatico.py)
│   │
│   ├── monitoring/             ❌ NÃO CARREGADO
│   │   ├── metrics/            ❌ gerenciador_metricas.py (conflito timeseries)
│   │   ├── observability/      ❌ observabilidade.py
│   │   └── integration/        ❌ dashboard_bridge.py
│   │
│   ├── security/               ❌ NÃO CARREGADO  
│   │   └── criptografia/       ❌ quantum_safe_crypto.py
│   │
│   ├── utils/                  ✅ ESTRUTURA CRIADA
│   │   ├── logging/            ✅ logger.py
│   │   ├── cache/              ✅ redis_cache.py
│   │   └── config/             ✅ manager.py
│   │
│   └── api/                    ✅ ESTRUTURA CRIADA
│       ├── routes/             ✅ (estrutura preparada)
│       ├── middleware/         ✅ (estrutura preparada)
│       └── models/             ✅ (estrutura preparada)
│
├── main_modular.py             ✅ EXECUTANDO (FastAPI app)
├── dashboard.html              ✅ disponível
├── memoria_compartilhada.json  ✅ acessível
└── requirements.txt            ✅ instalado
```

### **🔧 Status dos Módulos no Container Modular:**
- **Core:** ✅ Funcionando (memoria, interfaces, messaging)
- **Services:** ❌ Falha na importação (problema com MetricasSistema resolvido parcialmente)
- **Monitoring:** ❌ Conflito de timeseries no Prometheus
- **Security:** ❌ Não implementado completamente

---

## 📁 **Container: `autocura-api` (Estrutura Original)**

### **📍 Localização:** `docker-autocura-api:latest`  
### **🌐 Porta:** 8000
### **📁 Estrutura Interna:**

```
/app/
├── src/                        📁 ESTRUTURA ORIGINAL
│   ├── core/                   ✅ TOTALMENTE FUNCIONAL
│   │   ├── memoria/            ✅ gerenciador_memoria.py
│   │   ├── self_modify/        ✅ safe_code_generator.py, evolution_controller.py
│   │   ├── messaging/          ✅ universal_bus.py
│   │   └── ...                 ✅ todos módulos funcionais
│   │
│   ├── services/               ✅ TOTALMENTE FUNCIONAL
│   │   ├── ia/                 ✅ cliente_ia.py, agente_adaptativo.py
│   │   ├── diagnostico/        ✅ diagnostico.py, real_suggestions.py
│   │   ├── monitoramento/      ✅ coletor_metricas.py
│   │   └── ...                 ✅ todos serviços funcionais
│   │
│   ├── monitoring/             ✅ TOTALMENTE FUNCIONAL
│   │   ├── metrics/            ✅ gerenciador_metricas.py
│   │   └── ...                 ✅ sem conflitos
│   │
│   └── seguranca/              ✅ FUNCIONAL
│       └── criptografia.py     ✅ implementado
│
├── main.py                     ✅ EXECUTANDO (sistema original)
└── ...                         ✅ todos arquivos originais
```

### **🔧 Status dos Módulos no Container Original:**
- **Todos os módulos:** ✅ 100% funcionais
- **IA com OpenAI:** ✅ Operacional
- **Auto-modificação:** ✅ Validada
- **Sistema completo:** ✅ Pronto para produção

---

## 💾 **Container: `autocura-redis` (Cache Distribuído)**

### **📍 Localização:** `redis:7-alpine`
### **🌐 Porta:** 6379  
### **🔧 Função:**
- **Cache de sessões** para ambos os sistemas
- **Message queue** para comunicação entre módulos
- **Armazenamento temporário** de métricas
- **Cache de resultados** de IA e análises

### **📊 Uso pelos Sistemas:**
- ✅ **Sistema Original (8000):** Conectado e funcionando
- ⚠️ **Sistema Modular (8001):** Conectado mas uso limitado

---

## 🗄️ **Container: `autocura-postgres` (Banco de Dados)**

### **📍 Localização:** `postgres:15-alpine`
### **🌐 Porta:** 5432
### **🔧 Função:**
- **Persistência de dados** de ambos os sistemas
- **Histórico de métricas** e eventos
- **Configurações de sistema**
- **Logs de evolução** e auto-modificação

### **📊 Uso pelos Sistemas:**
- ✅ **Sistema Original (8000):** Conectado e funcionando
- ⚠️ **Sistema Modular (8001):** Conectado mas esquemas limitados

---

## 🔄 **Mapeamento de Comunicação entre Containers**

```
┌─────────────────────┐    ┌─────────────────────┐
│  autocura-api       │    │ autocura-api-modular│
│  (Original - 8000)  │    │ (Modular - 8001)    │
│  ✅ COMPLETO        │    │ ⚠️ PARCIAL          │
└─────────┬───────────┘    └─────────┬───────────┘
          │                          │
          ├────────┬─────────────────┤
          │        │                 │
          ▼        ▼                 ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│autocura-redis│ │autocura-    │ │  Volumes    │
│   (Cache)   │ │ postgres    │ │  Shared     │
│ ✅ FUNCIONAL│ │ (Database)  │ │ ✅ MONTADOS │
└─────────────┘ └─────────────┘ └─────────────┘
```

---

## 📊 **Resumo de Localização por Funcionalidade**

| Funcionalidade | Container Original (8000) | Container Modular (8001) | Status |
|----------------|---------------------------|--------------------------|--------|
| **Core Memory** | ✅ src/core/memoria/ | ✅ autocura/core/memoria/ | Dual |
| **IA Services** | ✅ src/services/ia/ | ❌ autocura/services/ia/ | Original apenas |
| **Auto-Modify** | ✅ src/core/self_modify/ | ✅ autocura/core/self_modify/ | Dual |
| **Monitoring** | ✅ src/monitoring/ | ❌ autocura/monitoring/ | Original apenas |
| **Security** | ✅ src/seguranca/ | ❌ autocura/security/ | Original apenas |
| **API Endpoints** | ✅ Completa | ⚠️ Parcial | Original + Modular |

---

## 🎯 **Status Atual de Cada Sistema**

### **🟢 Sistema Original (8000) - 100% Operacional:**
- Todos os módulos carregados e funcionais
- IA, auto-modificação, monitoramento ativos
- Pronto para produção imediata
- Backup mantido e funcional

### **🟡 Sistema Modular (8001) - 25% Operacional:**
- Apenas módulo Core carregado
- Estrutura criada mas imports falhando
- Fallbacks funcionando
- Base sólida para evolução

### **🔵 Infraestrutura (Redis + PostgreSQL) - 100% Operacional:**
- Ambos sistemas conectados
- Cache e persistência funcionais
- Monitoramento de saúde ativo

---

## 🚀 **Recomendações para Completar a Migração**

### **Imediato:**
1. **Corrigir imports** dos módulos services no container modular
2. **Resolver conflito** de timeseries no Prometheus
3. **Implementar security** module completo

### **Próxima Fase:**
1. **Migrar gradualmente** funcionalidades do original para modular
2. **Testar isoladamente** cada módulo no container modular
3. **Configurar load balancer** entre os dois sistemas

---

*Mapeamento atualizado em: 2025-05-27 15:35:00*  
*Status: Dual deployment operacional com sistema original completo* 