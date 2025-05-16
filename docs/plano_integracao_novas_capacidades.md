# Plano de Estrutura e Integração para Novas Capacidades do Módulo de Consciência Situacional

## 1. Introdução

Este documento detalha o plano para a estruturação e integração das novas capacidades modulares no sistema de Consciência Situacional do projeto Autocura. O objetivo é estender as funcionalidades existentes de forma modular, não intrusiva, com isolamento de componentes e ativação condicional, conforme os requisitos fornecidos.

## 2. Princípios Gerais de Design

As seguintes diretrizes serão seguidas:

*   **Modularidade**: Cada nova capacidade será desenvolvida como um conjunto coeso de módulos ou, se necessário, como um microsserviço independente.
*   **Não Intrusividade**: As alterações no código existente do `conscienciaSituacional/core.py` serão minimizadas, focando na orquestração e agregação de dados dos novos módulos.
*   **Ativação Condicional**: A utilização de cada nova capacidade será controlada por flags de configuração (preferencialmente via Helm `values.yaml` e variáveis de ambiente), permitindo que sejam habilitadas ou desabilitadas dinamicamente.
*   **Isolamento de Dependências**: Módulos com dependências pesadas ou conflitantes (ex: TensorFlow, MetaTrader5) terão seus próprios `requirements.txt` e, se necessário, `Dockerfile` e deployment Kubernetes separados.
*   **Comunicação**: A comunicação entre o `conscienciaSituacional` e quaisquer novos microsserviços (ex: um possível serviço de Finanças) se dará preferencialmente por APIs internas (REST/gRPC) ou, para fluxos de dados assíncronos, via Kafka. A comunicação interna dentro do mesmo serviço `conscienciaSituacional` será por chamadas diretas de Python.

## 3. Estrutura de Diretórios Proposta (Visão Geral)

```
/Autocura_project/Autocura/
├── src/
│   ├── conscienciaSituacional/
│   │   ├── futuro/                     # 2.1 Análise de Cenários Futuros
│   │   │   ├── __init__.py
│   │   │   ├── predictive_engine.py
│   │   │   ├── scenario_simulator.py
│   │   │   └── market_monitor.py
│   │   ├── tecnologiasEmergentes/      # 2.2 Adoção de Tecnologias Emergentes
│   │   │   ├── __init__.py
│   │   │   ├── sandbox_manager.py      # Orquestrador do Sandbox
│   │   │   ├── blockchain_adapter.py   # Adaptador para Hyperledger
│   │   │   └── edge_computing_adapter.py # Adaptador para EdgeIQ
│   │   ├── planejamento/               # 2.4 Integração com Planejamento Estratégico
│   │   │   ├── __init__.py
│   │   │   ├── roi_calculator.py
│   │   │   └── strategic_roadmap.py
│   │   ├── exemplos/                   # 2.5 Exemplo Prático: Logística
│   │   │   ├── __init__.py
│   │   │   └── logistica_optimizer.py
│   │   ├── monitoramento/              # 2.6 Monitoramento Contínuo
│   │   │   ├── __init__.py
│   │   │   └── metrics_exporter.py
│   │   ├── web/                        # Existente
│   │   ├── shared_utils/               # Existente
│   │   ├── __init__.py
│   │   ├── core.py                     # Existente, será atualizado
│   │   └── requirements.txt            # Existente, pode ser atualizado
│   ├── financas/                       # 2.3 Captação de Recursos Financeiros (Novo Serviço)
│   │   ├── __init__.py
│   │   ├── forex_trader.py
│   │   ├── crowdfunding_integrator.py
│   │   ├── risk_manager.py
│   │   ├── api.py                      # Ponto de entrada da API para este serviço
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── ... (outros módulos existentes)
├── config/
│   └── ... (configurações existentes e novas, como para o módulo financas)
├── charts/
│   ├── ConscienciaSituacional/       # Helm Chart existente, será atualizado
│   │   └── ...
│   └── FinancasService/              # Novo Helm Chart para o serviço de Finanças
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           └── ...
└── ...
```

## 4. Planejamento Detalhado por Capacidade

