# Integração com MetaTrader 5

Este documento descreve a integração do sistema Will com o MetaTrader 5 (MT5) para operações de trading automatizado.

## Requisitos

1. **MetaTrader 5**
   - Versão 5.0 ou superior
   - Conta demo ou real configurada
   - Terminal MT5 instalado e configurado

2. **Python**
   - Python 3.8 ou superior
   - Pacote MetaTrader5 instalado
   - Outras dependências em `requirements.txt`

## Configuração

1. **Instalação do MT5**
   - Baixe e instale o MetaTrader 5
   - Configure uma conta demo ou real
   - Anote o caminho de instalação

2. **Configuração do Sistema**
   - Edite o arquivo `src/will/inst/config/mt5_config.yaml`:
     ```yaml
     mt5:
       server: "MetaQuotes-Demo"  # Nome do servidor
       login: 12345678  # Número da conta
       password: "sua_senha"  # Senha da conta
       path: "C:/Program Files/MetaTrader 5/terminal64.exe"  # Caminho do terminal
     ```

3. **Instalação das Dependências**
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. **Iniciar o Sistema**
   ```bash
   python src/will/inst/app.py
   ```

2. **Conectar ao MT5**
   ```bash
   curl -X POST http://localhost:5000/api/will/connect
   ```

3. **Verificar Status**
   ```bash
   curl http://localhost:5000/api/will/status
   ```

4. **Obter Decisão de Trading**
   ```bash
   curl -X POST http://localhost:5000/api/will/decision \
     -H "Content-Type: application/json" \
     -d '{"asset": "EURUSD", "volume": 0.1}'
   ```

5. **Listar Posições Abertas**
   ```bash
   curl http://localhost:5000/api/will/positions
   ```

6. **Fechar Posição**
   ```bash
   curl -X DELETE http://localhost:5000/api/will/positions/123456
   ```

## Estrutura do Código

1. **MT5Handler** (`src/will/inst/trading/mt5_handler.py`)
   - Classe base para interação com o MT5
   - Gerencia conexão e operações
   - Validações e tratamento de erros

2. **MT5Manager** (`src/will/inst/trading/mt5_manager.py`)
   - Gerencia configurações e estado
   - Interface para a API
   - Logging e monitoramento

3. **API** (`src/will/inst/app.py`)
   - Endpoints REST
   - Integração com MT5Manager
   - Validações e respostas

## Testes

1. **Testes Unitários**
   ```bash
   pytest src/will/inst/tests/test_mt5.py -v
   ```

2. **Testes de Integração**
   ```bash
   pytest src/will/inst/tests/test_integration.py -v
   ```

## Logs

Os logs são salvos em `logs/mt5.log` e incluem:
- Conexão/desconexão
- Operações de trading
- Erros e exceções
- Informações de debug

## Segurança

1. **Credenciais**
   - Nunca compartilhe suas credenciais
   - Use variáveis de ambiente para senhas
   - Mantenha o arquivo de configuração seguro

2. **Operações**
   - Valide todos os inputs
   - Use limites de volume
   - Implemente stop loss
   - Monitore as operações

## Troubleshooting

1. **Erro de Conexão**
   - Verifique se o MT5 está instalado
   - Confirme as credenciais
   - Verifique o caminho do terminal

2. **Erro de Operação**
   - Verifique o saldo da conta
   - Confirme os limites de volume
   - Verifique o horário de trading

3. **Erro de Dados**
   - Verifique a conexão com o servidor
   - Confirme os símbolos disponíveis
   - Verifique os timeframes

## Contribuição

1. **Desenvolvimento**
   - Siga o padrão de código
   - Adicione testes
   - Documente as mudanças

2. **Issues**
   - Reporte bugs
   - Sugira melhorias
   - Compartilhe ideias

## Licença

Este projeto está licenciado sob a licença MIT. 