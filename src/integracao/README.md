# Módulo de Integração

Este módulo implementa a camada de integração do sistema de autocura cognitiva, responsável por gerenciar a comunicação entre os diferentes componentes do sistema.

## 🎯 Funcionalidades

- **Adaptadores de Comunicação**
  - HTTP/HTTPS
  - WebSocket
  - Redis
  - Kafka

- **Tradutores de Formato**
  - JSON
  - MessagePack
  - YAML

- **Gateways de Serviço**
  - Monitoramento
  - Diagnóstico
  - Gerador de Ações
  - Executor de Ações

- **Segurança**
  - SSL/TLS
  - Autenticação JWT
  - Autorização baseada em roles

- **Monitoramento**
  - Métricas Prometheus
  - Health checks
  - Alertas

## 🚀 Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Configure os certificados SSL (opcional):
```bash
mkdir -p certs
# Adicione seus certificados em certs/
```

## ⚙️ Configuração

O módulo é configurado através do arquivo `config/integracao.yaml`. As principais seções são:

- **adaptadores**: Configurações dos adaptadores de comunicação
- **tradutores**: Configurações dos tradutores de formato
- **gateways**: Configurações dos gateways de serviço
- **seguranca**: Configurações de segurança
- **logging**: Configurações de logging
- **monitoramento**: Configurações de monitoramento
- **cache**: Configurações de cache

## 🏃‍♂️ Execução

Para executar o módulo:

```bash
python camada_integracao.py
```

O módulo irá:
1. Carregar a configuração
2. Inicializar os adaptadores
3. Registrar os gateways
4. Iniciar o ciclo de integração

## 📊 Monitoramento

O módulo expõe métricas Prometheus na porta 9090 (configurável). As principais métricas são:

- `integracao_mensagens_total`: Total de mensagens processadas
- `integracao_erros_total`: Total de erros
- `integracao_latencia_ms`: Latência de processamento
- `integracao_queue_size`: Tamanho da fila de mensagens

## 🔒 Segurança

O módulo implementa:

- **SSL/TLS**: Comunicação criptografada
- **JWT**: Autenticação baseada em tokens
- **RBAC**: Controle de acesso baseado em roles
- **Rate Limiting**: Proteção contra sobrecarga

## 📝 Logs

Os logs são salvos em `logs/integracao.log` e incluem:

- Informações de execução
- Erros e exceções
- Métricas de performance
- Eventos de segurança

## 🔄 Ciclo de Integração

1. **Carregamento**
   - Carrega configuração
   - Carrega estado da memória
   - Inicializa adaptadores

2. **Verificação**
   - Verifica status dos gateways
   - Valida conexões
   - Atualiza métricas

3. **Processamento**
   - Processa mensagens pendentes
   - Executa traduções
   - Atualiza estado

4. **Atualização**
   - Atualiza memória compartilhada
   - Registra métricas
   - Gera logs

## 🛠️ Desenvolvimento

Para contribuir com o desenvolvimento:

1. Clone o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Execute os testes
5. Envie um pull request

## 📚 Documentação

Documentação adicional disponível em:

- [API Reference](docs/api.md)
- [Guia de Desenvolvimento](docs/desenvolvimento.md)
- [Guia de Segurança](docs/seguranca.md)
- [Guia de Monitoramento](docs/monitoramento.md)

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, leia o [guia de contribuição](CONTRIBUTING.md) antes de enviar um pull request.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 