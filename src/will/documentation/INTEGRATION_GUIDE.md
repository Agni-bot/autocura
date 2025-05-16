# Guia de Integração do Sistema Will

Este documento descreve como integrar o Sistema Will com outros módulos, especialmente dentro de um Sistema de Autocura Cognitiva. O Will expõe uma API RESTful para facilitar essa interação.

## 1. Visão Geral da API

O Sistema Will fornece os seguintes endpoints principais:

*   **`POST /api/will/decision`**: Submete dados de entrada para o Will e recebe uma decisão de trading ou análise.
*   **`GET /api/will/status`**: Obtém o status operacional atual do sistema Will.

Todas as respostas da API são em formato JSON.

## 2. Configuração e Deploy

O sistema Will é projetado para ser executado como um contêiner Docker.

### Pré-requisitos

*   Docker instalado
*   Docker Compose instalado (opcional, mas recomendado para facilidade de deploy)

### Arquivos de Deploy

*   `Dockerfile`: Define como construir a imagem Docker para a API do Will.
*   `docker-compose.yml`: Facilita a execução do contêiner Will, gerenciando portas e configurações de ambiente.
*   `requirements.txt`: Lista as dependências Python necessárias.

### Executando com Docker Compose

1.  Navegue até o diretório `will_system_enhancements`.
2.  Execute o comando: `docker-compose up -d`

Isso construirá a imagem (se ainda não existir) e iniciará o contêiner da API do Will, que estará acessível em `http://localhost:5000`.

### Configuração da Chave da API Gemini

A integração com o Gemini 2.5 Pro requer uma chave de API. Esta chave deve ser fornecida ao sistema Will. A forma preferencial é através de variáveis de ambiente ao executar o contêiner. No `docker-compose.yml`, você pode descomentar e configurar a variável `GEMINI_API_KEY`.

Alternativamente, o módulo `GeminiConfigHandler` dentro do sistema Will (se implementado de forma interativa e acessível pela API, o que não é o caso desta API RESTful de exemplo) poderia solicitar a chave e salvá-la. Para esta API, a configuração via variável de ambiente é a mais indicada.

## 3. Endpoints da API em Detalhe

### 3.1. `POST /api/will/decision`

Este endpoint é usado para solicitar uma decisão de trading ou análise do sistema Will.

*   **Método:** `POST`
*   **Content-Type:** `application/json`
*   **Corpo da Requisição (Exemplo de Payload de Entrada):**

    ```json
    {
        "request_id": "REQ12345",
        "timestamp": "2025-05-09T10:20:00Z",
        "source_module": "CognitiveCoreOrchestrator",
        "asset": "EUR/USD",
        "timeframe": "H1",
        "market_conditions": {
            "volatility_index": 25.5,
            "current_price": 1.0855,
            "recent_news_sentiment_score": 0.65
        },
        "requested_volume": 50000,
        "additional_parameters": {
            "user_risk_profile": "balanced",
            "max_slippage_allowed_bps": 5
        }
    }
    ```

*   **Resposta de Sucesso (200 OK) (Exemplo de Payload de Saída):**

    ```json
    {
        "timestamp": "2025-05-09T10:20:05Z",
        "input_parameters": {
            "request_id": "REQ12345",
            "asset": "EUR/USD",
            "requested_volume": 50000
        },
        "decision_engine_version": "1.0.0-enh",
        "trade_signal": "BUY",
        "confidence_score": 0.95,
        "target_asset": "EUR/USD",
        "recommended_volume": 45000,
        "risk_assessment": "MODERATE",
        "supporting_factors": [
            "Positive sentiment spike",
            "Favorable macroeconomic indicator XYZ"
        ],
        "gemini_analysis_summary": "Gemini Pro 2.5 suggests a short-term bullish trend based on correlated news events.",
        "execution_parameters": {
            "order_type": "LIMIT",
            "limit_price": 1.0857,
            "stop_loss_price": 1.0830,
            "take_profit_price": 1.0900
        }
    }
    ```

*   **Resposta de Erro (Ex: 400 Bad Request):**

    ```json
    {
        "error": "Invalid input data",
        "message": "O campo 'asset' é obrigatório."
    }
    ```

### 3.2. `GET /api/will/status`

Este endpoint retorna o status operacional atual do sistema Will.

*   **Método:** `GET`
*   **Resposta de Sucesso (200 OK) (Exemplo de Payload de Saída):**

    ```json
    {
        "timestamp": "2025-05-09T10:21:00Z",
        "system_name": "Will Predictive Trading System",
        "version": "1.0.0-enh",
        "status": "OPERATIONAL",
        "active_models": ["TemporalLSTM", "ProbabilisticBN", "GeminiProIntegration"],
        "last_decision_time": "2025-05-09T10:20:05Z",
        "data_feed_status": {
            "market_data_api": "CONNECTED",
            "geospatial_api": "CONNECTED",
            "news_feed_api": "DISCONNECTED_MAINTENANCE"
        },
        "system_health_metrics": {
            "cpu_load_avg": 0.38,
            "memory_usage_gb": 2.6,
            "api_latency_ms_avg": 70
        },
        "alerts": [
            {"level": "WARNING", "message": "News feed API is currently undergoing maintenance."}
        ]
    }
    ```

## 4. Logs Estruturados

O sistema Will (especificamente a API `app.py`) está configurado para gerar logs em formato JSON. Isso facilita a coleta, análise e monitoramento dos logs por ferramentas como ELK Stack, Splunk, ou outras soluções de observabilidade.

**Exemplo de Log JSON:**

```json
{
    "asctime": "2025-05-09 10:15:00,123",
    "levelname": "INFO",
    "name": "will_api_logger",
    "module": "app",
    "funcName": "get_will_decision_mock",
    "lineno": 35,
    "message": "Decision generated successfully",
    "decision": {
        "timestamp": "2025-05-09T10:15:00Z", 
        "trade_signal": "BUY", 
        "confidence_score": 0.95
    }
}
```

## 5. Considerações Adicionais para Integração

*   **Autenticação/Autorização:** A API de exemplo atual não implementa autenticação. Em um ambiente de produção, endpoints devem ser protegidos (ex: API Keys, OAuth2).
*   **Tratamento de Erros:** A API retorna códigos de status HTTP apropriados e mensagens de erro em JSON.
*   **Versionamento da API:** Considere implementar versionamento da API (ex: `/api/v1/will/decision`) para futuras atualizações sem quebrar integrações existentes.
*   **Limites de Taxa (Rate Limiting):** Para proteger o sistema contra abuso, implemente limites de taxa nos endpoints da API.

Este guia deve fornecer as informações necessárias para integrar o Sistema Will com outros componentes do Sistema de Autocura Cognitiva. Para mais detalhes sobre a lógica interna do Will, consulte a documentação técnica principal do sistema.