### 4.1. Análise de Cenários Futuros e Previsibilidade
*   **Localização**: `src/conscienciaSituacional/futuro/`
*   **Componentes**: `predictive_engine.py`, `scenario_simulator.py`, `market_monitor.py`.
*   **Integração**: `conscienciaSituacional/core.py` instanciará e chamará classes/métodos destes módulos condicionalmente (flag: `features.futuro.enabled`). Os resultados serão agregados à mensagem enviada ao tópico `autocura.estrategia`.
*   **Isolamento**: Se `predictive_engine.py` (com TensorFlow/PyTorch) se tornar muito pesado, poderá ser refatorado para um serviço separado no futuro. Inicialmente, será um módulo Python. `market_monitor.py` usará bibliotecas de scraping padrão.
*   **Configuração**: Caminhos para modelos ML, URLs para scraping, chaves de API (se necessárias para relatórios pagos) via `values.yaml` do Helm de `ConscienciaSituacional` e variáveis de ambiente.

### 4.2. Adoção de Tecnologias Emergentes
*   **Localização**: `src/conscienciaSituacional/tecnologiasEmergentes/`
*   **Componentes**: `sandbox_manager.py`, `blockchain_adapter.py`, `edge_computing_adapter.py`.
*   **Integração**: O `sandbox_manager.py` será o ponto de entrada. A ativação e configuração do sandbox (recursos, tecnologias específicas) serão controladas via Helm (`features.tecnologiasEmergentes.sandbox.enabled`, `features.tecnologiasEmergentes.sandbox.resources`, etc.). O `conscienciaSituacional/core.py` poderá interagir com o `sandbox_manager` para obter status ou resultados de experimentos, se relevante para o contexto do diagnóstico.
*   **Isolamento**: O "sandbox" em si, conforme descrito com recursos Kubernetes dedicados, sugere que as tecnologias testadas (ex: um nó Hyperledger) rodariam em seus próprios pods, orquestrados possivelmente por um operador ou scripts gerenciados pelo `sandbox_manager`. As integrações (`blockchain_adapter`, `edge_computing_adapter`) no código do `conscienciaSituacional` seriam clientes para esses sistemas em sandbox.
*   **Configuração**: Endereços dos serviços em sandbox, credenciais, via `values.yaml` e Secrets.

### 4.3. Captação de Recursos Financeiros
*   **Localização**: Novo microsserviço em `src/financas/`.
*   **Componentes**: `forex_trader.py`, `crowdfunding_integrator.py`, `risk_manager.py`, `api.py` (Flask/FastAPI).
*   **Integração**: O serviço `FinancasService` exporá uma API interna. O `conscienciaSituacional/core.py`, se habilitado (flag: `features.financas.enabled`), fará chamadas a esta API para obter dados de "alocacao_recursos".
*   **Isolamento**: Totalmente isolado em seu próprio Docker container e deployment Kubernetes, com suas dependências (`MetaTrader5`, etc.) gerenciadas em seu `requirements.txt` e `Dockerfile`. Terá seu próprio Helm Chart (`charts/FinancasService/`).
*   **Configuração**: Credenciais da API MetaTrader5, chaves da API Kickstarter, limites de risco, via `values.yaml` do Helm `FinancasService` e Kubernetes Secrets.

### 4.4. Integração com Planejamento Estratégico
*   **Localização**: `src/conscienciaSituacional/planejamento/`
*   **Componentes**: `roi_calculator.py`, `strategic_roadmap.py`.
*   **Integração**: `conscienciaSituacional/core.py` utilizará estes módulos (flag: `features.planejamento.enabled`) para gerar análises de ROI e sugestões de roadmap, que serão incluídas na mensagem para `autocura.estrategia` (ex: na seção `tecnologias_recomendadas`).
*   **Isolamento**: Módulos Python padrão, sem dependências pesadas previstas.
*   **Configuração**: Parâmetros para modelos de ROI (taxa de desconto, etc.) via `values.yaml` do Helm `ConscienciaSituacional`.

