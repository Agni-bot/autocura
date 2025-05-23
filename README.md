# Sistema de Autocura Cognitiva

Sistema modular de autocura cognitiva com foco em ética, segurança e evolução contínua.

## 🏗️ Estrutura do Projeto

```
sistema-autocura/
├── modulos/                    # Módulos principais do sistema
│   ├── core/                   # Módulo central com interfaces comuns
│   ├── monitoramento/          # Módulo de monitoramento independente
│   ├── diagnostico/            # Módulo de diagnóstico independente
│   ├── gerador-acoes/          # Módulo gerador de ações independente
│   ├── integracao/             # Módulo de integração independente
│   ├── observabilidade/        # Módulo de observabilidade independente
│   ├── guardiao-cognitivo/     # Módulo guardião cognitivo independente
│   └── etica/                  # Módulos ético-operacionais
│       ├── circuitos-morais/
│       ├── decisao-hibrida/
│       ├── auditoria/
│       ├── governanca/
│       ├── fluxo-autonomia/
│       ├── validadores-eticos/
│       ├── priorizacao-financeira/
│       └── registro-decisoes/
├── shared/                     # Bibliotecas compartilhadas
├── tests/                      # Testes por módulo
├── docker/                     # Dockerfiles por módulo
└── deployment/                 # Configurações de deployment
```

## 🚀 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/sistema-autocura.git
cd sistema-autocura
```

2. Instale as dependências:
```bash
poetry install
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## 🧪 Testes

Execute os testes com:
```bash
poetry run pytest
```

## 🐳 Docker

Para executar com Docker:
```bash
docker-compose up -d
```

## 📚 Documentação

A documentação completa está disponível em `docs/`:
- [Arquitetura](docs/01-Etapa1/arquitetura.md)
- [Plano Modular](docs/02-Etapa2/plano_modular_ia.md)
- [Guia de Desenvolvimento](docs/03-Etapa3/guia_desenvolvimento.md)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua branch de feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📫 Contato

Seu Nome - [@seutwitter](https://twitter.com/seutwitter) - email@example.com

Link do Projeto: [https://github.com/seu-usuario/sistema-autocura](https://github.com/seu-usuario/sistema-autocura)

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