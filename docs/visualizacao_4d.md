# Visualização 4D

O módulo de Visualização 4D do AutoCura fornece uma visão multidimensional do sistema, permitindo análise temporal, detecção de anomalias, correlações entre métricas e geração de relatórios.

## Conceitos

### Dimensões 4D

Uma dimensão 4D representa uma métrica do sistema com contexto temporal e metadados. Cada dimensão possui:

- Nome: Identificador único da dimensão
- Valor: Valor numérico da métrica
- Timestamp: Momento da coleta
- Contexto: Metadados adicionais (host, serviço, etc)

### Análise Temporal

O módulo permite analisar o comportamento das métricas ao longo do tempo, incluindo:

- Tendências: Detecção de padrões de crescimento/decrescimento
- Sazonalidade: Identificação de padrões cíclicos
- Anomalias: Detecção de valores fora do padrão esperado

### Correlações

O sistema calcula correlações entre diferentes dimensões, permitindo:

- Identificar relações causais
- Detectar dependências entre métricas
- Prever impactos em cascata

## API

### Dimensões

```python
# Criar uma nova dimensão
dimensao = Dimensao4D(
    nome="performance",
    valor=85.5,
    timestamp=datetime.now(),
    contexto={"host": "server1"}
)

# Atualizar dimensão
visualizador.atualizar_dimensao(
    nome="performance",
    valor=90.0,
    contexto={"host": "server1"}
)

# Obter dimensões
dimensoes = visualizador.obter_dimensao(
    nome="performance",
    periodo=timedelta(hours=1)
)
```

### Estatísticas

```python
# Calcular estatísticas
estatisticas = visualizador.calcular_estatisticas("performance")
print(f"Média: {estatisticas['media']:.2f}")
print(f"Mediana: {estatisticas['mediana']:.2f}")
print(f"Desvio Padrão: {estatisticas['desvio_padrao']:.2f}")
```

### Anomalias

```python
# Detectar anomalias
anomalias = visualizador.detectar_anomalias(
    "performance",
    threshold=2.0  # desvios padrão
)

for anomalia in anomalias:
    print(f"Valor: {anomalia['valor']:.2f}")
    print(f"Z-score: {anomalia['z_score']:.2f}")
    print(f"Timestamp: {anomalia['timestamp']}")
```

### Correlações

```python
# Calcular correlação entre duas dimensões
correlacao = visualizador.calcular_correlacoes(
    "performance",
    "saude"
)

# Gerar matriz de correlação
matriz = visualizador.gerar_matriz_correlacao()
```

### Tendências

```python
# Detectar tendências
tendencias = visualizador.detectar_tendencias("performance")
print(f"Tendência: {tendencias['tendencia']}")
print(f"Inclinação: {tendencias['inclinacao']:.2f}")
print(f"R²: {tendencias['r2']:.2f}")
```

### Relatórios

```python
# Gerar relatório completo
relatorio = visualizador.gerar_relatorio()
```

## Configuração

O módulo pode ser configurado através do arquivo `config.py` ou variáveis de ambiente:

```python
CONFIG = {
    "VISUALIZACAO_PERIODO": timedelta(days=7),
    "VISUALIZACAO_INTERVALO": 60,  # segundos
    "VISUALIZACAO_ANOMALIA_THRESHOLD": 2.0,
    "VISUALIZACAO_CORRELACAO_THRESHOLD": 0.7,
    "VISUALIZACAO_TENDENCIA_THRESHOLD": 0.1,
    "VISUALIZACAO_DIMENSOES": {
        "performance": {
            "descricao": "Métricas de performance",
            "unidade": "porcentagem",
            "limites": {"min": 0, "max": 100}
        }
    }
}
```

## Exemplos

### Monitoramento de Performance

```python
# Inicializar visualizador
visualizador = Visualizacao4D(CONFIG)

# Coletar métricas
while True:
    # Obter métricas do sistema
    cpu = psutil.cpu_percent()
    memoria = psutil.virtual_memory().percent
    
    # Atualizar dimensões
    visualizador.atualizar_dimensao(
        "performance",
        cpu,
        {"host": "server1", "tipo": "cpu"}
    )
    
    visualizador.atualizar_dimensao(
        "performance",
        memoria,
        {"host": "server1", "tipo": "memoria"}
    )
    
    # Verificar anomalias
    anomalias = visualizador.detectar_anomalias("performance")
    if anomalias:
        print("Anomalias detectadas!")
        for anomalia in anomalias:
            print(f"- {anomalia['valor']:.2f}")
    
    time.sleep(60)
```

### Análise de Correlações

```python
# Obter matriz de correlação
matriz = visualizador.gerar_matriz_correlacao()

# Identificar correlações fortes
for dim1 in matriz:
    for dim2, corr in matriz[dim1].items():
        if dim1 != dim2 and abs(corr) > 0.7:
            print(f"Correlação forte entre {dim1} e {dim2}: {corr:.2f}")
```

### Geração de Relatórios

```python
# Gerar relatório diário
relatorio = visualizador.gerar_relatorio()

# Salvar em arquivo
with open("relatorio_diario.json", "w") as f:
    json.dump(relatorio, f, indent=2)
```

## Boas Práticas

1. **Definição de Dimensões**
   - Use nomes descritivos
   - Inclua metadados relevantes
   - Defina limites apropriados

2. **Coleta de Dados**
   - Mantenha intervalo consistente
   - Valide dados antes de inserir
   - Limpe dados antigos regularmente

3. **Análise**
   - Ajuste thresholds conforme necessário
   - Considere contexto ao analisar anomalias
   - Monitore correlações importantes

4. **Visualização**
   - Use gráficos apropriados
   - Mantenha dashboard atualizado
   - Destaque informações relevantes

## Troubleshooting

### Problemas Comuns

1. **Dados Inconsistentes**
   - Verifique timestamps
   - Valide limites das dimensões
   - Confira formato dos dados

2. **Anomalias Falsas**
   - Ajuste threshold
   - Verifique sazonalidade
   - Considere contexto

3. **Performance**
   - Limpe dados antigos
   - Otimize queries
   - Use índices apropriados

### Logs e Monitoramento

- Verifique `visualizacao.log`
- Monitore uso de memória
- Acompanhe tempo de resposta

## Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature
3. Adicione testes
4. Atualize documentação
5. Envie pull request 