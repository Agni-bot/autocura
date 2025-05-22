# Testes Unitários

Este diretório contém os testes unitários do sistema de autocura. Testes unitários são responsáveis por testar componentes individuais do sistema de forma isolada.

## Estrutura

- `test_*.py`: Arquivos de teste unitário
- `conftest.py`: Configurações e fixtures específicas para testes unitários

## Convenções

1. Nome dos arquivos: `test_[componente].py`
2. Nome das classes: `Test[Componente]`
3. Nome dos métodos: `test_[cenario]`

## Componentes Testados

- Gerenciadores (memória, logs, eventos, configuração)
- Validadores
- Orquestradores
- Guardiões
- Observadores
- Geradores
- Redes neurais
- Criptografia
- Cache
- Detecção de anomalias
- Diagnóstico
- Auto-scaling

## Executando os Testes

```bash
# Executar todos os testes unitários
pytest tests/unit/

# Executar um teste específico
pytest tests/unit/test_[componente].py

# Executar com cobertura
pytest tests/unit/ --cov=src --cov-report=term-missing
``` 