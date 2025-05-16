# Relatório de Inclusão: Microsserviço de Consciência Situacional

## 1. Introdução

Este relatório detalha a inclusão do novo microsserviço de Consciência Situacional ao projeto Autocura. O objetivo deste módulo é enriquecer os diagnósticos gerados pelo sistema com informações contextuais relevantes obtidas de fontes externas da web, como notícias globais, indicadores econômicos e dados climáticos. Este enriquecimento visa aprimorar a tomada de decisão do sistema, fornecendo uma perspectiva mais ampla sobre os eventos e anomalias detectados.

O microsserviço foi projetado para operar de forma assíncrona, integrando-se ao fluxo de dados existente através de tópicos Apache Kafka.

## 2. Arquitetura e Funcionalidades Implementadas

O microsserviço `consciencia-situacional-service` foi implementado em Python e estruturado da seguinte forma:

*   **Diretório Principal**: `/home/ubuntu/Autocura_project/Autocura/src/conscienciaSituacional/`
    *   `core.py`: Contém a lógica principal do serviço, incluindo a inicialização, conexão com Kafka, consumo de mensagens do tópico de diagnóstico, orquestração da coleta de dados web, enriquecimento da mensagem e produção para o tópico de estratégia.
    *   `requirements.txt`: Lista as dependências Python do serviço.
    *   **Subdiretório `web/`**:
        *   `data_sources.py`: Implementa a classe `WebDataMiner`, responsável por interagir com APIs externas para coletar notícias, dados financeiros e climáticos. Inclui mecanismos de retry para chamadas de API.
        *   `validation.py`: Contém funções para validar os dados coletados da web, como checagem de anomalias temporais e verificação contra uma whitelist de domínios (carregada de `config/whitelist.yaml`).
        *   `rate_limiter.py`: Implementa um `APIRateLimiter` baseado em Token Bucket para controlar a frequência de chamadas às APIs externas, evitando sobrecarga e bloqueios.
    *   **Subdiretório `shared_utils/`**:
        *   `cache.py`: Implementa um `RedisCache` e um decorador `@cache` para armazenar em cache os resultados das chamadas às APIs externas, otimizando o desempenho e reduzindo o número de requisições repetidas. A conexão com Redis é configurável via variáveis de ambiente.
*   **Arquivos de Configuração**: Localizados em `/home/ubuntu/Autocura_project/Autocura/config/`
    *   `whitelist.yaml`: Define os domínios permitidos para fontes de notícias e outros dados.
    *   `api_endpoints.yaml`: Define os URLs primários e de fallback para as APIs externas. Estes podem ser sobrescritos por variáveis de ambiente ou configurações do Helm.
*   **Helm Chart**: Localizado em `/home/ubuntu/Autocura_project/Autocura/charts/ConscienciaSituacional/`
    *   `Chart.yaml` (não gerado, mas seria necessário para um chart completo)
    *   `values.yaml`: Permite a configuração de parâmetros de deployment, como número de réplicas, imagem Docker, URLs de Kafka e Redis, nomes de secrets para chaves de API, e recursos do pod.
    *   `templates/deployment.yaml`: Manifesto Kubernetes para o deployment do microsserviço. Inclui configuração de variáveis de ambiente (incluindo montagem de chaves de API a partir de Secrets) e montagem de ConfigMaps para os arquivos `whitelist.yaml` e `api_endpoints.yaml`.

### Funcionalidades Principais:

1.  **Consumo de Mensagens Kafka**: O serviço consome mensagens do tópico `autocura.diagnostico`.
2.  **Coleta de Dados Web**: Com base nas informações do diagnóstico (palavras-chave, localização), o `WebDataMiner` coleta:
    *   Eventos globais (notícias).
    *   Indicadores econômicos.
    *   Dados climáticos.
3.  **Rate Limiting**: Controla a taxa de chamadas às APIs externas.
4.  **Caching**: Utiliza Redis para cachear respostas das APIs, com TTLs configuráveis.
5.  **Validação de Dados**: Realiza validações básicas nos dados coletados, incluindo checagem contra whitelist de domínios.
6.  **Enriquecimento de Mensagem**: Adiciona os dados web coletados (`contexto_web`) à mensagem de diagnóstico original.
7.  **Produção de Mensagens Kafka**: Publica a mensagem enriquecida no tópico `autocura.estrategia`.
8.  **Configurabilidade**: Altamente configurável via variáveis de ambiente e Helm `values.yaml` para adaptação a diferentes ambientes.
9.  **Observabilidade**: Logs detalhados são gerados para rastrear o processamento das mensagens e interações com serviços externos.

## 3. Integração com o Sistema Autocura

O microsserviço Consciência Situacional se posiciona no fluxo de processamento do Autocura da seguinte maneira:

1.  O **Módulo de Diagnóstico** publica suas descobertas no tópico Kafka `autocura.diagnostico`.
2.  O **Microsserviço de Consciência Situacional** consome essas mensagens.
3.  Para cada diagnóstico, ele busca informações contextuais relevantes na web.
4.  A mensagem de diagnóstico original é enriquecida com o `contexto_web`.
5.  A mensagem enriquecida é publicada no tópico Kafka `autocura.estrategia`.
6.  O **Módulo Gerador de Ações/Estratégia** consome as mensagens enriquecidas deste tópico para tomar decisões mais informadas.

