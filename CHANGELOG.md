# Changelog

## [1.0.2] - 2025-05-23

### Corrigido
- Removido import circular em `acoes_correcao.py`
- Corrigido cálculo de probabilidade de sucesso em `PlanoAcao`
- Melhorado tratamento de erros em operações assíncronas
- Adicionada validação de parâmetros em `GerenciadorAcoes`

### Alterado
- Movido mapeamento de ações para arquivo de configuração JSON
- Atualizada estrutura de testes para cobrir novos casos
- Melhorada documentação do código

### Adicionado
- Novo arquivo de configuração `acoes_config.json`
- Novos testes para cenários de erro
- Validações adicionais em `GeradorAcoes`
- Testes de integração para fluxos completos

### Otimizado
- Melhorada performance no carregamento de configurações
- Otimizada estrutura de dados para escalabilidade

## [1.0.1] - 2025-05-22

### Corrigido
- Removido import circular em `acoes_correcao.py`
- Corrigido cálculo de taxa de sucesso
- Padronizado imports relativos

### Alterado
- Movido valores hardcoded para arquivo de configuração JSON
- Atualizada estrutura do README

### Adicionado
- Novo arquivo de configuração
- Testes unitários para módulos principais
- Documentação de código

### Otimizado
- Modularização do código
- Tratamento de erros 