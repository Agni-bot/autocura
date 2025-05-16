# Configuração de Infraestrutura para Autocura

Este documento descreve requisitos e recomendações de infraestrutura para o sistema Autocura, especialmente para funcionalidades avançadas como testes de autoadaptação e sandboxing.

## 1. Namespace Kubernetes para Testes de Autoadaptação

Para garantir o isolamento e a segurança ao testar modificações na própria configuração ou arquitetura do sistema Autocura (conforme gerenciado pelo `AdvancedSandboxManager` ou `AdaptationEngine`), é **altamente recomendado** criar um ou mais Namespaces Kubernetes dedicados.

**Nome Sugerido para o Namespace:** `autocura-self-adaptation-sandbox` ou `autocura-sandbox-<test-id>`

**Benefícios de um Namespace Dedicado:**

*   **Isolamento de Recursos:** Impede que os testes de adaptação consumam recursos (CPU, memória, rede) destinados aos componentes de produção do Autocura ou outros aplicativos no cluster.
*   **Segurança:** Limita o escopo de impacto de qualquer falha ou comportamento inesperado durante um teste de adaptação. As permissões (RBAC) podem ser estritamente controladas dentro deste namespace.
*   **Limpeza Facilitada:** Após a conclusão dos testes, todo o namespace pode ser facilmente excluído, removendo todos os recursos associados (Pods, Services, ConfigMaps, etc.) sem afetar o ambiente de produção.
*   **Configurações Específicas:** Permite aplicar políticas de rede, cotas de recursos (ResourceQuotas), e outras configurações específicas para o ambiente de teste sem interferir com as configurações globais do cluster ou de outros namespaces.

**Configuração Recomendada (Exemplo de ResourceQuota):**

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: autocura-sandbox-quota
  namespace: autocura-self-adaptation-sandbox # Aplicar ao namespace criado
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    limits.cpu: "8"
    limits.memory: "16Gi"
    pods: "20"
    services: "10"
    configmaps: "30"
```

**Criação do Namespace:**

```bash
kubectl create namespace autocura-self-adaptation-sandbox
kubectl apply -f path/to/your/resource-quota.yaml -n autocura-self-adaptation-sandbox
```

O `AdvancedSandboxManager` (se configurado para usar Kubernetes) ou o `AdaptationEngine` devem ser configurados para utilizar este namespace ao realizar testes de automodificação ou ao validar novas configurações de componentes do Autocura.

## 2. Outras Considerações de Infraestrutura

*   **Docker Engine:** Necessário se o `AdvancedSandboxManager` estiver configurado para usar Docker como método de isolamento. O daemon do Docker deve estar acessível ao processo que executa o `AdvancedSandboxManager`.
*   **Acesso a APIs Externas:** Garantir conectividade de rede para todas as APIs externas que os módulos do Autocura (ex: `MarketMonitor`, `PoliticalPredictor`, `CrowdfundingIntegrator`) precisam acessar. Considerar firewalls, proxies e listas de permissões.
*   **Recursos para Modelos de ML/IA:** Componentes como `PredictiveEngine`, `ReinforcementLearner`, `AdaptationDecisionModel` (PyTorch), e `PoliticalPredictor` (Hugging Face Transformers) podem exigir recursos significativos de CPU e, especialmente, GPU para treinamento e inferência eficiente. Planejar a alocação desses recursos no cluster Kubernetes.
*   **Armazenamento Persistente:** Para dados de treinamento de modelos, logs extensos, e estados de sandboxes (se necessário), configurar soluções de armazenamento persistente (PersistentVolumes) no Kubernetes.
*   **Broker de Mensagens (Kafka):** Se o sistema depende de Kafka para comunicação entre microsserviços, garantir que o broker esteja devidamente configurado, com alta disponibilidade e capacidade adequada.
*   **Cache (Redis):** Se Redis é usado para cache, garantir sua disponibilidade e configuração ótima.

