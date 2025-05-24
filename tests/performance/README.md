# Testes de Performance - AutoCura

Este diretório contém os testes de performance do projeto AutoCura, utilizando o framework Locust para simulação de carga.

## Estrutura

```
tests/performance/
├── README.md
├── carga_baixa/
│   └── locustfile.py
├── carga_media/
│   └── locustfile.py
├── carga_alta/
│   └── locustfile.py
├── estresse/
│   └── locustfile.py
└── longa_duracao/
    └── locustfile.py
```

## Cenários de Teste

### 1. Carga Baixa
- Simula uso normal do sistema
- Poucos usuários simultâneos
- Operações básicas
- Tempo entre requisições: 1-3 segundos

### 2. Carga Média
- Simula uso moderado do sistema
- Número médio de usuários
- Operações comuns
- Tempo entre requisições: 0.5-1.5 segundos

### 3. Carga Alta
- Simula uso intenso do sistema
- Muitos usuários simultâneos
- Operações frequentes
- Tempo entre requisições: 0.5-1.5 segundos

### 4. Estresse
- Simula condições extremas
- Número máximo de usuários
- Operações complexas e pesadas
- Tempo entre requisições: 0.1-0.5 segundos

### 5. Longa Duração
- Simula uso contínuo
- Poucos usuários por longos períodos
- Operações de manutenção
- Tempo entre requisições: 2-5 segundos

## Requisitos

- Python 3.8+
- Locust
- Docker
- Kubernetes
- Dependências do projeto

## Instalação

```bash
# Instalar dependências
pip install -r requirements-test.txt

# Instalar Locust
pip install locust
```

## Execução

### Via Script

```bash
# Executar todos os cenários
python scripts/run_performance.py

# Executar cenário específico
python scripts/run_performance.py --cenario carga_baixa

# Executar com argumentos adicionais
python scripts/run_performance.py --cenario carga_alta --args --users 100 --spawn-rate 10
```

### Via Locust Diretamente

```bash
# Executar cenário específico
locust -f tests/performance/carga_baixa/locustfile.py

# Executar com argumentos
locust -f tests/performance/carga_alta/locustfile.py --users 100 --spawn-rate 10 --run-time 1h
```

## Relatórios

Os relatórios são gerados em dois formatos:

1. **HTML**: Relatório detalhado do Locust com gráficos e estatísticas
   - Localização: `test-results/performance/report_*.html`

2. **JSON**: Relatório estruturado com resultados e métricas
   - Localização: `test-results/performance/performance_*.json`

## Métricas Monitoradas

- Tempo de resposta
- Requisições por segundo
- Taxa de falhas
- Uso de recursos (CPU, memória, rede)
- Latência
- Throughput

## Boas Práticas

1. **Preparação**
   - Limpe o ambiente antes dos testes
   - Verifique recursos disponíveis
   - Configure limites adequados

2. **Execução**
   - Comece com carga baixa
   - Aumente gradualmente
   - Monitore recursos
   - Documente resultados

3. **Análise**
   - Compare com baseline
   - Identifique gargalos
   - Verifique logs
   - Documente conclusões

## Troubleshooting

### Problemas Comuns

1. **Erro de Conexão**
   - Verifique se o servidor está rodando
   - Confirme configurações de rede
   - Verifique firewall

2. **Erro de Autenticação**
   - Verifique credenciais
   - Confirme tokens
   - Verifique permissões

3. **Erro de Recursos**
   - Aumente limites do sistema
   - Reduza carga de teste
   - Otimize configurações

### Logs

- Logs do Locust: `test-results/performance/locust.log`
- Logs do sistema: `test-results/performance/system.log`

## Contribuição

1. Crie um branch para sua feature
2. Implemente os testes
3. Documente as alterações
4. Envie um pull request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes. 