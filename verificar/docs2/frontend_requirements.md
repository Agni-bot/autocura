# Requisitos do Frontend Integrado Autocura

## 1. Visão Geral

O frontend integrado do Autocura servirá como um painel de controle centralizado, permitindo aos usuários monitorar o status dos componentes do sistema, visualizar informações relevantes e, potencialmente, acionar ações básicas. O objetivo é fornecer uma interface amigável e informativa para interagir com as diversas funcionalidades do Autocura.

## 2. Requisitos Funcionais

### 2.1. Visualização de Status de Componentes
*   O frontend deve exibir o status atual dos principais componentes do Autocura (ex: Diagnóstico, Gerador de Ações, Monitoramento, Consciência Situacional, Guardião Cognitivo, Operadores Kubernetes).
*   O status pode incluir: Ativo, Inativo, Em Alerta, Erro.
*   Deve haver uma forma de atualizar o status dos componentes (manual ou automaticamente).

### 2.2. Acesso a Logs (Simplificado)
*   Permitir a visualização dos logs recentes (últimas N linhas) de componentes selecionados.
*   Esta funcionalidade pode ser simplificada inicialmente, buscando logs via uma API do servidor Flask que, por sua vez, acessaria os logs dos containers ou arquivos.

### 2.3. Dashboard Principal
*   Uma página inicial (index.html) que apresente um resumo do estado geral do sistema.
*   Links de navegação para seções específicas (Status, Logs, Ações - se implementado).

### 2.4. Acionamento de Ações Básicas (Opcional/Futuro)
*   Considerar a possibilidade de acionar ações simples, como reiniciar um componente (via API).
*   Esta funcionalidade é secundária para a primeira versão.

## 3. Requisitos Não Funcionais

### 3.1. Usabilidade
*   Interface intuitiva e fácil de navegar.
*   Informações apresentadas de forma clara e concisa.

### 3.2. Responsividade (Básica)
*   O layout deve ser minimamente adaptável a diferentes tamanhos de tela (desktop).

### 3.3. Desempenho
*   Carregamento rápido das páginas.
*   Respostas rápidas da API (para busca de status/logs).

### 3.4. Segurança
*   O acesso ao frontend pode, inicialmente, não requerer autenticação se estiver em uma rede interna segura. Para acesso externo, autenticação será necessária (fora do escopo inicial).
*   A comunicação com as APIs do backend (Flask) deve ser segura se exposta externamente.

## 4. Estrutura de Navegação Sugerida

*   **Página Inicial (Dashboard):** Resumo geral, links rápidos.
*   **Status dos Componentes:** Lista detalhada de cada componente e seu status.
*   **Visualizador de Logs:** Seleção de componente e exibição de logs.
*   **(Opcional) Ações do Sistema:** Interface para acionar comandos.

## 5. Stack Tecnológica Proposta

*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS ou uma biblioteca leve como Alpine.js para interatividade básica).
*   **Servidor Backend (para servir o frontend e APIs):** Python com Flask.
*   **Comunicação Frontend-Backend:** APIs RESTful (JSON).

## 6. Considerações de Integração

*   O servidor Flask precisará de mecanismos para obter informações dos componentes do Autocura. Isso pode ser feito através de:
    *   Leitura de arquivos de status/log (se centralizados).
    *   Comunicação com APIs dos próprios componentes (se existirem).
    *   Consultas a sistemas de monitoramento (ex: Prometheus, se integrado).
    *   Comandos `kubectl` para status de pods/serviços Kubernetes (se o servidor Flask tiver permissão).

Este documento serve como base para o desenvolvimento inicial do frontend.