### 4.5. Exemplo Prático: Sistema de Logística
*   **Localização**: `src/exemplos/logistica/`
*   **Componentes**: `logistics_optimizer.py`.
*   **Integração**: Este módulo servirá como um exemplo de orquestração que utiliza outras capacidades (ex: `DemandPredictor` de `futuro/`, `BlockchainTracker` de `tecnologiasEmergentes/`). Não será diretamente integrado ao fluxo principal do `conscienciaSituacional/core.py`, mas pode ser executado como um script de demonstração ou um serviço de exemplo separado se necessário.
*   **Isolamento**: Dependerá dos módulos que utiliza.
*   **Configuração**: Específica do exemplo.

### 4.6. Monitoramento Contínuo
*   **Localização**: `src/conscienciaSituacional/monitoramento/metrics_exporter.py` e, similarmente, em `src/financas/metrics_exporter.py` se este for um serviço separado.
*   **Componentes**: `metrics_exporter.py` (usando `prometheus_client`).
*   **Integração**: O `metrics_exporter` será inicializado no `core.py` (e no `api.py` do `FinancasService`) para expor um endpoint `/metrics`. A configuração do Prometheus (`prometheus.yml`) será externa ao projeto, mas o projeto fornecerá a documentação de quais métricas são expostas e como configurar o scrape.
*   **Isolamento**: Biblioteca Python padrão.
*   **Configuração**: Nenhuma configuração específica no Helm, além de garantir que o endpoint de métricas esteja acessível.

## 5. Atualizações no `conscienciaSituacional/core.py`

O `core.py` será modificado para:

1.  Ler as flags de ativação de features do ambiente (originadas do Helm `values.yaml`).
2.  Condicionalmente importar e instanciar os novos módulos internos (Futuro, Planejamento, adaptadores de Tecnologias Emergentes, Monitoramento).
3.  Condicionalmente chamar a API do `FinancasService` se habilitado.
4.  Orquestrar a coleta de dados dessas novas fontes.
5.  Agregar os dados coletados ao payload da mensagem enviada para o tópico `autocura.estrategia`, seguindo a estrutura de saída JSON de exemplo.

## 6. Atualizações no Helm Chart `ConscienciaSituacional`

O `charts/ConscienciaSituacional/values.yaml` será estendido para incluir:

*   Seção `features` com subseções para habilitar/desabilitar cada nova capacidade (ex: `futuro.enabled`, `planejamento.enabled`, `tecnologiasEmergentes.sandbox.enabled`, `financas.enabled` (para controlar a chamada à API do serviço de finanças)).
*   Configurações específicas para cada módulo habilitado (caminhos de modelo, URLs, parâmetros de sandbox, endereço da API do `FinancasService`).
*   Se o sandbox de tecnologias emergentes for gerenciado como parte deste deployment, seções para seus recursos e configurações.

## 7. Novo Helm Chart: `FinancasService`

Será criado um novo Helm Chart em `charts/FinancasService/` para o deployment independente do microsserviço de Finanças. Este chart incluirá:

*   Deployment e Service manifests.
*   Configuração para imagem Docker, réplicas, recursos.
*   Montagem de Secrets para credenciais (MT5, Kickstarter).
*   ConfigMaps para configurações específicas do serviço de finanças.

## 8. Formato da Mensagem Enriquecida (Exemplo)

A mensagem enviada ao tópico `autocura.estrategia` será estendida para incluir os novos campos, conforme o exemplo:

```json
{
  "id_diagnostico": "...",
  "timestamp": "...",
  // ... campos existentes do diagnóstico ...
  "contexto_web": {
    // ... dados existentes do WebDataMiner ...
  },
  "previsao_demanda": { /* Dados do predictive_engine.py */ },
  "simulacao_cenario_hardware": { /* Dados do scenario_simulator.py */ },
  "insights_mercado": [ /* Dados do market_monitor.py */ ],
  "tecnologias_recomendadas": [
    { "nome": "Edge Computing", "roi_esperado": "37%", "sandbox_status": "testes_em_andamento", "roadmap_sugerido": "..." }
    /* Dados do roi_calculator.py, strategic_roadmap.py, sandbox_manager.py */
  ],
  "alocacao_recursos_financeiros": { /* Dados do FinancasService */ },
  "metricas_consciencia_situacional": { /* Métricas internas, se relevante para estratégia */ }
}
```

Este plano servirá como base para a implementação das novas capacidades, garantindo uma abordagem estruturada e alinhada com os requisitos do projeto.

