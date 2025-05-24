# Módulo de Deployment

## Descrição
Módulo responsável por gerenciar o processo de implantação do sistema em diferentes ambientes, garantindo confiabilidade e automação.

## Estrutura
```
deployment/
├── scripts/               # Scripts de deployment
│   ├── dev/              # Scripts de desenvolvimento
│   ├── staging/          # Scripts de homologação
│   └── prod/             # Scripts de produção
├── config/               # Configurações de deployment
│   ├── dev/              # Config de desenvolvimento
│   ├── staging/          # Config de homologação
│   └── prod/             # Config de produção
├── kubernetes/           # Manifests Kubernetes
│   ├── dev/              # Manifests de desenvolvimento
│   ├── staging/          # Manifests de homologação
│   └── prod/             # Manifests de produção
└── monitoring/           # Monitoramento de deployment
```

## Funcionalidades

### Scripts
- Automatização de deploy
- Rollback
- Verificação de saúde
- Limpeza de recursos

### Configuração
- Variáveis de ambiente
- Secrets
- ConfigMaps
- Volumes

### Kubernetes
- Deployments
- Services
- Ingress
- HPA

### Monitoramento
- Logs de deployment
- Métricas
- Alertas
- Dashboards

## Configuração

1. Instale as dependências:
```bash
# Instale o kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Instale o helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Execute os testes:
```bash
# Testa o deployment
./scripts/test-deploy.sh

# Testa o rollback
./scripts/test-rollback.sh
```

## Uso

```bash
# Deploy em desenvolvimento
./scripts/deploy.sh dev

# Deploy em homologação
./scripts/deploy.sh staging

# Deploy em produção
./scripts/deploy.sh prod

# Rollback
./scripts/rollback.sh <versao>
```

## Contribuição

1. Siga a estrutura modular
2. Adicione testes
3. Atualize a documentação
4. Envie um pull request

## Licença

Este módulo está sob a licença MIT. 