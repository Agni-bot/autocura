# Sistema de Autocura Cognitiva

## Estrutura Modular

```
modulos/
├── core/                    # Módulo central com interfaces comuns
├── monitoramento/           # Módulo de monitoramento independente
├── diagnostico/             # Módulo de diagnóstico independente
├── gerador-acoes/           # Módulo gerador de ações independente
├── integracao/              # Módulo de integração independente
├── observabilidade/         # Módulo de observabilidade independente
├── guardiao-cognitivo/      # Módulo guardião cognitivo independente
├── etica/                   # Módulos ético-operacionais
│   ├── circuitos-morais/
│   ├── decisao-hibrida/
│   ├── auditoria/
│   ├── governanca/
│   ├── fluxo-autonomia/
│   ├── validadores-eticos/
│   ├── priorizacao-financeira/
│   └── registro-decisoes/
├── shared/                  # Bibliotecas compartilhadas
├── tests/                   # Testes por módulo
├── docker/                  # Dockerfiles por módulo
└── deployment/              # Configurações de deployment
```

## Princípios de Design Modular

- **Separação de Responsabilidades**: Cada módulo tem uma única responsabilidade bem definida
- **Baixo Acoplamento**: Módulos se comunicam apenas através de interfaces padronizadas
- **Alta Coesão**: Componentes dentro de cada módulo trabalham em conjunto para um objetivo comum
- **Testabilidade Independente**: Cada módulo pode ser testado isoladamente
- **Implantação Independente**: Módulos podem ser desenvolvidos e implantados separadamente

## Estrutura Padrão de Módulo

```
[nome-modulo]/
├── src/                    # Todo código fonte aqui
│   ├── [submodulos]/      # Subdiretórios específicos
│   └── [arquivos].py      # Arquivos do módulo
├── tests/                  # Testes do módulo
├── config/                 # Configurações
├── docker/                 # Dockerfiles
├── README.md              # Documentação
└── __init__.py            # Inicialização
```

## Convenções

- Todos os nomes de diretórios e arquivos em português
- Documentação em português
- Código com comentários em português
- Testes com nomes descritivos em português

## Desenvolvimento

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute os testes: `pytest tests/`
4. Desenvolva seguindo a estrutura modular

## Contribuição

1. Crie uma branch para sua feature
2. Siga a estrutura modular
3. Adicione testes
4. Atualize a documentação
5. Envie um pull request

## Licença

Este projeto está sob a licença MIT. 