# Módulo Shared

## Descrição
Módulo responsável por compartilhar recursos, utilitários e funcionalidades comuns entre todos os outros módulos do sistema.

## Estrutura
```
shared/
├── src/                    # Código fonte
│   ├── utils/             # Utilitários compartilhados
│   ├── constants/         # Constantes do sistema
│   ├── types/             # Tipos compartilhados
│   └── helpers/           # Helpers comuns
├── tests/                 # Testes
├── config/               # Configurações
├── docker/              # Dockerfiles
├── README.md           # Documentação
└── __init__.py         # Inicialização
```

## Funcionalidades

### Utilitários
- Funções de manipulação de dados
- Formatadores
- Validadores
- Conversores

### Constantes
- Constantes do sistema
- Enums
- Configurações padrão
- Mensagens

### Tipos
- Tipos personalizados
- Interfaces
- Classes base
- DTOs

### Helpers
- Funções auxiliares
- Decoradores
- Context managers
- Mixins

## Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Execute os testes:
```bash
pytest tests/
```

## Uso

```python
from shared import utils, constants, types, helpers

# Usa utilitários
dados_formatados = utils.formatar_dados(dados)

# Usa constantes
valor = constants.VALOR_PADRAO

# Usa tipos
objeto = types.TipoPersonalizado()

# Usa helpers
resultado = helpers.processar_dados(dados)
```

## Contribuição

1. Siga a estrutura modular
2. Adicione testes
3. Atualize a documentação
4. Envie um pull request

## Licença

Este módulo está sob a licença MIT. 