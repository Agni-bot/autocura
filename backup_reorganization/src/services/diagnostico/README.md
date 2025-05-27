# Serviço de Diagnóstico

Este serviço é responsável por analisar métricas do sistema e gerar diagnósticos baseados em anomalias detectadas.

## Funcionalidades

- Análise de métricas do sistema
- Detecção de anomalias
- Geração de diagnósticos
- Recomendações de ações corretivas

## Requisitos

- Python 3.11+
- Docker
- Docker Compose

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

O serviço é configurado através do arquivo `config.json`. As principais configurações incluem:

- Limites de métricas
- Regras de diagnóstico
- Configurações de logging
- Integrações com outros serviços

## Executando o Serviço

### Localmente

```bash
python app.py
```

### Com Docker

```bash
docker-compose up -d diagnostico
```

## Testes

Execute os testes com:

```bash
pytest
```

Para cobertura de código:

```bash
pytest --cov=.
```

## Linting e Formatação

- Black: `black .`
- Flake8: `flake8 .`
- MyPy: `mypy .`

## API

### Endpoints

- `GET /health`: Verifica a saúde do serviço
- `POST /analisar`: Analisa um problema e gera diagnóstico

### Exemplo de Uso

```python
import requests

response = requests.post('http://localhost:5001/analisar', json={
    'problema': {
        'tipo': 'desempenho',
        'descricao': 'Alto uso de CPU'
    },
    'metricas': {
        'cpu_uso': 90.0,
        'memoria_uso': 60.0
    },
    'logs': [
        'CPU usage high',
        'Memory usage normal'
    ]
})

print(response.json())
```

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 