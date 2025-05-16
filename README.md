# Sistema de Autocura Cognitiva

<<<<<<< HEAD
Este repositório contém o Sistema de Autocura Cognitiva, uma solução avançada para manutenção autônoma de sistemas de Inteligência Artificial.

## Visão Geral

O Sistema de Autocura Cognitiva representa uma evolução significativa na manutenção autônoma de sistemas de IA. Diferentemente dos sistemas tradicionais de monitoramento e recuperação, este sistema incorpora princípios de cognição adaptativa, permitindo não apenas identificar e corrigir falhas, mas também evoluir continuamente para prevenir problemas futuros.

## Pré-requisitos

Para executar o Sistema de Autocura Cognitiva localmente, você precisará ter instalado:

- Docker
- kubectl
- kind (Kubernetes in Docker)

## Configuração do Ambiente Local

Siga estas etapas para configurar e executar o Sistema de Autocura Cognitiva em seu ambiente local:

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/autocura.git
cd autocura
```

### 2. Configure o ambiente Kubernetes local

Execute o script de configuração do ambiente para criar um cluster kind configurado para o Sistema de Autocura Cognitiva:

```bash
# Torne o script executável
chmod +x setup-kind.sh

# Execute o script
./setup-kind.sh
```

Este script irá:
- Verificar os pré-requisitos (Docker, kubectl, kind)
- Criar um cluster kind com a configuração necessária
- Configurar um registro Docker local
- Conectar o registro à rede do kind

### 3. Construa as imagens Docker

Execute o script de build para construir todas as imagens Docker necessárias:

```bash
# Torne o script executável
chmod +x build.sh

# Execute o script
./build.sh
```

Este script irá:
- Construir as imagens Docker para todos os componentes (monitoramento, diagnóstico, gerador de ações, observabilidade)
- Construir as imagens Docker para os operadores (healing, rollback)
- Enviar as imagens para o registro local

### 4. Implante o sistema no cluster

Implante o Sistema de Autocura Cognitiva no cluster kind:

```bash
# Implante o ambiente de desenvolvimento
kubectl apply -k kubernetes/environments/development
```

### 5. Verifique a implantação

Verifique se todos os componentes foram implantados corretamente:

```bash
# Verifique os pods
kubectl get pods -n autocura-dev

