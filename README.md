# Sistema de Autocura

Sistema inteligente para detecção, diagnóstico e correção automática de problemas em sistemas computacionais.

## Características

- Detecção automática de problemas
- Diagnóstico inteligente de causas raiz
- Geração e execução de ações corretivas
- Monitoramento contínuo do sistema
- Logging detalhado de todas as operações
- Interface de gerenciamento de ações
- Configuração flexível via arquivos JSON

## Requisitos

- Python 3.11+
- Docker e Docker Compose
- Acesso root/sudo para execução de ações do sistema

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/autocura.git
cd autocura
```

2. Crie um ambiente virtual Python:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## Uso

### Executando com Docker

```bash
docker-compose up -d
```

### Executando localmente

```bash
python src/main.py
```

## Estrutura do Projeto

```
autocura/
├── config/                 # Arquivos de configuração
├── docs/                   # Documentação
├── logs/                   # Logs do sistema
├── src/                    # Código fonte
│   ├── autocorrection/     # Módulo de autocorreção
│   ├── core/              # Núcleo do sistema
│   ├── diagnostico/       # Módulo de diagnóstico
│   ├── executor/          # Módulo de execução
│   ├── monitoramento/     # Módulo de monitoramento
│   └── portal/            # Interface de gerenciamento
├── tests/                 # Testes automatizados
├── docker-compose.yml     # Configuração Docker
└── requirements.txt       # Dependências Python
```

## Configuração

O sistema é configurado através de arquivos JSON na pasta `config/`:

- `acoes.json`: Configuração de tipos de ações e prioridades
- `monitoramento.json`: Configuração de métricas e alertas
- `sistema.json`: Configurações gerais do sistema

## Desenvolvimento

### Executando Testes

```bash
pytest tests/
```

### Formatação de Código

```bash
black src/
isort src/
flake8 src/
```

### Documentação

```bash
cd docs
make html
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Para suporte, envie um email para suporte@exemplo.com ou abra uma issue no GitHub.