Esta integração é totalmente desacoplada, dependendo apenas da disponibilidade do broker Kafka e da correta definição dos tópicos e schemas de mensagem.

## 4. Instruções de Implantação e Configuração

As instruções detalhadas para build da imagem Docker, configuração de ConfigMaps/Secrets no Kubernetes e implantação via Helm Chart foram fornecidas no arquivo `instrucoes_teste_kafka.md`. Recomenda-se seguir rigorosamente essas instruções para garantir uma implantação bem-sucedida.

**Pontos Chave da Configuração (via `values.yaml` do Helm Chart):**

*   **Imagem Docker**: Especifique o repositório e tag corretos.
*   **Conexão Kafka**: Forneça o `broker_url` correto.
*   **Conexão Redis**: Configure `redis.host` e `redis.port`. O cache pode ser desabilitado se `REDIS_ENABLED` for `false` (ou se a conexão falhar).
*   **Chaves de API**: As chaves para News, Finance e Climate APIs devem ser armazenadas em Secrets do Kubernetes e seus nomes referenciados em `web_integration.apis.*.key_secret_name`.
*   **Endpoints de API e Whitelist**: Os arquivos `api_endpoints.yaml` e `whitelist.yaml` são montados via ConfigMaps. Os nomes desses ConfigMaps podem ser definidos em `api_configmap_name` e `whitelist_configmap_name`.

## 5. Testes e Validação

Conforme detalhado no arquivo `instrucoes_teste_kafka.md`, os testes completos do fluxo Kafka e a validação da funcionalidade do cache Redis devem ser realizados em um ambiente integrado que possua instâncias de Kafka e Redis acessíveis.

**Resumo dos Testes a Serem Realizados no Ambiente Integrado:**

1.  **Conectividade**: Verificar logs para confirmar conexão bem-sucedida com Kafka e Redis.
2.  **Fluxo de Mensagens**: Produzir uma mensagem de teste no tópico `autocura.diagnostico` e verificar se uma mensagem enriquecida é produzida no tópico `autocura.estrategia`.
3.  **Conteúdo do Enriquecimento**: Validar se o campo `contexto_web` na mensagem de saída contém dados relevantes e corretos.
4.  **Funcionamento do Cache**: Enviar diagnósticos similares e verificar (via logs e tempo de resposta) se o cache Redis está sendo utilizado.
5.  **Rate Limiting e Retries**: Observar o comportamento em caso de múltiplas chamadas (difícil de simular sem carga) e a resiliência a falhas temporárias de API (mecanismo de retry).
6.  **Validação e Whitelist**: Testar com fontes diversas para garantir que a validação e a whitelist funcionem conforme esperado.

## 6. Considerações Adicionais e Próximos Passos

*   **Segurança das Chaves de API**: É crucial que as chaves de API sejam gerenciadas de forma segura usando Kubernetes Secrets e que o acesso a esses secrets seja restrito.
*   **Monitoramento e Alertas**: Em um ambiente de produção, configurar monitoramento para o microsserviço, incluindo a saúde das conexões Kafka/Redis, latência de processamento, taxa de erros nas chamadas de API externas e utilização de recursos.
*   **Schema de Mensagens**: Definir e versionar formalmente os schemas das mensagens trocadas via Kafka (ex: usando Avro e um Schema Registry) para garantir a compatibilidade entre os microsserviços.
*   **Tratamento de Erros e Dead-Letter Queues (DLQ)**: Implementar estratégias mais robustas para tratamento de erros persistentes na comunicação com Kafka ou no processamento de mensagens, como o uso de DLQs.
*   **Evolução do WebDataMiner**: As fontes de dados e os parsers no `WebDataMiner` são exemplos e podem precisar de adaptação e expansão para APIs específicas e mais robustas, conforme os requisitos de qualidade e cobertura da informação evoluam.
*   **Testes Unitários e de Integração**: Desenvolver um conjunto abrangente de testes unitários para os componentes individuais e testes de integração para os fluxos internos do microsserviço.

## 7. Artefatos Entregues

Junto com este relatório, os seguintes artefatos principais são disponibilizados:

*   **Código Fonte Completo do Microsserviço**: `/home/ubuntu/Autocura_project/Autocura/src/conscienciaSituacional/`
*   **Arquivos de Configuração Base**: `/home/ubuntu/Autocura_project/Autocura/config/` (contendo `whitelist.yaml` e `api_endpoints.yaml`)
*   **Helm Chart para Deployment**: `/home/ubuntu/Autocura_project/Autocura/charts/ConscienciaSituacional/`
*   **Instruções para Teste em Ambiente com Kafka**: `/home/ubuntu/instrucoes_teste_kafka.md`

Este novo microsserviço representa um passo importante para aumentar a inteligência e a capacidade de resposta do sistema Autocura. Recomenda-se uma revisão cuidadosa dos artefatos e um processo de teste completo no ambiente de destino.