# Verifique os serviços
kubectl get services -n autocura-dev
```

### 6. Acesse o painel de observabilidade

O painel de observabilidade está disponível através do serviço de observabilidade:

```bash
# Encaminhe a porta do serviço de observabilidade
kubectl port-forward -n autocura-dev svc/observabilidade 8080:8080
```

Acesse o painel em seu navegador: http://localhost:8080

## Estrutura do Projeto

```
autocura/
├── src/                      # Código-fonte dos componentes
│   ├── monitoramento/        # Módulo de Monitoramento Multidimensional
│   ├── diagnostico/          # Módulo de Diagnóstico Neural
│   ├── gerador/        # Gerador de Ações Emergentes
│   ├── observabilidade/      # Interface de Observabilidade 4D
│   └── integracao/           # Módulos de integração
├── kubernetes/               # Configurações de implantação
│   ├── base/                 # Recursos base
│   ├── operators/            # Operadores customizados
│   ├── components/           # Componentes do sistema
│   ├── environments/         # Ambientes paralelos
│   └── storage/              # Configurações de armazenamento
├── docs/                     # Documentação
├── tests/                    # Testes
└── config/                   # Configurações
```

## Solução de Problemas

### Erro ImagePullBackOff

Se você encontrar erros de ImagePullBackOff:

1. Verifique se o registro local está em execução:
   ```bash
   docker ps | grep registry
   ```

2. Verifique se as imagens foram construídas e enviadas corretamente:
   ```bash
   docker images | grep autocura
   ```

3. Verifique se o cluster kind está configurado para acessar o registro local:
   ```bash
   kubectl get nodes -o wide
   ```

4. Reconstrua as imagens e reimplante o sistema:
   ```bash
   ./build.sh
   kubectl delete -k kubernetes/environments/development
   kubectl apply -k kubernetes/environments/development
   ```

## Documentação Adicional

Para mais informações, consulte os documentos na pasta `docs/`:

- [Análise de Requisitos](docs/analise_requisitos.md)
- [Arquitetura Modular](docs/arquitetura_modular.md)
- [Plano de Implantação](docs/plano_implantacao.md)
- [Protocolo de Emergência](docs/protocolo_emergencia.md)
- [Documentação Completa](docs/documentacao_completa.md)

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
=======
## Sumário
- [Visão Geral](#visão-geral)
- [Arquitetura do Sistema](#arquitetura-do-sistema)
- [Requisitos](#requisitos)
- [Configuração e Execução](#configuração-e-execução)
- [Monitoramento](#monitoramento)
- [Desenvolvimento](#desenvolvimento)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Módulo Will - Detalhes](#módulo-will---detalhes)
- [Contribuição](#contribuição)
- [Licença](#licença)

## Visão Geral
O Sistema de Autocura Cognitiva é uma plataforma modular para automação, monitoramento e autocura de sistemas de IA, com foco inicial em operações no mercado Forex. O sistema é composto por múltiplos módulos (Will, Portal, Observabilidade, Monitoramento, Diagnóstico, Gerador) orquestrados via Kubernetes.

## Arquitetura do Sistema
- **Will API**: Serviço principal de trading e decisão
- **Portal**: Interface web para monitoramento e controle
- **Observabilidade**: Dashboard central e visualização 4D
- **Monitoramento**: Coleta e análise de métricas
- **Diagnóstico**: Análise neural e detecção de anomalias
- **Gerador**: Geração de ações corretivas e automações
- **MongoDB**: Armazenamento de dados
- **Elasticsearch**: Armazenamento e análise de logs
- **Kibana**: Visualização de métricas e logs

## Requisitos
- Docker e Docker Compose
- Python 3.11+
- Kubernetes (KIND recomendado para desenvolvimento local)
- Chaves de API:
  - News API
  - Gemini API
  - Binance API

## Configuração e Execução
1. Clone o repositório:
   ```bash
   git clone [URL_DO_REPOSITORIO]
   cd autocura
   ```
2. Configure as variáveis de ambiente:
   ```bash
   cp src/will/inst/.env.example src/will/inst/.env
   # Edite o arquivo .env com suas chaves de API
   ```
3. Build, tag e push das imagens para o registry local:
   ```bash
   docker build -t portal:latest ./src/portal
   docker tag portal:latest localhost:5000/portal:latest
   docker push localhost:5000/portal:latest
   # Repita para todos os módulos
   ```
4. Aplique os manifests do Kubernetes:
   ```bash
   kubectl apply -k kubernetes/components
   ```
5. Acesse os serviços:
   - Portal: http://localhost:8080
   - Will API: http://localhost:5000
   - Kibana: http://localhost:5601

## Monitoramento
O sistema inclui monitoramento completo via Observabilidade e Kibana:
- Métricas de trading
- Performance do modelo
- Saúde do sistema
- Métricas de risco

## Desenvolvimento
Para desenvolvimento local de qualquer módulo:
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute os testes:
   ```bash
   pytest
   ```
3. Execute o servidor de desenvolvimento:
   ```bash
   python <arquivo_principal>.py
   # ou flask run / uvicorn ...
   ```

## Estrutura do Projeto
```
src/
├── will/
│   └── inst/
│       ├── app.py
│       ├── ...
├── portal/
├── observabilidade/
├── monitoramento/
├── diagnostico/
├── gerador/
kubernetes/
├── components/
├── operators/
...
```

## Módulo Will - Detalhes

### Visão Geral
O Will é o módulo de trading algorítmico do sistema, focado em decisões de negociação no mercado Forex, integrando modelos de IA e a API Gemini 2.5 Pro.

### Arquitetura Interna
- **core_ai/**: Modelos de IA (Temporal, Probabilístico, Evolutivo, Simulação, Sincronizador)
- **data_interface/**: Integração com feeds de mercado e saída de decisões
- **gemini_integration/**: Integração com a API Gemini
- **processing_engine/**: Lógica central de decisão
- **security_protocols/**: Criptografia, anonimização, scripts de segurança
- **training_orchestrator/**: Treinamento contínuo dos modelos
- **tests/**: Scripts de teste
- **configs/**: Arquivos de configuração

### Execução e Testes
- Instale as dependências:
  ```bash
  pip install -r requirements.txt
  ```
- Configure a chave da API Gemini via variável de ambiente `GEMINI_API_KEY` ou arquivo de configuração.
- Execute os testes:
  ```bash
  docker build --no-cache -t will:latest -f src/will/inst/Dockerfile .
  docker run --rm -w /app will:latest python -m pytest tests/test_will_api.py -v
  ```
- Execute a aplicação:
  ```bash
  docker run --rm -p 5000:5000 will:latest
  # ou via Kubernetes, após push para o registry local
  ```
- Endpoints principais:
  - `/api/will/status`: Status do sistema
  - `/api/will/decision`: Decisão de trading

### Estado Atual dos Testes
- **test_status_endpoint**: ✅ PASSED
- **test_decision_endpoint**: ✅ PASSED
- **test_decision_endpoint_invalid_input**: ✅ PASSED
- **test_decision_endpoint_invalid_json**: ✅ PASSED

### Próximos Passos
- Implementar validação para o campo `asset`
- Adicionar mais testes
- Melhorar a documentação e exemplos de uso

### Documentação Adicional
- `documentacao_tecnica_will.md`: Visão geral da arquitetura
- `arquitetura_detalhada_will.md`: Detalhes da arquitetura

## Contribuição
1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença
Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
>>>>>>> origin/main
