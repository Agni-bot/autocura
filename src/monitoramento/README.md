# Sistema de Monitoramento AutoCura

Sistema abrangente para monitoramento, diagnóstico e análise de sistemas.

## Componentes Principais

### Monitoramento Multidimensional
- Coleta de métricas em tempo real
- Análise de tendências e anomalias
- Integração com Prometheus
- Visualização de dados em tempo real

### Sistema de Diagnóstico
- Detecção automática de problemas
- Análise de causa raiz
- Geração de recomendações
- Histórico de diagnósticos
- Logs e métricas associadas

### Monitoramento de Recursos
- CPU, memória, rede e disco
- Processos e serviços
- Uso de recursos em tempo real
- Alertas de limiares

### Sistema de Notificações
- Alertas em tempo real
- Múltiplos canais (email, Slack, etc)
- Diferentes níveis de severidade
- Agrupamento de alertas

### Visualização 4D
- Visualização temporal de métricas
- Análise de correlações entre dimensões
- Detecção de anomalias
- Geração de relatórios
- Análise de tendências
- Matriz de correlação
- Limpeza automática de dados antigos

## Endpoints da API

### Monitoramento
- `GET /api/monitoramento/health` - Verifica saúde do sistema
- `GET /api/monitoramento/metricas` - Obtém métricas atuais
- `GET /api/monitoramento/historico` - Obtém histórico de métricas
- `GET /api/monitoramento/processos` - Lista processos monitorados

### Diagnóstico
- `GET /api/diagnostico/problemas` - Lista problemas detectados
- `GET /api/diagnostico/problemas/{id}` - Obtém detalhes de um problema
- `POST /api/diagnostico/analisar` - Inicia nova análise
- `GET /api/diagnostico/historico` - Obtém histórico de diagnósticos
- `PUT /api/diagnostico/problemas/{id}/status` - Atualiza status
- `POST /api/diagnostico/problemas/{id}/recomendacoes` - Adiciona recomendação
- `POST /api/diagnostico/problemas/{id}/logs` - Adiciona log

### Visualização 4D
- `GET /api/visualizacao/dimensoes/{nome}` - Obtém dados de uma dimensão
- `GET /api/visualizacao/dimensoes/{nome}/estatisticas` - Obtém estatísticas
- `GET /api/visualizacao/dimensoes/{nome}/anomalias` - Obtém anomalias
- `GET /api/visualizacao/correlacoes` - Obtém matriz de correlação
- `GET /api/visualizacao/dimensoes/{nome}/tendencias` - Obtém tendências
- `GET /api/visualizacao/relatorio` - Gera relatório completo

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```
3. Configure as variáveis de ambiente
4. Execute os testes:
```bash
python -m pytest tests/
```
5. Inicie o serviço:
```bash
python -m src.monitoramento.app
```

## Configuração

O sistema pode ser configurado através do arquivo `config.py` ou variáveis de ambiente:

- `MONITORAMENTO_INTERVALO`: Intervalo de coleta (default: 60s)
- `ALERTAS_THRESHOLD`: Limiares para alertas
- `LOG_LEVEL`: Nível de log (default: INFO)
- `NOTIFICACOES_CANAIS`: Canais de notificação
- `PROMETHEUS_URL`: URL do Prometheus
- `VISUALIZACAO_PERIODO`: Período de retenção de dados (default: 7d)

## Estrutura do Projeto

```
src/monitoramento/
├── __init__.py
├── app.py
├── config.py
├── monitoramento.py
├── metricas.py
├── monitor_recursos.py
├── notificador.py
├── diagnostico.py
├── visualizacao_4d.py
└── tests/
    ├── __init__.py
    ├── test_monitoramento.py
    ├── test_metricas.py
    ├── test_monitor_recursos.py
    ├── test_notificador.py
    ├── test_diagnostico.py
    └── test_visualizacao_4d.py
```

## Adicionando Novos Diagnósticos

1. Crie um método na classe `SistemaDiagnostico`
2. Implemente a lógica de detecção
3. Adicione testes
4. Atualize a documentação

## Adicionando Novas Dimensões 4D

1. Crie uma nova dimensão usando `Dimensao4D`
2. Implemente a lógica de coleta
3. Adicione testes
4. Atualize a documentação

## Contribuindo

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Envie um pull request

## Licença

Este projeto está licenciado sob a licença MIT. 