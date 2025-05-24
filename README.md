# Sistema de Autocura

## Descrição
Sistema de Inteligência Artificial com capacidade de autocura, diagnóstico e evolução contínua, baseado em princípios éticos e segurança.

## Estrutura
```
.
├── modulos/               # Módulos do sistema
│   ├── core/             # Módulo core
│   ├── monitoramento/    # Monitoramento
│   ├── diagnostico/      # Diagnóstico
│   ├── gerador-acoes/    # Gerador de ações
│   ├── integracao/       # Integração
│   ├── observabilidade/  # Observabilidade
│   ├── guardiao-cognitivo/ # Guardião cognitivo
│   ├── etica/            # Ética
│   ├── shared/           # Recursos compartilhados
│   ├── tests/            # Testes
│   ├── docker/           # Docker
│   └── deployment/       # Deployment
├── docs/                 # Documentação
├── scripts/              # Scripts de automação
└── README.md            # Esta documentação
```

## Módulos

### Core
Módulo central do sistema, responsável pelas funcionalidades essenciais e compartilhadas.

### Monitoramento
Coleta e processa métricas, logs e traces do sistema.

### Diagnóstico
Analisa e identifica problemas no sistema.

### Gerador de Ações
Gera, prioriza e executa ações corretivas.

### Integração
Gerencia a comunicação entre módulos.

### Observabilidade
Fornece visibilidade do sistema.

### Guardião Cognitivo
Protege e evolui o sistema cognitivo.

### Ética
Garante conformidade ética e regulatória.

### Shared
Recursos compartilhados entre módulos.

### Tests
Testes automatizados do sistema.

### Docker
Containerização do sistema.

### Deployment
Implantação do sistema.

## Configuração

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/autocura.git
cd autocura
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

4. Execute os testes:
```bash
pytest modulos/tests/
```

## Uso

```python
from autocura import Autocura

# Inicializa o sistema
sistema = Autocura()

# Configura o sistema
sistema.configurar(config)

# Inicia o sistema
sistema.iniciar()

# Monitora o sistema
sistema.monitorar()

# Diagnostica problemas
diagnostico = sistema.diagnosticar()

# Gera e executa ações
acoes = sistema.gerar_acoes(diagnostico)
sistema.executar_acoes(acoes)
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

# Sistema de Monitoramento de Recursos

Este módulo implementa um sistema de monitoramento de recursos para o sistema de autocura, fornecendo métricas em tempo real e ajustes automáticos.

## Funcionalidades

- Monitoramento contínuo de recursos do sistema (CPU, memória, disco)
- Coleta de métricas via Prometheus
- Alertas configuráveis via email e Slack
- Ajuste automático de recursos
- Integração com sistema de autocura
- Histórico de métricas e alertas

## Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

O sistema é configurado através do arquivo `src/monitoramento/config.py`. Principais configurações:

- Intervalo de monitoramento
- Limites de recursos
- Configurações de alertas
- Parâmetros de ajuste automático

## Uso

Para iniciar o monitoramento:

```bash
python src/monitoramento/executar_monitoramento.py
```

O sistema irá:
1. Iniciar o servidor Prometheus na porta 9090
2. Começar a coletar métricas
3. Enviar alertas quando necessário
4. Realizar ajustes automáticos

## Métricas Prometheus

O sistema expõe as seguintes métricas:

### Contadores
- `autocura_ajustes_total`: Total de ajustes realizados
- `autocura_alertas_total`: Total de alertas gerados

### Gauges
- `autocura_cpu_usage`: Uso de CPU por core
- `autocura_memory_usage`: Uso de memória (RAM e swap)
- `autocura_disk_usage`: Uso de disco por partição
- `autocura_equidade`: Índice de equidade na distribuição

### Histogramas
- `autocura_ajuste_duration_seconds`: Duração dos ajustes

## Alertas

O sistema envia alertas quando:

- Uso de CPU excede limite configurado
- Uso de memória excede limite configurado
- Uso de disco excede limite configurado
- Índice de equidade cai abaixo do limite

Alertas são enviados via:
- Email (SMTP)
- Slack (Webhook)

## Integração com Autocura

O monitoramento se integra com o sistema de autocura através de:

1. Métricas em tempo real
2. Ajustes automáticos de recursos
3. Histórico de métricas e alertas
4. Memória compartilhada

## Logs

Logs são salvos em:
- `logs/monitoramento.log`: Log geral do sistema
- `logs/dependencias.log`: Log de dependências

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 