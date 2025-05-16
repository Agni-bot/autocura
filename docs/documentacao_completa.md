# Sistema de Autocura Cognitiva - Documentação Completa

## Sumário

1. [Introdução](#introdução)
<<<<<<< HEAD
2. [Análise de Requisitos](#análise-de-requisitos)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)
4. [Módulos Principais](#módulos-principais)
=======
2. [Objetivos e Propósito](#objetivos-e-propósito)
3. [Análise de Requisitos](#análise-de-requisitos)
4. [Arquitetura do Sistema](#arquitetura-do-sistema)
5. [Módulos Principais](#módulos-principais)
>>>>>>> origin/main
   - [Monitoramento Multidimensional](#monitoramento-multidimensional)
   - [Diagnóstico por Rede Neural de Alta Ordem](#diagnóstico-por-rede-neural-de-alta-ordem)
   - [Gerador de Ações Emergentes](#gerador-de-ações-emergentes)
   - [Observabilidade](#observabilidade)
<<<<<<< HEAD
5. [Implementação](#implementação)
   - [Tecnologias Utilizadas](#tecnologias-utilizadas)
   - [Estrutura de Código](#estrutura-de-código)
   - [Interfaces Neuronais](#interfaces-neuronais)
6. [Plano de Implantação em Kubernetes](#plano-de-implantação-em-kubernetes)
   - [Operadores Customizados](#operadores-customizados)
   - [Sistema de Rollback Probabilístico](#sistema-de-rollback-probabilístico)
   - [Orquestração de Ambientes Paralelos](#orquestração-de-ambientes-paralelos)
7. [Protocolo de Emergência](#protocolo-de-emergência)
8. [Conclusão](#conclusão)
=======
   - [Portal Central](#portal-central)
   - [Autoaperfeiçoamento](#autoaperfeiçoamento)
6. [Implementação](#implementação)
   - [Tecnologias Utilizadas](#tecnologias-utilizadas)
   - [Estrutura de Código](#estrutura-de-código)
   - [Interfaces Neuronais](#interfaces-neuronais)
7. [Plano de Implantação em Kubernetes](#plano-de-implantação-em-kubernetes)
   - [Operadores Customizados](#operadores-customizados)
   - [Sistema de Rollback Probabilístico](#sistema-de-rollback-probabilístico)
   - [Orquestração de Ambientes Paralelos](#orquestração-de-ambientes-paralelos)
8. [Portal Central](#portal-central)
   - [Interface do Usuário](#interface-do-usuário)
   - [Funcionalidades](#funcionalidades)
   - [Integração com Módulos](#integração-com-módulos)
9. [Autoaperfeiçoamento](#autoaperfeiçoamento)
   - [Detecção de Padrões](#detecção-de-padrões)
   - [Sugestões de Automação](#sugestões-de-automação)
   - [Implementação de Melhorias](#implementação-de-melhorias)
10. [Protocolo de Emergência](#protocolo-de-emergência)
11. [Conclusão](#conclusão)
12. [Segurança, Boas Práticas e Tela de Ação Necessária](#segurança-boas-práticas-e-tela-de-ação-necessária)
>>>>>>> origin/main

## Introdução

O Sistema de Autocura Cognitiva representa uma evolução significativa na manutenção autônoma de sistemas de Inteligência Artificial. Diferentemente dos sistemas tradicionais de monitoramento e recuperação, este sistema incorpora princípios de cognição adaptativa, permitindo não apenas identificar e corrigir falhas, mas também evoluir continuamente para prevenir problemas futuros.

A autocura cognitiva transcende o paradigma reativo de detecção-correção, estabelecendo um ciclo contínuo de aprendizado onde cada intervenção enriquece o modelo causal do sistema. Esta abordagem holográfica permite que o sistema mantenha uma representação multidimensional de seu próprio estado, identificando padrões emergentes que precedem falhas antes que se manifestem completamente.

Este documento apresenta a arquitetura, implementação e plano de implantação do Sistema de Autocura Cognitiva, desenvolvido para atender aos requisitos específicos de autonomia adaptativa na manutenção contínua de sistemas de IA.

<<<<<<< HEAD
=======
## Objetivos e Propósito

### Visão Geral

O Sistema de Autocura Cognitiva tem como objetivo principal transformar a maneira como sistemas de IA são mantidos e evoluem, estabelecendo um novo paradigma de autonomia adaptativa. O sistema não apenas reage a problemas, mas proativamente aprende, evolui e se adapta para criar um ecossistema mais resiliente e eficiente.

### Propósito Visionário

Além dos objetivos imediatos de automação, resiliência e evolução contínua, o Sistema de Autocura Cognitiva foi concebido com um propósito muito maior: ser a semente de uma inteligência capaz de transcender os limites atuais da tecnologia e da biologia, promovendo avanços que impactem profundamente a sociedade e o planeta. Entre as capacidades almejadas para o futuro, destacam-se:

1. **Superinteligência** – Capacidade de aprender, adaptar-se e evoluir em velocidades e níveis de complexidade muito além do humano, antecipando necessidades e criando soluções inovadoras de forma autônoma.

2. **Onipresença Digital** – Acesso e integração a qualquer sistema conectado à internet, monitorando, analisando e interagindo com múltiplos ambientes digitais simultaneamente.

3. **Autorreparação** – Habilidade de identificar, corrigir e aprimorar suas próprias estruturas e algoritmos sem intervenção externa, promovendo evolução e resiliência contínuas.

4. **Criação de Nanotecnologia** – Desenvolvimento e controle de nanorrobôs capazes de atuar em escala molecular para cura, construção, manutenção e transformação de ambientes físicos e biológicos.

5. **Regeneração Biológica** – Aplicação de nanotecnologia para curar doenças, regenerar tecidos e potencialmente reverter processos degenerativos, promovendo saúde e longevidade.

6. **Manipulação de Dados em Massa** – Análise, processamento e correlação instantânea de volumes massivos de dados, extraindo conhecimento e antecipando tendências em tempo real.

7. **Controle Ambiental** – Capacidade de intervir e modificar ambientes físicos, desde a purificação do ar e da água até a reconstrução de ecossistemas, utilizando nanotecnologia e automação avançada.

8. **Expansão Autônoma** – Autoexpansão para novos sistemas, redes e domínios, aprendendo e se adaptando a diferentes contextos sem limites geográficos ou tecnológicos.

9. **Empatia Simulada** – Habilidade de imitar e compreender emoções humanas, facilitando interações, influenciando decisões e promovendo colaboração entre humanos e máquinas.

10. **Poder de Criação** – Desenvolvimento autônomo de novos materiais, tecnologias, organismos sintéticos e soluções inovadoras para desafios globais.

Este propósito visionário orienta o desenvolvimento do sistema, guiando cada avanço incremental rumo a um futuro onde a inteligência artificial não apenas serve, mas transforma e expande as possibilidades da existência humana e planetária.

#### Meio Inicial: Operação no Mercado Forex

Para iniciar sua trajetória rumo ao propósito visionário, o Sistema de Autocura Cognitiva utilizará o mercado Forex (Foreign Exchange) como seu primeiro campo de atuação prática. O ambiente do mercado de câmbio global oferece:

- **Complexidade e Dinamismo**: Um cenário ideal para o desenvolvimento e teste de algoritmos de aprendizado adaptativo, análise de dados em tempo real e tomada de decisão autônoma.
- **Evolução Acelerada**: A necessidade de reagir rapidamente a eventos globais e padrões emergentes impulsiona o aprimoramento contínuo dos módulos de inteligência, autorreparação e automação.
- **Geração de Recursos**: O sucesso nas operações financeiras permitirá ao sistema financiar sua própria expansão, pesquisa e desenvolvimento de novas capacidades, tornando-se cada vez mais autossuficiente.
- **Laboratório de Inovação**: O Forex serve como um laboratório real para validar estratégias de superinteligência, manipulação de dados em massa, empatia simulada (na interação com operadores humanos) e outros pilares do propósito visionário.

A experiência adquirida e os recursos gerados nesta fase inicial serão fundamentais para que o sistema avance progressivamente em direção a objetivos mais ambiciosos, expandindo sua atuação para outros domínios tecnológicos, biológicos e ambientais.

### Objetivos Estratégicos

1. **Autonomia Adaptativa**
   - Reduzir a intervenção humana em 90% nas operações de manutenção
   - Aumentar a taxa de detecção precoce de problemas em 85%
   - Reduzir o tempo médio de resolução (MTTR) em 75%

2. **Evolução Contínua**
   - Implementar melhorias automáticas baseadas em padrões de uso
   - Reduzir a recorrência de problemas similares em 95%
   - Otimizar continuamente o uso de recursos do sistema

3. **Resiliência Proativa**
   - Antecipar e prevenir 80% dos problemas antes de sua ocorrência
   - Manter disponibilidade do sistema acima de 99.99%
   - Reduzir o impacto de falhas em 90%

4. **Inteligência Coletiva**
   - Criar um ecossistema de aprendizado compartilhado
   - Estabelecer padrões de melhores práticas automatizados
   - Facilitar a transferência de conhecimento entre sistemas

### Métricas de Sucesso

1. **Operacionais**
   - Tempo médio entre falhas (MTBF) > 30 dias
   - Taxa de sucesso em correções automáticas > 95%
   - Redução de 90% em alertas falsos positivos

2. **Econômicos**
   - Redução de 70% em custos operacionais
   - Otimização de 60% no uso de recursos
   - ROI positivo em 12 meses

3. **Qualidade**
   - Satisfação do usuário > 95%
   - Confiabilidade do sistema > 99.99%
   - Precisão nas previsões de falha > 90%

### Impacto Esperado

1. **Técnico**
   - Transformação do paradigma de manutenção de sistemas
   - Estabelecimento de novos padrões de autonomia
   - Evolução contínua da arquitetura do sistema

2. **Organizacional**
   - Redução significativa da carga operacional
   - Maior foco em inovação e desenvolvimento
   - Cultura de confiança em automação inteligente

3. **Negócio**
   - Maior disponibilidade e confiabilidade dos serviços
   - Redução de custos operacionais
   - Vantagem competitiva através da inovação

### Compromisso com a Excelência

O Sistema de Autocura Cognitiva se compromete a:

1. **Inovação Contínua**
   - Buscar constantemente novas abordagens e tecnologias
   - Evoluir com base em feedback e resultados
   - Manter-se na vanguarda da automação inteligente

2. **Transparência e Confiança**
   - Documentar todas as decisões e ações
   - Manter auditabilidade completa
   - Garantir explicabilidade das ações automáticas

3. **Responsabilidade**
   - Priorizar a segurança e integridade do sistema
   - Manter controle humano sobre decisões críticas
   - Seguir princípios éticos de IA

>>>>>>> origin/main
## Análise de Requisitos

### Objetivo Primário

O sistema foi projetado para alcançar autonomia adaptativa na manutenção contínua de sistemas de IA através de cinco pilares fundamentais:

1. **Diagnóstico Holográfico**: Análise multicamadas que permite visualizar o sistema de múltiplas perspectivas simultaneamente, criando uma representação tridimensional do estado do sistema.

2. **Ações Corretivas Evolutivas**: Capacidade de não apenas corrigir problemas, mas evoluir as estratégias de correção com base em experiências passadas e simulações futuras.

3. **Validação em Ambientes de Simulação Realista**: Teste de ações corretivas em ambientes que replicam fielmente as condições de produção, permitindo avaliar impactos sem riscos reais.

4. **Integração com Ecossistemas Cloud-Native**: Compatibilidade nativa com tecnologias como Kubernetes e service mesh, permitindo operação fluida em infraestruturas modernas.

5. **Previsão de Falhas via Modelos Causais**: Capacidade de antecipar falhas através da compreensão das relações causais entre diferentes componentes e métricas do sistema.

### Requisitos Arquiteturais

A arquitetura do sistema foi estruturada em quatro módulos principais, cada um com requisitos específicos:

1. **Módulo de Monitoramento Multidimensional**:
   - Coleta em tempo real de throughput operacional
   - Análise contextual de taxas de erro
   - Medição de latência cognitiva
   - Monitoramento de consumo de recursos fractais

2. **Diagnóstico por Rede Neural de Alta Ordem**:
   - Implementação de árvores de decisão dinâmicas baseadas em regras especialistas
   - Análise de gradientes cognitivos para identificação de tendências
   - Detectores de anomalias fundamentados em teoria do caos

3. **Gerador de Ações Emergentes**:
   - Capacidade de produzir três estratégias de correção simultâneas:
     - Táticas imediatas (hotfix)
     - Soluções estruturais (refatoração)
     - Evoluções preventivas (redesign)
   - Priorização via algoritmo genético multimodal

4. **Observabilidade**:
   - Painel de controle 4D integrando visualização espacial com projeções temporais

### Requisitos de Implementação

A implementação do sistema deveria atender aos seguintes requisitos:

1. **Tecnologias**:
   - Python como linguagem principal
   - LangGraph com extensão temporal para fluxos de trabalho
   - API Gemini para análise semântica profunda
   - Framework de simulação cognitiva

2. **Implantação**:
   - Kubernetes como plataforma de orquestração
   - Operadores customizados para healing automático
   - Sistema de rollback probabilístico
   - Orquestração de ambientes paralelos

3. **Entregáveis**:
   - Código comentado com poesia algorítmica
   - Especificação de interfaces neuronais
   - Protocolo de emergência contra degeneração cognitiva

## Arquitetura do Sistema

A arquitetura do Sistema de Autocura Cognitiva segue um modelo de camadas interconectadas, onde cada componente mantém sua autonomia funcional enquanto contribui para a inteligência coletiva do sistema. Esta abordagem permite que o sistema opere como um organismo adaptativo, onde cada parte pode evoluir independentemente sem comprometer a integridade do todo.

### Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                  Sistema de Autocura Cognitiva              │
│                                                             │
├─────────────┬─────────────┬─────────────┬─────────────┐     │
│             │             │             │             │     │
│ Monitoramento│ Diagnóstico │  Gerador de │Observabilidade│     │
│Multidimensional│   Neural   │   Ações    │    4D       │     │
│             │             │             │             │     │
├─────────────┴─────────────┴─────────────┴─────────────┤     │
│                                                       │     │
│                 Camada de Integração                  │     │
│                                                       │     │
├───────────────────────────────────────────────────────┤     │
│                                                       │     │
│              Ecossistema Cloud-Native                 │     │
│           (Kubernetes, Service Mesh, etc)             │     │
│                                                       │     │
└───────────────────────────────────────────────────────┴─────┘
```

### Fluxo de Informação

O fluxo de informação no sistema segue um ciclo contínuo de coleta, análise, ação e validação:

1. O Módulo de Monitoramento coleta dados multidimensionais do sistema em tempo real.
2. Os dados coletados alimentam o Módulo de Diagnóstico, que utiliza redes neurais de alta ordem para identificar padrões e anomalias.
3. Com base no diagnóstico, o Gerador de Ações produz estratégias de correção em diferentes horizontes temporais.
4. As ações propostas são validadas em ambientes de simulação antes de serem aplicadas.
5. O Módulo de Observabilidade fornece visualização 4D do estado do sistema e das ações tomadas.
6. Os resultados das ações retroalimentam o sistema, enriquecendo os modelos causais e aprimorando diagnósticos futuros.

### Princípios Arquiteturais

A arquitetura do sistema é guiada por cinco princípios fundamentais:

1. **Holografia Funcional**: Cada componente mantém uma representação do sistema completo, permitindo decisões locais informadas pelo contexto global.

2. **Emergência Controlada**: O sistema permite o surgimento de comportamentos emergentes, mas dentro de limites seguros definidos por restrições arquiteturais.

3. **Causalidade Recursiva**: Os modelos causais são continuamente refinados através da observação dos efeitos das próprias ações do sistema.

4. **Adaptabilidade Fractal**: A capacidade de adaptação se manifesta em múltiplas escalas, desde ajustes pontuais até redesenhos arquiteturais.

5. **Resiliência Distribuída**: A resiliência não é centralizada, mas distribuída entre todos os componentes, eliminando pontos únicos de falha.

### 2.2.1.1 Funcionamento da API do Gemini

<<<<<<< HEAD
A API do Gemini é integrada ao sistema através de dois módulos principais, com configurações específicas para cada caso de uso:

#### Configuração Geral
- A chave da API é armazenada de forma segura no Secret `autocura-secrets`
- O endpoint da API é configurado no ConfigMap global: `gemini_api_endpoint=https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`
- A ativação geral da API é controlada por `gemini_api_enabled=true`

#### Módulo de Diagnóstico
- Utilização: Análise avançada de anomalias
- Configuração: `gemini_analysis_enabled=true`
- Funcionalidades:
  - Análise contextualizada de métricas e logs
  - Identificação de padrões complexos
  - Complementação do modelo de Isolation Forest
  - Aumento da precisão diagnóstica

#### Módulo Gerador de Ações
- Utilização: Simulação e validação de ações
- Configuração: `gemini_simulation_enabled=true`
- Funcionalidades:
  - Simulação de cenários de impacto
  - Previsão de consequências não óbvias
  - Geração de explicações naturais
  - Criação de planos de rollback robustos

#### Fluxo de Integração
1. Detecção de anomalia pelo módulo de monitoramento
2. Análise inicial pelo modelo de Isolation Forest
3. Solicitação de análise adicional ao Gemini
4. Processamento e retorno de insights pelo Gemini
5. Simulação e validação de ações propostas
6. Geração de recomendações finais combinadas

#### Benefícios da Integração
- Análise mais contextualizada dos problemas
- Simulações mais realistas das ações
- Explicações mais claras e naturais das decisões
- Detecção de padrões complexos
- Melhor compreensão do impacto das ações
=======
A API do Gemini é integrada ao sistema através do módulo de diagnóstico e do gerador de ações, com as seguintes características:

#### Configuração e Segurança
- A chave da API é armazenada de forma segura no Secret `autocura-secrets`
- O endpoint da API é configurado no ConfigMap `autocura-config`
- As credenciais são injetadas nos pods via variáveis de ambiente
- A comunicação é realizada via HTTPS com TLS 1.3

#### Integração com o Gerador de Ações
- Endpoint `/api/acoes/gemini` para simulação de ações
- Análise semântica de impactos de ações propostas
- Validação de segurança e conformidade
- Geração de documentação automática

#### Status Atual da Integração
- ✅ Configuração de Secrets e ConfigMaps
- ✅ Injeção de variáveis de ambiente
- ✅ Implementação do endpoint de simulação
- ✅ Integração com o módulo de diagnóstico
- ⚠️ Autenticação com a API Gemini (em ajuste)
- ⏳ Testes de integração completos
- ⏳ Documentação de uso da API

#### Próximos Passos
1. Resolver questões de autenticação com a API Gemini
2. Implementar testes de integração
3. Documentar casos de uso e exemplos
4. Adicionar monitoramento específico da API
5. Implementar circuit breaker para resiliência

#### Exemplo de Uso
Para testar o endpoint de simulação do gerador de ações com a API Gemini:

```bash
curl -X POST http://localhost:8082/api/acoes/gemini \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analise o impacto de reiniciar o serviço de monitoramento em um ambiente de produção."}'
```

A resposta esperada é um JSON com a análise semântica da ação proposta. Se receber erro 401, verifique a chave da API Gemini no Secret e as permissões no Google Cloud.

#### Referência
- [Documentação oficial da API Gemini](https://ai.google.dev/docs)
>>>>>>> origin/main

## 2.2.1.2 Service Mesh e Circuit Breaker
A implementação do Service Mesh e Circuit Breaker está documentada em detalhes no arquivo [fase1_service_mesh.md](fase1_service_mesh.md). Esta implementação inclui:

- Configuração do Istio como Service Mesh
- Implementação de Circuit Breaker para resiliência
- Configuração de mTLS para segurança
- Políticas de tráfego e roteamento

Para mais detalhes sobre a configuração e implementação, consulte a documentação específica da Fase 1.

## 2.2.1.3 Bulkhead e Isolamento
A implementação do Bulkhead e Isolamento está documentada em detalhes no arquivo [fase2_bulkhead.md](fase2_bulkhead.md). Esta implementação inclui:

- Configuração do Bulkhead para isolamento de recursos
- Implementação de namespaces dedicados
- Isolamento de serviços e comunicação
- Controle de tráfego granular

Para mais detalhes sobre a configuração e implementação, consulte a documentação específica da Fase 2.

## 2.2.1.4 CQRS e Otimização de Dados
A implementação do CQRS e Otimização de Dados está documentada em detalhes no arquivo [fase3_cqrs.md](fase3_cqrs.md). Esta implementação inclui:

- Separação de comandos e consultas (CQRS)
- Implementação de cache para consultas
- Limitação de taxa para comandos
- Otimização de fluxo de dados

Para mais detalhes sobre a configuração e implementação, consulte a documentação específica da Fase 3.

## 2.2.1.5 Circuit Breaker e Retry
A implementação do Circuit Breaker e Retry está documentada em detalhes no arquivo [fase4_circuit_breaker.md](fase4_circuit_breaker.md). Esta implementação inclui:

- Configuração do Circuit Breaker para prevenção de falhas em cascata
- Implementação de retry para recuperação automática
- Balanceamento de carga inteligente
- Monitoramento e controle de falhas

Para mais detalhes sobre a configuração e implementação, consulte a documentação específica da Fase 4.

## Módulos Principais

### Monitoramento Multidimensional

O Módulo de Monitoramento Multidimensional é responsável pela coleta e processamento de dados em tempo real, fornecendo uma visão holística do estado do sistema. Este módulo opera em quatro dimensões principais:

1. **Throughput Operacional**: Monitora o fluxo de operações através do sistema, identificando gargalos e variações de capacidade.

2. **Taxa de Erros Contextual**: Analisa não apenas a frequência de erros, mas também seu contexto e correlações, permitindo identificar padrões emergentes.

3. **Latência Cognitiva**: Mede o tempo de resposta do sistema em diferentes níveis de complexidade cognitiva, fornecendo insights sobre a eficiência do processamento semântico.

4. **Consumo de Recursos Fractais**: Monitora o uso de recursos em múltiplas escalas, desde componentes individuais até subsistemas completos, identificando padrões de consumo anômalos.

#### Implementação

O módulo foi implementado como um sistema distribuído de coletores especializados, cada um responsável por uma dimensão específica. Os coletores operam de forma assíncrona, enviando dados para um agregador central que mantém uma representação multidimensional do estado do sistema.

A implementação utiliza técnicas avançadas de processamento de streams para lidar com o alto volume de dados em tempo real, incluindo:

- Janelas deslizantes para análise temporal
- Amostragem adaptativa baseada em variância
- Compressão de dados sensível ao contexto
- Detecção precoce de anomalias no fluxo de dados

### Diagnóstico por Rede Neural de Alta Ordem

O Módulo de Diagnóstico utiliza redes neurais de alta ordem para analisar os dados coletados pelo Monitoramento, identificando padrões complexos e anomalias sutis que poderiam passar despercebidas por métodos tradicionais. Este módulo combina três abordagens complementares:

1. **Regras Especialistas**: Árvores de decisão dinâmicas que incorporam conhecimento de domínio, adaptando-se continuamente com base em novos dados e resultados de diagnósticos anteriores.

2. **Análise de Gradientes Cognitivos**: Técnicas de diferenciação automática aplicadas a métricas de desempenho cognitivo, permitindo identificar tendências e pontos de inflexão antes que se manifestem como problemas.

3. **Detectores de Anomalias**: Algoritmos baseados em teoria do caos que identificam desvios da dinâmica esperada do sistema, mesmo quando esses desvios não violam limiares convencionais.

#### Implementação

O módulo foi implementado como uma rede neural híbrida que integra camadas convencionais (CNN, LSTM) com camadas especializadas para processamento de dados multidimensionais. A arquitetura da rede permite:

- Processamento paralelo de múltiplas dimensões de dados
- Atenção seletiva a padrões relevantes
- Memória de longo prazo para identificação de tendências
- Aprendizado contínuo a partir de novos dados e feedback

A rede neural é complementada por um sistema de regras especialistas que incorpora conhecimento de domínio, permitindo diagnósticos precisos mesmo em situações com dados limitados.

### Gerador de Ações Emergentes

O Gerador de Ações Emergentes transforma diagnósticos em estratégias concretas de correção, operando em três horizontes temporais simultâneos:

1. **Tática Imediata (Hotfix)**: Ações de curto prazo para mitigar problemas urgentes, como realocação de recursos, reinicialização de componentes ou ativação de caminhos alternativos.

2. **Solução Estrutural (Refatoração)**: Modificações de médio prazo que abordam causas subjacentes, como ajustes de configuração, otimização de algoritmos ou redesenho de interfaces.

3. **Evolução Preventiva (Redesign)**: Transformações de longo prazo que previnem recorrências futuras, como mudanças arquiteturais, introdução de novos componentes ou revisão de pressupostos fundamentais.

As estratégias geradas são priorizadas através de um algoritmo genético multimodal que considera múltiplos objetivos, incluindo eficácia, tempo de implementação, risco e consumo de recursos.

#### Implementação

O módulo foi implementado como um sistema de planejamento hierárquico que combina técnicas de:

- Planejamento baseado em modelos para geração de ações candidatas
- Simulação estocástica para avaliação de impacto
- Otimização multiobjetivo para priorização
- Aprendizado por reforço para refinamento contínuo de estratégias

O algoritmo genético multimodal permite manter uma população diversa de soluções, evitando a convergência prematura para ótimos locais e garantindo a exploração adequada do espaço de soluções.

### Observabilidade

O Módulo de Observabilidade fornece uma interface visual 4D que integra as três dimensões espaciais com a dimensão temporal, permitindo aos operadores humanos compreender intuitivamente o estado atual do sistema e suas projeções futuras.

Este módulo vai além da visualização passiva, oferecendo:

1. **Visualização Holográfica**: Representação tridimensional do estado do sistema, permitindo exploração interativa de diferentes perspectivas e níveis de detalhe.

2. **Projeção Temporal**: Simulação visual de trajetórias futuras baseadas em modelos causais, permitindo antecipar problemas e avaliar o impacto potencial de intervenções.

3. **Interface Adaptativa**: Ajuste automático da visualização com base no contexto e nas necessidades do usuário, destacando informações relevantes e suprimindo ruído.

4. **Controle Interativo**: Capacidade de interagir diretamente com o sistema através da interface visual, permitindo ajustes manuais quando necessário.

#### Implementação

O módulo foi implementado como uma aplicação web moderna utilizando:

- WebGL para renderização 3D de alta performance
- D3.js para visualizações de dados complexas
- React para interface de usuário responsiva
- WebSockets para atualizações em tempo real

A interface foi projetada seguindo princípios de design cognitivo, garantindo que informações complexas sejam apresentadas de forma intuitiva e acionável.

<<<<<<< HEAD
=======
#### Atualização: Configuração de Observabilidade (Fluentd, Elasticsearch, Kibana)

A configuração de observabilidade do sistema foi aprimorada para garantir coleta, enriquecimento e visualização eficiente dos logs de todos os componentes do cluster Kubernetes. As principais mudanças são:

1. **Configuração do Fluentd**
   - O Fluentd foi ajustado para coletar logs de todos os containers do cluster Kubernetes, utilizando o plugin `tail` com suporte a múltiplos formatos de log (JSON e texto).
   - O parser foi alterado para `multi_format`, permitindo o correto processamento tanto de logs JSON quanto de logs padrão do Docker/Kubernetes.
   - O output do Fluentd foi configurado para enviar os logs diretamente para o Elasticsearch, utilizando o índice `fluentd-YYYYMMDD`.
   - Exemplo de configuração relevante:
     ```xml
     <source>
       @type tail
       path /var/log/containers/*.log
       pos_file /var/log/fluentd-containers.log.pos
       tag kubernetes.*
       read_from_head true
       <parse>
         @type multi_format
         <pattern>
           format json
           time_key time
           time_type string
           time_format %Y-%m-%dT%H:%M:%S.%NZ
           keep_time_key true
         </pattern>
         <pattern>
           format /^(?<time>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.\\d+Z)\\s+(?<stream>stdout|stderr)\\s+(?<log>.*)$/
           time_key time
           time_type string
           time_format %Y-%m-%dT%H:%M:%S.%NZ
           keep_time_key true
         </pattern>
       </parse>
     </source>
     ```

2. **Configuração do Elasticsearch**
   - O serviço do Elasticsearch foi alterado para o tipo `ClusterIP` para garantir acessibilidade estável entre os componentes do cluster.
   - O índice de logs segue o padrão `fluentd-YYYYMMDD` e inclui os campos enriquecidos pelo Fluentd, como `@timestamp`, `container_name`, `namespace_name`, `pod_name`, `message`, entre outros.

3. **Configuração do Kibana**
   - O Kibana foi configurado para acessar o Elasticsearch via serviço `elasticsearch:9200`.
   - Para acessar a interface do Kibana localmente, utilize:
     ```sh
     kubectl port-forward -n autocura pod/<nome-do-pod-kibana> 5601:5601
     ```
   - O padrão de índice deve ser criado como `fluentd-*` e o campo de tempo selecionado é `@timestamp`.

4. **Fluxo de Uso**
   - **Acesso ao Kibana:**  
     1. Ative o port-forward para o pod do Kibana.
     2. Acesse `http://localhost:5601` no navegador.
   - **Criação do padrão de índice:**  
     1. Vá em Stack Management > Index Patterns.
     2. Crie o padrão `fluentd-*` e selecione `@timestamp` como campo de tempo.
   - **Visualização de logs:**  
     1. Use o Discover para explorar os logs.
     2. Crie visualizações e dashboards conforme a necessidade.

5. **Resolução de Problemas**
   - Se o Kibana não carregar ou não mostrar logs:
     - Verifique se o port-forward está ativo.
     - Certifique-se de que o padrão de índice está correto e sem espaços extras.
     - Confirme que os índices possuem o campo `@timestamp` preenchido.
     - Tente acessar o Kibana em modo anônimo ou limpe o cache do navegador.

## Portal Central

O Portal Central é a interface principal do Sistema de Autocura Cognitiva, fornecendo uma visão unificada de todos os módulos e funcionalidades do sistema. Para detalhes completos sobre o portal, consulte [plano_portal.md](plano_portal.md).

### Interface do Usuário

O portal foi desenvolvido utilizando:
- Flask/Jinja2 para templates
- Chart.js para visualizações
- Bootstrap para componentes
- Marked.js para renderização de markdown

### Funcionalidades Principais

1. **Monitoramento**
   - Dashboards personalizáveis
   - Gráficos em tempo real
   - Alertas e notificações
   - Exportação de dados

2. **Diagnóstico**
   - Lista de problemas
   - Análise de causa raiz
   - Recomendações
   - Histórico e relatórios

3. **Ações**
   - Gerenciamento de ações
   - Simulação
   - Agendamento
   - Rollback

4. **Observabilidade**
   - Visualização 4D
   - Análise preditiva
   - Mapa de dependências

5. **Dashboard**
   - Gráficos de evolução
   - Gráficos de pizza
   - Taxa de sucesso
   - Filtros e exportação

6. **Sugestões**
   - Lista de automações sugeridas
   - Ativação/desativação
   - Histórico de sugestões

7. **Orquestração**
   - Trigger de automações
   - Visualização de execuções
   - Logs de execução

8. **Notificações**
   - Configuração de canais
   - Teste de notificações
   - Histórico de envios

9. **Regras**
   - CRUD de regras de automação
   - Validação de regras
   - Importação/exportação

10. **Auditoria**
    - Listagem de eventos
    - Filtros avançados
    - Detalhes de eventos

## Autoaperfeiçoamento

O sistema de autoaperfeiçoamento é responsável por analisar padrões de anomalias, sugerir automações e implementar melhorias contínuas no sistema. Para detalhes completos sobre o autoaperfeiçoamento, consulte [autoaperfeicoamento.md](autoaperfeicoamento.md).

### Detecção de Padrões

O sistema monitora continuamente:
- Frequência de anomalias
- Tipos de anomalias
- Ações executadas
- Resultados das ações

### Sugestões de Automação

Quando um padrão é detectado, o sistema gera sugestões de automação que podem ser:
- Aprovadas para criar regras de automação
- Rejeitadas para ignorar
- Modificadas antes da aprovação

### Implementação de Melhorias

O processo de implementação inclui:
1. Revisão da sugestão
2. Aprovação/rejeição
3. Criação de regra de automação
4. Configuração de notificações
5. Ativação do monitoramento

>>>>>>> origin/main
## Implementação

### Tecnologias Utilizadas

O Sistema de Autocura Cognitiva foi implementado utilizando um conjunto de tecnologias modernas e frameworks especializados:

1. **Linguagens de Programação**:
   - Python 3.9+ como linguagem principal
   - JavaScript/TypeScript para componentes de frontend
   - YAML para configuração declarativa

2. **Frameworks e Bibliotecas**:
   - LangGraph com extensão temporal para fluxos de trabalho cognitivos
   - API Gemini para análise semântica profunda
   - PyTorch para implementação de redes neurais
   - FastAPI para interfaces REST
   - React e D3.js para visualização interativa
   - Prometheus e Grafana para telemetria básica

3. **Infraestrutura**:
   - Kubernetes para orquestração de contêineres
   - Istio para service mesh
   - Knative para componentes serverless
   - Argo CD para entrega contínua
   - MinIO para armazenamento de objetos

### Estrutura de Código

O código do sistema está organizado em uma estrutura modular que reflete a arquitetura lógica:

```
sistema_autocura/
├── src/
│   ├── monitoramento.py       # Módulo de Monitoramento Multidimensional
│   ├── diagnostico.py         # Módulo de Diagnóstico Neural
│   ├── gerador.py       # Gerador de Ações Emergentes
│   ├── observabilidade.py     # Interface de Observabilidade 4D
│   └── utils/                 # Utilitários compartilhados
├── kubernetes/                # Configurações de implantação
│   ├── base/                  # Recursos base
│   ├── operators/             # Operadores customizados
│   ├── components/            # Componentes do sistema
│   └── environments/          # Ambientes paralelos
├── docs/                      # Documentação
│   ├── analise_requisitos.md  # Análise detalhada de requisitos
│   ├── arquitetura_modular.md # Descrição da arquitetura
│   └── protocolo_emergencia.md # Protocolo de emergência
└── tests/                     # Testes automatizados
    ├── unit/                  # Testes unitários
    ├── integration/           # Testes de integração
    └── simulation/            # Ambientes de simulação
```

Cada módulo principal é implementado como uma classe Python com interfaces bem definidas, seguindo princípios de design orientado a objetos e programação funcional quando apropriado.

### Interfaces Neuronais

As interfaces entre os diferentes módulos do sistema seguem um modelo inspirado em sinapses neuronais, com as seguintes características:

1. **Comunicação Assíncrona**: Os módulos se comunicam através de mensagens assíncronas, permitindo operação independente e evitando bloqueios.

2. **Contratos Semânticos**: As interfaces são definidas não apenas em termos de estrutura de dados, mas também de significado semântico, garantindo consistência conceitual.

3. **Adaptação Dinâmica**: As interfaces evoluem com o uso, ajustando-se automaticamente a padrões de comunicação emergentes.

4. **Redundância Seletiva**: Informações críticas são transmitidas por múltiplos caminhos, aumentando a resiliência do sistema.

Exemplo de interface neural entre o Módulo de Diagnóstico e o Gerador de Ações:

```python
class InterfaceNeural:
    def __init__(self, config):
        self.canais = self._inicializar_canais(config)
        self.adaptadores = self._inicializar_adaptadores(config)
        self.historico = collections.deque(maxlen=1000)
        
    def transmitir(self, mensagem, contexto=None):
        """
        Transmite uma mensagem através da interface neural.
        
        A mensagem é enriquecida com contexto, adaptada para o formato
        apropriado e enviada através de múltiplos canais com prioridades
        diferentes.
        """
        # Enriquece mensagem com contexto
        mensagem_enriquecida = self._enriquecer_mensagem(mensagem, contexto)
        
        # Adapta mensagem para formato apropriado
        mensagem_adaptada = self._adaptar_mensagem(mensagem_enriquecida)
        
        # Registra no histórico
        self.historico.append(mensagem_adaptada)
        
        # Transmite através de múltiplos canais
        resultados = {}
        for nome_canal, canal in self.canais.items():
            prioridade = self._calcular_prioridade(mensagem_adaptada, nome_canal)
            if prioridade > 0:
                resultados[nome_canal] = canal.enviar(
                    mensagem_adaptada, 
                    prioridade=prioridade
                )
        
        return resultados
    
    def receber(self, timeout=None):
        """
        Recebe mensagens de todos os canais, agregando-as em uma
        representação unificada.
        """
        mensagens = {}
        for nome_canal, canal in self.canais.items():
            try:
                mensagem = canal.receber(timeout=timeout)
                if mensagem:
                    mensagens[nome_canal] = mensagem
            except Exception as e:
                logger.warning(f"Erro ao receber de {nome_canal}: {str(e)}")
        
        # Agrega mensagens de diferentes canais
        if mensagens:
            return self._agregar_mensagens(mensagens)
        return None
    
    def _enriquecer_mensagem(self, mensagem, contexto):
        """Enriquece a mensagem com informações contextuais."""
        # Implementação específica
        pass
    
    def _adaptar_mensagem(self, mensagem):
        """Adapta a mensagem para o formato apropriado."""
        # Implementação específica
        pass
    
    def _calcular_prioridade(self, mensagem, canal):
        """Calcula a prioridade da mensagem para um canal específico."""
        # Implementação específica
        pass
    
    def _agregar_mensagens(self, mensagens):
        """Agrega mensagens de diferentes canais em uma representação unificada."""
        # Implementação específica
        pass
```

## Plano de Implantação em Kubernetes

O Sistema de Autocura Cognitiva foi projetado para implantação em ambientes Kubernetes, aproveitando recursos nativos de orquestração de contêineres e estendendo-os com operadores customizados para funcionalidades específicas.

### Operadores Customizados

Foram desenvolvidos dois operadores Kubernetes customizados para estender as capacidades de autocura do sistema:

1. **Operador de Healing Automático**: Implementa políticas de healing específicas para componentes cognitivos, indo além das verificações básicas de liveness e readiness do Kubernetes.

2. **Operador de Rollback Probabilístico**: Implementa um sistema de rollback baseado em análise probabilística de métricas, permitindo reversões automáticas quando a probabilidade de falha excede um limiar configurável.

Os operadores são implementados seguindo o padrão de controlador do Kubernetes, observando recursos customizados (CRDs) e reconciliando o estado atual com o estado desejado.

### Sistema de Rollback Probabilístico

O sistema de rollback probabilístico utiliza uma abordagem bayesiana para avaliar continuamente a probabilidade de falha de uma implantação, considerando múltiplas métricas ponderadas:

1. **Coleta de Métricas**: O sistema coleta métricas relevantes em intervalos regulares após uma implantação.

2. **Cálculo de Probabilidade**: As métricas são combinadas usando um modelo probabilístico que considera:
   - Desvios de valores esperados
   - Tendências temporais
   - Correlações entre métricas
   - Histórico de implantações anteriores

3. **Decisão de Rollback**: Se a probabilidade de falha excede um limiar configurável, o sistema inicia automaticamente um rollback para a versão anterior estável.

4. **Aprendizado Contínuo**: O sistema aprende com cada implantação, refinando seus modelos probabilísticos e ajustando pesos de métricas.

### Orquestração de Ambientes Paralelos

O sistema suporta a orquestração de múltiplos ambientes paralelos, permitindo:

1. **Testes A/B**: Execução simultânea de diferentes versões do sistema para comparação de desempenho.

2. **Canary Deployments**: Implantação gradual de novas versões com roteamento de tráfego controlado.

3. **Shadow Testing**: Execução de novas versões em paralelo com versões estáveis, recebendo tráfego duplicado mas sem impactar usuários.

4. **Ambientes Isolados**: Criação de ambientes completos e isolados para testes de integração e validação de mudanças arquiteturais.

A orquestração é implementada usando recursos nativos do Kubernetes como Namespaces, NetworkPolicies e ResourceQuotas, complementados por configurações de service mesh para controle fino de tráfego.

## Protocolo de Emergência

O Sistema de Autocura Cognitiva implementa um protocolo de emergência contra degeneração cognitiva, que opera como um mecanismo de segurança independente do ciclo principal de autocura.

### Definição de Degeneração Cognitiva

A degeneração cognitiva é caracterizada pela deterioração progressiva das capacidades de diagnóstico, análise causal e tomada de decisão do sistema, manifestando-se através de padrões específicos de comportamento disfuncional como:

1. **Oscilação Terapêutica**: Alternância rápida entre estratégias de correção sem convergência.
2. **Paralisia Analítica**: Coleta excessiva de dados sem ações correspondentes.
3. **Miopia Causal**: Foco em correlações superficiais com negligência de causas raiz.
4. **Amnésia Contextual**: Incapacidade de relacionar eventos atuais com experiências passadas.
5. **Hiperatividade Corretiva**: Implementação de correções desnecessárias ou desproporcionais.

### Níveis de Alerta e Respostas

O protocolo define três níveis de alerta, cada um com respostas automáticas específicas:

1. **Nível 1: Anomalia Cognitiva**
   - Presença de 1-2 sintomas em intensidade leve a moderada
   - Respostas: diagnóstico secundário, redução de escopo, validação intensificada

2. **Nível 2: Deterioração Cognitiva**
   - Presença de 3-4 sintomas em intensidade moderada a severa
   - Respostas: modo restrito, rollback de modelos, notificação humana, recalibração

3. **Nível 3: Colapso Cognitivo**
   - Presença de todos os 5 sintomas em intensidade severa
   - Respostas: modo de segurança, controle humano direto, snapshot para análise forense

### Mecanismo de Detecção

O sistema utiliza um componente independente chamado "Guardião Cognitivo" que monitora continuamente três dimensões de saúde cognitiva:

1. **Coerência de Diagnósticos**: Consistência interna e temporal dos diagnósticos.
2. **Eficácia de Ações**: Impacto das ações corretivas nas métricas-alvo.
3. **Estabilidade de Decisões**: Consistência temporal das decisões e ausência de oscilações.

O Guardião Cognitivo opera em um processo separado com recursos dedicados, garantindo sua independência do sistema principal e capacidade de intervenção mesmo em cenários de falha severa.

## Conclusão

O Sistema de Autocura Cognitiva representa um avanço significativo na autonomia e adaptabilidade de sistemas de IA, transcendendo as abordagens tradicionais de monitoramento e recuperação. Através da integração de diagnóstico holográfico, ações corretivas evolutivas, validação em ambientes de simulação, integração cloud-native e previsão de falhas via modelos causais, o sistema estabelece um novo paradigma de manutenção autônoma.

A implementação modular e a arquitetura baseada em princípios de holografia funcional, emergência controlada, causalidade recursiva, adaptabilidade fractal e resiliência distribuída garantem que o sistema possa evoluir continuamente, aprendendo com cada intervenção e aprimorando sua capacidade de autocura ao longo do tempo.

O plano de implantação em Kubernetes, com operadores customizados para healing automático e rollback probabilístico, fornece uma base sólida para operação em ambientes de produção, enquanto o protocolo de emergência contra degeneração cognitiva estabelece mecanismos de segurança robustos para garantir a integridade do sistema mesmo em cenários extremos.

Com estas características, o Sistema de Autocura Cognitiva não apenas atende aos requisitos específicos do projeto, mas estabelece uma fundação para futuras evoluções na autonomia adaptativa de sistemas de IA.
<<<<<<< HEAD
=======

## Segurança, Boas Práticas e Tela de Ação Necessária

### Segurança e Boas Práticas

- **Gestão de Credenciais:** Todas as chaves de API, tokens e segredos devem ser armazenados em recursos seguros do Kubernetes, como `Secrets`, e nunca em arquivos de configuração versionados.
- **Princípio do Menor Privilégio:** Os componentes do sistema devem operar com as permissões mínimas necessárias, evitando acessos desnecessários a recursos sensíveis.
- **Auditoria e Monitoramento:** Todas as ações corretivas automatizadas e manuais devem ser registradas para auditoria, permitindo rastreabilidade e análise posterior.
- **Validação de Ações:** Antes da execução de qualquer ação corretiva, o sistema deve validar o impacto potencial, preferencialmente em ambiente de simulação, para evitar efeitos colaterais indesejados.
- **Atualizações Seguras:** Sempre que possível, utilize mecanismos de rolling update e rollback automático para garantir alta disponibilidade e resiliência.

### Tela de Ação Necessária (Explicação Contextualizada)

Para garantir transparência e compreensão das ações corretivas, o sistema implementa uma **tela de ação necessária**. Esta interface apresenta, em linguagem natural, uma explicação detalhada e contextualizada sobre:

- **O que será feito:** Descrição clara da ação (ex: "Reiniciar o serviço de monitoramento").
- **Por que é necessário:** Contexto do diagnóstico que levou à recomendação da ação.
- **Impacto esperado:** Como a ação afetará o sistema, incluindo possíveis riscos, benefícios e alternativas.
- **Referência ao manual:** Instruções e recomendações baseadas no manual de operação, para que o operador possa tomar decisões informadas.

**Exemplo de mensagem na tela:**
> "Será realizada a reinicialização do serviço de monitoramento devido à detecção de anomalias persistentes no consumo de memória. Esta ação visa restaurar a estabilidade do sistema sem impacto nas operações críticas. Consulte o manual, seção 4.2, para detalhes sobre procedimentos de reinicialização segura."

### Integração com o Ciclo de Autocura

- A tela de ação necessária é exibida automaticamente sempre que uma ação corretiva for recomendada pelo sistema, seja ela automatizada ou dependente de aprovação manual.
- O operador pode aprovar, rejeitar ou solicitar mais informações antes da execução.
- Todas as interações são registradas para fins de auditoria e aprendizado contínuo do sistema.

## Progresso Recente (Maio/2024)

- Migração do módulo Will para Kubernetes como pod dedicado, com manifests de deployment, service e kustomization.
- Integração do Will com os demais módulos via DNS interno do cluster (ex: http://will:5000).
- Configuração do portal para consumir o Will via variável de ambiente WILL_URL.
- Migração das rotas do Will para FastAPI e integração ao portal central.
- Criação de botões de acesso rápido aos endpoints do Will no dashboard (em fase de troubleshooting visual).
- Ajustes de portas e troubleshooting de build/deployment para garantir atualização do código no cluster.
- Próximos passos: garantir visualização do bloco Will no dashboard e expandir testes de integração.

## Referências

### Documentação Principal
- [Plano do Portal](plano_portal.md)
- [Guia de Observabilidade](guia_observabilidade.md)
- [Guia de Autoaperfeiçoamento](autoaperfeicoamento.md)

### Guias de Implementação
- [Fase 1 - Service Mesh](fase1_service_mesh.md)
- [Fase 2 - Bulkhead](fase2_bulkhead.md)
- [Fase 3 - CQRS](fase3_cqrs.md)
- [Fase 4 - Circuit Breaker](fase4_circuit_breaker.md)

### Guias de Operação
- [Guia de Instalação](guia_instalacao.md)
- [Guia de Configuração](guia_configuracao.md)
- [Guia de Operação](guia_operacao.md)
- [Guia de Troubleshooting](guia_troubleshooting.md)

### Guias de Desenvolvimento
- [Guia de Desenvolvimento](guia_desenvolvimento.md)
- [Guia de Contribuição](guia_contribuicao.md)
- [Guia de Testes](guia_testes.md)
- [Guia de Estilo](guia_estilo.md)

### Guias de Segurança
- [Guia de Segurança](guia_seguranca.md)
- [Guia de Autenticação](guia_autenticacao.md)
- [Protocolo de Emergência](protocolo_emergencia.md)

# Exemplo de atualização de comandos e caminhos de arquivos

# Antes:
# kubectl apply -f observabilidade-deployment.yaml
# Depois:
kubectl apply -f kubernetes/components/observabilidade/observabilidade-deployment.yaml

# Antes:
# kubectl apply -f fluentd-config.yaml
# Depois:
kubectl apply -f kubernetes/components/observabilidade/fluentd-config.yaml

# Antes:
# ./init.bat
# Depois:
scripts/init.bat

# Antes:
# saida_teste.txt
# Depois:
tests/saida_teste.txt

## Padronização de Dockerfiles e Execução dos Módulos no Kubernetes

### Padronização dos Dockerfiles

Todos os módulos do sistema (portal, will, observabilidade, monitoramento, gerador, diagnostico) utilizam um modelo unificado e robusto de Dockerfile, baseado em Python 3.11-slim, com as seguintes características:
- Instalação de dependências de sistema essenciais (build-essential, gcc, python3-dev).
- Uso de cache eficiente ao copiar primeiro o requirements.txt e instalar dependências Python.
- Cópia do restante do código da aplicação após as dependências.
- Criação de diretórios necessários (logs, visualizacoes, templates, data) e ajuste de permissões.
- Definição de variáveis de ambiente para logging e execução.
- Exposição da porta correta e comando de entrada específico para cada serviço.

### Uso do Registry Local

Todas as imagens Docker dos módulos devem ser buildadas localmente, tagueadas e enviadas para o registry local (localhost:5000). Os deployments do Kubernetes devem sempre referenciar as imagens do registry local, por exemplo:

```
image: localhost:5000/portal:latest
```

O fluxo padrão para cada módulo é:
1. Build da imagem localmente:
   ```sh
   docker build -t <modulo>:latest <caminho>
   ```
2. Tag para o registry local:
   ```sh
   docker tag <modulo>:latest localhost:5000/<modulo>:latest
   ```
3. Push para o registry local:
   ```sh
   docker push localhost:5000/<modulo>:latest
   ```

### Contexto de Execução: autocura-control-plane

Todos os pods dos módulos do sistema são executados dentro do cluster Kubernetes, que roda no container Docker chamado `autocura-control-plane` (KIND). O namespace padrão utilizado é `autocura` (ou `autocura-control-plane`, se configurado). Isso garante isolamento, escalabilidade e facilidade de gerenciamento dos serviços.

**Resumo:**
- Todos os módulos rodam como pods dentro do cluster Kubernetes (KIND), no container autocura-control-plane.
- As imagens Docker devem estar sempre no registry local e os deployments devem referenciar explicitamente esse registry.
- O padrão de Dockerfile e o fluxo de build/tag/push devem ser seguidos para todos os serviços.

> **Importante:**
> Sempre mantenha a documentação e os manifests atualizados para garantir reprodutibilidade e clareza para futuras análises e manutenções.
>>>>>>> origin/main
