# Módulo de Observabilidade

Este módulo é responsável por integrar e visualizar dados de todo o sistema de autocura, fornecendo uma visão holística do estado do sistema.

## Funcionalidades

- Coleta e visualização de métricas
- Monitoramento de diagnósticos
- Acompanhamento de ações corretivas
- Geração de relatórios
- Visualizações temporais e correlacionais
- Grafos causais de anomalias

## Requisitos

- Python 3.9+
- Docker Desktop com Kubernetes habilitado
- kubectl configurado
- Helm 3.x

## Instalação

1. Construa a imagem Docker:
```bash
docker build -t observabilidade:latest .
```

2. Aplique os manifests Kubernetes:
```bash
kubectl apply -f k8s/
```

3. Verifique se os pods estão rodando:
```bash
kubectl get pods -l app=observabilidade
```

## Testando o Sistema

### Testes Automatizados

Execute os testes de integração:
```bash
python -m pytest tests/test_integracao.py -v
```

### Testes Manuais

Execute o script de testes manuais:
```bash
python tests/test_manual.py
```

### Testando via API

1. Health Check:
```bash
curl http://localhost:8080/health
```

2. Obter Métricas:
```bash
curl http://localhost:8080/api/v1/metricas
```

3. Obter Diagnósticos:
```bash
curl http://localhost:8080/api/v1/diagnosticos
```

4. Obter Ações:
```bash
curl http://localhost:8080/api/v1/acoes
```

5. Criar Visualização:
```bash
curl -X POST http://localhost:8080/api/visualizacoes/metricas-temporais \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Teste", "agrupar_por_dimensao": true, "salvar": true}'
```

6. Gerar Relatório:
```bash
curl http://localhost:8080/api/v1/relatorio-completo
```

## Visualizando no Grafana

1. Acesse o Grafana em http://localhost:3000
2. Use as credenciais padrão:
   - Usuário: admin
   - Senha: admin
3. Configure a fonte de dados Prometheus:
   - URL: http://prometheus:9090
4. Importe os dashboards:
   - Métricas do Sistema
   - Diagnósticos
   - Ações Corretivas
   - Eventos

## Monitoramento

O módulo expõe métricas no endpoint `/metrics` que podem ser coletadas pelo Prometheus:

- `observabilidade_requisicoes_total`: Total de requisições
- `observabilidade_requisicoes_erro_total`: Total de erros
- `observabilidade_tempo_resposta`: Tempo de resposta
- `observabilidade_metricas_coletadas`: Número de métricas coletadas
- `observabilidade_diagnosticos_gerados`: Número de diagnósticos
- `observabilidade_acoes_executadas`: Número de ações

## Troubleshooting

1. Verifique os logs do pod:
```bash
kubectl logs -l app=observabilidade
```

2. Verifique a conectividade entre serviços:
```bash
kubectl exec -it $(kubectl get pod -l app=observabilidade -o jsonpath='{.items[0].metadata.name}') -- curl http://monitoramento:8081/health
```

3. Verifique as métricas no Prometheus:
```bash
kubectl port-forward svc/prometheus 9090:9090
```
Acesse http://localhost:9090

## Contribuindo

1. Faça fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Faça push para a branch
5. Crie um Pull Request

## Licença

MIT 