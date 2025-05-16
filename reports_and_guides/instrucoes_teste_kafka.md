# Instruções para Teste e Validação do Microsserviço Consciência Situacional com Kafka

## Limitação do Ambiente de Teste Atual

O microsserviço Consciência Situacional foi desenvolvido e testado localmente em relação à sua lógica interna, estrutura de arquivos, configurações e integrações web (simuladas com chaves dummy e endpoints de exemplo). No entanto, o ambiente de desenvolvimento atual não possui um broker Kafka (esperado em `kafka:9092`) nem um servidor Redis (esperado em `localhost:6379`) acessíveis para testes de integração completos.

Devido a essa limitação, não foi possível validar o fluxo de mensagens ponta a ponta via Kafka (consumo do tópico `autocura.diagnostico` e produção para `autocura.estrategia`) nem o funcionamento efetivo do cache com Redis neste ambiente.

## Próximos Passos: Teste em Ambiente Integrado

Para validar completamente o microsserviço Consciência Situacional, é crucial implantá-lo e testá-lo em um ambiente que possua Kafka e Redis configurados e acessíveis, como:

1.  **Ambiente Docker Compose Local**: Se você possui um `docker-compose.yml` que orquestra os demais microsserviços do sistema Autocura, incluindo Kafka e Redis, adicione o serviço `consciencia-situacional-service` a essa composição.
2.  **Cluster Kubernetes (Desenvolvimento/Homologação)**: Utilize o Helm Chart fornecido (`/home/ubuntu/Autocura_project/Autocura/charts/ConscienciaSituacional`) para implantar o microsserviço em um namespace de desenvolvimento ou homologação do seu cluster Kubernetes. Certifique-se de que as configurações de conexão com Kafka e Redis no `values.yaml` (ou via ConfigMaps/Secrets) apontem para as instâncias corretas no cluster.

## Instruções para Implantação e Teste

### 1. Build da Imagem Docker

Se ainda não o fez, construa a imagem Docker para o microsserviço:

```bash
cd /home/ubuntu/Autocura_project/Autocura/src/conscienciaSituacional
docker build -t seu-registro/consciencia-situacional-service:latest .
# Faça o push para o seu registro de container, se necessário
# docker push seu-registro/consciencia-situacional-service:latest
```

Lembre-se de substituir `seu-registro` pelo nome do seu Docker registry.

### 2. Configuração (Kubernetes via Helm)

Antes de implantar com Helm, revise e ajuste o arquivo `/home/ubuntu/Autocura_project/Autocura/charts/ConscienciaSituacional/values.yaml`:

*   **`image.repository`**: Verifique se aponta para a imagem Docker correta que você construiu/enviou.
*   **`image.tag`**: Defina a tag correta da imagem.
*   **`kafka.broker_url`**: Confirme o endereço do seu broker Kafka no cluster.
*   **`redis.host` / `redis.port`**: Confirme os detalhes de conexão do Redis.
*   **`web_integration.apis.*.key_secret_name`**: Certifique-se de que os Secrets do Kubernetes contendo as chaves de API para News, Finance e Climate (`NEWS_API_KEY`, `FINANCE_API_KEY`, `CLIMATE_API_KEY`) existem no namespace e estão corretamente nomeados aqui.
*   **`api_configmap_name`**: Nome do ConfigMap que deve conter o conteúdo do arquivo `config/api_endpoints.yaml`.
*   **`whitelist_configmap_name`**: Nome do ConfigMap que deve conter o conteúdo do arquivo `config/whitelist.yaml`.

**Criação dos ConfigMaps e Secrets (Exemplo)**:

Você precisará criar os ConfigMaps para `api_endpoints.yaml` e `whitelist.yaml`, e os Secrets para as chaves de API antes de instalar o Helm chart.

```bash
# Exemplo para ConfigMap de whitelist (adapte para api_endpoints)
kubectl create configmap consciencia-whitelist-config --from-file=/home/ubuntu/Autocura_project/Autocura/config/whitelist.yaml -n seu-namespace

# Exemplo para Secret de chave de API (adapte para as outras chaves)
kubectl create secret generic news-api-key-secret --from-literal=NEWS_API_KEY=\"sua_chave_news_api_aqui\" -n seu-namespace
```

### 3. Implantação (Kubernetes via Helm)

Instale o Helm chart:

```bash
helm install consciencia-situacional /home/ubuntu/Autocura_project/Autocura/charts/ConscienciaSituacional -n seu-namespace -f /home/ubuntu/Autocura_project/Autocura/charts/ConscienciaSituacional/values.yaml
```

### 4. Verificação e Teste do Fluxo Kafka

Após a implantação bem-sucedida:

*   **Verifique os Logs**: Monitore os logs do pod `consciencia-situacional-service` para garantir que ele se conectou ao Kafka e Redis (se habilitado) e que está pronto para consumir mensagens.
    ```bash
    kubectl logs -f <nome-do-pod-consciencia-situacional> -n seu-namespace
    ```
*   **Produza uma Mensagem de Teste**: Envie uma mensagem de exemplo para o tópico `autocura.diagnostico`. A mensagem deve ser um JSON com uma estrutura que o serviço espera (ex: contendo `entidades_detectadas` ou `termos_relevantes`, e `local_afetado`).
    *   Você pode usar uma ferramenta como `kafkacat` ou um script Python simples com `kafka-python` para produzir a mensagem.
    *   Exemplo de mensagem de diagnóstico:
        ```json
        {
          "id_diagnostico": "diag-001",
          "timestamp": "2025-05-14T19:00:00Z",
          "sistema_afetado": "PainelSolarXPTO",
          "entidades_detectadas": ["crise energética global", "aumento preço silício"],
          "termos_relevantes": ["energia renovável", "geopolítica"],
          "local_afetado": "Brasil",
          "severidade": "alta",
          "descricao": "Detectada possível escassez de componentes devido a fatores macroeconômicos."
        }
        ```
*   **Consuma do Tópico de Estratégia**: Verifique se o microsserviço processa a mensagem e produz uma nova mensagem enriquecida no tópico `autocura.estrategia`.
    *   Monitore o tópico `autocura.estrategia` para ver a mensagem de saída. Ela deve conter o diagnóstico original mais um campo `contexto_web` com os dados coletados.
    *   Verifique nos logs do serviço se houve chamadas às APIs externas (News, Finance, Climate) e se os dados foram validados.
*   **Teste o Cache Redis**: Envie a mesma mensagem de diagnóstico (ou uma com as mesmas `palavras_chave` e `localizacao`) novamente após um curto período. Verifique nos logs se o cache Redis foi utilizado (deve haver mensagens de "Cache HIT"). O tempo de resposta também deve ser menor.

### 5. Validação Funcional

*   Confirme se os dados em `contexto_web` são relevantes e corretos.
*   Teste diferentes tipos de diagnósticos para ver como o enriquecimento se comporta.
*   Verifique o comportamento do rate limiting (se possível, simulando múltiplas chamadas rápidas, embora isso seja mais difícil de testar diretamente sem instrumentação adicional ou ferramentas de carga).
*   Valide a lógica da whitelist (se uma fonte não permitida for usada por uma API, como isso é tratado – atualmente a validação de whitelist no código está mais focada em URLs diretas, o que pode precisar de ajuste dependendo de como as fontes são retornadas pelas APIs).

Ao seguir estes passos, você poderá validar completamente a funcionalidade e a integração do microsserviço Consciência Situacional no seu ambiente.

