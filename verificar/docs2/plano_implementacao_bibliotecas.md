# Plano Lógico-Estratégico para Implementação de Bibliotecas Avançadas no Autocura

## Visão Geral

Este documento apresenta um plano estratégico para implementação das bibliotecas avançadas pendentes no sistema Autocura, estruturado como um tutorial prático. O plano segue uma abordagem incremental, priorizando integrações que oferecem maior valor imediato e considerando as dependências entre componentes.

## Estratégia de Implementação

### Princípios Orientadores

1. **Modularidade**: Manter a separação de responsabilidades e interfaces bem definidas.
2. **Testabilidade**: Implementar testes unitários e de integração para cada novo componente.
3. **Isolamento**: Usar ambientes virtuais Python para gerenciar dependências.
4. **Documentação**: Documentar APIs, modelos e fluxos de dados.
5. **Versionamento**: Controlar versões de modelos e dados de treinamento.

### Ordem de Implementação Recomendada

Recomendamos a seguinte sequência de implementação, baseada em dependências e valor agregado:

1. **PyTorch** - Base para modelos de ML/DL
2. **Hugging Face Transformers** - Modelos pré-treinados para NLP
3. **TensorFlow Agents** - Aprendizado por reforço
4. **SHAP/LIME** - Explicabilidade para modelos implementados
5. **MLflow** - Tracking de experimentos e modelos
6. **Apache Arrow** - Otimização de processamento de dados
7. **GraphQL** - API para consultas cruzadas

### Pré-requisitos Gerais

Antes de iniciar as implementações específicas, configure o ambiente de desenvolvimento:

```bash
# Criar ambiente virtual Python
python -m venv autocura-env

# Ativar ambiente virtual
source autocura-env/bin/activate  # Linux/Mac
# ou
.\autocura-env\Scripts\activate  # Windows

# Instalar dependências básicas
pip install -U pip setuptools wheel
pip install pytest pytest-cov black isort mypy
```

Agora, vamos detalhar a implementação de cada biblioteca.

## 1. Implementação do TensorFlow Agents para Aprendizado por Reforço

### Contexto no Autocura
O TensorFlow Agents será utilizado no módulo de autocorreção avançada (`advanced_repair.py`), especificamente na classe `ReinforcementLearner`, para implementar aprendizado por reforço que permitirá ao sistema aprender a corrigir falhas cognitivas de forma autônoma.

### Passo 1: Instalação e Configuração

```bash
# Ativar ambiente virtual
source autocura-env/bin/activate

# Instalar TensorFlow e TF-Agents
pip install tensorflow==2.12.0
pip install tf-agents==0.16.0

# Dependências adicionais para visualização e debugging
pip install matplotlib
pip install tensorboard
```

### Passo 2: Definir o Ambiente de Aprendizado por Reforço

Crie um novo arquivo `src/autocorrection/rl_environment.py`:

```python
import numpy as np
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
from ..core.failure_definitions import CognitiveFailureTypes

class AutocuraRLEnvironment(py_environment.PyEnvironment):
    """Ambiente de RL para o Autocura que simula o processo de correção de falhas."""
    
    def __init__(self):
        # Define o espaço de ações (discreto para este exemplo)
        # Exemplo: 0=retrain, 1=patch_ontology, 2=adjust_resources, etc.
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=3, name='action')
        
        # Define o espaço de observação (features do estado do sistema)
        # Exemplo: [falha_tipo, severidade, componente_afetado_id, ...]
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(10,), dtype=np.float32, minimum=0, maximum=1, name='observation')
        
        # Estado interno
        self._state = np.zeros(10, dtype=np.float32)
        self._episode_ended = False
    
    def action_spec(self):
        return self._action_spec
    
    def observation_spec(self):
        return self._observation_spec
    
    def _reset(self):
        """Reinicia o ambiente para um novo episódio."""
        self._state = np.random.uniform(0, 1, 10).astype(np.float32)
        self._episode_ended = False
        return ts.restart(self._state)
    
    def _step(self, action):
        """Executa uma ação no ambiente e retorna o próximo estado e recompensa."""
        if self._episode_ended:
            # Se o episódio terminou, reinicie o ambiente
            return self.reset()
        
        # Simular o efeito da ação no ambiente
        # Em um ambiente real, isso interagiria com o sistema Autocura
        
        # Exemplo: Atualizar o estado com base na ação
        if action == 0:  # retrain
            self._state[2:5] += 0.1  # Melhora alguns aspectos do estado
        elif action == 1:  # patch_ontology
            self._state[5:8] += 0.1  # Melhora outros aspectos
        elif action == 2:  # adjust_resources
            self._state[8:] += 0.1  # Melhora recursos
        
        # Normalizar estado para manter valores entre 0 e 1
        self._state = np.clip(self._state, 0, 1)
        
        # Calcular recompensa baseada na melhoria do estado
        # Maior recompensa para estados mais próximos do ideal (1.0)
        reward = np.mean(self._state)
        
        # Verificar se o episódio deve terminar
        # Exemplo: terminar se a média do estado for alta o suficiente
        if reward > 0.8:
            self._episode_ended = True
            return ts.termination(self._state, reward)
        else:
            return ts.transition(self._state, reward, discount=0.99)
```

### Passo 3: Implementar o ReinforcementLearner

Modifique o arquivo `src/autocorrection/advanced_repair.py` para implementar a classe `ReinforcementLearner`:

```python
from tf_agents.agents.dqn import dqn_agent
from tf_agents.networks import q_network
from tf_agents.environments import tf_py_environment
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.trajectories import trajectory
from tf_agents.utils import common
from tf_agents.policies import random_tf_policy
from tf_agents.eval import metric_utils

from .rl_environment import AutocuraRLEnvironment

import tensorflow as tf
import numpy as np
import os

class ReinforcementLearner:
    """Implementa aprendizado por reforço para correção autônoma de falhas."""
    
    def __init__(self, model_dir='/tmp/autocura_rl_model'):
        """Inicializa o agente de RL.
        
        Args:
            model_dir: Diretório para salvar/carregar o modelo treinado.
        """
        print("[ReinforcementLearner] Inicializando com TF-Agents")
        
        # Criar ambientes de treino e avaliação
        self._train_py_env = AutocuraRLEnvironment()
        self._eval_py_env = AutocuraRLEnvironment()
        
        self._train_env = tf_py_environment.TFPyEnvironment(self._train_py_env)
        self._eval_env = tf_py_environment.TFPyEnvironment(self._eval_py_env)
        
        # Criar rede Q para o agente DQN
        fc_layer_params = (100, 50)
        q_net = q_network.QNetwork(
            self._train_env.observation_spec(),
            self._train_env.action_spec(),
            fc_layer_params=fc_layer_params)
        
        # Hiperparâmetros para o agente
        learning_rate = 1e-3
        optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        
        train_step_counter = tf.Variable(0)
        
        # Criar o agente DQN
        self.agent = dqn_agent.DqnAgent(
            self._train_env.time_step_spec(),
            self._train_env.action_spec(),
            q_network=q_net,
            optimizer=optimizer,
            td_errors_loss_fn=common.element_wise_squared_loss,
            train_step_counter=train_step_counter)
        
        self.agent.initialize()
        
        # Política para coleta de dados
        self.eval_policy = self.agent.policy
        self.collect_policy = self.agent.collect_policy
        
        # Replay buffer para armazenar experiências
        self.replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
            data_spec=self.agent.collect_data_spec,
            batch_size=self._train_env.batch_size,
            max_length=100000)
        
        # Diretório para salvar o modelo
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Carregar modelo se existir
        self._try_load_model()
    
    def _try_load_model(self):
        """Tenta carregar um modelo previamente treinado."""
        checkpoint_dir = os.path.join(self.model_dir, 'checkpoint')
        train_checkpointer = common.Checkpointer(
            ckpt_dir=checkpoint_dir,
            agent=self.agent,
            global_step=self.agent.train_step_counter)
        
        train_checkpointer.initialize_or_restore()
        print(f"[ReinforcementLearner] Modelo restaurado do passo: {self.agent.train_step_counter.numpy()}")
    
    def collect_data(self, steps=1000):
        """Coleta dados para treinamento usando a política atual."""
        print(f"[ReinforcementLearner] Coletando {steps} passos de dados para treinamento")
        
        initial_collect_policy = random_tf_policy.RandomTFPolicy(
            self._train_env.time_step_spec(),
            self._train_env.action_spec())
        
        # Coletar dados iniciais com política aleatória
        dynamic_step_driver = dynamic_step_driver.DynamicStepDriver(
            self._train_env,
            initial_collect_policy,
            observers=[self.replay_buffer.add_batch],
            num_steps=steps)
        
        dynamic_step_driver.run()
    
    def train(self, num_iterations=1000):
        """Treina o agente por um número específico de iterações."""
        print(f"[ReinforcementLearner] Iniciando treinamento por {num_iterations} iterações")
        
        # Dataset para treinamento
        dataset = self.replay_buffer.as_dataset(
            num_parallel_calls=3,
            sample_batch_size=64,
            num_steps=2).prefetch(3)
        
        iterator = iter(dataset)
        
        # Compilar o método de treinamento do agente para melhor desempenho
        self.agent.train = common.function(self.agent.train)
        
        # Loop de treinamento
        for _ in range(num_iterations):
            # Amostra uma batch do replay buffer
            experience, unused_info = next(iterator)
            # Treina o agente
            train_loss = self.agent.train(experience).loss
            
            # Periodicamente, salva o modelo e avalia o desempenho
            step = self.agent.train_step_counter.numpy()
            if step % 100 == 0:
                print(f'Step {step}: loss = {train_loss}')
            
            if step % 1000 == 0:
                self._save_model()
                self._evaluate_agent()
    
    def _save_model(self):
        """Salva o modelo treinado."""
        checkpoint_dir = os.path.join(self.model_dir, 'checkpoint')
        train_checkpointer = common.Checkpointer(
            ckpt_dir=checkpoint_dir,
            agent=self.agent,
            global_step=self.agent.train_step_counter)
        
        train_checkpointer.save(self.agent.train_step_counter)
        print(f"[ReinforcementLearner] Modelo salvo no passo: {self.agent.train_step_counter.numpy()}")
    
    def _evaluate_agent(self, num_episodes=10):
        """Avalia o desempenho do agente."""
        results = metric_utils.eager_compute(
            metrics.AverageReturnMetric(),
            self._eval_env,
            self.agent.policy,
            num_episodes=num_episodes)
        
        print(f'Avaliação: Retorno médio = {results["AverageReturn"].numpy()}')
        return results
    
    def learn_and_propose_action(self, state, failure_context):
        """Propõe uma ação corretiva com base no estado atual e contexto da falha.
        
        Args:
            state: Estado atual do sistema.
            failure_context: Contexto da falha detectada.
            
        Returns:
            dict: Ação proposta e seus parâmetros.
        """
        print(f"[ReinforcementLearner] Analisando estado: {state}, contexto: {failure_context}")
        
        # Converter o estado e contexto para o formato esperado pelo ambiente
        observation = self._convert_to_observation(state, failure_context)
        
        # Criar um time_step com a observação
        time_step = ts.restart(observation)
        
        # Usar a política para selecionar uma ação
        action_step = self.eval_policy.action(time_step)
        action = action_step.action.numpy()
        
        # Mapear o ID da ação para uma ação concreta
        action_map = {
            0: {"action_type": "retrain_model", "parameters": {"model_id": failure_context.get("model_id")}},
            1: {"action_type": "patch_ontology", "parameters": {"module_id": failure_context.get("module_id")}},
            2: {"action_type": "adjust_resources", "parameters": {"service_id": failure_context.get("service_id"), "new_limits": {"cpu": "1500m", "memory": "1Gi"}}},
            3: {"action_type": "restart_service", "parameters": {"service_id": failure_context.get("service_id")}}
        }
        
        proposed_action = action_map.get(action, {"action_type": "unknown", "parameters": {}})
        print(f"[ReinforcementLearner] Ação proposta: {proposed_action}")
        
        return proposed_action
    
    def _convert_to_observation(self, state, failure_context):
        """Converte o estado e contexto para o formato de observação do ambiente RL."""
        # Exemplo de conversão - adaptar conforme necessário
        observation = np.zeros(10, dtype=np.float32)
        
        # Mapear tipo de falha para índice
        failure_type_map = {
            "ALGORITHMIC_DRIFT": 0,
            "SEMANTIC_DECAY": 1,
            "LOGICAL_INCONSISTENCY": 2,
            "RESOURCE_DEGRADATION": 3
        }
        
        failure_type = failure_context.get("failure_type", "UNKNOWN")
        if failure_type in failure_type_map:
            observation[0] = failure_type_map[failure_type] / 3.0  # Normalizar para [0,1]
        
        # Mapear severidade
        observation[1] = failure_context.get("severity", 0.5)
        
        # Mapear outros aspectos do estado
        if isinstance(state, dict):
            if "market_trend" in state:
                observation[2] = 1.0 if state["market_trend"] == "bullish" else 0.0
            if "internal_risk_appetite" in state:
                observation[3] = 1.0 if state["internal_risk_appetite"] == "high" else 0.0
        
        return observation
    
    def provide_feedback(self, state, action, reward):
        """Fornece feedback ao agente sobre o resultado de uma ação.
        
        Args:
            state: Estado do sistema antes da ação.
            action: Ação executada.
            reward: Recompensa obtida (positiva para sucesso, negativa para falha).
        """
        print(f"[ReinforcementLearner] Recebendo feedback: Estado={state}, Ação={action}, Recompensa={reward}")
        
        # Em um cenário real, este feedback seria usado para atualizar o replay buffer
        # e treinar o agente incrementalmente. Para simplificar, apenas registramos.
        
        # Exemplo de como seria a atualização do replay buffer:
        # observation = self._convert_to_observation(state, {})
        # time_step = ts.restart(observation)
        # action_step = self.agent.policy.action(time_step)
        # next_time_step = ts.transition(observation, reward)
        # traj = trajectory.from_transition(time_step, action_step, next_time_step)
        # self.replay_buffer.add_batch(traj)
        
        # Periodicamente treinar o agente com os dados coletados
        # if self.replay_buffer.num_frames() > 1000:
        #     self.train(num_iterations=10)
```

### Passo 4: Criar Script de Treinamento

Crie um script para treinar o agente de RL em `scripts/train_rl_agent.py`:

```python
#!/usr/bin/env python3
"""Script para treinar o agente de RL do Autocura."""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.autocorrection.advanced_repair import ReinforcementLearner

def main():
    """Função principal para treinar o agente RL."""
    print("Iniciando treinamento do agente RL para o Autocura...")
    
    # Criar o agente
    learner = ReinforcementLearner(model_dir='./models/rl_agent')
    
    # Coletar dados iniciais
    learner.collect_data(steps=1000)
    
    # Treinar o agente
    learner.train(num_iterations=10000)
    
    print("Treinamento concluído!")

if __name__ == "__main__":
    main()
```

### Passo 5: Integrar com o Sistema Autocura

Modifique a classe `MetaLearningRepair` em `src/autocorrection/advanced_repair.py` para usar o `ReinforcementLearner` implementado:

```python
# Modificar a inicialização para usar a implementação real
def __init__(self):
    print("[MetaLearningRepair] Inicializado.")
    self.rl_agent = ReinforcementLearner(model_dir='/opt/autocura/models/rl_agent')
```

### Passo 6: Testar a Implementação

Crie um script de teste em `tests/test_reinforcement_learner.py`:

```python
import unittest
import numpy as np
from src.autocorrection.advanced_repair import ReinforcementLearner
from src.core.failure_definitions import CognitiveFailureTypes

class TestReinforcementLearner(unittest.TestCase):
    
    def setUp(self):
        # Usar um diretório temporário para testes
        self.learner = ReinforcementLearner(model_dir='/tmp/test_rl_model')
    
    def test_initialization(self):
        """Testa se o ReinforcementLearner inicializa corretamente."""
        self.assertIsNotNone(self.learner.agent)
        self.assertIsNotNone(self.learner.eval_policy)
    
    def test_learn_and_propose_action(self):
        """Testa se o método learn_and_propose_action retorna uma ação válida."""
        state = {"market_trend": "bullish", "internal_risk_appetite": "low"}
        failure_context = {
            "failure_type": "LOGICAL_INCONSISTENCY",
            "severity": 0.8,
            "model_id": "decision_model_v1"
        }
        
        action = self.learner.learn_and_propose_action(state, failure_context)
        
        self.assertIsInstance(action, dict)
        self.assertIn("action_type", action)
        self.assertIn("parameters", action)
    
    def test_provide_feedback(self):
        """Testa se o método provide_feedback funciona corretamente."""
        state = {"market_trend": "bearish", "internal_risk_appetite": "high"}
        action = {"action_type": "retrain_model", "parameters": {"model_id": "risk_model_v1"}}
        reward = 0.75
        
        # Não deve lançar exceções
        self.learner.provide_feedback(state, action, reward)

if __name__ == '__main__':
    unittest.main()
```

### Passo 7: Documentação e Melhores Práticas

Crie um arquivo de documentação em `docs/reinforcement_learning.md`:

```markdown
# Aprendizado por Reforço no Autocura

Este documento descreve a implementação do aprendizado por reforço (RL) no sistema Autocura, usando TensorFlow Agents.

## Visão Geral

O módulo de RL permite que o sistema aprenda autonomamente a corrigir falhas cognitivas, melhorando continuamente com base em feedback.

## Componentes Principais

1. **AutocuraRLEnvironment**: Ambiente que simula o processo de correção de falhas.
2. **ReinforcementLearner**: Implementa o agente DQN que aprende a selecionar ações corretivas.

## Fluxo de Trabalho

1. O sistema detecta uma falha cognitiva.
2. O `ReinforcementLearner` analisa o estado e contexto da falha.
3. O agente propõe uma ação corretiva.
4. A ação é executada e o resultado é avaliado.
5. O feedback é fornecido ao agente para melhorar futuras decisões.

## Treinamento

O agente é treinado usando:
- Experiências coletadas durante operação real
- Simulações em ambiente controlado
- Feedback de especialistas humanos (opcional)

## Manutenção e Atualização

- Modelos são salvos periodicamente em `/opt/autocura/models/rl_agent`
- Recomenda-se retreinar o modelo mensalmente com novos dados
- Monitore o desempenho do agente através de métricas como recompensa média

## Referências

- [Documentação TF-Agents](https://www.tensorflow.org/agents)
- [Tutorial DQN](https://www.tensorflow.org/agents/tutorials/1_dqn_tutorial)
```

### Considerações Finais para TensorFlow Agents

- **Requisitos de Hardware**: Recomenda-se GPU para treinamento eficiente.
- **Monitoramento**: Use TensorBoard para visualizar métricas de treinamento.
- **Evolução**: Considere explorar algoritmos mais avançados como PPO ou SAC para casos complexos.
- **Integração Gradual**: Implemente primeiro em ambiente de teste antes de usar em produção.
- **Feedback Humano**: Considere incorporar feedback de especialistas no loop de treinamento.

## 2. Implementação do PyTorch para Modelos de Decisão de Adaptação

### Contexto no Autocura
O PyTorch será utilizado no módulo de adaptação autônoma (`autonomous_adapter.py`), especificamente na classe `AdaptationDecisionModel`, para implementar um modelo de aprendizado de máquina que decidirá as melhores ações adaptativas com base em cenários detectados.

### Passo 1: Instalação e Configuração

```bash
# Ativar ambiente virtual
source autocura-env/bin/activate

# Instalar PyTorch (versão estável com suporte a CUDA se tiver GPU)
pip install torch==2.0.1 torchvision==0.15.2

# Dependências adicionais para processamento de dados e visualização
pip install pandas matplotlib scikit-learn
```

### Passo 2: Definir a Estrutura de Dados e Modelo

Crie um novo arquivo `src/adaptation/adaptation_model.py`:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import os
import json
from datetime import datetime

class AdaptationDataset(torch.utils.data.Dataset):
    """Dataset para treinar o modelo de decisão de adaptação."""
    
    def __init__(self, data_file=None, transform=None):
        """Inicializa o dataset.
        
        Args:
            data_file: Caminho para o arquivo de dados (JSON).
            transform: Transformações a serem aplicadas nos dados.
        """
        self.transform = transform
        self.data = []
        self.targets = []
        
        if data_file and os.path.exists(data_file):
            self._load_data(data_file)
        else:
            print(f"[AdaptationDataset] Arquivo de dados não encontrado: {data_file}")
            print("[AdaptationDataset] Inicializando dataset vazio.")
    
    def _load_data(self, data_file):
        """Carrega dados de um arquivo JSON."""
        try:
            with open(data_file, 'r') as f:
                raw_data = json.load(f)
            
            for item in raw_data:
                # Exemplo de formato esperado:
                # {"features": [0.1, 0.2, ...], "action_id": 1}
                if "features" in item and "action_id" in item:
                    self.data.append(np.array(item["features"], dtype=np.float32))
                    self.targets.append(item["action_id"])
            
            print(f"[AdaptationDataset] Carregados {len(self.data)} exemplos de {data_file}")
        except Exception as e:
            print(f"[AdaptationDataset] Erro ao carregar dados: {e}")
    
    def add_example(self, features, action_id):
        """Adiciona um exemplo ao dataset.
        
        Args:
            features: Lista ou array de características do cenário.
            action_id: ID da ação tomada (alvo).
        """
        self.data.append(np.array(features, dtype=np.float32))
        self.targets.append(action_id)
    
    def save_to_file(self, data_file):
        """Salva o dataset em um arquivo JSON.
        
        Args:
            data_file: Caminho para o arquivo de saída.
        """
        output_data = []
        for i in range(len(self.data)):
            output_data.append({
                "features": self.data[i].tolist(),
                "action_id": self.targets[i]
            })
        
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        with open(data_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"[AdaptationDataset] Dataset salvo em {data_file}")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        x = self.data[idx]
        y = self.targets[idx]
        
        if self.transform:
            x = self.transform(x)
        
        return torch.tensor(x), torch.tensor(y, dtype=torch.long)


class AdaptationModel(nn.Module):
    """Modelo de rede neural para decisão de adaptação."""
    
    def __init__(self, input_size, hidden_size, num_actions):
        """Inicializa o modelo.
        
        Args:
            input_size: Tamanho do vetor de entrada (número de features).
            hidden_size: Tamanho das camadas ocultas.
            num_actions: Número de ações possíveis (classes de saída).
        """
        super(AdaptationModel, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_actions = num_actions
        
        # Definir camadas da rede neural
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, num_actions)
        
        # Dropout para regularização
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        """Forward pass da rede neural."""
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x


class AdaptationModelTrainer:
    """Classe para treinar e gerenciar o modelo de decisão de adaptação."""
    
    def __init__(self, input_size=10, hidden_size=64, num_actions=4, 
                 model_dir='/opt/autocura/models/adaptation'):
        """Inicializa o treinador.
        
        Args:
            input_size: Tamanho do vetor de entrada.
            hidden_size: Tamanho das camadas ocultas.
            num_actions: Número de ações possíveis.
            model_dir: Diretório para salvar/carregar modelos.
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_actions = num_actions
        self.model_dir = model_dir
        
        # Criar diretório para modelos se não existir
        os.makedirs(model_dir, exist_ok=True)
        
        # Inicializar modelo
        self.model = AdaptationModel(input_size, hidden_size, num_actions)
        
        # Definir otimizador e função de perda
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss()
        
        # Carregar modelo se existir
        self._try_load_latest_model()
        
        # Dataset para treinamento contínuo
        self.dataset = AdaptationDataset(
            data_file=os.path.join(model_dir, 'adaptation_data.json'))
    
    def _try_load_latest_model(self):
        """Tenta carregar o modelo mais recente."""
        model_files = [f for f in os.listdir(self.model_dir) 
                      if f.startswith('adaptation_model_') and f.endswith('.pth')]
        
        if not model_files:
            print("[AdaptationModelTrainer] Nenhum modelo encontrado. Iniciando do zero.")
            return
        
        # Ordenar por data (assumindo formato adaptation_model_YYYYMMDD_HHMMSS.pth)
        latest_model = sorted(model_files)[-1]
        model_path = os.path.join(self.model_dir, latest_model)
        
        try:
            self.model.load_state_dict(torch.load(model_path))
            self.model.eval()  # Modo de avaliação
            print(f"[AdaptationModelTrainer] Modelo carregado: {model_path}")
        except Exception as e:
            print(f"[AdaptationModelTrainer] Erro ao carregar modelo: {e}")
    
    def save_model(self, suffix=None):
        """Salva o modelo atual.
        
        Args:
            suffix: Sufixo opcional para o nome do arquivo.
        """
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_path = os.path.join(self.model_dir, f'adaptation_model_{suffix}.pth')
        torch.save(self.model.state_dict(), model_path)
        print(f"[AdaptationModelTrainer] Modelo salvo em: {model_path}")
    
    def train(self, epochs=100, batch_size=32):
        """Treina o modelo com os dados disponíveis.
        
        Args:
            epochs: Número de épocas de treinamento.
            batch_size: Tamanho do batch.
        """
        if len(self.dataset) == 0:
            print("[AdaptationModelTrainer] Sem dados para treinamento.")
            return
        
        # Criar DataLoader
        dataloader = torch.utils.data.DataLoader(
            self.dataset, batch_size=batch_size, shuffle=True)
        
        # Modo de treinamento
        self.model.train()
        
        # Loop de treinamento
        for epoch in range(epochs):
            running_loss = 0.0
            correct = 0
            total = 0
            
            for inputs, targets in dataloader:
                # Zerar gradientes
                self.optimizer.zero_grad()
                
                # Forward pass
                outputs = self.model(inputs)
                loss = self.criterion(outputs, targets)
                
                # Backward pass e otimização
                loss.backward()
                self.optimizer.step()
                
                # Estatísticas
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += targets.size(0)
                correct += (predicted == targets).sum().item()
            
            # Imprimir progresso
            if (epoch + 1) % 10 == 0:
                accuracy = 100 * correct / total
                print(f'Época {epoch+1}/{epochs}, Loss: {running_loss/len(dataloader):.4f}, Acurácia: {accuracy:.2f}%')
        
        # Salvar modelo após treinamento
        self.save_model()
        
        # Modo de avaliação
        self.model.eval()
        print("[AdaptationModelTrainer] Treinamento concluído.")
    
    def predict(self, features):
        """Faz uma previsão com o modelo.
        
        Args:
            features: Vetor de características do cenário.
            
        Returns:
            tuple: (action_id, probabilities)
        """
        # Converter para tensor
        if isinstance(features, list):
            features = np.array(features, dtype=np.float32)
        
        x = torch.tensor(features, dtype=torch.float32)
        
        # Modo de avaliação
        self.model.eval()
        
        # Fazer previsão
        with torch.no_grad():
            outputs = self.model(x)
            probabilities = F.softmax(outputs, dim=0)
            action_id = torch.argmax(probabilities).item()
        
        return action_id, probabilities.numpy()
    
    def add_feedback(self, features, action_id, save=True):
        """Adiciona um exemplo de feedback ao dataset.
        
        Args:
            features: Vetor de características do cenário.
            action_id: ID da ação tomada.
            save: Se True, salva o dataset após adicionar o exemplo.
        """
        self.dataset.add_example(features, action_id)
        
        if save:
            self.dataset.save_to_file(os.path.join(self.model_dir, 'adaptation_data.json'))
        
        print(f"[AdaptationModelTrainer] Exemplo adicionado ao dataset. Total: {len(self.dataset)}")
```

### Passo 3: Implementar o AdaptationDecisionModel

Modifique o arquivo `src/adaptation/autonomous_adapter.py` para implementar a classe `AdaptationDecisionModel` usando PyTorch:

```python
from .adaptation_model import AdaptationModelTrainer
import numpy as np

class AdaptationDecisionModel:
    """Modelo de decisão para adaptação autônoma usando PyTorch."""
    
    def __init__(self, model_dir='/opt/autocura/models/adaptation'):
        """Inicializa o modelo de decisão.
        
        Args:
            model_dir: Diretório para salvar/carregar modelos.
        """
        print("[AdaptationDecisionModel] Inicializando com PyTorch")
        
        # Inicializar o treinador com o modelo
        self.trainer = AdaptationModelTrainer(
            input_size=10,  # Ajuste conforme necessário
            hidden_size=64,
            num_actions=4,  # Número de ações possíveis
            model_dir=model_dir
        )
        
        # Mapeamento de IDs de ação para ações concretas
        self.action_map = {
            0: {"action_type": "adapt_component_A", "target_component": "component_A", "new_config": {"param": "value_optimized"}},
            1: {"action_type": "adapt_component_B", "target_component": "component_B", "new_config": {"threshold": 0.75}},
            2: {"action_type": "adapt_component_C", "target_component": "component_C", "new_config": {"mode": "high_performance"}},
            3: {"action_type": "no_adaptation", "target_component": None, "new_config": {}}
        }
    
    def _extract_features(self, scenario_data):
        """Extrai features do cenário para o modelo.
        
        Args:
            scenario_data: Dados do cenário.
            
        Returns:
            numpy.ndarray: Vetor de features.
        """
        # Inicializar vetor de features com zeros
        features = np.zeros(10, dtype=np.float32)
        
        # Exemplo de extração de features - adaptar conforme necessário
        if "scenario_id" in scenario_data:
            # Usar hash do ID como seed para features aleatórias (apenas para demonstração)
            # Em um caso real, você extrairia features significativas dos dados
            import hashlib
            seed = int(hashlib.md5(scenario_data["scenario_id"].encode()).hexdigest(), 16) % 10000
            np.random.seed(seed)
            features = np.random.uniform(0, 1, 10).astype(np.float32)
        
        # Exemplo de features específicas
        if "type" in scenario_data:
            if scenario_data["type"] == "economic_downturn":
                features[0] = 1.0
            elif scenario_data["type"] == "technological_shift":
                features[1] = 1.0
        
        if "impact_level" in scenario_data:
            if scenario_data["impact_level"] == "high":
                features[2] = 1.0
            elif scenario_data["impact_level"] == "medium":
                features[2] = 0.5
            elif scenario_data["impact_level"] == "low":
                features[2] = 0.1
        
        # Se houver features explícitas, usá-las
        if "features_for_model" in scenario_data and isinstance(scenario_data["features_for_model"], list):
            # Garantir que o tamanho seja compatível
            model_features = scenario_data["features_for_model"]
            for i in range(min(len(model_features), len(features))):
                features[i] = float(model_features[i])
        
        return features
    
    def predict_best_action(self, scenario_data):
        """Prevê a melhor ação adaptativa para o cenário.
        
        Args:
            scenario_data: Dados do cenário.
            
        Returns:
            dict: Ação prevista e detalhes.
        """
        print(f"[AdaptationDecisionModel] Prevendo melhor ação para cenário: {scenario_data}")
        
        # Extrair features do cenário
        features = self._extract_features(scenario_data)
        
        # Fazer previsão com o modelo
        action_id, probabilities = self.trainer.predict(features)
        
        # Mapear ID da ação para ação concreta
        action = self.action_map.get(action_id, {"action_type": "unknown", "target_component": None, "new_config": {}})
        
        # Adicionar informações da previsão
        action["action_id"] = action_id
        action["confidence"] = float(probabilities[action_id])
        
        print(f"[AdaptationDecisionModel] Ação prevista: {action}")
        return action
    
    def provide_feedback(self, scenario_data, action_id, success=True):
        """Fornece feedback para o modelo sobre uma ação tomada.
        
        Args:
            scenario_data: Dados do cenário.
            action_id: ID da ação tomada.
            success: Se a ação foi bem-sucedida.
        """
        # Extrair features do cenário
        features = self._extract_features(scenario_data)
        
        # Adicionar exemplo ao dataset
        self.trainer.add_feedback(features, action_id)
        
        # Se acumular muitos exemplos, retreinar o modelo
        if len(self.trainer.dataset) % 50 == 0:  # A cada 50 exemplos
            print("[AdaptationDecisionModel] Retreinando modelo com novos dados...")
            self.trainer.train(epochs=50, batch_size=16)
```

### Passo 4: Criar Script de Treinamento

Crie um script para treinar o modelo em `scripts/train_adaptation_model.py`:

```python
#!/usr/bin/env python3
"""Script para treinar o modelo de decisão de adaptação."""

import sys
import os
import numpy as np
import json
from datetime import datetime

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adaptation.adaptation_model import AdaptationModelTrainer, AdaptationDataset

def generate_synthetic_data(num_samples=1000, output_file=None):
    """Gera dados sintéticos para treinamento inicial.
    
    Args:
        num_samples: Número de exemplos a gerar.
        output_file: Arquivo para salvar os dados.
    
    Returns:
        AdaptationDataset: Dataset com os dados gerados.
    """
    print(f"Gerando {num_samples} exemplos sintéticos...")
    
    dataset = AdaptationDataset()
    
    # Tipos de cenários
    scenario_types = ["economic_downturn", "technological_shift", "market_opportunity", "regulatory_change"]
    
    for _ in range(num_samples):
        # Gerar features aleatórias
        features = np.random.uniform(0, 1, 10).astype(np.float32)
        
        # Lógica sintética para determinar a melhor ação
        # Esta é uma lógica simplificada para demonstração
        # Em um caso real, isso seria baseado em conhecimento de domínio
        
        # Exemplo: Se as primeiras features são altas, adaptar componente A
        if features[0] > 0.7 and features[1] > 0.6:
            action_id = 0  # adapt_component_A
        # Se as features do meio são altas, adaptar componente B
        elif features[3] > 0.7 and features[4] > 0.6:
            action_id = 1  # adapt_component_B
        # Se as últimas features são altas, adaptar componente C
        elif features[7] > 0.7 and features[8] > 0.6:
            action_id = 2  # adapt_component_C
        # Caso contrário, não adaptar
        else:
            action_id = 3  # no_adaptation
        
        # Adicionar ruído à decisão (10% de chance de escolher outra ação)
        if np.random.random() < 0.1:
            action_id = np.random.randint(0, 4)
        
        # Adicionar ao dataset
        dataset.add_example(features, action_id)
    
    # Salvar dataset se especificado
    if output_file:
        dataset.save_to_file(output_file)
    
    return dataset

def main():
    """Função principal para treinar o modelo de adaptação."""
    print("Iniciando treinamento do modelo de decisão de adaptação...")
    
    # Diretório para modelos
    model_dir = './models/adaptation'
    os.makedirs(model_dir, exist_ok=True)
    
    # Arquivo de dados
    data_file = os.path.join(model_dir, 'adaptation_data.json')
    
    # Verificar se já existem dados
    if not os.path.exists(data_file):
        print(f"Arquivo de dados {data_file} não encontrado. Gerando dados sintéticos...")
        dataset = generate_synthetic_data(num_samples=1000, output_file=data_file)
    else:
        print(f"Usando dados existentes de {data_file}")
        dataset = AdaptationDataset(data_file=data_file)
    
    # Criar e treinar o modelo
    trainer = AdaptationModelTrainer(
        input_size=10,
        hidden_size=64,
        num_actions=4,
        model_dir=model_dir
    )
    
    # Se o dataset foi carregado externamente, substituir o do trainer
    if dataset:
        trainer.dataset = dataset
    
    # Treinar o modelo
    print(f"Treinando modelo com {len(trainer.dataset)} exemplos...")
    trainer.train(epochs=200, batch_size=32)
    
    # Testar o modelo com alguns exemplos
    print("\nTestando modelo com exemplos aleatórios:")
    for i in range(5):
        features = np.random.uniform(0, 1, 10).astype(np.float32)
        action_id, probs = trainer.predict(features)
        print(f"Exemplo {i+1}: Action ID = {action_id}, Probabilidades = {probs}")
    
    print("\nTreinamento e teste concluídos!")

if __name__ == "__main__":
    main()
```

### Passo 5: Integrar com o AdaptationEngine

Modifique a classe `AdaptationEngine` em `src/adaptation/autonomous_adapter.py` para usar o `AdaptationDecisionModel` implementado:

```python
# Modificar a inicialização para usar a implementação real
def __init__(self):
    print("[AdaptationEngine] Inicializado.")
    self.decision_model = AdaptationDecisionModel(model_dir='/opt/autocura/models/adaptation')
    # Manter o resto da inicialização...
    self.sandbox = SandboxManager(namespace="autocura-adaptation-tests") 
    self.k8s_orchestrator = K8sOrchestrator()
```

### Passo 6: Testar a Implementação

Crie um script de teste em `tests/test_adaptation_model.py`:

```python
import unittest
import numpy as np
import os
import tempfile
import shutil

from src.adaptation.adaptation_model import AdaptationModelTrainer, AdaptationDataset
from src.adaptation.autonomous_adapter import AdaptationDecisionModel

class TestAdaptationModel(unittest.TestCase):
    
    def setUp(self):
        # Criar diretório temporário para testes
        self.test_dir = tempfile.mkdtemp()
        self.model_dir = os.path.join(self.test_dir, 'models')
        os.makedirs(self.model_dir, exist_ok=True)
    
    def tearDown(self):
        # Limpar diretório temporário
        shutil.rmtree(self.test_dir)
    
    def test_dataset_operations(self):
        """Testa operações básicas do dataset."""
        dataset = AdaptationDataset()
        
        # Adicionar exemplos
        dataset.add_example([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 0)
        dataset.add_example([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0], 1)
        
        # Verificar tamanho
        self.assertEqual(len(dataset), 2)
        
        # Verificar acesso a itens
        x, y = dataset[0]
        self.assertEqual(y.item(), 0)
        self.assertEqual(x.shape[0], 10)
        
        # Testar salvamento e carregamento
        data_file = os.path.join(self.test_dir, 'test_data.json')
        dataset.save_to_file(data_file)
        
        # Carregar em um novo dataset
        new_dataset = AdaptationDataset(data_file=data_file)
        self.assertEqual(len(new_dataset), 2)
    
    def test_model_training(self):
        """Testa o treinamento básico do modelo."""
        # Criar dataset sintético
        dataset = AdaptationDataset()
        for _ in range(100):
            features = np.random.uniform(0, 1, 10).astype(np.float32)
            action_id = np.random.randint(0, 4)
            dataset.add_example(features, action_id)
        
        # Criar treinador
        trainer = AdaptationModelTrainer(
            input_size=10,
            hidden_size=32,
            num_actions=4,
            model_dir=self.model_dir
        )
        
        # Substituir dataset
        trainer.dataset = dataset
        
        # Treinar por poucas épocas para teste
        trainer.train(epochs=10, batch_size=16)
        
        # Verificar se o modelo foi salvo
        model_files = [f for f in os.listdir(self.model_dir) if f.endswith('.pth')]
        self.assertGreater(len(model_files), 0)
        
        # Testar previsão
        features = np.random.uniform(0, 1, 10).astype(np.float32)
        action_id, probs = trainer.predict(features)
        
        # Verificar formato da saída
        self.assertIsInstance(action_id, int)
        self.assertGreaterEqual(action_id, 0)
        self.assertLess(action_id, 4)
        self.assertEqual(len(probs), 4)
    
    def test_adaptation_decision_model(self):
        """Testa o modelo de decisão de adaptação."""
        # Criar modelo
        model = AdaptationDecisionModel(model_dir=self.model_dir)
        
        # Testar previsão com cenário
        scenario_data = {
            "scenario_id": "test_scenario_001",
            "type": "economic_downturn",
            "impact_level": "high",
            "features_for_model": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        }
        
        action = model.predict_best_action(scenario_data)
        
        # Verificar formato da ação
        self.assertIn("action_type", action)
        self.assertIn("target_component", action)
        self.assertIn("new_config", action)
        self.assertIn("action_id", action)
        self.assertIn("confidence", action)

if __name__ == '__main__':
    unittest.main()
```

### Passo 7: Documentação e Melhores Práticas

Crie um arquivo de documentação em `docs/adaptation_model.md`:

```markdown
# Modelo de Decisão de Adaptação no Autocura

Este documento descreve a implementação do modelo de decisão de adaptação no sistema Autocura, usando PyTorch.

## Visão Geral

O modelo de decisão de adaptação permite que o sistema escolha automaticamente as melhores ações adaptativas em resposta a diferentes cenários detectados, como mudanças econômicas, avanços tecnológicos ou alterações regulatórias.

## Componentes Principais

1. **AdaptationDataset**: Gerencia os dados de treinamento e avaliação.
2. **AdaptationModel**: Implementa a rede neural para classificação de ações.
3. **AdaptationModelTrainer**: Gerencia o treinamento, avaliação e uso do modelo.
4. **AdaptationDecisionModel**: Interface de alto nível para o sistema Autocura.

## Fluxo de Trabalho

1. O sistema detecta um cenário que pode exigir adaptação.
2. O `AdaptationDecisionModel` extrai características relevantes do cenário.
3. O modelo neural prevê a melhor ação adaptativa.
4. A ação é validada em um ambiente sandbox antes da aplicação.
5. Após a aplicação, o feedback é coletado para melhorar o modelo.

## Treinamento

O modelo é treinado usando:
- Dados históricos de adaptações bem-sucedidas
- Dados sintéticos para cenários não observados
- Feedback contínuo durante a operação

## Manutenção e Atualização

- Modelos são salvos em `/opt/autocura/models/adaptation`
- O dataset é atualizado continuamente com novos exemplos
- Retreinamento automático ocorre a cada 50 novos exemplos
- Monitoramento de desempenho através da acurácia de previsão

## Referências

- [Documentação PyTorch](https://pytorch.org/docs/stable/index.html)
- [Tutorial de Classificação com PyTorch](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)
```

### Considerações Finais para PyTorch

- **Requisitos de Hardware**: GPU acelera significativamente o treinamento, mas CPU é suficiente para inferência.
- **Versionamento de Modelos**: Mantenha versões anteriores dos modelos para fallback.
- **Dados de Treinamento**: Comece com dados sintéticos e evolua para dados reais conforme disponíveis.
- **Monitoramento**: Acompanhe a acurácia do modelo e a distribuição de ações previstas.
- **Evolução**: Considere arquiteturas mais complexas (RNN, Transformer) para cenários com dependência temporal.

## 3. Implementação do Hugging Face Transformers para Análise Política

### Contexto no Autocura
O Hugging Face Transformers será utilizado no módulo de previsão de cenários políticos (`political_analyzer.py`), especificamente para implementar análise de sentimento e classificação de risco político a partir de notícias e outros dados textuais.

### Passo 1: Instalação e Configuração

```bash
# Ativar ambiente virtual
source autocura-env/bin/activate

# Instalar Transformers e dependências
pip install transformers==4.30.2
pip install torch==2.0.1  # Se ainda não instalou no passo do PyTorch
pip install sentencepiece protobuf
pip install datasets  # Para gerenciar datasets de treinamento/fine-tuning

# Dependências para processamento de texto
pip install nltk spacy
python -m spacy download pt_core_news_sm  # Modelo em português
python -m spacy download en_core_web_sm   # Modelo em inglês
```

### Passo 2: Implementar o Módulo de Análise Política

Modifique o arquivo `src/prediction/political_analyzer.py` para usar Transformers:

```python
import os
import json
import requests
import numpy as np
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar Transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

class PoliticalPredictor:
    """Analisa notícias e outros dados para prever cenários políticos."""
    
    def __init__(self, model_name="distilbert-base-uncased", 
                 model_dir="/opt/autocura/models/political",
                 news_api_key_env_var="NEWS_API_KEY"):
        """Inicializa o preditor político.
        
        Args:
            model_name: Nome do modelo pré-treinado ou caminho para modelo fine-tuned.
            model_dir: Diretório para salvar/carregar modelos fine-tuned.
            news_api_key_env_var: Nome da variável de ambiente com a chave da API de notícias.
        """
        logger.info(f"Inicializando PoliticalPredictor com modelo: {model_name}")
        
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Verificar se existe um modelo fine-tuned
        fine_tuned_model = os.path.join(model_dir, "political-bert")
        if os.path.exists(fine_tuned_model):
            logger.info(f"Carregando modelo fine-tuned de: {fine_tuned_model}")
            model_path = fine_tuned_model
        else:
            logger.info(f"Usando modelo pré-treinado: {model_name}")
            model_path = model_name
        
        # Carregar tokenizer e modelo
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            # Modelo para classificação com 3 classes: Estável, Instável, Crise
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_path, num_labels=3)
            
            # Mapear índices para labels
            self.id2label = {0: "Estável", 1: "Instável", 2: "Crise"}
            self.label2id = {"Estável": 0, "Instável": 1, "Crise": 2}
            
            # Definir device (GPU se disponível)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            
            logger.info(f"Modelo carregado com sucesso. Usando device: {self.device}")
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            self.tokenizer = None
            self.model = None
        
        # Configurar API de notícias
        self.news_api_key = os.environ.get(news_api_key_env_var)
        if not self.news_api_key:
            logger.warning(f"Variável de ambiente {news_api_key_env_var} não configurada.")
    
    def _fetch_news(self, country_code, keywords="political stability,government,protest,election", max_articles=5):
        """Busca notícias recentes para um país específico.
        
        Args:
            country_code: Código do país (ex: 'us', 'br').
            keywords: Palavras-chave para a busca.
            max_articles: Número máximo de artigos para retornar.
            
        Returns:
            list: Lista de textos de notícias.
        """
        logger.info(f"Buscando notícias para {country_code} com keywords: {keywords}")
        
        if not self.news_api_key:
            logger.warning("API key não configurada. Retornando dados mockados.")
            return [
                f"Mocked news 1 for {country_code}: Government announces new economic plan amid stability concerns.",
                f"Mocked news 2 for {country_code}: Upcoming election sparks debate on future policies.",
                f"Mocked news 3 for {country_code}: Protests reported in capital over social reforms."
            ]
        
        # Usar NewsAPI.org (substitua pela API de sua preferência)
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            "country": country_code,
            "q": keywords,
            "apiKey": self.news_api_key,
            "pageSize": max_articles
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            
            # Extrair texto dos artigos
            news_texts = []
            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "")
                content = article.get("content", "")
                
                # Combinar informações disponíveis
                text = f"{title}. {description} {content}"
                news_texts.append(text)
            
            logger.info(f"Encontrados {len(news_texts)} artigos.")
            return news_texts
        
        except Exception as e:
            logger.error(f"Erro ao buscar notícias: {e}")
            return []
    
    def _analyze_text(self, text):
        """Analisa um texto para determinar o nível de instabilidade política.
        
        Args:
            text: Texto a ser analisado.
            
        Returns:
            dict: Resultado da análise com classe prevista e probabilidades.
        """
        if not self.model or not self.tokenizer:
            logger.error("Modelo não inicializado.")
            return {"error": "Modelo não disponível"}
        
        # Tokenizar o texto
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, 
                               padding=True, max_length=512)
        
        # Mover para o device correto
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Fazer a previsão
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            
            # Converter logits para probabilidades
            probs = F.softmax(logits, dim=1).squeeze().cpu().numpy()
            
            # Obter a classe com maior probabilidade
            predicted_class_id = np.argmax(probs)
            predicted_label = self.id2label[predicted_class_id]
            
            # Calcular score de instabilidade (soma das probabilidades de Instável e Crise)
            instability_score = float(probs[1] + probs[2])  # Índices 1 e 2 são Instável e Crise
        
        # Retornar resultado
        result = {
            "predicted_class": predicted_label,
            "instability_score": instability_score,
            "probabilities": {self.id2label[i]: float(p) for i, p in enumerate(probs)}
        }
        
        return result
    
    def predict_instability(self, country_code):
        """Prevê o nível de instabilidade política para um país.
        
        Args:
            country_code: Código do país.
            
        Returns:
            dict: Resultado da previsão.
        """
        logger.info(f"Prevendo instabilidade para {country_code}")
        
        # Buscar notícias
        news_items = self._fetch_news(country_code)
        
        if not news_items:
            logger.warning(f"Nenhuma notícia encontrada para {country_code}")
            return {
                "country": country_code,
                "instability_score": None,
                "predicted_class": "Dados Insuficientes",
                "error": "Nenhuma notícia encontrada"
            }
        
        # Analisar cada notícia
        results = []
        for news in news_items:
            result = self._analyze_text(news)
            results.append(result)
        
        # Agregar resultados
        if not results:
            return {
                "country": country_code,
                "instability_score": None,
                "predicted_class": "Erro",
                "error": "Falha na análise de notícias"
            }
        
        # Calcular média dos scores de instabilidade
        avg_instability = sum(r["instability_score"] for r in results) / len(results)
        
        # Determinar classe final com base na média
        if avg_instability > 0.66:
            final_class = "Crise"
        elif avg_instability > 0.33:
            final_class = "Instável"
        else:
            final_class = "Estável"
        
        # Resultado final
        final_result = {
            "country": country_code,
            "instability_score": avg_instability,
            "predicted_class": final_class,
            "analysis_count": len(results),
            "detailed_results": results
        }
        
        logger.info(f"Previsão para {country_code}: {final_class} (score: {avg_instability:.2f})")
        return final_result
    
    def fine_tune(self, dataset_path, epochs=3, batch_size=16):
        """Fine-tune o modelo com dados específicos.
        
        Args:
            dataset_path: Caminho para o dataset (formato Hugging Face ou JSON).
            epochs: Número de épocas de treinamento.
            batch_size: Tamanho do batch.
            
        Returns:
            dict: Métricas de treinamento.
        """
        from transformers import Trainer, TrainingArguments
        from datasets import load_dataset
        import evaluate
        
        logger.info(f"Iniciando fine-tuning com dataset: {dataset_path}")
        
        # Verificar se o modelo e tokenizer estão disponíveis
        if not self.model or not self.tokenizer:
            logger.error("Modelo não inicializado.")
            return {"error": "Modelo não disponível"}
        
        try:
            # Carregar dataset
            if dataset_path.endswith('.json'):
                # Formato JSON personalizado
                dataset = self._load_custom_dataset(dataset_path)
            else:
                # Dataset do Hugging Face
                dataset = load_dataset(dataset_path)
            
            # Função para tokenizar dataset
            def tokenize_function(examples):
                return self.tokenizer(examples["text"], padding="max_length", truncation=True)
            
            # Tokenizar dataset
            tokenized_dataset = dataset.map(tokenize_function, batched=True)
            
            # Métricas
            metric = evaluate.load("accuracy")
            
            def compute_metrics(eval_pred):
                logits, labels = eval_pred
                predictions = np.argmax(logits, axis=-1)
                return metric.compute(predictions=predictions, references=labels)
            
            # Configurar treinamento
            training_args = TrainingArguments(
                output_dir=os.path.join(self.model_dir, "results"),
                num_train_epochs=epochs,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                warmup_steps=500,
                weight_decay=0.01,
                logging_dir=os.path.join(self.model_dir, "logs"),
                logging_steps=10,
                evaluation_strategy="epoch",
                save_strategy="epoch",
                load_best_model_at_end=True,
            )
            
            # Inicializar trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=tokenized_dataset["train"],
                eval_dataset=tokenized_dataset["validation"],
                compute_metrics=compute_metrics,
            )
            
            # Treinar modelo
            train_result = trainer.train()
            
            # Salvar modelo fine-tuned
            self.model.save_pretrained(os.path.join(self.model_dir, "political-bert"))
            self.tokenizer.save_pretrained(os.path.join(self.model_dir, "political-bert"))
            
            # Avaliar modelo
            eval_result = trainer.evaluate()
            
            logger.info(f"Fine-tuning concluído. Métricas: {eval_result}")
            return {
                "train_runtime": train_result.metrics.get("train_runtime"),
                "eval_accuracy": eval_result.get("eval_accuracy"),
                "model_path": os.path.join(self.model_dir, "political-bert")
            }
            
        except Exception as e:
            logger.error(f"Erro durante fine-tuning: {e}")
            return {"error": str(e)}
    
    def _load_custom_dataset(self, json_path):
        """Carrega um dataset personalizado em formato JSON.
        
        Args:
            json_path: Caminho para o arquivo JSON.
            
        Returns:
            datasets.Dataset: Dataset no formato Hugging Face.
        """
        from datasets import Dataset, DatasetDict
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Converter para formato esperado pelo Hugging Face
            train_data = {"text": [], "label": []}
            val_data = {"text": [], "label": []}
            
            # Dividir em treino (80%) e validação (20%)
            for item in data:
                if "text" in item and "label" in item:
                    if np.random.random() < 0.8:
                        train_data["text"].append(item["text"])
                        train_data["label"].append(self.label2id.get(item["label"], 0))
                    else:
                        val_data["text"].append(item["text"])
                        val_data["label"].append(self.label2id.get(item["label"], 0))
            
            # Criar datasets
            train_dataset = Dataset.from_dict(train_data)
            val_dataset = Dataset.from_dict(val_data)
            
            # Criar DatasetDict
            dataset_dict = DatasetDict({
                "train": train_dataset,
                "validation": val_dataset
            })
            
            logger.info(f"Dataset carregado: {len(train_data['text'])} exemplos de treino, {len(val_data['text'])} de validação")
            return dataset_dict
            
        except Exception as e:
            logger.error(f"Erro ao carregar dataset personalizado: {e}")
            raise
```

### Passo 3: Criar Script para Fine-tuning

Crie um script para fine-tuning do modelo em `scripts/finetune_political_model.py`:

```python
#!/usr/bin/env python3
"""Script para fine-tuning do modelo de análise política."""

import sys
import os
import json
import argparse
from datetime import datetime

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.prediction.political_analyzer import PoliticalPredictor

def generate_synthetic_dataset(output_file, num_samples=1000):
    """Gera um dataset sintético para fine-tuning.
    
    Args:
        output_file: Caminho para salvar o dataset.
        num_samples: Número de exemplos a gerar.
    """
    print(f"Gerando dataset sintético com {num_samples} exemplos...")
    
    # Exemplos de notícias para cada classe
    stable_examples = [
        "Government announces new economic plan with broad support from opposition.",
        "Peaceful elections conclude with high voter turnout and international praise.",
        "Parliament passes budget with bipartisan support, markets respond positively.",
        "President's approval rating reaches 65% amid economic growth.",
        "International trade agreement signed, expected to boost economy by 3%."
    ]
    
    unstable_examples = [
        "Opposition parties boycott parliamentary session amid controversy.",
        "Protests erupt in capital over controversial new law.",
        "Government coalition loses majority after party withdraws support.",
        "Central bank raises interest rates to combat inflation, markets volatile.",
        "Regional tensions escalate as diplomatic talks break down."
    ]
    
    crisis_examples = [
        "Violent protests spread to multiple cities, government declares emergency.",
        "Military mobilizes as political crisis deepens, international concern grows.",
        "President faces impeachment proceedings amid corruption allegations.",
        "Economy in freefall as currency loses 30% value in one week.",
        "Government collapses after no-confidence vote, new elections called."
    ]
    
    # Gerar dataset
    dataset = []
    
    import random
    for i in range(num_samples):
        # Escolher classe aleatoriamente, com distribuição desbalanceada
        # (mais exemplos estáveis que de crise)
        r = random.random()
        if r < 0.5:  # 50% estável
            label = "Estável"
            base_text = random.choice(stable_examples)
        elif r < 0.8:  # 30% instável
            label = "Instável"
            base_text = random.choice(unstable_examples)
        else:  # 20% crise
            label = "Crise"
            base_text = random.choice(crisis_examples)
        
        # Adicionar variações aleatórias ao texto
        country = random.choice(["Brazil", "USA", "France", "Japan", "India", "South Africa"])
        year = random.randint(2020, 2025)
        
        # Criar texto final
        text = f"{base_text} {country}, {year}."
        
        # Adicionar ao dataset
        dataset.append({"text": text, "label": label})
    
    # Salvar dataset
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Dataset salvo em {output_file}")
    return output_file

def main():
    """Função principal para fine-tuning do modelo político."""
    parser = argparse.ArgumentParser(description="Fine-tuning do modelo de análise política")
    parser.add_argument("--dataset", help="Caminho para o dataset (JSON)")
    parser.add_argument("--model", default="distilbert-base-uncased", help="Modelo base para fine-tuning")
    parser.add_argument("--epochs", type=int, default=3, help="Número de épocas de treinamento")
    parser.add_argument("--batch-size", type=int, default=16, help="Tamanho do batch")
    parser.add_argument("--output-dir", default="./models/political", help="Diretório para salvar o modelo")
    parser.add_argument("--generate-data", action="store_true", help="Gerar dataset sintético")
    parser.add_argument("--samples", type=int, default=1000, help="Número de exemplos sintéticos a gerar")
    
    args = parser.parse_args()
    
    # Gerar dataset sintético se solicitado
    if args.generate_data:
        dataset_path = os.path.join(args.output_dir, "synthetic_political_data.json")
        dataset_path = generate_synthetic_dataset(dataset_path, args.samples)
    else:
        dataset_path = args.dataset
    
    if not dataset_path:
        print("Erro: É necessário fornecer um dataset ou usar --generate-data")
        return
    
    # Inicializar o preditor
    predictor = PoliticalPredictor(model_name=args.model, model_dir=args.output_dir)
    
    # Realizar fine-tuning
    print(f"Iniciando fine-tuning com {args.epochs} épocas...")
    result = predictor.fine_tune(dataset_path, epochs=args.epochs, batch_size=args.batch_size)
    
    print(f"Fine-tuning concluído: {result}")
    
    # Testar o modelo
    print("\nTestando modelo com exemplos:")
    
    test_texts = [
        "Government announces new economic plan with broad support.",
        "Protests erupt in capital over controversial new law.",
        "Violent clashes between protesters and police, state of emergency declared."
    ]
    
    for text in test_texts:
        result = predictor._analyze_text(text)
        print(f"\nTexto: {text}")
        print(f"Classe: {result['predicted_class']}")
        print(f"Score de instabilidade: {result['instability_score']:.2f}")
        print(f"Probabilidades: {result['probabilities']}")

if __name__ == "__main__":
    main()
```

### Passo 4: Criar Script para Testar o Modelo

Crie um script para testar o modelo em `scripts/test_political_predictor.py`:

```python
#!/usr/bin/env python3
"""Script para testar o preditor político."""

import sys
import os
import argparse
import json
from pprint import pprint

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.prediction.political_analyzer import PoliticalPredictor

def main():
    """Função principal para testar o preditor político."""
    parser = argparse.ArgumentParser(description="Testar o preditor político")
    parser.add_argument("--country", default="us", help="Código do país para análise")
    parser.add_argument("--model-dir", default="./models/political", help="Diretório do modelo")
    parser.add_argument("--output", help="Arquivo para salvar os resultados (JSON)")
    
    args = parser.parse_args()
    
    # Inicializar o preditor
    print(f"Inicializando preditor político com modelo de {args.model_dir}...")
    predictor = PoliticalPredictor(model_dir=args.model_dir)
    
    # Fazer previsão
    print(f"Analisando instabilidade política para {args.country}...")
    result = predictor.predict_instability(args.country)
    
    # Exibir resultado
    print("\nResultado da análise:")
    pprint(result)
    
    # Salvar resultado se solicitado
    if args.output:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResultado salvo em {args.output}")

if __name__ == "__main__":
    main()
```

### Passo 5: Implementar Testes Unitários

Crie testes unitários em `tests/test_political_predictor.py`:

```python
import unittest
import os
import tempfile
import shutil
import json

from src.prediction.political_analyzer import PoliticalPredictor

class TestPoliticalPredictor(unittest.TestCase):
    
    def setUp(self):
        # Criar diretório temporário para testes
        self.test_dir = tempfile.mkdtemp()
        self.model_dir = os.path.join(self.test_dir, 'models')
        os.makedirs(self.model_dir, exist_ok=True)
    
    def tearDown(self):
        # Limpar diretório temporário
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Testa se o PoliticalPredictor inicializa corretamente."""
        predictor = PoliticalPredictor(model_dir=self.model_dir)
        self.assertIsNotNone(predictor.tokenizer)
        self.assertIsNotNone(predictor.model)
    
    def test_analyze_text(self):
        """Testa a análise de texto."""
        predictor = PoliticalPredictor(model_dir=self.model_dir)
        
        # Textos de exemplo
        stable_text = "Government announces new economic plan with broad support from opposition."
        unstable_text = "Protests erupt in capital over controversial new law."
        crisis_text = "Violent protests spread to multiple cities, government declares emergency."
        
        # Analisar textos
        stable_result = predictor._analyze_text(stable_text)
        unstable_result = predictor._analyze_text(unstable_text)
        crisis_result = predictor._analyze_text(crisis_text)
        
        # Verificar formato dos resultados
        for result in [stable_result, unstable_result, crisis_result]:
            self.assertIn("predicted_class", result)
            self.assertIn("instability_score", result)
            self.assertIn("probabilities", result)
        
        # Verificar ordenamento dos scores de instabilidade
        # Espera-se que o texto de crise tenha score maior que o instável,
        # que por sua vez deve ter score maior que o estável
        self.assertGreater(crisis_result["instability_score"], unstable_result["instability_score"])
        self.assertGreater(unstable_result["instability_score"], stable_result["instability_score"])
    
    def test_fetch_news(self):
        """Testa a busca de notícias."""
        predictor = PoliticalPredictor(model_dir=self.model_dir)
        
        # Buscar notícias (deve retornar dados mockados sem API key)
        news = predictor._fetch_news("us")
        
        # Verificar se retornou algo
        self.assertIsInstance(news, list)
        self.assertGreater(len(news), 0)
    
    def test_predict_instability(self):
        """Testa a previsão de instabilidade para um país."""
        predictor = PoliticalPredictor(model_dir=self.model_dir)
        
        # Fazer previsão
        result = predictor.predict_instability("us")
        
        # Verificar formato do resultado
        self.assertIn("country", result)
        self.assertEqual(result["country"], "us")
        self.assertIn("instability_score", result)
        self.assertIn("predicted_class", result)
        self.assertIn("analysis_count", result)
        self.assertIn("detailed_results", result)

if __name__ == '__main__':
    unittest.main()
```

### Passo 6: Documentação e Melhores Práticas

Crie um arquivo de documentação em `docs/political_analysis.md`:

```markdown
# Análise Política com Transformers no Autocura

Este documento descreve a implementação do módulo de análise política no sistema Autocura, usando Hugging Face Transformers.

## Visão Geral

O módulo de análise política permite que o sistema avalie o nível de instabilidade política em diferentes países, com base na análise de notícias e outros dados textuais. Isso é fundamental para a previsão de cenários políticos que podem impactar decisões estratégicas.

## Componentes Principais

1. **PoliticalPredictor**: Classe principal que gerencia o modelo e realiza previsões.
2. **Modelo Transformer**: Modelo de linguagem pré-treinado (DistilBERT por padrão) para análise de texto.
3. **API de Notícias**: Interface para buscar notícias recentes sobre países específicos.

## Fluxo de Trabalho

1. O sistema solicita uma análise para um país específico.
2. O `PoliticalPredictor` busca notícias recentes sobre o país.
3. Cada notícia é analisada pelo modelo Transformer para determinar o nível de instabilidade.
4. Os resultados são agregados para produzir uma avaliação final.
5. O sistema utiliza essa avaliação para ajustar estratégias e decisões.

## Modelo e Fine-tuning

O sistema utiliza um modelo DistilBERT pré-treinado, que pode ser fine-tuned com dados específicos para melhorar a precisão na análise política. O processo de fine-tuning envolve:

1. Preparação de um dataset rotulado (estável, instável, crise).
2. Treinamento do modelo com esse dataset.
3. Avaliação e ajuste de hiperparâmetros.
4. Implantação do modelo fine-tuned.

## Manutenção e Atualização

- Modelos são salvos em `/opt/autocura/models/political`
- Recomenda-se fine-tuning periódico com novos dados
- Monitore a precisão do modelo e ajuste conforme necessário
- Considere atualizar para modelos mais recentes quando disponíveis

## Referências

- [Documentação Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [Tutorial de Fine-tuning](https://huggingface.co/docs/transformers/training)
- [Modelos Pré-treinados Recomendados](https://huggingface.co/models?pipeline_tag=text-classification&sort=downloads)
```

### Considerações Finais para Hugging Face Transformers

- **Requisitos de Hardware**: Modelos Transformer são computacionalmente intensivos; GPU é altamente recomendada.
- **Escolha do Modelo**: Comece com modelos menores como DistilBERT para prototipagem, evolua para modelos maiores se necessário.
- **Dados de Fine-tuning**: A qualidade dos dados de fine-tuning é crucial; priorize dados reais e relevantes.
- **Multilinguismo**: Para análise global, considere modelos multilíngues como XLM-RoBERTa.
- **Atualização de Modelos**: O campo de NLP evolui rapidamente; verifique periodicamente novos modelos e técnicas.

## 4. Implementação do GraphQL para Consultas Cruzadas

### Contexto no Autocura
O GraphQL será utilizado para criar uma API unificada que permita consultas cruzadas entre diferentes módulos do sistema Autocura, facilitando a integração de dados de previsão econômica, política, análise de risco e outros domínios em uma única interface.

### Passo 1: Instalação e Configuração

```bash
# Ativar ambiente virtual
source autocura-env/bin/activate

# Instalar GraphQL com Python (usando Strawberry GraphQL)
pip install strawberry-graphql==0.171.1
pip install uvicorn==0.22.0
pip install fastapi==0.95.2

# Dependências adicionais
pip install sqlalchemy  # Para integração com banco de dados
pip install aiohttp     # Para requisições assíncronas
```

### Passo 2: Definir Esquema GraphQL

Crie um novo arquivo `src/synthesis/graphql_schema.py`:

```python
import typing
import strawberry
from datetime import datetime
from enum import Enum

# Enums
@strawberry.enum
class PoliticalStabilityLevel(Enum):
    STABLE = "Estável"
    UNSTABLE = "Instável"
    CRISIS = "Crise"
    UNKNOWN = "Desconhecido"

@strawberry.enum
class EconomicTrendType(Enum):
    GROWTH = "Crescimento"
    RECESSION = "Recessão"
    STAGNATION = "Estagnação"
    RECOVERY = "Recuperação"
    UNKNOWN = "Desconhecido"

# Tipos
@strawberry.type
class PoliticalAnalysis:
    country_code: str
    stability_level: PoliticalStabilityLevel
    instability_score: float
    analysis_date: datetime
    confidence: float
    data_sources: typing.List[str]

@strawberry.type
class EconomicForecast:
    country_code: str
    trend: EconomicTrendType
    gdp_growth_prediction: float
    inflation_prediction: float
    unemployment_prediction: float
    forecast_date: datetime
    confidence: float
    time_horizon_months: int

@strawberry.type
class RiskAssessment:
    country_code: str
    overall_risk_score: float
    political_risk_component: float
    economic_risk_component: float
    social_risk_component: float
    assessment_date: datetime
    
@strawberry.type
class AdaptationRecommendation:
    id: str
    target_component: str
    action_type: str
    priority_level: int
    expected_impact: float
    creation_date: datetime
    implementation_status: str
    
@strawberry.type
class IntegratedIntelligence:
    country_code: str
    overall_assessment: str
    risk_score: float
    political_analysis: PoliticalAnalysis
    economic_forecast: EconomicForecast
    risk_assessment: RiskAssessment
    adaptation_recommendations: typing.List[AdaptationRecommendation]
    generation_date: datetime

# Queries
@strawberry.type
class Query:
    @strawberry.field
    async def political_analysis(self, country_code: str) -> PoliticalAnalysis:
        # Em uma implementação real, isso chamaria o serviço de análise política
        # Por enquanto, retornamos dados mockados
        return PoliticalAnalysis(
            country_code=country_code,
            stability_level=PoliticalStabilityLevel.STABLE,
            instability_score=0.25,
            analysis_date=datetime.now(),
            confidence=0.85,
            data_sources=["NewsAPI", "GDELT", "Internal Analysis"]
        )
    
    @strawberry.field
    async def economic_forecast(self, country_code: str) -> EconomicForecast:
        # Em uma implementação real, isso chamaria o serviço de previsão econômica
        return EconomicForecast(
            country_code=country_code,
            trend=EconomicTrendType.GROWTH,
            gdp_growth_prediction=2.5,
            inflation_prediction=3.2,
            unemployment_prediction=5.1,
            forecast_date=datetime.now(),
            confidence=0.78,
            time_horizon_months=12
        )
    
    @strawberry.field
    async def risk_assessment(self, country_code: str) -> RiskAssessment:
        # Em uma implementação real, isso chamaria o serviço de avaliação de risco
        return RiskAssessment(
            country_code=country_code,
            overall_risk_score=0.35,
            political_risk_component=0.25,
            economic_risk_component=0.40,
            social_risk_component=0.30,
            assessment_date=datetime.now()
        )
    
    @strawberry.field
    async def adaptation_recommendations(
        self, target_component: typing.Optional[str] = None
    ) -> typing.List[AdaptationRecommendation]:
        # Em uma implementação real, isso chamaria o serviço de adaptação
        recommendations = [
            AdaptationRecommendation(
                id="rec-001",
                target_component="data_ingestion_service",
                action_type="scale_resources",
                priority_level=2,
                expected_impact=0.7,
                creation_date=datetime.now(),
                implementation_status="pending"
            ),
            AdaptationRecommendation(
                id="rec-002",
                target_component="prediction_engine",
                action_type="update_model",
                priority_level=1,
                expected_impact=0.9,
                creation_date=datetime.now(),
                implementation_status="in_progress"
            )
        ]
        
        if target_component:
            return [r for r in recommendations if r.target_component == target_component]
        return recommendations
    
    @strawberry.field
    async def integrated_intelligence(self, country_code: str) -> IntegratedIntelligence:
        # Em uma implementação real, isso agregaria dados de vários serviços
        political = await self.political_analysis(country_code)
        economic = await self.economic_forecast(country_code)
        risk = await self.risk_assessment(country_code)
        recommendations = await self.adaptation_recommendations()
        
        # Calcular uma avaliação geral com base nos componentes
        overall = "Favorável"
        if political.instability_score > 0.6 or risk.overall_risk_score > 0.6:
            overall = "Desfavorável"
        elif political.instability_score > 0.3 or risk.overall_risk_score > 0.3:
            overall = "Neutro"
        
        return IntegratedIntelligence(
            country_code=country_code,
            overall_assessment=overall,
            risk_score=(political.instability_score + risk.overall_risk_score) / 2,
            political_analysis=political,
            economic_forecast=economic,
            risk_assessment=risk,
            adaptation_recommendations=recommendations,
            generation_date=datetime.now()
        )

# Mutations (para atualizar dados)
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def update_adaptation_status(
        self, recommendation_id: str, new_status: str
    ) -> AdaptationRecommendation:
        # Em uma implementação real, isso atualizaria o status no banco de dados
        return AdaptationRecommendation(
            id=recommendation_id,
            target_component="prediction_engine",
            action_type="update_model",
            priority_level=1,
            expected_impact=0.9,
            creation_date=datetime.now(),
            implementation_status=new_status
        )

# Esquema GraphQL
schema = strawberry.Schema(query=Query, mutation=Mutation)
```

### Passo 3: Implementar o Servidor GraphQL

Crie um novo arquivo `src/synthesis/graphql_server.py`:

```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
import uvicorn
import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar esquema GraphQL
from .graphql_schema import schema

# Criar router GraphQL
graphql_router = GraphQLRouter(schema)

# Criar aplicação FastAPI
app = FastAPI(title="Autocura Intelligence API")

# Adicionar router GraphQL
app.include_router(graphql_router, prefix="/graphql")

# Rota de status
@app.get("/status")
async def status():
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

def start_server(host="0.0.0.0", port=8000):
    """Inicia o servidor GraphQL."""
    logger.info(f"Iniciando servidor GraphQL em http://{host}:{port}/graphql")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # Obter host e porta dos argumentos ou usar padrões
    import argparse
    parser = argparse.ArgumentParser(description="Servidor GraphQL do Autocura")
    parser.add_argument("--host", default="0.0.0.0", help="Host para o servidor")
    parser.add_argument("--port", type=int, default=8000, help="Porta para o servidor")
    
    args = parser.parse_args()
    start_server(host=args.host, port=args.port)
```

### Passo 4: Implementar Resolvers Reais

Crie um novo arquivo `src/synthesis/graphql_resolvers.py`:

```python
"""
Resolvers para o esquema GraphQL.
Este arquivo contém as implementações reais das funções que buscam dados
dos diferentes módulos do sistema Autocura.
"""

import logging
import asyncio
from datetime import datetime
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar módulos do Autocura
# Em uma implementação real, estes seriam os módulos reais do sistema
# Por enquanto, usamos imports condicionais para evitar erros se os módulos não existirem
try:
    from ..prediction.political_analyzer import PoliticalPredictor
    political_analyzer_available = True
except ImportError:
    logger.warning("Módulo political_analyzer não disponível. Usando dados mockados.")
    political_analyzer_available = False

try:
    from ..prediction.economic_forecaster import EconomicForecaster
    economic_forecaster_available = True
except ImportError:
    logger.warning("Módulo economic_forecaster não disponível. Usando dados mockados.")
    economic_forecaster_available = False

try:
    from ..adaptation.autonomous_adapter import AdaptationEngine
    adaptation_engine_available = True
except ImportError:
    logger.warning("Módulo autonomous_adapter não disponível. Usando dados mockados.")
    adaptation_engine_available = False

# Classe para gerenciar os resolvers
class AutocuraResolvers:
    def __init__(self):
        """Inicializa os resolvers com conexões aos módulos do Autocura."""
        # Inicializar conexões com os módulos
        self.political_predictor = None
        self.economic_forecaster = None
        self.adaptation_engine = None
        
        if political_analyzer_available:
            try:
                self.political_predictor = PoliticalPredictor()
                logger.info("PoliticalPredictor inicializado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao inicializar PoliticalPredictor: {e}")
        
        if economic_forecaster_available:
            try:
                self.economic_forecaster = EconomicForecaster()
                logger.info("EconomicForecaster inicializado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao inicializar EconomicForecaster: {e}")
        
        if adaptation_engine_available:
            try:
                self.adaptation_engine = AdaptationEngine()
                logger.info("AdaptationEngine inicializado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao inicializar AdaptationEngine: {e}")
    
    async def get_political_analysis(self, country_code):
        """Obtém análise política para um país."""
        from .graphql_schema import PoliticalAnalysis, PoliticalStabilityLevel
        
        if self.political_predictor:
            try:
                # Chamar o método real
                result = self.political_predictor.predict_instability(country_code)
                
                # Mapear o resultado para o tipo GraphQL
                stability_level = PoliticalStabilityLevel.UNKNOWN
                if result.get("predicted_class") == "Estável":
                    stability_level = PoliticalStabilityLevel.STABLE
                elif result.get("predicted_class") == "Instável":
                    stability_level = PoliticalStabilityLevel.UNSTABLE
                elif result.get("predicted_class") == "Crise":
                    stability_level = PoliticalStabilityLevel.CRISIS
                
                return PoliticalAnalysis(
                    country_code=country_code,
                    stability_level=stability_level,
                    instability_score=result.get("instability_score", 0.0),
                    analysis_date=datetime.now(),
                    confidence=result.get("confidence", 0.0),
                    data_sources=result.get("data_sources", ["Internal Analysis"])
                )
            except Exception as e:
                logger.error(f"Erro ao obter análise política: {e}")
        
        # Fallback para dados mockados
        return PoliticalAnalysis(
            country_code=country_code,
            stability_level=PoliticalStabilityLevel.STABLE,
            instability_score=0.25,
            analysis_date=datetime.now(),
            confidence=0.85,
            data_sources=["Mocked Data"]
        )
    
    async def get_economic_forecast(self, country_code):
        """Obtém previsão econômica para um país."""
        from .graphql_schema import EconomicForecast, EconomicTrendType
        
        if self.economic_forecaster:
            try:
                # Chamar o método real
                # Exemplo: result = self.economic_forecaster.predict(country_code)
                
                # Por enquanto, usamos dados mockados
                pass
            except Exception as e:
                logger.error(f"Erro ao obter previsão econômica: {e}")
        
        # Dados mockados
        return EconomicForecast(
            country_code=country_code,
            trend=EconomicTrendType.GROWTH,
            gdp_growth_prediction=2.5,
            inflation_prediction=3.2,
            unemployment_prediction=5.1,
            forecast_date=datetime.now(),
            confidence=0.78,
            time_horizon_months=12
        )
    
    async def get_adaptation_recommendations(self, target_component=None):
        """Obtém recomendações de adaptação."""
        from .graphql_schema import AdaptationRecommendation
        
        if self.adaptation_engine:
            try:
                # Chamar o método real
                # Exemplo: recommendations = self.adaptation_engine.get_recommendations(target_component)
                
                # Por enquanto, usamos dados mockados
                pass
            except Exception as e:
                logger.error(f"Erro ao obter recomendações de adaptação: {e}")
        
        # Dados mockados
        recommendations = [
            AdaptationRecommendation(
                id="rec-001",
                target_component="data_ingestion_service",
                action_type="scale_resources",
                priority_level=2,
                expected_impact=0.7,
                creation_date=datetime.now(),
                implementation_status="pending"
            ),
            AdaptationRecommendation(
                id="rec-002",
                target_component="prediction_engine",
                action_type="update_model",
                priority_level=1,
                expected_impact=0.9,
                creation_date=datetime.now(),
                implementation_status="in_progress"
            )
        ]
        
        if target_component:
            return [r for r in recommendations if r.target_component == target_component]
        return recommendations
    
    async def update_adaptation_status(self, recommendation_id, new_status):
        """Atualiza o status de uma recomendação de adaptação."""
        from .graphql_schema import AdaptationRecommendation
        
        if self.adaptation_engine:
            try:
                # Chamar o método real
                # Exemplo: result = self.adaptation_engine.update_recommendation_status(recommendation_id, new_status)
                
                # Por enquanto, usamos dados mockados
                pass
            except Exception as e:
                logger.error(f"Erro ao atualizar status de adaptação: {e}")
        
        # Dados mockados
        return AdaptationRecommendation(
            id=recommendation_id,
            target_component="prediction_engine",
            action_type="update_model",
            priority_level=1,
            expected_impact=0.9,
            creation_date=datetime.now(),
            implementation_status=new_status
        )

# Instância global dos resolvers
resolvers = AutocuraResolvers()
```

### Passo 5: Integrar Resolvers com o Esquema

Modifique o arquivo `src/synthesis/graphql_schema.py` para usar os resolvers reais:

```python
# No início do arquivo, após os imports
from .graphql_resolvers import resolvers

# Substitua as implementações das queries por chamadas aos resolvers
@strawberry.type
class Query:
    @strawberry.field
    async def political_analysis(self, country_code: str) -> PoliticalAnalysis:
        return await resolvers.get_political_analysis(country_code)
    
    @strawberry.field
    async def economic_forecast(self, country_code: str) -> EconomicForecast:
        return await resolvers.get_economic_forecast(country_code)
    
    # ... outras queries ...

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def update_adaptation_status(
        self, recommendation_id: str, new_status: str
    ) -> AdaptationRecommendation:
        return await resolvers.update_adaptation_status(recommendation_id, new_status)
```

### Passo 6: Criar Script para Iniciar o Servidor

Crie um script em `scripts/start_graphql_server.py`:

```python
#!/usr/bin/env python3
"""Script para iniciar o servidor GraphQL do Autocura."""

import sys
import os
import argparse

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.synthesis.graphql_server import start_server

def main():
    """Função principal para iniciar o servidor GraphQL."""
    parser = argparse.ArgumentParser(description="Servidor GraphQL do Autocura")
    parser.add_argument("--host", default="0.0.0.0", help="Host para o servidor")
    parser.add_argument("--port", type=int, default=8000, help="Porta para o servidor")
    
    args = parser.parse_args()
    
    print(f"Iniciando servidor GraphQL em http://{args.host}:{args.port}/graphql")
    start_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main()
```

### Passo 7: Criar Cliente de Exemplo

Crie um script de cliente em `scripts/graphql_client_example.py`:

```python
#!/usr/bin/env python3
"""Script de exemplo para consultar a API GraphQL do Autocura."""

import sys
import os
import argparse
import json
import requests
from pprint import pprint

def run_query(url, query, variables=None):
    """Executa uma consulta GraphQL.
    
    Args:
        url: URL do servidor GraphQL.
        query: Consulta GraphQL.
        variables: Variáveis para a consulta (opcional).
    
    Returns:
        dict: Resultado da consulta.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {'query': query}
    
    if variables:
        payload['variables'] = variables
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"Erro na consulta: {response.status_code} {response.text}")
    
    return response.json()

def main():
    """Função principal para executar consultas de exemplo."""
    parser = argparse.ArgumentParser(description="Cliente GraphQL do Autocura")
    parser.add_argument("--url", default="http://localhost:8000/graphql", help="URL do servidor GraphQL")
    parser.add_argument("--country", default="br", help="Código do país para análise")
    
    args = parser.parse_args()
    
    # Consulta de exemplo: análise política
    political_query = """
    query GetPoliticalAnalysis($countryCode: String!) {
        politicalAnalysis(countryCode: $countryCode) {
            countryCode
            stabilityLevel
            instabilityScore
            analysisDate
            confidence
            dataSources
        }
    }
    """
    
    # Consulta de exemplo: inteligência integrada
    integrated_query = """
    query GetIntegratedIntelligence($countryCode: String!) {
        integratedIntelligence(countryCode: $countryCode) {
            countryCode
            overallAssessment
            riskScore
            generationDate
            politicalAnalysis {
                stabilityLevel
                instabilityScore
            }
            economicForecast {
                trend
                gdpGrowthPrediction
                inflationPrediction
            }
            adaptationRecommendations {
                id
                targetComponent
                actionType
                priorityLevel
            }
        }
    }
    """
    
    # Executar consultas
    try:
        print(f"Consultando análise política para {args.country}...")
        political_result = run_query(
            args.url, 
            political_query, 
            variables={"countryCode": args.country}
        )
        print("\nResultado da análise política:")
        pprint(political_result)
        
        print(f"\nConsultando inteligência integrada para {args.country}...")
        integrated_result = run_query(
            args.url, 
            integrated_query, 
            variables={"countryCode": args.country}
        )
        print("\nResultado da inteligência integrada:")
        pprint(integrated_result)
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
```

### Passo 8: Implementar Testes Unitários

Crie testes unitários em `tests/test_graphql_api.py`:

```python
import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.synthesis.graphql_schema import schema

class TestGraphQLSchema(unittest.TestCase):
    
    def test_political_analysis_query(self):
        """Testa a consulta de análise política."""
        # Consulta GraphQL
        query = """
        query {
            politicalAnalysis(countryCode: "br") {
                countryCode
                stabilityLevel
                instabilityScore
            }
        }
        """
        
        # Executar consulta
        result = schema.execute_sync(query)
        
        # Verificar se não há erros
        self.assertIsNone(result.errors)
        
        # Verificar resultado
        data = result.data
        self.assertIn("politicalAnalysis", data)
        self.assertEqual(data["politicalAnalysis"]["countryCode"], "br")
    
    def test_integrated_intelligence_query(self):
        """Testa a consulta de inteligência integrada."""
        # Consulta GraphQL
        query = """
        query {
            integratedIntelligence(countryCode: "us") {
                countryCode
                overallAssessment
                riskScore
            }
        }
        """
        
        # Executar consulta
        result = schema.execute_sync(query)
        
        # Verificar se não há erros
        self.assertIsNone(result.errors)
        
        # Verificar resultado
        data = result.data
        self.assertIn("integratedIntelligence", data)
        self.assertEqual(data["integratedIntelligence"]["countryCode"], "us")
    
    def test_update_adaptation_status_mutation(self):
        """Testa a mutação de atualização de status de adaptação."""
        # Mutação GraphQL
        mutation = """
        mutation {
            updateAdaptationStatus(recommendationId: "rec-001", newStatus: "completed") {
                id
                implementationStatus
            }
        }
        """
        
        # Executar mutação
        result = schema.execute_sync(mutation)
        
        # Verificar se não há erros
        self.assertIsNone(result.errors)
        
        # Verificar resultado
        data = result.data
        self.assertIn("updateAdaptationStatus", data)
        self.assertEqual(data["updateAdaptationStatus"]["id"], "rec-001")
        self.assertEqual(data["updateAdaptationStatus"]["implementationStatus"], "completed")

if __name__ == '__main__':
    unittest.main()
```

### Passo 9: Documentação e Melhores Práticas

Crie um arquivo de documentação em `docs/graphql_api.md`:

```markdown
# API GraphQL do Autocura

Este documento descreve a implementação da API GraphQL no sistema Autocura, que permite consultas cruzadas entre diferentes módulos do sistema.

## Visão Geral

A API GraphQL fornece uma interface unificada para acessar dados de diferentes módulos do Autocura, como análise política, previsão econômica, avaliação de risco e recomendações de adaptação. Isso permite que os clientes obtenham exatamente os dados que precisam em uma única requisição, facilitando a integração e visualização de informações.

## Componentes Principais

1. **Esquema GraphQL**: Define os tipos de dados e operações disponíveis na API.
2. **Resolvers**: Implementam a lógica para buscar dados dos diferentes módulos do sistema.
3. **Servidor GraphQL**: Expõe a API através de um servidor HTTP.

## Tipos de Dados

A API GraphQL define os seguintes tipos principais:

- **PoliticalAnalysis**: Análise de estabilidade política para um país.
- **EconomicForecast**: Previsão de indicadores econômicos para um país.
- **RiskAssessment**: Avaliação de risco global para um país.
- **AdaptationRecommendation**: Recomendação de adaptação para um componente do sistema.
- **IntegratedIntelligence**: Visão integrada de todos os dados para um país.

## Operações Disponíveis

### Queries

- **politicalAnalysis(countryCode: String!)**: Obtém análise política para um país.
- **economicForecast(countryCode: String!)**: Obtém previsão econômica para um país.
- **riskAssessment(countryCode: String!)**: Obtém avaliação de risco para um país.
- **adaptationRecommendations(targetComponent: String)**: Obtém recomendações de adaptação, opcionalmente filtradas por componente.
- **integratedIntelligence(countryCode: String!)**: Obtém visão integrada de todos os dados para um país.

### Mutations

- **updateAdaptationStatus(recommendationId: String!, newStatus: String!)**: Atualiza o status de uma recomendação de adaptação.

## Uso da API

### Exemplo de Consulta

```graphql
query {
  integratedIntelligence(countryCode: "br") {
    countryCode
    overallAssessment
    riskScore
    politicalAnalysis {
      stabilityLevel
      instabilityScore
    }
    economicForecast {
      trend
      gdpGrowthPrediction
    }
  }
}
```

### Exemplo de Mutação

```graphql
mutation {
  updateAdaptationStatus(
    recommendationId: "rec-001", 
    newStatus: "completed"
  ) {
    id
    implementationStatus
  }
}
```

## Manutenção e Evolução

- **Adicionar Novos Tipos**: Para adicionar novos tipos de dados, atualize o arquivo `graphql_schema.py`.
- **Adicionar Novas Operações**: Para adicionar novas queries ou mutations, atualize as classes `Query` e `Mutation` no esquema.
- **Integrar Novos Módulos**: Para integrar novos módulos do Autocura, adicione novos resolvers em `graphql_resolvers.py`.

## Referências

- [Documentação Strawberry GraphQL](https://strawberry.rocks/)
- [Especificação GraphQL](https://spec.graphql.org/)
- [Tutorial GraphQL com Python](https://www.howtographql.com/graphql-python/0-introduction/)
```

### Considerações Finais para GraphQL

- **Escalabilidade**: Para aplicações de produção, considere usar um servidor GraphQL mais robusto como Apollo Server ou GraphQL Yoga.
- **Autenticação e Autorização**: Implemente autenticação e autorização para proteger a API em ambientes de produção.
- **Caching**: Considere implementar caching para melhorar o desempenho de consultas frequentes.
- **Monitoramento**: Use ferramentas como Apollo Studio para monitorar o desempenho e uso da API.
- **Evolução do Esquema**: Planeje cuidadosamente a evolução do esquema para evitar quebrar clientes existentes.

## 5. Implementação do Apache Arrow para Processamento de Dados de Alto Desempenho

### Contexto no Autocura
O Apache Arrow será utilizado no sistema Autocura para otimizar a transferência e processamento de dados entre diferentes módulos, especialmente no componente `metrics_exporter.py` do módulo de monitoramento, permitindo exportação e análise de métricas com alta performance.

### Passo 1: Instalação e Configuração

```bash
# Ativar ambiente virtual
source autocura-env/bin/activate

# Instalar PyArrow (implementação Python do Apache Arrow)
pip install pyarrow==12.0.1

# Dependências adicionais para integração com outras bibliotecas
pip install pandas  # Para integração com pandas
pip install numpy   # Para operações numéricas
pip install fastparquet  # Para suporte a formato Parquet
```

### Passo 2: Implementar Exportador de Métricas com Arrow

Modifique o arquivo `src/conscienciaSituacional/monitoramento/metrics_exporter.py` para usar Apache Arrow:

```python
import os
import json
import time
import logging
from datetime import datetime
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pyarrow import csv
from typing import Dict, List, Any, Optional, Union

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetricsExporter:
    """Exporta métricas do sistema Autocura usando Apache Arrow para alta performance."""
    
    def __init__(self, export_dir="/opt/autocura/metrics", 
                 format="parquet", compression="snappy"):
        """Inicializa o exportador de métricas.
        
        Args:
            export_dir: Diretório para exportar os dados.
            format: Formato de exportação ('parquet', 'csv', 'json', 'arrow').
            compression: Método de compressão para formatos que suportam.
        """
        self.export_dir = export_dir
        self.format = format.lower()
        self.compression = compression
        
        # Validar formato
        valid_formats = ["parquet", "csv", "json", "arrow"]
        if self.format not in valid_formats:
            logger.warning(f"Formato {format} não suportado. Usando parquet como padrão.")
            self.format = "parquet"
        
        # Criar diretório de exportação se não existir
        os.makedirs(export_dir, exist_ok=True)
        
        logger.info(f"MetricsExporter inicializado. Formato: {self.format}, Diretório: {self.export_dir}")
    
    def _convert_to_arrow_table(self, data: Union[List[Dict], pd.DataFrame]) -> pa.Table:
        """Converte dados para uma tabela Arrow.
        
        Args:
            data: Dados a serem convertidos (lista de dicionários ou DataFrame).
            
        Returns:
            pa.Table: Tabela Arrow.
        """
        if isinstance(data, pd.DataFrame):
            return pa.Table.from_pandas(data)
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # Converter lista de dicionários para DataFrame e depois para tabela Arrow
            df = pd.DataFrame(data)
            return pa.Table.from_pandas(df)
        else:
            raise ValueError("Dados devem ser uma lista de dicionários ou um DataFrame")
    
    def export_metrics(self, metrics_data: Union[List[Dict], pd.DataFrame], 
                      name: str, timestamp: Optional[datetime] = None) -> str:
        """Exporta métricas para o formato especificado.
        
        Args:
            metrics_data: Dados das métricas (lista de dicionários ou DataFrame).
            name: Nome base para o arquivo de saída.
            timestamp: Timestamp para incluir no nome do arquivo (opcional).
            
        Returns:
            str: Caminho para o arquivo exportado.
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Formatar timestamp para o nome do arquivo
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Converter dados para tabela Arrow
        try:
            table = self._convert_to_arrow_table(metrics_data)
            logger.info(f"Dados convertidos para tabela Arrow: {len(table)} linhas, {len(table.column_names)} colunas")
        except Exception as e:
            logger.error(f"Erro ao converter dados para tabela Arrow: {e}")
            raise
        
        # Exportar tabela no formato especificado
        try:
            if self.format == "parquet":
                filename = f"{name}_{timestamp_str}.parquet"
                filepath = os.path.join(self.export_dir, filename)
                pq.write_table(table, filepath, compression=self.compression)
            
            elif self.format == "csv":
                filename = f"{name}_{timestamp_str}.csv"
                filepath = os.path.join(self.export_dir, filename)
                csv.write_csv(table, filepath)
            
            elif self.format == "json":
                filename = f"{name}_{timestamp_str}.json"
                filepath = os.path.join(self.export_dir, filename)
                # Converter para pandas e depois para JSON
                df = table.to_pandas()
                df.to_json(filepath, orient="records", lines=True)
            
            elif self.format == "arrow":
                filename = f"{name}_{timestamp_str}.arrow"
                filepath = os.path.join(self.export_dir, filename)
                with pa.OSFile(filepath, 'wb') as sink:
                    writer = pa.RecordBatchFileWriter(sink, table.schema)
                    writer.write_table(table)
                    writer.close()
            
            logger.info(f"Métricas exportadas para {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao exportar métricas: {e}")
            raise
    
    def import_metrics(self, filepath: str) -> pd.DataFrame:
        """Importa métricas de um arquivo.
        
        Args:
            filepath: Caminho para o arquivo.
            
        Returns:
            pd.DataFrame: DataFrame com os dados importados.
        """
        try:
            # Determinar formato pelo nome do arquivo
            if filepath.endswith(".parquet"):
                table = pq.read_table(filepath)
            elif filepath.endswith(".csv"):
                table = csv.read_csv(filepath)
            elif filepath.endswith(".json"):
                # Ler JSON diretamente para pandas
                df = pd.read_json(filepath, lines=True)
                return df
            elif filepath.endswith(".arrow"):
                with pa.memory_map(filepath, 'rb') as source:
                    reader = pa.ipc.open_file(source)
                    table = reader.read_all()
            else:
                raise ValueError(f"Formato de arquivo não suportado: {filepath}")
            
            # Converter tabela Arrow para DataFrame
            df = table.to_pandas()
            logger.info(f"Métricas importadas de {filepath}: {len(df)} linhas, {len(df.columns)} colunas")
            return df
            
        except Exception as e:
            logger.error(f"Erro ao importar métricas: {e}")
            raise
    
    def aggregate_metrics(self, filepaths: List[str], 
                         aggregation_type: str = "concat") -> pd.DataFrame:
        """Agrega métricas de múltiplos arquivos.
        
        Args:
            filepaths: Lista de caminhos para arquivos.
            aggregation_type: Tipo de agregação ('concat' ou 'merge').
            
        Returns:
            pd.DataFrame: DataFrame com os dados agregados.
        """
        if not filepaths:
            raise ValueError("Lista de arquivos vazia")
        
        try:
            # Importar primeiro arquivo
            result_df = self.import_metrics(filepaths[0])
            
            # Agregar arquivos restantes
            for filepath in filepaths[1:]:
                df = self.import_metrics(filepath)
                
                if aggregation_type == "concat":
                    # Concatenar DataFrames
                    result_df = pd.concat([result_df, df], ignore_index=True)
                elif aggregation_type == "merge":
                    # Mesclar DataFrames (requer colunas em comum)
                    # Aqui assumimos que a primeira coluna é a chave de mesclagem
                    key_column = result_df.columns[0]
                    result_df = pd.merge(result_df, df, on=key_column, how="outer")
                else:
                    raise ValueError(f"Tipo de agregação não suportado: {aggregation_type}")
            
            logger.info(f"Métricas agregadas de {len(filepaths)} arquivos: {len(result_df)} linhas")
            return result_df
            
        except Exception as e:
            logger.error(f"Erro ao agregar métricas: {e}")
            raise
    
    def export_to_prometheus(self, metrics_data: Union[List[Dict], pd.DataFrame], 
                           prometheus_gateway_url: str) -> bool:
        """Exporta métricas para Prometheus via Pushgateway.
        
        Args:
            metrics_data: Dados das métricas.
            prometheus_gateway_url: URL do Prometheus Pushgateway.
            
        Returns:
            bool: True se a exportação foi bem-sucedida.
        """
        try:
            # Converter para DataFrame se necessário
            if not isinstance(metrics_data, pd.DataFrame):
                df = pd.DataFrame(metrics_data)
            else:
                df = metrics_data
            
            # Implementação simplificada - em um caso real, usaríamos
            # a biblioteca prometheus_client para exportar as métricas
            logger.info(f"Simulando exportação de {len(df)} métricas para Prometheus: {prometheus_gateway_url}")
            
            # Aqui seria a implementação real com prometheus_client
            # from prometheus_client import push_to_gateway, Counter, Gauge
            # ...
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao exportar para Prometheus: {e}")
            return False
```

### Passo 3: Implementar Utilitário para Processamento de Dados com Arrow

Crie um novo arquivo `src/utils/arrow_utils.py` para funções utilitárias:

```python
"""
Utilitários para processamento de dados com Apache Arrow.
"""

import os
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq
import pyarrow.csv as csv
import logging
from typing import Dict, List, Any, Optional, Union, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_pandas_to_arrow(df: pd.DataFrame) -> pa.Table:
    """Converte um DataFrame pandas para uma tabela Arrow.
    
    Args:
        df: DataFrame pandas.
        
    Returns:
        pa.Table: Tabela Arrow.
    """
    return pa.Table.from_pandas(df)

def convert_arrow_to_pandas(table: pa.Table) -> pd.DataFrame:
    """Converte uma tabela Arrow para um DataFrame pandas.
    
    Args:
        table: Tabela Arrow.
        
    Returns:
        pd.DataFrame: DataFrame pandas.
    """
    return table.to_pandas()

def filter_arrow_table(table: pa.Table, condition_col: str, 
                      condition_op: str, condition_val: Any) -> pa.Table:
    """Filtra uma tabela Arrow com base em uma condição.
    
    Args:
        table: Tabela Arrow.
        condition_col: Nome da coluna para filtrar.
        condition_op: Operador de comparação ('==', '!=', '>', '<', '>=', '<=').
        condition_val: Valor para comparação.
        
    Returns:
        pa.Table: Tabela Arrow filtrada.
    """
    # Obter a coluna
    col = table[condition_col]
    
    # Aplicar a condição
    if condition_op == "==":
        mask = pc.equal(col, condition_val)
    elif condition_op == "!=":
        mask = pc.not_equal(col, condition_val)
    elif condition_op == ">":
        mask = pc.greater(col, condition_val)
    elif condition_op == "<":
        mask = pc.less(col, condition_val)
    elif condition_op == ">=":
        mask = pc.greater_equal(col, condition_val)
    elif condition_op == "<=":
        mask = pc.less_equal(col, condition_val)
    else:
        raise ValueError(f"Operador não suportado: {condition_op}")
    
    # Filtrar a tabela
    return table.filter(mask)

def aggregate_arrow_table(table: pa.Table, group_by_cols: List[str], 
                         agg_col: str, agg_func: str) -> pa.Table:
    """Agrega uma tabela Arrow.
    
    Args:
        table: Tabela Arrow.
        group_by_cols: Colunas para agrupar.
        agg_col: Coluna para agregar.
        agg_func: Função de agregação ('sum', 'mean', 'min', 'max', 'count').
        
    Returns:
        pa.Table: Tabela Arrow agregada.
    """
    # Converter para pandas para agregação (Arrow não tem API de agregação completa)
    df = table.to_pandas()
    
    # Agrupar e agregar
    if agg_func == "sum":
        result_df = df.groupby(group_by_cols)[agg_col].sum().reset_index()
    elif agg_func == "mean":
        result_df = df.groupby(group_by_cols)[agg_col].mean().reset_index()
    elif agg_func == "min":
        result_df = df.groupby(group_by_cols)[agg_col].min().reset_index()
    elif agg_func == "max":
        result_df = df.groupby(group_by_cols)[agg_col].max().reset_index()
    elif agg_func == "count":
        result_df = df.groupby(group_by_cols)[agg_col].count().reset_index()
    else:
        raise ValueError(f"Função de agregação não suportada: {agg_func}")
    
    # Converter de volta para Arrow
    return pa.Table.from_pandas(result_df)

def join_arrow_tables(left_table: pa.Table, right_table: pa.Table, 
                     join_key: str, join_type: str = "inner") -> pa.Table:
    """Une duas tabelas Arrow.
    
    Args:
        left_table: Tabela Arrow esquerda.
        right_table: Tabela Arrow direita.
        join_key: Coluna para junção.
        join_type: Tipo de junção ('inner', 'left', 'right', 'outer').
        
    Returns:
        pa.Table: Tabela Arrow resultante da junção.
    """
    # Converter para pandas para junção (Arrow não tem API de junção completa)
    left_df = left_table.to_pandas()
    right_df = right_table.to_pandas()
    
    # Realizar junção
    result_df = pd.merge(left_df, right_df, on=join_key, how=join_type)
    
    # Converter de volta para Arrow
    return pa.Table.from_pandas(result_df)

def save_arrow_table(table: pa.Table, filepath: str, 
                    format: str = "parquet", compression: str = "snappy") -> str:
    """Salva uma tabela Arrow em um arquivo.
    
    Args:
        table: Tabela Arrow.
        filepath: Caminho para o arquivo.
        format: Formato de arquivo ('parquet', 'csv', 'json', 'arrow').
        compression: Método de compressão para formatos que suportam.
        
    Returns:
        str: Caminho para o arquivo salvo.
    """
    # Garantir que o diretório exista
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Salvar no formato especificado
    if format == "parquet":
        if not filepath.endswith(".parquet"):
            filepath += ".parquet"
        pq.write_table(table, filepath, compression=compression)
    
    elif format == "csv":
        if not filepath.endswith(".csv"):
            filepath += ".csv"
        csv.write_csv(table, filepath)
    
    elif format == "json":
        if not filepath.endswith(".json"):
            filepath += ".json"
        # Converter para pandas e depois para JSON
        df = table.to_pandas()
        df.to_json(filepath, orient="records", lines=True)
    
    elif format == "arrow":
        if not filepath.endswith(".arrow"):
            filepath += ".arrow"
        with pa.OSFile(filepath, 'wb') as sink:
            writer = pa.RecordBatchFileWriter(sink, table.schema)
            writer.write_table(table)
            writer.close()
    
    else:
        raise ValueError(f"Formato não suportado: {format}")
    
    logger.info(f"Tabela Arrow salva em {filepath}")
    return filepath

def load_arrow_table(filepath: str) -> pa.Table:
    """Carrega uma tabela Arrow de um arquivo.
    
    Args:
        filepath: Caminho para o arquivo.
        
    Returns:
        pa.Table: Tabela Arrow.
    """
    # Determinar formato pelo nome do arquivo
    if filepath.endswith(".parquet"):
        table = pq.read_table(filepath)
    elif filepath.endswith(".csv"):
        table = csv.read_csv(filepath)
    elif filepath.endswith(".json"):
        # Ler JSON para pandas e converter para Arrow
        df = pd.read_json(filepath, lines=True)
        table = pa.Table.from_pandas(df)
    elif filepath.endswith(".arrow"):
        with pa.memory_map(filepath, 'rb') as source:
            reader = pa.ipc.open_file(source)
            table = reader.read_all()
    else:
        raise ValueError(f"Formato de arquivo não suportado: {filepath}")
    
    logger.info(f"Tabela Arrow carregada de {filepath}: {len(table)} linhas, {len(table.column_names)} colunas")
    return table

def create_arrow_ipc_stream(table: pa.Table) -> bytes:
    """Cria um stream IPC Arrow para transferência de dados entre processos.
    
    Args:
        table: Tabela Arrow.
        
    Returns:
        bytes: Stream IPC serializado.
    """
    # Serializar a tabela para um stream IPC
    sink = pa.BufferOutputStream()
    writer = pa.RecordBatchStreamWriter(sink, table.schema)
    writer.write_table(table)
    writer.close()
    
    # Obter o buffer serializado
    buf = sink.getvalue()
    return buf.to_pybytes()

def read_arrow_ipc_stream(ipc_stream: bytes) -> pa.Table:
    """Lê um stream IPC Arrow.
    
    Args:
        ipc_stream: Stream IPC serializado.
        
    Returns:
        pa.Table: Tabela Arrow.
    """
    # Criar um buffer a partir dos bytes
    buf = pa.py_buffer(ipc_stream)
    
    # Ler a tabela do stream
    reader = pa.RecordBatchStreamReader(buf)
    table = reader.read_all()
    
    return table
```

### Passo 4: Implementar Exemplo de Uso para Transferência de Dados entre Processos

Crie um exemplo em `examples/arrow_ipc_example.py`:

```python
#!/usr/bin/env python3
"""
Exemplo de uso do Apache Arrow para transferência de dados entre processos.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import pyarrow as pa
from multiprocessing import Process, Queue
import argparse

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.arrow_utils import create_arrow_ipc_stream, read_arrow_ipc_stream

def generate_data(size=1000000):
    """Gera dados de exemplo.
    
    Args:
        size: Número de linhas.
        
    Returns:
        pd.DataFrame: DataFrame com dados gerados.
    """
    # Gerar dados aleatórios
    data = {
        'id': np.arange(size),
        'value_a': np.random.rand(size),
        'value_b': np.random.rand(size),
        'category': np.random.choice(['A', 'B', 'C', 'D'], size),
        'timestamp': pd.date_range(start='2023-01-01', periods=size, freq='S')
    }
    
    return pd.DataFrame(data)

def producer_process(queue, size, use_arrow):
    """Processo produtor que gera dados e os envia para a fila.
    
    Args:
        queue: Fila para comunicação entre processos.
        size: Tamanho dos dados a gerar.
        use_arrow: Se True, usa Arrow para serialização; se False, usa pickle (padrão do Python).
    """
    print(f"Produtor: Gerando {size} linhas de dados...")
    df = generate_data(size)
    
    # Medir tempo de serialização
    start_time = time.time()
    
    if use_arrow:
        # Converter para Arrow e serializar
        table = pa.Table.from_pandas(df)
        serialized_data = create_arrow_ipc_stream(table)
        print(f"Produtor: Dados serializados com Arrow em {time.time() - start_time:.2f} segundos")
    else:
        # Usar serialização padrão (pickle)
        serialized_data = df
        print(f"Produtor: Dados preparados com pickle em {time.time() - start_time:.2f} segundos")
    
    # Enviar dados para a fila
    start_time = time.time()
    queue.put(serialized_data)
    print(f"Produtor: Dados enviados para a fila em {time.time() - start_time:.2f} segundos")

def consumer_process(queue, use_arrow):
    """Processo consumidor que recebe dados da fila e os processa.
    
    Args:
        queue: Fila para comunicação entre processos.
        use_arrow: Se True, espera dados serializados com Arrow; se False, espera DataFrame.
    """
    print("Consumidor: Aguardando dados...")
    
    # Receber dados da fila
    start_time = time.time()
    data = queue.get()
    print(f"Consumidor: Dados recebidos da fila em {time.time() - start_time:.2f} segundos")
    
    # Medir tempo de desserialização
    start_time = time.time()
    
    if use_arrow:
        # Desserializar dados Arrow
        table = read_arrow_ipc_stream(data)
        df = table.to_pandas()
        print(f"Consumidor: Dados desserializados com Arrow em {time.time() - start_time:.2f} segundos")
    else:
        # Dados já estão como DataFrame (desserialização automática)
        df = data
        print(f"Consumidor: Dados recebidos com pickle em {time.time() - start_time:.2f} segundos")
    
    # Processar dados (exemplo: calcular estatísticas)
    start_time = time.time()
    stats = {
        'count': len(df),
        'mean_a': df['value_a'].mean(),
        'mean_b': df['value_b'].mean(),
        'category_counts': df['category'].value_counts().to_dict()
    }
    print(f"Consumidor: Dados processados em {time.time() - start_time:.2f} segundos")
    
    # Exibir estatísticas
    print("\nEstatísticas calculadas:")
    print(f"  Contagem: {stats['count']}")
    print(f"  Média value_a: {stats['mean_a']:.4f}")
    print(f"  Média value_b: {stats['mean_b']:.4f}")
    print("  Contagem por categoria:")
    for category, count in stats['category_counts'].items():
        print(f"    {category}: {count}")

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Exemplo de IPC com Apache Arrow")
    parser.add_argument("--size", type=int, default=1000000, help="Número de linhas de dados")
    parser.add_argument("--method", choices=["arrow", "pickle"], default="arrow", 
                        help="Método de serialização")
    
    args = parser.parse_args()
    use_arrow = args.method == "arrow"
    
    print(f"Iniciando exemplo com {args.size} linhas usando {args.method}...")
    
    # Criar fila para comunicação entre processos
    queue = Queue()
    
    # Iniciar processos
    producer = Process(target=producer_process, args=(queue, args.size, use_arrow))
    consumer = Process(target=consumer_process, args=(queue, use_arrow))
    
    # Iniciar produtor
    start_time = time.time()
    producer.start()
    
    # Iniciar consumidor
    consumer.start()
    
    # Aguardar conclusão
    producer.join()
    consumer.join()
    
    print(f"\nProcesso concluído em {time.time() - start_time:.2f} segundos")

if __name__ == "__main__":
    main()
```

### Passo 5: Implementar Exemplo de Benchmark para Comparação de Performance

Crie um benchmark em `examples/arrow_benchmark.py`:

```python
#!/usr/bin/env python3
"""
Benchmark para comparar a performance do Apache Arrow com outras abordagens.
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pickle
import json
import tempfile
import argparse
from tabulate import tabulate

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.arrow_utils import (
    convert_pandas_to_arrow, 
    convert_arrow_to_pandas,
    save_arrow_table,
    load_arrow_table,
    create_arrow_ipc_stream,
    read_arrow_ipc_stream
)

def generate_data(size=1000000):
    """Gera dados de exemplo.
    
    Args:
        size: Número de linhas.
        
    Returns:
        pd.DataFrame: DataFrame com dados gerados.
    """
    # Gerar dados aleatórios
    data = {
        'id': np.arange(size),
        'value_a': np.random.rand(size),
        'value_b': np.random.rand(size),
        'category': np.random.choice(['A', 'B', 'C', 'D'], size),
        'timestamp': pd.date_range(start='2023-01-01', periods=size, freq='S')
    }
    
    return pd.DataFrame(data)

def benchmark_serialization(df, temp_dir):
    """Benchmark de serialização/desserialização.
    
    Args:
        df: DataFrame para benchmark.
        temp_dir: Diretório temporário para arquivos.
        
    Returns:
        list: Resultados do benchmark.
    """
    results = []
    
    # Tamanho do DataFrame em memória
    df_size_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    # 1. Pickle (Python padrão)
    pickle_path = os.path.join(temp_dir, "data.pickle")
    
    start_time = time.time()
    with open(pickle_path, 'wb') as f:
        pickle.dump(df, f)
    pickle_write_time = time.time() - start_time
    
    pickle_size_mb = os.path.getsize(pickle_path) / (1024 * 1024)
    
    start_time = time.time()
    with open(pickle_path, 'rb') as f:
        df_pickle = pickle.load(f)
    pickle_read_time = time.time() - start_time
    
    results.append({
        'Format': 'Pickle',
        'Write Time (s)': pickle_write_time,
        'Read Time (s)': pickle_read_time,
        'File Size (MB)': pickle_size_mb,
        'Compression Ratio': df_size_mb / pickle_size_mb
    })
    
    # 2. CSV
    csv_path = os.path.join(temp_dir, "data.csv")
    
    start_time = time.time()
    df.to_csv(csv_path, index=False)
    csv_write_time = time.time() - start_time
    
    csv_size_mb = os.path.getsize(csv_path) / (1024 * 1024)
    
    start_time = time.time()
    df_csv = pd.read_csv(csv_path)
    csv_read_time = time.time() - start_time
    
    results.append({
        'Format': 'CSV',
        'Write Time (s)': csv_write_time,
        'Read Time (s)': csv_read_time,
        'File Size (MB)': csv_size_mb,
        'Compression Ratio': df_size_mb / csv_size_mb
    })
    
    # 3. JSON
    json_path = os.path.join(temp_dir, "data.json")
    
    start_time = time.time()
    df.to_json(json_path, orient="records", lines=True)
    json_write_time = time.time() - start_time
    
    json_size_mb = os.path.getsize(json_path) / (1024 * 1024)
    
    start_time = time.time()
    df_json = pd.read_json(json_path, lines=True)
    json_read_time = time.time() - start_time
    
    results.append({
        'Format': 'JSON',
        'Write Time (s)': json_write_time,
        'Read Time (s)': json_read_time,
        'File Size (MB)': json_size_mb,
        'Compression Ratio': df_size_mb / json_size_mb
    })
    
    # 4. Parquet (via pandas)
    parquet_pandas_path = os.path.join(temp_dir, "data_pandas.parquet")
    
    start_time = time.time()
    df.to_parquet(parquet_pandas_path)
    parquet_pandas_write_time = time.time() - start_time
    
    parquet_pandas_size_mb = os.path.getsize(parquet_pandas_path) / (1024 * 1024)
    
    start_time = time.time()
    df_parquet_pandas = pd.read_parquet(parquet_pandas_path)
    parquet_pandas_read_time = time.time() - start_time
    
    results.append({
        'Format': 'Parquet (pandas)',
        'Write Time (s)': parquet_pandas_write_time,
        'Read Time (s)': parquet_pandas_read_time,
        'File Size (MB)': parquet_pandas_size_mb,
        'Compression Ratio': df_size_mb / parquet_pandas_size_mb
    })
    
    # 5. Parquet (via Arrow)
    parquet_arrow_path = os.path.join(temp_dir, "data_arrow.parquet")
    
    start_time = time.time()
    table = convert_pandas_to_arrow(df)
    pq.write_table(table, parquet_arrow_path)
    parquet_arrow_write_time = time.time() - start_time
    
    parquet_arrow_size_mb = os.path.getsize(parquet_arrow_path) / (1024 * 1024)
    
    start_time = time.time()
    table = pq.read_table(parquet_arrow_path)
    df_parquet_arrow = convert_arrow_to_pandas(table)
    parquet_arrow_read_time = time.time() - start_time
    
    results.append({
        'Format': 'Parquet (Arrow)',
        'Write Time (s)': parquet_arrow_write_time,
        'Read Time (s)': parquet_arrow_read_time,
        'File Size (MB)': parquet_arrow_size_mb,
        'Compression Ratio': df_size_mb / parquet_arrow_size_mb
    })
    
    # 6. Arrow IPC
    arrow_path = os.path.join(temp_dir, "data.arrow")
    
    start_time = time.time()
    table = convert_pandas_to_arrow(df)
    with pa.OSFile(arrow_path, 'wb') as sink:
        writer = pa.RecordBatchFileWriter(sink, table.schema)
        writer.write_table(table)
        writer.close()
    arrow_write_time = time.time() - start_time
    
    arrow_size_mb = os.path.getsize(arrow_path) / (1024 * 1024)
    
    start_time = time.time()
    with pa.memory_map(arrow_path, 'rb') as source:
        reader = pa.ipc.open_file(source)
        table = reader.read_all()
    df_arrow = convert_arrow_to_pandas(table)
    arrow_read_time = time.time() - start_time
    
    results.append({
        'Format': 'Arrow IPC',
        'Write Time (s)': arrow_write_time,
        'Read Time (s)': arrow_read_time,
        'File Size (MB)': arrow_size_mb,
        'Compression Ratio': df_size_mb / arrow_size_mb
    })
    
    return results

def benchmark_operations(df):
    """Benchmark de operações.
    
    Args:
        df: DataFrame para benchmark.
        
    Returns:
        list: Resultados do benchmark.
    """
    results = []
    
    # 1. Filtrar linhas
    start_time = time.time()
    filtered_df = df[df['value_a'] > 0.5]
    pandas_filter_time = time.time() - start_time
    
    start_time = time.time()
    table = convert_pandas_to_arrow(df)
    mask = pa.compute.greater(table['value_a'], 0.5)
    filtered_table = table.filter(mask)
    arrow_filter_time = time.time() - start_time
    
    results.append({
        'Operation': 'Filter rows',
        'Pandas Time (s)': pandas_filter_time,
        'Arrow Time (s)': arrow_filter_time,
        'Speedup': pandas_filter_time / arrow_filter_time
    })
    
    # 2. Selecionar colunas
    start_time = time.time()
    selected_df = df[['id', 'value_a', 'value_b']]
    pandas_select_time = time.time() - start_time
    
    start_time = time.time()
    table = convert_pandas_to_arrow(df)
    selected_table = table.select(['id', 'value_a', 'value_b'])
    arrow_select_time = time.time() - start_time
    
    results.append({
        'Operation': 'Select columns',
        'Pandas Time (s)': pandas_select_time,
        'Arrow Time (s)': arrow_select_time,
        'Speedup': pandas_select_time / arrow_select_time
    })
    
    # 3. Calcular estatísticas
    start_time = time.time()
    mean_a = df['value_a'].mean()
    mean_b = df['value_b'].mean()
    std_a = df['value_a'].std()
    std_b = df['value_b'].std()
    pandas_stats_time = time.time() - start_time
    
    start_time = time.time()
    table = convert_pandas_to_arrow(df)
    mean_a = pa.compute.mean(table['value_a']).as_py()
    mean_b = pa.compute.mean(table['value_b']).as_py()
    # Arrow não tem std diretamente, então usamos variância e raiz quadrada
    var_a = pa.compute.variance(table['value_a']).as_py()
    var_b = pa.compute.variance(table['value_b']).as_py()
    std_a = np.sqrt(var_a)
    std_b = np.sqrt(var_b)
    arrow_stats_time = time.time() - start_time
    
    results.append({
        'Operation': 'Calculate statistics',
        'Pandas Time (s)': pandas_stats_time,
        'Arrow Time (s)': arrow_stats_time,
        'Speedup': pandas_stats_time / arrow_stats_time
    })
    
    # 4. Agrupar e agregar
    start_time = time.time()
    grouped_df = df.groupby('category').agg({'value_a': 'mean', 'value_b': 'sum'})
    pandas_group_time = time.time() - start_time
    
    # Arrow não tem API de agrupamento direta, então convertemos para pandas
    start_time = time.time()
    table = convert_pandas_to_arrow(df)
    df_arrow = convert_arrow_to_pandas(table)
    grouped_df_arrow = df_arrow.groupby('category').agg({'value_a': 'mean', 'value_b': 'sum'})
    arrow_group_time = time.time() - start_time
    
    results.append({
        'Operation': 'Group and aggregate',
        'Pandas Time (s)': pandas_group_time,
        'Arrow Time (s)': arrow_group_time,
        'Speedup': pandas_group_time / arrow_group_time
    })
    
    return results

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Benchmark do Apache Arrow")
    parser.add_argument("--size", type=int, default=1000000, help="Número de linhas de dados")
    
    args = parser.parse_args()
    
    print(f"Iniciando benchmark com {args.size} linhas...")
    
    # Gerar dados
    start_time = time.time()
    df = generate_data(args.size)
    print(f"Dados gerados em {time.time() - start_time:.2f} segundos")
    
    # Criar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        # Benchmark de serialização
        print("\nExecutando benchmark de serialização/desserialização...")
        serialization_results = benchmark_serialization(df, temp_dir)
        
        # Benchmark de operações
        print("\nExecutando benchmark de operações...")
        operations_results = benchmark_operations(df)
        
        # Exibir resultados
        print("\nResultados do benchmark de serialização/desserialização:")
        print(tabulate(serialization_results, headers="keys", tablefmt="grid"))
        
        print("\nResultados do benchmark de operações:")
        print(tabulate(operations_results, headers="keys", tablefmt="grid"))

if __name__ == "__main__":
    main()
```

### Passo 6: Implementar Testes Unitários

Crie testes unitários em `tests/test_arrow_utils.py`:

```python
import unittest
import os
import tempfile
import numpy as np
import pandas as pd
import pyarrow as pa

from src.utils.arrow_utils import (
    convert_pandas_to_arrow,
    convert_arrow_to_pandas,
    filter_arrow_table,
    aggregate_arrow_table,
    join_arrow_tables,
    save_arrow_table,
    load_arrow_table,
    create_arrow_ipc_stream,
    read_arrow_ipc_stream
)

class TestArrowUtils(unittest.TestCase):
    
    def setUp(self):
        # Criar dados de teste
        self.df = pd.DataFrame({
            'id': range(100),
            'value': np.random.rand(100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        # Converter para tabela Arrow
        self.table = convert_pandas_to_arrow(self.df)
        
        # Criar diretório temporário para testes
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        # Limpar diretório temporário
        self.temp_dir.cleanup()
    
    def test_convert_pandas_to_arrow(self):
        """Testa a conversão de pandas para Arrow."""
        # Verificar se a conversão mantém o número de linhas e colunas
        self.assertEqual(len(self.table), len(self.df))
        self.assertEqual(len(self.table.column_names), len(self.df.columns))
        
        # Verificar se os nomes das colunas são preservados
        for col in self.df.columns:
            self.assertIn(col, self.table.column_names)
    
    def test_convert_arrow_to_pandas(self):
        """Testa a conversão de Arrow para pandas."""
        # Converter de volta para pandas
        df2 = convert_arrow_to_pandas(self.table)
        
        # Verificar se a conversão mantém o número de linhas e colunas
        self.assertEqual(len(df2), len(self.df))
        self.assertEqual(len(df2.columns), len(self.df.columns))
        
        # Verificar se os valores são preservados
        pd.testing.assert_frame_equal(df2, self.df)
    
    def test_filter_arrow_table(self):
        """Testa a filtragem de tabela Arrow."""
        # Filtrar linhas com value > 0.5
        filtered_table = filter_arrow_table(self.table, 'value', '>', 0.5)
        
        # Converter para pandas para verificação
        filtered_df = convert_arrow_to_pandas(filtered_table)
        
        # Verificar se o filtro foi aplicado corretamente
        self.assertTrue(all(filtered_df['value'] > 0.5))
        
        # Verificar se o número de linhas é consistente
        expected_count = len(self.df[self.df['value'] > 0.5])
        self.assertEqual(len(filtered_table), expected_count)
    
    def test_join_arrow_tables(self):
        """Testa a junção de tabelas Arrow."""
        # Criar segunda tabela
        df2 = pd.DataFrame({
            'id': range(50, 150),  # Sobreposição parcial com a primeira tabela
            'extra_value': np.random.rand(100)
        })
        table2 = convert_pandas_to_arrow(df2)
        
        # Junção inner
        joined_table = join_arrow_tables(self.table, table2, 'id', 'inner')
        joined_df = convert_arrow_to_pandas(joined_table)
        
        # Verificar se a junção tem o número correto de linhas
        expected_count = len(set(self.df['id']).intersection(set(df2['id'])))
        self.assertEqual(len(joined_table), expected_count)
        
        # Verificar se todas as colunas estão presentes
        self.assertIn('value', joined_df.columns)
        self.assertIn('category', joined_df.columns)
        self.assertIn('extra_value', joined_df.columns)
    
    def test_save_and_load_arrow_table(self):
        """Testa o salvamento e carregamento de tabela Arrow."""
        # Testar cada formato
        for format in ['parquet', 'csv', 'json', 'arrow']:
            # Caminho para o arquivo
            filepath = os.path.join(self.temp_dir.name, f"test_data.{format}")
            
            # Salvar tabela
            saved_path = save_arrow_table(self.table, filepath, format=format)
            
            # Verificar se o arquivo foi criado
            self.assertTrue(os.path.exists(saved_path))
            
            # Carregar tabela
            loaded_table = load_arrow_table(saved_path)
            
            # Verificar se a tabela carregada tem o mesmo número de linhas
            self.assertEqual(len(loaded_table), len(self.table))
            
            # Verificar se todas as colunas estão presentes
            for col in self.table.column_names:
                self.assertIn(col, loaded_table.column_names)
    
    def test_arrow_ipc_stream(self):
        """Testa a serialização e desserialização via IPC Arrow."""
        # Criar stream IPC
        ipc_stream = create_arrow_ipc_stream(self.table)
        
        # Verificar se o stream é bytes
        self.assertIsInstance(ipc_stream, bytes)
        
        # Ler stream IPC
        loaded_table = read_arrow_ipc_stream(ipc_stream)
        
        # Verificar se a tabela carregada tem o mesmo número de linhas
        self.assertEqual(len(loaded_table), len(self.table))
        
        # Verificar se todas as colunas estão presentes
        for col in self.table.column_names:
            self.assertIn(col, loaded_table.column_names)

if __name__ == '__main__':
    unittest.main()
```

### Passo 7: Documentação e Melhores Práticas

Crie um arquivo de documentação em `docs/arrow_usage.md`:

```markdown
# Uso do Apache Arrow no Autocura

Este documento descreve a implementação e uso do Apache Arrow no sistema Autocura para processamento de dados de alto desempenho.

## Visão Geral

O Apache Arrow é uma especificação de formato de memória para dados colunares que permite processamento eficiente e transferência de dados entre diferentes sistemas e linguagens de programação. No Autocura, o Arrow é utilizado para:

1. Exportação e importação de métricas de alta performance
2. Transferência eficiente de dados entre processos
3. Processamento analítico de grandes volumes de dados
4. Interoperabilidade com outras ferramentas do ecossistema de dados

## Componentes Principais

1. **MetricsExporter**: Classe para exportar métricas do sistema em formatos otimizados.
2. **Arrow Utils**: Utilitários para processamento de dados com Arrow.
3. **IPC (Inter-Process Communication)**: Mecanismos para transferência eficiente de dados entre processos.

## Formatos de Dados Suportados

O sistema suporta os seguintes formatos para persistência de dados:

1. **Parquet**: Formato colunar otimizado para armazenamento e consulta.
2. **Arrow IPC**: Formato binário para transferência de dados entre processos.
3. **CSV**: Formato texto para interoperabilidade com outras ferramentas.
4. **JSON**: Formato texto para interoperabilidade e legibilidade humana.

## Casos de Uso

### Exportação de Métricas

```python
from src.conscienciaSituacional.monitoramento.metrics_exporter import MetricsExporter

# Criar exportador
exporter = MetricsExporter(format="parquet", compression="snappy")

# Exportar métricas
metrics_data = [
    {"timestamp": "2023-01-01T00:00:00", "metric": "cpu_usage", "value": 0.75},
    {"timestamp": "2023-01-01T00:01:00", "metric": "cpu_usage", "value": 0.80},
    # ...
]
filepath = exporter.export_metrics(metrics_data, name="system_metrics")

# Importar métricas
df = exporter.import_metrics(filepath)
```

### Processamento de Dados com Arrow

```python
from src.utils.arrow_utils import filter_arrow_table, join_arrow_tables
import pyarrow as pa

# Carregar tabelas
table1 = pa.Table.from_pandas(df1)
table2 = pa.Table.from_pandas(df2)

# Filtrar dados
filtered_table = filter_arrow_table(table1, 'value', '>', 0.5)

# Juntar tabelas
joined_table = join_arrow_tables(filtered_table, table2, 'id', 'inner')

# Converter para pandas para análise
result_df = joined_table.to_pandas()
```

### Transferência de Dados entre Processos

```python
from src.utils.arrow_utils import create_arrow_ipc_stream, read_arrow_ipc_stream
from multiprocessing import Process, Queue

# No processo produtor
table = pa.Table.from_pandas(df)
ipc_stream = create_arrow_ipc_stream(table)
queue.put(ipc_stream)

# No processo consumidor
ipc_stream = queue.get()
table = read_arrow_ipc_stream(ipc_stream)
df = table.to_pandas()
```

## Melhores Práticas

1. **Formato de Armazenamento**: Use Parquet para armazenamento persistente de dados.
2. **Transferência de Dados**: Use Arrow IPC para transferência entre processos.
3. **Memória**: Para grandes conjuntos de dados, mantenha-os em formato Arrow o máximo possível.
4. **Conversão**: Minimize conversões entre Arrow e pandas; faça operações em Arrow quando possível.
5. **Compressão**: Use compressão Snappy para equilíbrio entre velocidade e tamanho.

## Benchmarks

Os benchmarks mostram que o Apache Arrow oferece vantagens significativas em:

1. **Velocidade de Leitura/Escrita**: 2-10x mais rápido que formatos tradicionais.
2. **Eficiência de Armazenamento**: Arquivos 30-50% menores que CSV.
3. **Processamento**: Operações de filtragem e seleção 2-5x mais rápidas.
4. **Transferência entre Processos**: 3-8x mais rápido que pickle para grandes conjuntos de dados.

## Referências

- [Documentação Apache Arrow](https://arrow.apache.org/docs/)
- [PyArrow API](https://arrow.apache.org/docs/python/)
- [Formato Parquet](https://parquet.apache.org/)
- [Arrow vs. Pandas Performance](https://wesmckinney.com/blog/apache-arrow-pandas-internals/)
```

### Considerações Finais para Apache Arrow

- **Requisitos de Memória**: Arrow mantém dados em memória em formato colunar, o que pode aumentar o uso de memória para conjuntos de dados muito grandes.
- **Curva de Aprendizado**: A API do Arrow é mais complexa que pandas; comece com operações simples e evolua gradualmente.
- **Interoperabilidade**: Arrow é especialmente valioso quando você precisa integrar com outras ferramentas e linguagens.
- **Operações Ausentes**: Algumas operações comuns em pandas (como groupby) não têm equivalentes diretos em Arrow; nesses casos, converta para pandas.
- **Evolução Rápida**: O ecossistema Arrow evolui rapidamente; verifique a documentação para novos recursos e melhorias.

## 6. Implementação do MLflow para Rastreamento de Experimentos e Modelos

### Contexto no Autocura
O MLflow será utilizado no sistema Autocura para rastrear experimentos, versionar modelos e gerenciar o ciclo de vida de modelos de machine learning, especialmente no módulo de validação (`backtester.py`), permitindo comparar diferentes abordagens e manter um registro histórico de experimentos.

### Passo 1: Instalação e Configuração

```bash
# Ativar ambiente virtual
source autocura-env/bin/activate

# Instalar MLflow e dependências
pip install mlflow==2.3.1
pip install sqlalchemy  # Para backend de banco de dados
pip install boto3       # Para armazenamento em S3 (opcional)
pip install azure-storage-blob  # Para armazenamento no Azure (opcional)

# Dependências adicionais para integração com frameworks
pip install scikit-learn  # Para integração com scikit-learn
```

### Passo 2: Configurar o Servidor MLflow

Crie um script para iniciar o servidor MLflow em `scripts/start_mlflow_server.py`:

```python
#!/usr/bin/env python3
"""Script para iniciar o servidor MLflow."""

import os
import argparse
import subprocess
import sys

def main():
    """Função principal para iniciar o servidor MLflow."""
    parser = argparse.ArgumentParser(description="Iniciar servidor MLflow")
    parser.add_argument("--host", default="0.0.0.0", help="Host para o servidor")
    parser.add_argument("--port", type=int, default=5000, help="Porta para o servidor")
    parser.add_argument("--backend-store-uri", default="sqlite:///mlflow.db",
                        help="URI para o backend de armazenamento")
    parser.add_argument("--default-artifact-root", default="./mlruns",
                        help="Diretório raiz para artefatos")
    
    args = parser.parse_args()
    
    # Criar diretório para artefatos se não existir
    os.makedirs(args.default_artifact_root, exist_ok=True)
    
    # Construir comando
    cmd = [
        "mlflow", "server",
        "--host", args.host,
        "--port", str(args.port),
        "--backend-store-uri", args.backend_store_uri,
        "--default-artifact-root", args.default_artifact_root
    ]
    
    print(f"Iniciando servidor MLflow com comando: {' '.join(cmd)}")
    
    # Iniciar servidor
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nServidor MLflow encerrado.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao iniciar servidor MLflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Passo 3: Implementar Wrapper para Rastreamento de Experimentos

Crie um arquivo `src/validation/mlflow_tracker.py`:

```python
"""
Wrapper para rastreamento de experimentos com MLflow.
"""

import os
import mlflow
import mlflow.pytorch
import mlflow.tensorflow
import mlflow.sklearn
import logging
from typing import Dict, List, Any, Optional, Union
import numpy as np
import pandas as pd
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLflowExperimentTracker:
    """Wrapper para rastreamento de experimentos com MLflow."""
    
    def __init__(self, experiment_name: str, tracking_uri: Optional[str] = None):
        """Inicializa o rastreador de experimentos.
        
        Args:
            experiment_name: Nome do experimento.
            tracking_uri: URI para o servidor MLflow (opcional).
        """
        self.experiment_name = experiment_name
        
        # Configurar URI de rastreamento
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        
        # Obter ou criar experimento
        try:
            self.experiment = mlflow.get_experiment_by_name(experiment_name)
            if not self.experiment:
                self.experiment_id = mlflow.create_experiment(experiment_name)
                self.experiment = mlflow.get_experiment(self.experiment_id)
            else:
                self.experiment_id = self.experiment.experiment_id
            
            logger.info(f"Experimento '{experiment_name}' configurado com ID: {self.experiment_id}")
        except Exception as e:
            logger.error(f"Erro ao configurar experimento: {e}")
            raise
    
    def start_run(self, run_name: Optional[str] = None, 
                 nested: bool = False) -> mlflow.ActiveRun:
        """Inicia uma execução de experimento.
        
        Args:
            run_name: Nome da execução (opcional).
            nested: Se True, permite execuções aninhadas.
            
        Returns:
            mlflow.ActiveRun: Contexto de execução ativa.
        """
        return mlflow.start_run(
            experiment_id=self.experiment_id,
            run_name=run_name,
            nested=nested
        )
    
    def log_param(self, key: str, value: Any):
        """Registra um parâmetro.
        
        Args:
            key: Nome do parâmetro.
            value: Valor do parâmetro.
        """
        mlflow.log_param(key, value)
    
    def log_params(self, params: Dict[str, Any]):
        """Registra múltiplos parâmetros.
        
        Args:
            params: Dicionário de parâmetros.
        """
        mlflow.log_params(params)
    
    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        """Registra uma métrica.
        
        Args:
            key: Nome da métrica.
            value: Valor da métrica.
            step: Passo da métrica (opcional).
        """
        mlflow.log_metric(key, value, step=step)
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Registra múltiplas métricas.
        
        Args:
            metrics: Dicionário de métricas.
            step: Passo das métricas (opcional).
        """
        mlflow.log_metrics(metrics, step=step)
    
    def log_artifact(self, local_path: str):
        """Registra um artefato.
        
        Args:
            local_path: Caminho local para o artefato.
        """
        mlflow.log_artifact(local_path)
    
    def log_dict(self, dictionary: Dict[str, Any], artifact_file: str):
        """Registra um dicionário como artefato JSON.
        
        Args:
            dictionary: Dicionário a ser registrado.
            artifact_file: Nome do arquivo de artefato.
        """
        mlflow.log_dict(dictionary, artifact_file)
    
    def log_figure(self, figure, artifact_file: str):
        """Registra uma figura como artefato.
        
        Args:
            figure: Figura matplotlib ou plotly.
            artifact_file: Nome do arquivo de artefato.
        """
        mlflow.log_figure(figure, artifact_file)
    
    def log_model(self, model: Any, artifact_path: str, 
                 framework: str = "pytorch", **kwargs):
        """Registra um modelo.
        
        Args:
            model: Modelo a ser registrado.
            artifact_path: Caminho para o artefato.
            framework: Framework do modelo ('pytorch', 'tensorflow', 'sklearn').
            **kwargs: Argumentos adicionais para o registrador de modelo.
        """
        if framework.lower() == "pytorch":
            mlflow.pytorch.log_model(model, artifact_path, **kwargs)
        elif framework.lower() == "tensorflow":
            mlflow.tensorflow.log_model(model, artifact_path, **kwargs)
        elif framework.lower() == "sklearn":
            mlflow.sklearn.log_model(model, artifact_path, **kwargs)
        else:
            logger.warning(f"Framework '{framework}' não suportado diretamente. Usando log_model genérico.")
            mlflow.pyfunc.log_model(artifact_path, python_model=model, **kwargs)
    
    def end_run(self, status: str = "FINISHED"):
        """Finaliza a execução atual.
        
        Args:
            status: Status da execução ('FINISHED', 'FAILED', 'KILLED').
        """
        mlflow.end_run(status=status)
    
    def get_tracking_uri(self) -> str:
        """Obtém a URI de rastreamento.
        
        Returns:
            str: URI de rastreamento.
        """
        return mlflow.get_tracking_uri()
    
    def get_artifact_uri(self) -> str:
        """Obtém a URI de artefatos para a execução atual.
        
        Returns:
            str: URI de artefatos.
        """
        return mlflow.get_artifact_uri()
    
    def search_runs(self, filter_string: str = "", 
                   max_results: int = 100) -> pd.DataFrame:
        """Busca execuções no experimento atual.
        
        Args:
            filter_string: String de filtro no formato "param.key = 'value'".
            max_results: Número máximo de resultados.
            
        Returns:
            pd.DataFrame: DataFrame com as execuções.
        """
        runs = mlflow.search_runs(
            experiment_ids=[self.experiment_id],
            filter_string=filter_string,
            max_results=max_results
        )
        return runs
    
    def get_best_run(self, metric_name: str, ascending: bool = False) -> Dict[str, Any]:
        """Obtém a melhor execução com base em uma métrica.
        
        Args:
            metric_name: Nome da métrica para ordenação.
            ascending: Se True, ordena em ordem crescente (menor é melhor).
            
        Returns:
            Dict: Informações da melhor execução.
        """
        metric_col = f"metrics.{metric_name}"
        
        runs = self.search_runs()
        if runs.empty:
            logger.warning(f"Nenhuma execução encontrada para o experimento '{self.experiment_name}'")
            return {}
        
        if metric_col not in runs.columns:
            logger.warning(f"Métrica '{metric_name}' não encontrada nas execuções")
            return {}
        
        # Ordenar execuções pela métrica
        sorted_runs = runs.sort_values(by=metric_col, ascending=ascending)
        
        if sorted_runs.empty:
            return {}
        
        best_run = sorted_runs.iloc[0]
        
        # Extrair parâmetros e métricas
        params = {k.replace("params.", ""): v for k, v in best_run.items() if k.startswith("params.")}
        metrics = {k.replace("metrics.", ""): v for k, v in best_run.items() if k.startswith("metrics.")}
        
        return {
            "run_id": best_run.run_id,
            "params": params,
            "metrics": metrics,
            "artifact_uri": best_run.artifact_uri,
            "start_time": best_run.start_time,
            "end_time": best_run.end_time
        }
    
    def load_model(self, run_id: str, artifact_path: str, 
                  framework: str = "pytorch") -> Any:
        """Carrega um modelo registrado.
        
        Args:
            run_id: ID da execução.
            artifact_path: Caminho do artefato.
            framework: Framework do modelo ('pytorch', 'tensorflow', 'sklearn').
            
        Returns:
            Any: Modelo carregado.
        """
        if framework.lower() == "pytorch":
            return mlflow.pytorch.load_model(f"runs:/{run_id}/{artifact_path}")
        elif framework.lower() == "tensorflow":
            return mlflow.tensorflow.load_model(f"runs:/{run_id}/{artifact_path}")
        elif framework.lower() == "sklearn":
            return mlflow.sklearn.load_model(f"runs:/{run_id}/{artifact_path}")
        else:
            logger.warning(f"Framework '{framework}' não suportado diretamente. Usando load_model genérico.")
            return mlflow.pyfunc.load_model(f"runs:/{run_id}/{artifact_path}")
```

### Passo 4: Integrar MLflow com o Backtester

Modifique o arquivo `src/validation/backtester.py` para usar MLflow:

```python
"""
Módulo para backtesting e validação de modelos.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
import json

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar o rastreador de experimentos
from .mlflow_tracker import MLflowExperimentTracker

class Backtester:
    """Classe para backtesting e validação de modelos."""
    
    def __init__(self, model_name: str, tracking_uri: Optional[str] = None):
        """Inicializa o backtester.
        
        Args:
            model_name: Nome do modelo para rastreamento.
            tracking_uri: URI para o servidor MLflow (opcional).
        """
        self.model_name = model_name
        
        # Inicializar rastreador de experimentos
        self.tracker = MLflowExperimentTracker(
            experiment_name=f"backtesting_{model_name}",
            tracking_uri=tracking_uri
        )
        
        logger.info(f"Backtester inicializado para modelo '{model_name}'")
    
    def run_backtest(self, model: Any, data: pd.DataFrame, 
                    target_col: str, feature_cols: List[str],
                    test_size: float = 0.2, random_state: int = 42,
                    model_params: Optional[Dict[str, Any]] = None,
                    framework: str = "pytorch") -> Dict[str, Any]:
        """Executa um backtest para um modelo.
        
        Args:
            model: Modelo a ser testado.
            data: DataFrame com os dados.
            target_col: Nome da coluna alvo.
            feature_cols: Lista de nomes das colunas de features.
            test_size: Proporção dos dados para teste.
            random_state: Semente aleatória para reprodutibilidade.
            model_params: Parâmetros do modelo (opcional).
            framework: Framework do modelo ('pytorch', 'tensorflow', 'sklearn').
            
        Returns:
            Dict: Resultados do backtest.
        """
        # Preparar dados
        from sklearn.model_selection import train_test_split
        
        X = data[feature_cols].values
        y = data[target_col].values
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Iniciar execução do MLflow
        run_name = f"{self.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with self.tracker.start_run(run_name=run_name):
            # Registrar parâmetros
            self.tracker.log_param("test_size", test_size)
            self.tracker.log_param("random_state", random_state)
            self.tracker.log_param("feature_columns", feature_cols)
            self.tracker.log_param("target_column", target_col)
            
            if model_params:
                self.tracker.log_params(model_params)
            
            # Treinar modelo (implementação genérica, adaptar conforme necessário)
            try:
                if framework.lower() == "pytorch":
                    # Implementação para PyTorch
                    import torch
                    
                    # Converter dados para tensores
                    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
                    y_train_tensor = torch.tensor(y_train, dtype=torch.float32)
                    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
                    y_test_tensor = torch.tensor(y_test, dtype=torch.float32)
                    
                    # Treinar modelo
                    model.train()
                    # ... código de treinamento específico para PyTorch ...
                    
                    # Avaliar modelo
                    model.eval()
                    with torch.no_grad():
                        y_pred = model(X_test_tensor).numpy()
                    
                elif framework.lower() == "tensorflow":
                    # Implementação para TensorFlow
                    import tensorflow as tf
                    
                    # Treinar modelo
                    model.fit(X_train, y_train, epochs=10, verbose=0)
                    
                    # Avaliar modelo
                    y_pred = model.predict(X_test)
                    
                else:  # sklearn e outros
                    # Implementação para scikit-learn
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calcular métricas
                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Registrar métricas
                metrics = {
                    "mse": mse,
                    "rmse": rmse,
                    "mae": mae,
                    "r2": r2
                }
                self.tracker.log_metrics(metrics)
                
                # Criar gráfico de previsão vs. real
                plt.figure(figsize=(10, 6))
                plt.scatter(y_test, y_pred, alpha=0.5)
                plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
                plt.xlabel('Valores Reais')
                plt.ylabel('Previsões')
                plt.title('Previsão vs. Real')
                
                # Salvar figura temporariamente
                fig_path = f"/tmp/{run_name}_prediction_plot.png"
                plt.savefig(fig_path)
                plt.close()
                
                # Registrar figura
                self.tracker.log_artifact(fig_path)
                
                # Registrar modelo
                self.tracker.log_model(model, "model", framework=framework)
                
                # Limpar arquivo temporário
                os.remove(fig_path)
                
                # Retornar resultados
                results = {
                    "run_id": mlflow.active_run().info.run_id,
                    "metrics": metrics,
                    "artifact_uri": self.tracker.get_artifact_uri()
                }
                
                logger.info(f"Backtest concluído com sucesso. MSE: {mse:.4f}, R²: {r2:.4f}")
                return results
                
            except Exception as e:
                logger.error(f"Erro durante o backtest: {e}")
                self.tracker.end_run(status="FAILED")
                raise
    
    def compare_models(self, models: List[Dict[str, Any]], 
                      data: pd.DataFrame, target_col: str, 
                      feature_cols: List[str]) -> pd.DataFrame:
        """Compara múltiplos modelos.
        
        Args:
            models: Lista de dicionários com modelos e parâmetros.
                Cada dicionário deve ter as chaves 'model', 'name', 'params' e 'framework'.
            data: DataFrame com os dados.
            target_col: Nome da coluna alvo.
            feature_cols: Lista de nomes das colunas de features.
            
        Returns:
            pd.DataFrame: DataFrame com os resultados da comparação.
        """
        results = []
        
        for model_info in models:
            model = model_info['model']
            name = model_info['name']
            params = model_info.get('params', {})
            framework = model_info.get('framework', 'sklearn')
            
            logger.info(f"Executando backtest para modelo '{name}'")
            
            try:
                result = self.run_backtest(
                    model=model,
                    data=data,
                    target_col=target_col,
                    feature_cols=feature_cols,
                    model_params=params,
                    framework=framework
                )
                
                # Adicionar informações do modelo
                result['model_name'] = name
                result['framework'] = framework
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Erro ao testar modelo '{name}': {e}")
        
        # Converter resultados para DataFrame
        if not results:
            return pd.DataFrame()
        
        # Extrair métricas para o DataFrame
        df_results = []
        for result in results:
            row = {
                'model_name': result['model_name'],
                'framework': result['framework'],
                'run_id': result['run_id']
            }
            row.update(result['metrics'])
            df_results.append(row)
        
        return pd.DataFrame(df_results)
    
    def load_best_model(self, metric_name: str = "rmse", 
                       ascending: bool = True) -> Tuple[Any, Dict[str, Any]]:
        """Carrega o melhor modelo com base em uma métrica.
        
        Args:
            metric_name: Nome da métrica para ordenação.
            ascending: Se True, ordena em ordem crescente (menor é melhor).
            
        Returns:
            Tuple: (modelo, informações da execução)
        """
        # Obter a melhor execução
        best_run = self.tracker.get_best_run(metric_name, ascending)
        
        if not best_run:
            logger.warning("Nenhuma execução encontrada")
            return None, {}
        
        # Carregar o modelo
        try:
            # Determinar o framework com base nos parâmetros
            framework = best_run.get('params', {}).get('framework', 'pytorch')
            
            model = self.tracker.load_model(
                run_id=best_run['run_id'],
                artifact_path="model",
                framework=framework
            )
            
            logger.info(f"Modelo carregado da execução {best_run['run_id']}")
            return model, best_run
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo: {e}")
            return None, best_run
```

### Passo 5: Criar Exemplo de Uso com PyTorch

Crie um exemplo em `examples/mlflow_pytorch_example.py`:

```python
#!/usr/bin/env python3
"""
Exemplo de uso do MLflow com PyTorch.
"""

import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
import argparse

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.validation.mlflow_tracker import MLflowExperimentTracker

# Definir modelo PyTorch
class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

def generate_data(n_samples=1000, n_features=10, noise=0.1):
    """Gera dados sintéticos.
    
    Args:
        n_samples: Número de amostras.
        n_features: Número de features.
        noise: Nível de ruído.
        
    Returns:
        tuple: (X, y) arrays numpy.
    """
    # Gerar coeficientes aleatórios
    true_weights = np.random.randn(n_features)
    
    # Gerar features
    X = np.random.randn(n_samples, n_features)
    
    # Gerar target com ruído
    y = X.dot(true_weights) + noise * np.random.randn(n_samples)
    
    return X, y

def train_model(model, X_train, y_train, X_val, y_val, 
               epochs=100, batch_size=32, learning_rate=0.01, 
               tracker=None, log_every=10):
    """Treina o modelo PyTorch.
    
    Args:
        model: Modelo PyTorch.
        X_train: Features de treino.
        y_train: Target de treino.
        X_val: Features de validação.
        y_val: Target de validação.
        epochs: Número de épocas.
        batch_size: Tamanho do batch.
        learning_rate: Taxa de aprendizado.
        tracker: Rastreador MLflow (opcional).
        log_every: Frequência de logging.
        
    Returns:
        dict: Histórico de treinamento.
    """
    # Converter para tensores
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
    X_val_tensor = torch.FloatTensor(X_val)
    y_val_tensor = torch.FloatTensor(y_val).unsqueeze(1)
    
    # Criar datasets e dataloaders
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    # Definir otimizador e função de perda
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    
    # Histórico de treinamento
    history = {
        'train_loss': [],
        'val_loss': []
    }
    
    # Treinar modelo
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        
        for inputs, targets in train_loader:
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            # Backward pass e otimização
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Calcular perda média de treino
        train_loss /= len(train_loader)
        history['train_loss'].append(train_loss)
        
        # Avaliar no conjunto de validação
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_tensor)
            val_loss = criterion(val_outputs, y_val_tensor).item()
            history['val_loss'].append(val_loss)
        
        # Registrar métricas no MLflow
        if tracker and epoch % log_every == 0:
            tracker.log_metrics({
                'train_loss': train_loss,
                'val_loss': val_loss
            }, step=epoch)
        
        # Imprimir progresso
        if epoch % log_every == 0:
            print(f"Época {epoch}/{epochs}, Perda Treino: {train_loss:.4f}, Perda Val: {val_loss:.4f}")
    
    return history

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Exemplo de MLflow com PyTorch")
    parser.add_argument("--tracking-uri", default="http://localhost:5000",
                        help="URI para o servidor MLflow")
    parser.add_argument("--experiment-name", default="pytorch_regression",
                        help="Nome do experimento")
    parser.add_argument("--epochs", type=int, default=100,
                        help="Número de épocas")
    parser.add_argument("--hidden-size", type=int, default=64,
                        help="Tamanho da camada oculta")
    parser.add_argument("--learning-rate", type=float, default=0.01,
                        help="Taxa de aprendizado")
    
    args = parser.parse_args()
    
    # Gerar dados
    X, y = generate_data(n_samples=1000, n_features=10, noise=0.1)
    
    # Dividir em treino e validação
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Inicializar rastreador MLflow
    tracker = MLflowExperimentTracker(
        experiment_name=args.experiment_name,
        tracking_uri=args.tracking_uri
    )
    
    # Iniciar execução
    with tracker.start_run(run_name=f"nn_h{args.hidden_size}_lr{args.learning_rate}"):
        # Registrar parâmetros
        params = {
            'hidden_size': args.hidden_size,
            'learning_rate': args.learning_rate,
            'epochs': args.epochs,
            'batch_size': 32,
            'input_size': X.shape[1],
            'output_size': 1,
            'framework': 'pytorch'
        }
        tracker.log_params(params)
        
        # Criar modelo
        model = SimpleNN(
            input_size=X.shape[1],
            hidden_size=args.hidden_size,
            output_size=1
        )
        
        # Treinar modelo
        history = train_model(
            model=model,
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            tracker=tracker
        )
        
        # Avaliar modelo final
        model.eval()
        with torch.no_grad():
            y_pred = model(torch.FloatTensor(X_val)).numpy().flatten()
        
        # Calcular métricas finais
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        mse = mean_squared_error(y_val, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_val, y_pred)
        r2 = r2_score(y_val, y_pred)
        
        # Registrar métricas finais
        final_metrics = {
            'final_mse': mse,
            'final_rmse': rmse,
            'final_mae': mae,
            'final_r2': r2
        }
        tracker.log_metrics(final_metrics)
        
        # Criar gráfico de histórico de treinamento
        plt.figure(figsize=(10, 6))
        plt.plot(history['train_loss'], label='Treino')
        plt.plot(history['val_loss'], label='Validação')
        plt.xlabel('Época')
        plt.ylabel('Perda (MSE)')
        plt.title('Histórico de Treinamento')
        plt.legend()
        
        # Salvar figura temporariamente
        fig_path = "/tmp/training_history.png"
        plt.savefig(fig_path)
        plt.close()
        
        # Registrar figura
        tracker.log_artifact(fig_path)
        
        # Criar gráfico de previsão vs. real
        plt.figure(figsize=(10, 6))
        plt.scatter(y_val, y_pred, alpha=0.5)
        plt.plot([y_val.min(), y_val.max()], [y_val.min(), y_val.max()], 'r--')
        plt.xlabel('Valores Reais')
        plt.ylabel('Previsões')
        plt.title('Previsão vs. Real')
        
        # Salvar figura temporariamente
        fig_path = "/tmp/prediction_plot.png"
        plt.savefig(fig_path)
        plt.close()
        
        # Registrar figura
        tracker.log_artifact(fig_path)
        
        # Registrar modelo
        tracker.log_model(model, "pytorch_model", framework="pytorch")
        
        # Limpar arquivos temporários
        os.remove("/tmp/training_history.png")
        os.remove("/tmp/prediction_plot.png")
        
        print(f"\nTreinamento concluído. Métricas finais:")
        print(f"  MSE: {mse:.4f}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  R²: {r2:.4f}")
        print(f"\nExperimento registrado no MLflow: {tracker.get_tracking_uri()}")
        print(f"Experimento: {args.experiment_name}")
        print(f"Run ID: {mlflow.active_run().info.run_id}")

if __name__ == "__main__":
    import mlflow
    main()
```

### Passo 6: Criar Exemplo de Uso com TensorFlow

Crie um exemplo em `examples/mlflow_tensorflow_example.py`:

```python
#!/usr/bin/env python3
"""
Exemplo de uso do MLflow com TensorFlow.
"""

import os
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import Callback
import matplotlib.pyplot as plt
import argparse

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.validation.mlflow_tracker import MLflowExperimentTracker

# Callback para registrar métricas no MLflow
class MLflowCallback(Callback):
    def __init__(self, tracker):
        super(MLflowCallback, self).__init__()
        self.tracker = tracker
    
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        self.tracker.log_metrics(logs, step=epoch)

def generate_data(n_samples=1000, n_features=10, noise=0.1):
    """Gera dados sintéticos.
    
    Args:
        n_samples: Número de amostras.
        n_features: Número de features.
        noise: Nível de ruído.
        
    Returns:
        tuple: (X, y) arrays numpy.
    """
    # Gerar coeficientes aleatórios
    true_weights = np.random.randn(n_features)
    
    # Gerar features
    X = np.random.randn(n_samples, n_features)
    
    # Gerar target com ruído
    y = X.dot(true_weights) + noise * np.random.randn(n_samples)
    
    return X, y

def create_model(input_size, hidden_size):
    """Cria um modelo TensorFlow.
    
    Args:
        input_size: Tamanho da entrada.
        hidden_size: Tamanho da camada oculta.
        
    Returns:
        tf.keras.Model: Modelo TensorFlow.
    """
    model = Sequential([
        Dense(hidden_size, activation='relu', input_shape=(input_size,)),
        Dense(1)
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Exemplo de MLflow com TensorFlow")
    parser.add_argument("--tracking-uri", default="http://localhost:5000",
                        help="URI para o servidor MLflow")
    parser.add_argument("--experiment-name", default="tensorflow_regression",
                        help="Nome do experimento")
    parser.add_argument("--epochs", type=int, default=100,
                        help="Número de épocas")
    parser.add_argument("--hidden-size", type=int, default=64,
                        help="Tamanho da camada oculta")
    parser.add_argument("--learning-rate", type=float, default=0.01,
                        help="Taxa de aprendizado")
    
    args = parser.parse_args()
    
    # Gerar dados
    X, y = generate_data(n_samples=1000, n_features=10, noise=0.1)
    
    # Dividir em treino e validação
    from sklearn.model_selection import train_test_split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Inicializar rastreador MLflow
    tracker = MLflowExperimentTracker(
        experiment_name=args.experiment_name,
        tracking_uri=args.tracking_uri
    )
    
    # Iniciar execução
    with tracker.start_run(run_name=f"tf_h{args.hidden_size}_lr{args.learning_rate}"):
        # Registrar parâmetros
        params = {
            'hidden_size': args.hidden_size,
            'learning_rate': args.learning_rate,
            'epochs': args.epochs,
            'batch_size': 32,
            'input_size': X.shape[1],
            'framework': 'tensorflow'
        }
        tracker.log_params(params)
        
        # Criar modelo
        model = create_model(
            input_size=X.shape[1],
            hidden_size=args.hidden_size
        )
        
        # Configurar otimizador com taxa de aprendizado personalizada
        optimizer = tf.keras.optimizers.Adam(learning_rate=args.learning_rate)
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
        
        # Treinar modelo
        mlflow_callback = MLflowCallback(tracker)
        history = model.fit(
            X_train, y_train,
            epochs=args.epochs,
            batch_size=32,
            validation_data=(X_val, y_val),
            verbose=1,
            callbacks=[mlflow_callback]
        )
        
        # Avaliar modelo final
        y_pred = model.predict(X_val).flatten()
        
        # Calcular métricas finais
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        mse = mean_squared_error(y_val, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_val, y_pred)
        r2 = r2_score(y_val, y_pred)
        
        # Registrar métricas finais
        final_metrics = {
            'final_mse': mse,
            'final_rmse': rmse,
            'final_mae': mae,
            'final_r2': r2
        }
        tracker.log_metrics(final_metrics)
        
        # Criar gráfico de histórico de treinamento
        plt.figure(figsize=(10, 6))
        plt.plot(history.history['loss'], label='Treino')
        plt.plot(history.history['val_loss'], label='Validação')
        plt.xlabel('Época')
        plt.ylabel('Perda (MSE)')
        plt.title('Histórico de Treinamento')
        plt.legend()
        
        # Salvar figura temporariamente
        fig_path = "/tmp/tf_training_history.png"
        plt.savefig(fig_path)
        plt.close()
        
        # Registrar figura
        tracker.log_artifact(fig_path)
        
        # Criar gráfico de previsão vs. real
        plt.figure(figsize=(10, 6))
        plt.scatter(y_val, y_pred, alpha=0.5)
        plt.plot([y_val.min(), y_val.max()], [y_val.min(), y_val.max()], 'r--')
        plt.xlabel('Valores Reais')
        plt.ylabel('Previsões')
        plt.title('Previsão vs. Real')
        
        # Salvar figura temporariamente
        fig_path = "/tmp/tf_prediction_plot.png"
        plt.savefig(fig_path)
        plt.close()
        
        # Registrar figura
        tracker.log_artifact(fig_path)
        
        # Registrar modelo
        tracker.log_model(model, "tensorflow_model", framework="tensorflow")
        
        # Limpar arquivos temporários
        os.remove("/tmp/tf_training_history.png")
        os.remove("/tmp/tf_prediction_plot.png")
        
        print(f"\nTreinamento concluído. Métricas finais:")
        print(f"  MSE: {mse:.4f}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        print(f"  R²: {r2:.4f}")
        print(f"\nExperimento registrado no MLflow: {tracker.get_tracking_uri()}")
        print(f"Experimento: {args.experiment_name}")
        print(f"Run ID: {mlflow.active_run().info.run_id}")

if __name__ == "__main__":
    import mlflow
    main()
```

### Passo 7: Implementar Testes Unitários

Crie testes unitários em `tests/test_mlflow_tracker.py`:

```python
import unittest
import os
import tempfile
import numpy as np
import pandas as pd
import mlflow
from unittest.mock import patch, MagicMock

from src.validation.mlflow_tracker import MLflowExperimentTracker

class TestMLflowTracker(unittest.TestCase):
    
    def setUp(self):
        # Configurar URI de rastreamento temporária
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tracking_uri = f"file://{self.temp_dir.name}"
        
        # Configurar rastreador
        self.experiment_name = "test_experiment"
        self.tracker = MLflowExperimentTracker(
            experiment_name=self.experiment_name,
            tracking_uri=self.tracking_uri
        )
    
    def tearDown(self):
        # Limpar diretório temporário
        self.temp_dir.cleanup()
    
    def test_experiment_creation(self):
        """Testa a criação de experimento."""
        # Verificar se o experimento foi criado
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        self.assertIsNotNone(experiment)
        self.assertEqual(experiment.name, self.experiment_name)
    
    def test_run_lifecycle(self):
        """Testa o ciclo de vida de uma execução."""
        # Iniciar execução
        with self.tracker.start_run(run_name="test_run"):
            # Verificar se a execução está ativa
            self.assertIsNotNone(mlflow.active_run())
            
            # Registrar parâmetros e métricas
            self.tracker.log_param("param1", 10)
            self.tracker.log_params({"param2": 20, "param3": "value"})
            self.tracker.log_metric("metric1", 0.5)
            self.tracker.log_metrics({"metric2": 0.8, "metric3": 0.9})
        
        # Verificar se a execução foi finalizada
        self.assertIsNone(mlflow.active_run())
        
        # Buscar execuções
        runs = self.tracker.search_runs()
        
        # Verificar se a execução foi registrada
        self.assertEqual(len(runs), 1)
        
        # Verificar parâmetros e métricas
        run = runs.iloc[0]
        self.assertEqual(run["params.param1"], "10")
        self.assertEqual(run["params.param2"], "20")
        self.assertEqual(run["params.param3"], "value")
        self.assertEqual(run["metrics.metric1"], 0.5)
        self.assertEqual(run["metrics.metric2"], 0.8)
        self.assertEqual(run["metrics.metric3"], 0.9)
    
    def test_get_best_run(self):
        """Testa a obtenção da melhor execução."""
        # Criar múltiplas execuções
        with self.tracker.start_run(run_name="run1"):
            self.tracker.log_metric("score", 0.7)
        
        with self.tracker.start_run(run_name="run2"):
            self.tracker.log_metric("score", 0.9)  # Melhor
        
        with self.tracker.start_run(run_name="run3"):
            self.tracker.log_metric("score", 0.5)
        
        # Obter melhor execução (maior score)
        best_run = self.tracker.get_best_run("score", ascending=False)
        
        # Verificar se a melhor execução foi encontrada
        self.assertIsNotNone(best_run)
        self.assertEqual(best_run["metrics"]["score"], 0.9)
        
        # Obter melhor execução (menor score)
        worst_run = self.tracker.get_best_run("score", ascending=True)
        
        # Verificar se a pior execução foi encontrada
        self.assertIsNotNone(worst_run)
        self.assertEqual(worst_run["metrics"]["score"], 0.5)

if __name__ == '__main__':
    unittest.main()
```

### Passo 8: Documentação e Melhores Práticas

Crie um arquivo de documentação em `docs/mlflow_usage.md`:

```markdown
# Uso do MLflow no Autocura

Este documento descreve a implementação e uso do MLflow no sistema Autocura para rastreamento de experimentos, versionamento de modelos e gerenciamento do ciclo de vida de modelos de machine learning.

## Visão Geral

O MLflow é uma plataforma de código aberto para gerenciar o ciclo de vida de modelos de machine learning. No Autocura, o MLflow é utilizado para:

1. Rastrear experimentos e parâmetros
2. Registrar métricas e artefatos
3. Versionar modelos
4. Comparar diferentes abordagens
5. Facilitar a reprodutibilidade

## Componentes Principais

1. **MLflowExperimentTracker**: Wrapper para facilitar o uso do MLflow no Autocura.
2. **Backtester**: Classe para backtesting e validação de modelos, integrada com MLflow.
3. **Servidor MLflow**: Servidor para visualização e gerenciamento de experimentos.

## Configuração do Servidor

O servidor MLflow pode ser iniciado com o script `scripts/start_mlflow_server.py`:

```bash
python scripts/start_mlflow_server.py --host 0.0.0.0 --port 5000
```

Por padrão, o servidor usa um banco de dados SQLite local e armazena artefatos no diretório `./mlruns`. Para ambientes de produção, recomenda-se configurar um banco de dados mais robusto e um armazenamento de artefatos centralizado.

## Casos de Uso

### Rastreamento de Experimentos

```python
from src.validation.mlflow_tracker import MLflowExperimentTracker

# Inicializar rastreador
tracker = MLflowExperimentTracker(
    experiment_name="my_experiment",
    tracking_uri="http://localhost:5000"
)

# Iniciar execução
with tracker.start_run(run_name="my_run"):
    # Registrar parâmetros
    tracker.log_params({
        "learning_rate": 0.01,
        "batch_size": 32,
        "epochs": 100
    })
    
    # Treinar modelo
    # ...
    
    # Registrar métricas
    tracker.log_metrics({
        "accuracy": 0.85,
        "loss": 0.25
    })
    
    # Registrar modelo
    tracker.log_model(model, "my_model", framework="pytorch")
```

### Backtesting de Modelos

```python
from src.validation.backtester import Backtester

# Inicializar backtester
backtester = Backtester(
    model_name="regression_model",
    tracking_uri="http://localhost:5000"
)

# Executar backtest
results = backtester.run_backtest(
    model=model,
    data=data,
    target_col="target",
    feature_cols=["feature1", "feature2", "feature3"],
    model_params={"learning_rate": 0.01},
    framework="pytorch"
)

# Comparar múltiplos modelos
models = [
    {"model": model1, "name": "Model A", "params": {"lr": 0.01}, "framework": "pytorch"},
    {"model": model2, "name": "Model B", "params": {"lr": 0.001}, "framework": "pytorch"}
]

comparison = backtester.compare_models(
    models=models,
    data=data,
    target_col="target",
    feature_cols=["feature1", "feature2", "feature3"]
)

# Carregar o melhor modelo
best_model, best_run = backtester.load_best_model(metric_name="rmse", ascending=True)
```

## Integração com Frameworks

### PyTorch

```python
# Registrar modelo PyTorch
tracker.log_model(model, "pytorch_model", framework="pytorch")

# Carregar modelo PyTorch
model = tracker.load_model(run_id, "pytorch_model", framework="pytorch")
```

### TensorFlow

```python
# Registrar modelo TensorFlow
tracker.log_model(model, "tensorflow_model", framework="tensorflow")

# Carregar modelo TensorFlow
model = tracker.load_model(run_id, "tensorflow_model", framework="tensorflow")
```

### Scikit-learn

```python
# Registrar modelo scikit-learn
tracker.log_model(model, "sklearn_model", framework="sklearn")

# Carregar modelo scikit-learn
model = tracker.load_model(run_id, "sklearn_model", framework="sklearn")
```

## Melhores Práticas

1. **Organização de Experimentos**: Use nomes de experimentos significativos e organizados hierarquicamente.
2. **Parâmetros**: Registre todos os parâmetros relevantes para garantir reprodutibilidade.
3. **Métricas**: Registre métricas intermediárias durante o treinamento para acompanhar o progresso.
4. **Artefatos**: Salve gráficos, exemplos de previsões e outros artefatos para facilitar a análise.
5. **Versionamento**: Use tags e versões para modelos importantes.
6. **Ambiente**: Registre informações sobre o ambiente de execução (versões de bibliotecas, etc.).

## Referências

- [Documentação MLflow](https://mlflow.org/docs/latest/index.html)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Models](https://mlflow.org/docs/latest/models.html)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
```

### Considerações Finais para MLflow

- **Escalabilidade**: Para ambientes de produção, considere usar um banco de dados SQL (MySQL, PostgreSQL) como backend e um armazenamento de objetos (S3, Azure Blob) para artefatos.
- **Segurança**: Implemente autenticação e autorização para proteger o servidor MLflow em ambientes compartilhados.
- **Integração com CI/CD**: Integre o MLflow com pipelines de CI/CD para automação de treinamento e implantação de modelos.
- **Monitoramento**: Use o MLflow para monitorar o desempenho de modelos em produção.
- **Governança**: Estabeleça políticas de governança para gerenciar o ciclo de vida dos modelos, incluindo aprovação, promoção e aposentadoria.

## 7. Implementação do SHAP e LIME para Interpretabilidade de Modelos

### Contexto no Autocura
As bibliotecas SHAP (SHapley Additive exPlanations) e LIME (Local Interpretable Model-agnostic Explanations) serão utilizadas no sistema Autocura para fornecer explicabilidade aos modelos de machine learning, especialmente no módulo de interpretabilidade (`explainer.py`), permitindo entender as decisões dos modelos e aumentar a confiança nas previsões.

### Passo 1: Instalação e Configuração

```bash
# Ativar ambiente virtual
source autocura-env/bin/activate

# Instalar SHAP e LIME
pip install shap==0.41.0
pip install lime==0.2.0.1

# Dependências adicionais
pip install matplotlib  # Para visualização
pip install scikit-image  # Para processamento de imagens (necessário para LIME)
```

### Passo 2: Implementar Wrapper para Explicabilidade

Crie um arquivo `src/interpretability/model_explainer.py`:

```python
"""
Wrapper para explicabilidade de modelos com SHAP e LIME.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
import json
from datetime import datetime

# Importar bibliotecas de explicabilidade
import shap
import lime
import lime.lime_tabular

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelExplainer:
    """Classe para explicabilidade de modelos usando SHAP e LIME."""
    
    def __init__(self, model_type: str = "sklearn", 
                 output_dir: str = "/opt/autocura/explanations"):
        """Inicializa o explicador de modelos.
        
        Args:
            model_type: Tipo do modelo ('sklearn', 'pytorch', 'tensorflow', 'xgboost').
            output_dir: Diretório para salvar explicações.
        """
        self.model_type = model_type.lower()
        self.output_dir = output_dir
        
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Inicializar explicadores
        self.shap_explainer = None
        self.lime_explainer = None
        
        logger.info(f"ModelExplainer inicializado para modelo tipo '{model_type}'")
    
    def _prepare_model_for_shap(self, model: Any) -> Callable:
        """Prepara o modelo para uso com SHAP.
        
        Args:
            model: Modelo a ser explicado.
            
        Returns:
            Callable: Função de previsão para o SHAP.
        """
        if self.model_type == "sklearn":
            # Para modelos scikit-learn, usar diretamente
            return model.predict
        
        elif self.model_type == "pytorch":
            # Para modelos PyTorch
            import torch
            
            def predict_fn(x):
                model.eval()
                with torch.no_grad():
                    x_tensor = torch.tensor(x, dtype=torch.float32)
                    return model(x_tensor).numpy()
            
            return predict_fn
        
        elif self.model_type == "tensorflow":
            # Para modelos TensorFlow
            def predict_fn(x):
                return model.predict(x)
            
            return predict_fn
        
        elif self.model_type == "xgboost":
            # Para modelos XGBoost
            return model.predict
        
        else:
            raise ValueError(f"Tipo de modelo não suportado: {self.model_type}")
    
    def setup_shap_explainer(self, model: Any, data: Union[np.ndarray, pd.DataFrame], 
                           algorithm: str = "auto"):
        """Configura o explicador SHAP.
        
        Args:
            model: Modelo a ser explicado.
            data: Dados de background para o explicador.
            algorithm: Algoritmo SHAP ('auto', 'tree', 'kernel', 'deep', 'gradient').
        """
        # Converter DataFrame para array se necessário
        if isinstance(data, pd.DataFrame):
            data_array = data.values
        else:
            data_array = data
        
        # Configurar explicador SHAP com base no tipo de modelo e algoritmo
        try:
            if algorithm == "auto":
                # Escolher algoritmo com base no tipo de modelo
                if self.model_type in ["sklearn", "xgboost"] and hasattr(model, "predict_proba"):
                    # Para modelos baseados em árvores
                    self.shap_explainer = shap.TreeExplainer(model)
                    logger.info("SHAP TreeExplainer configurado automaticamente")
                
                elif self.model_type in ["pytorch", "tensorflow"]:
                    # Para modelos de deep learning
                    predict_fn = self._prepare_model_for_shap(model)
                    self.shap_explainer = shap.DeepExplainer(predict_fn, data_array)
                    logger.info("SHAP DeepExplainer configurado automaticamente")
                
                else:
                    # Fallback para KernelExplainer
                    predict_fn = self._prepare_model_for_shap(model)
                    self.shap_explainer = shap.KernelExplainer(predict_fn, data_array)
                    logger.info("SHAP KernelExplainer configurado automaticamente")
            
            elif algorithm == "tree":
                self.shap_explainer = shap.TreeExplainer(model)
                logger.info("SHAP TreeExplainer configurado")
            
            elif algorithm == "kernel":
                predict_fn = self._prepare_model_for_shap(model)
                self.shap_explainer = shap.KernelExplainer(predict_fn, data_array)
                logger.info("SHAP KernelExplainer configurado")
            
            elif algorithm == "deep":
                predict_fn = self._prepare_model_for_shap(model)
                self.shap_explainer = shap.DeepExplainer(predict_fn, data_array)
                logger.info("SHAP DeepExplainer configurado")
            
            elif algorithm == "gradient":
                predict_fn = self._prepare_model_for_shap(model)
                self.shap_explainer = shap.GradientExplainer(predict_fn, data_array)
                logger.info("SHAP GradientExplainer configurado")
            
            else:
                raise ValueError(f"Algoritmo SHAP não suportado: {algorithm}")
            
        except Exception as e:
            logger.error(f"Erro ao configurar explicador SHAP: {e}")
            raise
    
    def setup_lime_explainer(self, data: Union[np.ndarray, pd.DataFrame], 
                           feature_names: Optional[List[str]] = None, 
                           class_names: Optional[List[str]] = None,
                           categorical_features: Optional[List[int]] = None):
        """Configura o explicador LIME.
        
        Args:
            data: Dados de treinamento para o explicador.
            feature_names: Nomes das features.
            class_names: Nomes das classes (para classificação).
            categorical_features: Índices das features categóricas.
        """
        try:
            # Converter DataFrame para array se necessário
            if isinstance(data, pd.DataFrame):
                if feature_names is None:
                    feature_names = list(data.columns)
                data_array = data.values
            else:
                data_array = data
            
            # Configurar explicador LIME
            self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
                training_data=data_array,
                feature_names=feature_names,
                class_names=class_names,
                categorical_features=categorical_features,
                mode="regression" if class_names is None else "classification",
                verbose=True
            )
            
            logger.info("LIME Explainer configurado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao configurar explicador LIME: {e}")
            raise
    
    def explain_with_shap(self, model: Any, data: Union[np.ndarray, pd.DataFrame], 
                         feature_names: Optional[List[str]] = None,
                         sample_idx: Optional[int] = None,
                         plot_type: str = "bar") -> Dict[str, Any]:
        """Gera explicações SHAP para o modelo.
        
        Args:
            model: Modelo a ser explicado.
            data: Dados para explicação.
            feature_names: Nomes das features.
            sample_idx: Índice da amostra para explicar (None para todas).
            plot_type: Tipo de gráfico ('bar', 'waterfall', 'force', 'summary').
            
        Returns:
            Dict: Resultados da explicação.
        """
        # Verificar se o explicador SHAP está configurado
        if self.shap_explainer is None:
            logger.info("Explicador SHAP não configurado. Configurando automaticamente.")
            self.setup_shap_explainer(model, data)
        
        # Converter DataFrame para array se necessário
        if isinstance(data, pd.DataFrame):
            if feature_names is None:
                feature_names = list(data.columns)
            data_array = data.values
        else:
            data_array = data
            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(data_array.shape[1])]
        
        try:
            # Calcular valores SHAP
            if sample_idx is not None:
                # Explicar uma única amostra
                sample = data_array[sample_idx:sample_idx+1]
                shap_values = self.shap_explainer.shap_values(sample)
                
                # Criar gráfico
                plt.figure(figsize=(10, 6))
                
                if plot_type == "bar":
                    # Gráfico de barras
                    shap_values_single = shap_values[0] if isinstance(shap_values, list) else shap_values[0, :]
                    plt.barh(feature_names, shap_values_single)
                    plt.xlabel("SHAP Value")
                    plt.ylabel("Feature")
                    plt.title(f"SHAP Values for Sample {sample_idx}")
                
                elif plot_type == "waterfall":
                    # Gráfico de cachoeira
                    shap.plots.waterfall(shap_values[0] if isinstance(shap_values, list) else shap_values[0, :], 
                                        feature_names=feature_names, show=False)
                
                elif plot_type == "force":
                    # Gráfico de força
                    shap.force_plot(self.shap_explainer.expected_value, 
                                   shap_values[0] if isinstance(shap_values, list) else shap_values[0, :], 
                                   feature_names=feature_names, matplotlib=True, show=False)
                
                # Salvar gráfico
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                plot_path = os.path.join(self.output_dir, f"shap_{plot_type}_{timestamp}.png")
                plt.tight_layout()
                plt.savefig(plot_path)
                plt.close()
                
                # Preparar resultados
                feature_importance = {}
                shap_values_single = shap_values[0] if isinstance(shap_values, list) else shap_values[0, :]
                for i, name in enumerate(feature_names):
                    feature_importance[name] = float(shap_values_single[i])
                
                result = {
                    "sample_idx": sample_idx,
                    "feature_importance": feature_importance,
                    "plot_path": plot_path,
                    "expected_value": float(self.shap_explainer.expected_value) if not isinstance(self.shap_explainer.expected_value, list) 
                                     else [float(v) for v in self.shap_explainer.expected_value]
                }
                
            else:
                # Explicar todas as amostras
                shap_values = self.shap_explainer.shap_values(data_array)
                
                # Criar gráfico de resumo
                plt.figure(figsize=(10, 8))
                
                if plot_type == "summary":
                    # Gráfico de resumo
                    shap.summary_plot(shap_values, data_array, feature_names=feature_names, show=False)
                
                # Salvar gráfico
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                plot_path = os.path.join(self.output_dir, f"shap_summary_{timestamp}.png")
                plt.tight_layout()
                plt.savefig(plot_path)
                plt.close()
                
                # Calcular importância média das features
                if isinstance(shap_values, list):  # Para modelos de classificação
                    # Média absoluta dos valores SHAP para todas as classes
                    mean_abs_shap = np.mean([np.abs(shap_values[i]) for i in range(len(shap_values))], axis=0)
                    mean_abs_shap = np.mean(mean_abs_shap, axis=0)
                else:
                    # Média absoluta dos valores SHAP
                    mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
                
                # Preparar resultados
                feature_importance = {}
                for i, name in enumerate(feature_names):
                    feature_importance[name] = float(mean_abs_shap[i])
                
                # Ordenar features por importância
                sorted_importance = {k: v for k, v in sorted(feature_importance.items(), 
                                                           key=lambda item: item[1], reverse=True)}
                
                result = {
                    "global_feature_importance": sorted_importance,
                    "plot_path": plot_path,
                    "expected_value": float(self.shap_explainer.expected_value) if not isinstance(self.shap_explainer.expected_value, list) 
                                     else [float(v) for v in self.shap_explainer.expected_value]
                }
            
            logger.info(f"Explicação SHAP gerada com sucesso. Gráfico salvo em {plot_path}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar explicação SHAP: {e}")
            raise
    
    def explain_with_lime(self, model: Any, data: Union[np.ndarray, pd.DataFrame], 
                         sample_idx: int, num_features: int = 10,
                         feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Gera explicações LIME para o modelo.
        
        Args:
            model: Modelo a ser explicado.
            data: Dados para explicação.
            sample_idx: Índice da amostra para explicar.
            num_features: Número de features a mostrar na explicação.
            feature_names: Nomes das features.
            
        Returns:
            Dict: Resultados da explicação.
        """
        # Verificar se o explicador LIME está configurado
        if self.lime_explainer is None:
            logger.info("Explicador LIME não configurado. Configurando automaticamente.")
            self.setup_lime_explainer(data, feature_names)
        
        # Converter DataFrame para array se necessário
        if isinstance(data, pd.DataFrame):
            if feature_names is None:
                feature_names = list(data.columns)
            sample = data.iloc[sample_idx].values
            data_array = data.values
        else:
            sample = data[sample_idx]
            data_array = data
            if feature_names is None:
                feature_names = [f"feature_{i}" for i in range(data_array.shape[1])]
        
        try:
            # Preparar função de previsão para LIME
            if self.model_type == "sklearn":
                if hasattr(model, "predict_proba"):
                    predict_fn = model.predict_proba
                else:
                    predict_fn = model.predict
            
            elif self.model_type == "pytorch":
                import torch
                
                def predict_fn(x):
                    model.eval()
                    with torch.no_grad():
                        x_tensor = torch.tensor(x, dtype=torch.float32)
                        return model(x_tensor).numpy()
            
            elif self.model_type == "tensorflow":
                predict_fn = model.predict
            
            else:
                predict_fn = model.predict
            
            # Gerar explicação LIME
            explanation = self.lime_explainer.explain_instance(
                sample, predict_fn, num_features=num_features
            )
            
            # Extrair features e pesos
            feature_weights = explanation.as_list()
            
            # Criar gráfico
            plt.figure(figsize=(10, 6))
            explanation.as_pyplot_figure()
            
            # Salvar gráfico
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_path = os.path.join(self.output_dir, f"lime_explanation_{timestamp}.png")
            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()
            
            # Preparar resultados
            result = {
                "sample_idx": sample_idx,
                "feature_weights": feature_weights,
                "plot_path": plot_path,
                "prediction": explanation.predict_proba.tolist() if hasattr(explanation, "predict_proba") else float(explanation.predict[0])
            }
            
            logger.info(f"Explicação LIME gerada com sucesso. Gráfico salvo em {plot_path}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar explicação LIME: {e}")
            raise
    
    def compare_explanations(self, model: Any, data: Union[np.ndarray, pd.DataFrame], 
                           sample_idx: int, feature_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Compara explicações SHAP e LIME para uma amostra.
        
        Args:
            model: Modelo a ser explicado.
            data: Dados para explicação.
            sample_idx: Índice da amostra para explicar.
            feature_names: Nomes das features.
            
        Returns:
            Dict: Resultados da comparação.
        """
        # Gerar explicações
        shap_result = self.explain_with_shap(model, data, feature_names, sample_idx, plot_type="bar")
        lime_result = self.explain_with_lime(model, data, sample_idx, feature_names=feature_names)
        
        # Extrair importâncias das features
        shap_importance = shap_result["feature_importance"]
        lime_weights = {feature: weight for feature, weight in lime_result["feature_weights"]}
        
        # Criar gráfico de comparação
        plt.figure(figsize=(12, 8))
        
        # Obter features comuns
        common_features = set(shap_importance.keys()).intersection(set(lime_weights.keys()))
        features = list(common_features)
        
        # Preparar dados para o gráfico
        shap_values = [abs(shap_importance.get(feature, 0)) for feature in features]
        lime_values = [abs(lime_weights.get(feature, 0)) for feature in features]
        
        # Normalizar valores para comparação justa
        shap_values = np.array(shap_values) / max(shap_values) if max(shap_values) > 0 else np.array(shap_values)
        lime_values = np.array(lime_values) / max(lime_values) if max(lime_values) > 0 else np.array(lime_values)
        
        # Criar gráfico de barras lado a lado
        x = np.arange(len(features))
        width = 0.35
        
        plt.bar(x - width/2, shap_values, width, label='SHAP')
        plt.bar(x + width/2, lime_values, width, label='LIME')
        
        plt.xlabel('Features')
        plt.ylabel('Importância Normalizada')
        plt.title('Comparação de Explicações SHAP vs LIME')
        plt.xticks(x, features, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        
        # Salvar gráfico
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(self.output_dir, f"comparison_{timestamp}.png")
        plt.savefig(plot_path)
        plt.close()
        
        # Calcular correlação entre as explicações
        correlation = np.corrcoef(shap_values, lime_values)[0, 1]
        
        # Preparar resultados
        result = {
            "sample_idx": sample_idx,
            "shap_explanation": shap_result,
            "lime_explanation": lime_result,
            "comparison_plot": plot_path,
            "correlation": float(correlation)
        }
        
        logger.info(f"Comparação de explicações gerada com sucesso. Correlação: {correlation:.4f}")
        return result
    
    def save_explanation(self, explanation: Dict[str, Any], 
                        name: str, timestamp: Optional[str] = None) -> str:
        """Salva uma explicação em formato JSON.
        
        Args:
            explanation: Dicionário com a explicação.
            name: Nome base para o arquivo.
            timestamp: Timestamp para incluir no nome do arquivo (opcional).
            
        Returns:
            str: Caminho para o arquivo salvo.
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar nome do arquivo
        filename = f"{name}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Salvar explicação
        with open(filepath, 'w') as f:
            json.dump(explanation, f, indent=2)
        
        logger.info(f"Explicação salva em {filepath}")
        return filepath
```

### Passo 3: Implementar Integração com o Módulo de Interpretabilidade

Modifique o arquivo `src/interpretability/explainer.py` para usar SHAP e LIME:

```python
"""
Módulo para interpretabilidade de modelos.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
import json
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar o explicador de modelos
from .model_explainer import ModelExplainer

class Explainer:
    """Classe para interpretabilidade de modelos no sistema Autocura."""
    
    def __init__(self, output_dir: str = "/opt/autocura/explanations"):
        """Inicializa o explicador.
        
        Args:
            output_dir: Diretório para salvar explicações.
        """
        self.output_dir = output_dir
        
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Dicionário para armazenar explicadores por modelo
        self.explainers = {}
        
        logger.info(f"Explainer inicializado. Diretório de saída: {output_dir}")
    
    def register_model(self, model_id: str, model: Any, model_type: str,
                      training_data: Union[np.ndarray, pd.DataFrame],
                      feature_names: Optional[List[str]] = None,
                      class_names: Optional[List[str]] = None,
                      categorical_features: Optional[List[int]] = None) -> None:
        """Registra um modelo para explicabilidade.
        
        Args:
            model_id: Identificador único do modelo.
            model: Modelo a ser explicado.
            model_type: Tipo do modelo ('sklearn', 'pytorch', 'tensorflow', 'xgboost').
            training_data: Dados de treinamento para o modelo.
            feature_names: Nomes das features.
            class_names: Nomes das classes (para classificação).
            categorical_features: Índices das features categóricas.
        """
        # Criar explicador para o modelo
        explainer = ModelExplainer(model_type=model_type, output_dir=self.output_dir)
        
        # Configurar explicadores SHAP e LIME
        explainer.setup_shap_explainer(model, training_data)
        explainer.setup_lime_explainer(
            training_data, 
            feature_names=feature_names,
            class_names=class_names,
            categorical_features=categorical_features
        )
        
        # Armazenar explicador e modelo
        self.explainers[model_id] = {
            "explainer": explainer,
            "model": model,
            "model_type": model_type,
            "feature_names": feature_names
        }
        
        logger.info(f"Modelo '{model_id}' registrado para explicabilidade")
    
    def explain_prediction(self, model_id: str, data: Union[np.ndarray, pd.DataFrame],
                          sample_idx: int, method: str = "both") -> Dict[str, Any]:
        """Explica uma previsão específica.
        
        Args:
            model_id: Identificador do modelo.
            data: Dados para explicação.
            sample_idx: Índice da amostra para explicar.
            method: Método de explicação ('shap', 'lime', 'both').
            
        Returns:
            Dict: Resultados da explicação.
        """
        # Verificar se o modelo está registrado
        if model_id not in self.explainers:
            raise ValueError(f"Modelo '{model_id}' não registrado")
        
        # Obter explicador e modelo
        explainer = self.explainers[model_id]["explainer"]
        model = self.explainers[model_id]["model"]
        feature_names = self.explainers[model_id]["feature_names"]
        
        # Gerar explicação
        if method.lower() == "shap":
            result = explainer.explain_with_shap(
                model, data, feature_names=feature_names, sample_idx=sample_idx
            )
            
        elif method.lower() == "lime":
            result = explainer.explain_with_lime(
                model, data, sample_idx=sample_idx, feature_names=feature_names
            )
            
        elif method.lower() == "both":
            result = explainer.compare_explanations(
                model, data, sample_idx=sample_idx, feature_names=feature_names
            )
            
        else:
            raise ValueError(f"Método de explicação não suportado: {method}")
        
        # Salvar explicação
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = explainer.save_explanation(
            result, f"{model_id}_{method}_explanation", timestamp
        )
        
        # Adicionar informações ao resultado
        result["model_id"] = model_id
        result["method"] = method
        result["timestamp"] = timestamp
        result["filepath"] = filepath
        
        return result
    
    def explain_model(self, model_id: str, data: Union[np.ndarray, pd.DataFrame],
                     method: str = "shap") -> Dict[str, Any]:
        """Gera uma explicação global para o modelo.
        
        Args:
            model_id: Identificador do modelo.
            data: Dados para explicação.
            method: Método de explicação ('shap', 'lime').
            
        Returns:
            Dict: Resultados da explicação.
        """
        # Verificar se o modelo está registrado
        if model_id not in self.explainers:
            raise ValueError(f"Modelo '{model_id}' não registrado")
        
        # Obter explicador e modelo
        explainer = self.explainers[model_id]["explainer"]
        model = self.explainers[model_id]["model"]
        feature_names = self.explainers[model_id]["feature_names"]
        
        # Gerar explicação global
        if method.lower() == "shap":
            result = explainer.explain_with_shap(
                model, data, feature_names=feature_names, sample_idx=None, plot_type="summary"
            )
            
        else:
            raise ValueError(f"Método de explicação global não suportado: {method}")
        
        # Salvar explicação
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = explainer.save_explanation(
            result, f"{model_id}_global_explanation", timestamp
        )
        
        # Adicionar informações ao resultado
        result["model_id"] = model_id
        result["method"] = method
        result["timestamp"] = timestamp
        result["filepath"] = filepath
        
        return result
    
    def explain_feature_impact(self, model_id: str, feature_name: str,
                              data: Union[np.ndarray, pd.DataFrame]) -> Dict[str, Any]:
        """Analisa o impacto de uma feature específica nas previsões.
        
        Args:
            model_id: Identificador do modelo.
            feature_name: Nome da feature para analisar.
            data: Dados para análise.
            
        Returns:
            Dict: Resultados da análise.
        """
        # Verificar se o modelo está registrado
        if model_id not in self.explainers:
            raise ValueError(f"Modelo '{model_id}' não registrado")
        
        # Obter explicador, modelo e nomes das features
        explainer = self.explainers[model_id]["explainer"]
        model = self.explainers[model_id]["model"]
        feature_names = self.explainers[model_id]["feature_names"]
        
        # Verificar se a feature existe
        if feature_names is None:
            raise ValueError("Nomes das features não disponíveis")
        
        if feature_name not in feature_names:
            raise ValueError(f"Feature '{feature_name}' não encontrada")
        
        # Obter índice da feature
        feature_idx = feature_names.index(feature_name)
        
        # Converter DataFrame para array se necessário
        if isinstance(data, pd.DataFrame):
            data_array = data.values
        else:
            data_array = data
        
        # Preparar função de previsão
        if explainer.model_type == "sklearn":
            predict_fn = model.predict
        elif explainer.model_type == "pytorch":
            import torch
            
            def predict_fn(x):
                model.eval()
                with torch.no_grad():
                    x_tensor = torch.tensor(x, dtype=torch.float32)
                    return model(x_tensor).numpy()
        elif explainer.model_type == "tensorflow":
            predict_fn = model.predict
        else:
            predict_fn = model.predict
        
        # Criar cópia dos dados
        data_modified = data_array.copy()
        
        # Obter valores únicos da feature
        if isinstance(data, pd.DataFrame):
            unique_values = sorted(data.iloc[:, feature_idx].unique())
        else:
            unique_values = sorted(np.unique(data_array[:, feature_idx]))
        
        # Limitar número de valores para análise
        if len(unique_values) > 10:
            # Para features contínuas, usar percentis
            unique_values = np.percentile(
                data_array[:, feature_idx], 
                np.linspace(0, 100, 10)
            )
        
        # Analisar impacto da feature
        impact_results = []
        
        for value in unique_values:
            # Modificar a feature para o valor específico
            data_modified[:, feature_idx] = value
            
            # Fazer previsões
            predictions = predict_fn(data_modified)
            
            # Calcular estatísticas das previsões
            if predictions.ndim > 1:
                # Para classificação, usar probabilidade da classe positiva
                pred_mean = np.mean(predictions[:, 1])
                pred_std = np.std(predictions[:, 1])
            else:
                # Para regressão
                pred_mean = np.mean(predictions)
                pred_std = np.std(predictions)
            
            impact_results.append({
                "feature_value": float(value),
                "prediction_mean": float(pred_mean),
                "prediction_std": float(pred_std)
            })
        
        # Criar gráfico de impacto
        plt.figure(figsize=(10, 6))
        
        # Extrair dados para o gráfico
        values = [r["feature_value"] for r in impact_results]
        means = [r["prediction_mean"] for r in impact_results]
        stds = [r["prediction_std"] for r in impact_results]
        
        # Plotar média e desvio padrão
        plt.errorbar(values, means, yerr=stds, marker='o', linestyle='-')
        plt.xlabel(feature_name)
        plt.ylabel('Previsão')
        plt.title(f'Impacto da Feature {feature_name} nas Previsões')
        plt.grid(True)
        
        # Salvar gráfico
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(self.output_dir, f"feature_impact_{feature_name}_{timestamp}.png")
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        
        # Preparar resultado
        result = {
            "model_id": model_id,
            "feature_name": feature_name,
            "impact_results": impact_results,
            "plot_path": plot_path
        }
        
        # Salvar resultado
        filepath = os.path.join(self.output_dir, f"feature_impact_{feature_name}_{timestamp}.json")
        with open(filepath, 'w') as f:
            json.dump(result, f, indent=2)
        
        result["filepath"] = filepath
        
        logger.info(f"Análise de impacto da feature '{feature_name}' concluída")
        return result
```

### Passo 4: Criar Exemplo de Uso com Scikit-learn

Crie um exemplo em `examples/shap_lime_sklearn_example.py`:

```python
#!/usr/bin/env python3
"""
Exemplo de uso do SHAP e LIME com scikit-learn.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import argparse

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.interpretability.explainer import Explainer

def generate_data(n_samples=1000, n_features=10, noise=0.1):
    """Gera dados sintéticos.
    
    Args:
        n_samples: Número de amostras.
        n_features: Número de features.
        noise: Nível de ruído.
        
    Returns:
        tuple: (X, y, feature_names) arrays numpy e lista de nomes.
    """
    # Gerar coeficientes aleatórios
    true_weights = np.random.randn(n_features)
    
    # Gerar features
    X = np.random.randn(n_samples, n_features)
    
    # Gerar target com ruído
    y = X.dot(true_weights) + noise * np.random.randn(n_samples)
    
    # Criar nomes de features
    feature_names = [f"feature_{i}" for i in range(n_features)]
    
    return X, y, feature_names

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Exemplo de SHAP e LIME com scikit-learn")
    parser.add_argument("--output-dir", default="./explanations",
                        help="Diretório para salvar explicações")
    parser.add_argument("--n-estimators", type=int, default=100,
                        help="Número de estimadores para o RandomForest")
    parser.add_argument("--max-depth", type=int, default=5,
                        help="Profundidade máxima para o RandomForest")
    
    args = parser.parse_args()
    
    # Criar diretório de saída
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Gerar dados
    X, y, feature_names = generate_data(n_samples=1000, n_features=10, noise=0.1)
    
    # Dividir em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Criar e treinar modelo
    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Avaliar modelo
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Modelo treinado. R² treino: {train_score:.4f}, R² teste: {test_score:.4f}")
    
    # Inicializar explicador
    explainer = Explainer(output_dir=args.output_dir)
    
    # Registrar modelo
    model_id = "random_forest_regressor"
    explainer.register_model(
        model_id=model_id,
        model=model,
        model_type="sklearn",
        training_data=X_train,
        feature_names=feature_names
    )
    
    print(f"Modelo registrado para explicabilidade: {model_id}")
    
    # Gerar explicação global
    global_explanation = explainer.explain_model(
        model_id=model_id,
        data=X_test,
        method="shap"
    )
    
    print(f"Explicação global gerada. Gráfico salvo em: {global_explanation['plot_path']}")
    print("Importância global das features:")
    for feature, importance in list(global_explanation["global_feature_importance"].items())[:5]:
        print(f"  {feature}: {importance:.4f}")
    
    # Gerar explicação para uma amostra específica
    sample_idx = 0
    
    # Explicação com SHAP
    shap_explanation = explainer.explain_prediction(
        model_id=model_id,
        data=X_test,
        sample_idx=sample_idx,
        method="shap"
    )
    
    print(f"Explicação SHAP gerada. Gráfico salvo em: {shap_explanation['plot_path']}")
    
    # Explicação com LIME
    lime_explanation = explainer.explain_prediction(
        model_id=model_id,
        data=X_test,
        sample_idx=sample_idx,
        method="lime"
    )
    
    print(f"Explicação LIME gerada. Gráfico salvo em: {lime_explanation['plot_path']}")
    
    # Comparação de explicações
    comparison = explainer.explain_prediction(
        model_id=model_id,
        data=X_test,
        sample_idx=sample_idx,
        method="both"
    )
    
    print(f"Comparação de explicações gerada. Gráfico salvo em: {comparison['comparison_plot']}")
    print(f"Correlação entre SHAP e LIME: {comparison['correlation']:.4f}")
    
    # Analisar impacto de uma feature específica
    feature_impact = explainer.explain_feature_impact(
        model_id=model_id,
        feature_name=feature_names[0],
        data=X_test
    )
    
    print(f"Análise de impacto da feature gerada. Gráfico salvo em: {feature_impact['plot_path']}")
    
    print("\nTodas as explicações foram salvas em:", args.output_dir)

if __name__ == "__main__":
    main()
```

### Passo 5: Criar Exemplo de Uso com PyTorch

Crie um exemplo em `examples/shap_lime_pytorch_example.py`:

```python
#!/usr/bin/env python3
"""
Exemplo de uso do SHAP e LIME com PyTorch.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import argparse

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.interpretability.explainer import Explainer

# Definir modelo PyTorch
class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

def generate_data(n_samples=1000, n_features=10, noise=0.1):
    """Gera dados sintéticos.
    
    Args:
        n_samples: Número de amostras.
        n_features: Número de features.
        noise: Nível de ruído.
        
    Returns:
        tuple: (X, y, feature_names) arrays numpy e lista de nomes.
    """
    # Gerar coeficientes aleatórios
    true_weights = np.random.randn(n_features)
    
    # Gerar features
    X = np.random.randn(n_samples, n_features)
    
    # Gerar target com ruído
    y = X.dot(true_weights) + noise * np.random.randn(n_samples)
    
    # Criar nomes de features
    feature_names = [f"feature_{i}" for i in range(n_features)]
    
    return X, y, feature_names

def train_model(model, X_train, y_train, epochs=100, batch_size=32, learning_rate=0.01):
    """Treina o modelo PyTorch.
    
    Args:
        model: Modelo PyTorch.
        X_train: Features de treino.
        y_train: Target de treino.
        epochs: Número de épocas.
        batch_size: Tamanho do batch.
        learning_rate: Taxa de aprendizado.
        
    Returns:
        dict: Histórico de treinamento.
    """
    # Converter para tensores
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
    
    # Criar dataset e dataloader
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    # Definir otimizador e função de perda
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    
    # Histórico de treinamento
    history = {
        'train_loss': []
    }
    
    # Treinar modelo
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        
        for inputs, targets in train_loader:
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            # Backward pass e otimização
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Calcular perda média de treino
        train_loss /= len(train_loader)
        history['train_loss'].append(train_loss)
        
        # Imprimir progresso
        if (epoch + 1) % 10 == 0:
            print(f"Época {epoch+1}/{epochs}, Perda: {train_loss:.4f}")
    
    return history

def evaluate_model(model, X, y):
    """Avalia o modelo PyTorch.
    
    Args:
        model: Modelo PyTorch.
        X: Features.
        y: Target.
        
    Returns:
        float: R² score.
    """
    # Converter para tensores
    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.FloatTensor(y)
    
    # Avaliar modelo
    model.eval()
    with torch.no_grad():
        y_pred = model(X_tensor).numpy().flatten()
    
    # Calcular R²
    from sklearn.metrics import r2_score
    return r2_score(y, y_pred)

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Exemplo de SHAP e LIME com PyTorch")
    parser.add_argument("--output-dir", default="./explanations",
                        help="Diretório para salvar explicações")
    parser.add_argument("--hidden-size", type=int, default=64,
                        help="Tamanho da camada oculta")
    parser.add_argument("--epochs", type=int, default=100,
                        help="Número de épocas")
    
    args = parser.parse_args()
    
    # Criar diretório de saída
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Gerar dados
    X, y, feature_names = generate_data(n_samples=1000, n_features=10, noise=0.1)
    
    # Dividir em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Criar modelo
    model = SimpleNN(
        input_size=X.shape[1],
        hidden_size=args.hidden_size,
        output_size=1
    )
    
    # Treinar modelo
    history = train_model(
        model=model,
        X_train=X_train,
        y_train=y_train,
        epochs=args.epochs
    )
    
    # Avaliar modelo
    train_score = evaluate_model(model, X_train, y_train)
    test_score = evaluate_model(model, X_test, y_test)
    
    print(f"Modelo treinado. R² treino: {train_score:.4f}, R² teste: {test_score:.4f}")
    
    # Inicializar explicador
    explainer = Explainer(output_dir=args.output_dir)
    
    # Registrar modelo
    model_id = "pytorch_nn"
    explainer.register_model(
        model_id=model_id,
        model=model,
        model_type="pytorch",
        training_data=X_train,
        feature_names=feature_names
    )
    
    print(f"Modelo registrado para explicabilidade: {model_id}")
    
    # Gerar explicação global
    global_explanation = explainer.explain_model(
        model_id=model_id,
        data=X_test,
        method="shap"
    )
    
    print(f"Explicação global gerada. Gráfico salvo em: {global_explanation['plot_path']}")
    print("Importância global das features:")
    for feature, importance in list(global_explanation["global_feature_importance"].items())[:5]:
        print(f"  {feature}: {importance:.4f}")
    
    # Gerar explicação para uma amostra específica
    sample_idx = 0
    
    # Explicação com SHAP
    shap_explanation = explainer.explain_prediction(
        model_id=model_id,
        data=X_test,
        sample_idx=sample_idx,
        method="shap"
    )
    
    print(f"Explicação SHAP gerada. Gráfico salvo em: {shap_explanation['plot_path']}")
    
    # Explicação com LIME
    lime_explanation = explainer.explain_prediction(
        model_id=model_id,
        data=X_test,
        sample_idx=sample_idx,
        method="lime"
    )
    
    print(f"Explicação LIME gerada. Gráfico salvo em: {lime_explanation['plot_path']}")
    
    # Comparação de explicações
    comparison = explainer.explain_prediction(
        model_id=model_id,
        data=X_test,
        sample_idx=sample_idx,
        method="both"
    )
    
    print(f"Comparação de explicações gerada. Gráfico salvo em: {comparison['comparison_plot']}")
    print(f"Correlação entre SHAP e LIME: {comparison['correlation']:.4f}")
    
    # Analisar impacto de uma feature específica
    feature_impact = explainer.explain_feature_impact(
        model_id=model_id,
        feature_name=feature_names[0],
        data=X_test
    )
    
    print(f"Análise de impacto da feature gerada. Gráfico salvo em: {feature_impact['plot_path']}")
    
    print("\nTodas as explicações foram salvas em:", args.output_dir)

if __name__ == "__main__":
    main()
```

### Passo 6: Implementar Testes Unitários

Crie testes unitários em `tests/test_model_explainer.py`:

```python
import unittest
import os
import tempfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression

from src.interpretability.model_explainer import ModelExplainer

class TestModelExplainer(unittest.TestCase):
    
    def setUp(self):
        # Criar diretório temporário para testes
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Gerar dados de teste
        X, y = make_regression(n_samples=100, n_features=5, random_state=42)
        self.X = X
        self.y = y
        self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]
        
        # Treinar modelo
        self.model = RandomForestRegressor(n_estimators=10, max_depth=3, random_state=42)
        self.model.fit(X, y)
        
        # Inicializar explicador
        self.explainer = ModelExplainer(
            model_type="sklearn",
            output_dir=self.temp_dir.name
        )
    
    def tearDown(self):
        # Limpar diretório temporário
        self.temp_dir.cleanup()
    
    def test_shap_explainer_setup(self):
        """Testa a configuração do explicador SHAP."""
        # Configurar explicador SHAP
        self.explainer.setup_shap_explainer(self.model, self.X)
        
        # Verificar se o explicador foi configurado
        self.assertIsNotNone(self.explainer.shap_explainer)
    
    def test_lime_explainer_setup(self):
        """Testa a configuração do explicador LIME."""
        # Configurar explicador LIME
        self.explainer.setup_lime_explainer(
            self.X, 
            feature_names=self.feature_names
        )
        
        # Verificar se o explicador foi configurado
        self.assertIsNotNone(self.explainer.lime_explainer)
    
    def test_shap_explanation(self):
        """Testa a geração de explicações SHAP."""
        # Configurar explicador SHAP
        self.explainer.setup_shap_explainer(self.model, self.X)
        
        # Gerar explicação para uma amostra
        result = self.explainer.explain_with_shap(
            self.model, 
            self.X, 
            feature_names=self.feature_names, 
            sample_idx=0
        )
        
        # Verificar resultado
        self.assertIn("feature_importance", result)
        self.assertIn("plot_path", result)
        self.assertTrue(os.path.exists(result["plot_path"]))
        
        # Verificar se todas as features estão presentes
        for feature in self.feature_names:
            self.assertIn(feature, result["feature_importance"])
    
    def test_lime_explanation(self):
        """Testa a geração de explicações LIME."""
        # Configurar explicador LIME
        self.explainer.setup_lime_explainer(
            self.X, 
            feature_names=self.feature_names
        )
        
        # Gerar explicação para uma amostra
        result = self.explainer.explain_with_lime(
            self.model, 
            self.X, 
            sample_idx=0,
            feature_names=self.feature_names
        )
        
        # Verificar resultado
        self.assertIn("feature_weights", result)
        self.assertIn("plot_path", result)
        self.assertTrue(os.path.exists(result["plot_path"]))
    
    def test_explanation_comparison(self):
        """Testa a comparação de explicações."""
        # Configurar explicadores
        self.explainer.setup_shap_explainer(self.model, self.X)
        self.explainer.setup_lime_explainer(
            self.X, 
            feature_names=self.feature_names
        )
        
        # Comparar explicações
        result = self.explainer.compare_explanations(
            self.model, 
            self.X, 
            sample_idx=0,
            feature_names=self.feature_names
        )
        
        # Verificar resultado
        self.assertIn("shap_explanation", result)
        self.assertIn("lime_explanation", result)
        self.assertIn("comparison_plot", result)
        self.assertIn("correlation", result)
        self.assertTrue(os.path.exists(result["comparison_plot"]))
        
        # Verificar correlação
        self.assertIsInstance(result["correlation"], float)

if __name__ == '__main__':
    unittest.main()
```

### Passo 7: Documentação e Melhores Práticas

Crie um arquivo de documentação em `docs/model_interpretability.md`:

```markdown
# Interpretabilidade de Modelos no Autocura

Este documento descreve a implementação e uso das bibliotecas SHAP e LIME no sistema Autocura para fornecer explicabilidade aos modelos de machine learning.

## Visão Geral

A interpretabilidade de modelos é essencial para entender as decisões dos modelos de machine learning e aumentar a confiança nas previsões. No Autocura, as bibliotecas SHAP (SHapley Additive exPlanations) e LIME (Local Interpretable Model-agnostic Explanations) são utilizadas para:

1. Explicar previsões individuais
2. Entender a importância global das features
3. Analisar o impacto de features específicas
4. Comparar diferentes métodos de explicabilidade

## Componentes Principais

1. **ModelExplainer**: Wrapper para as bibliotecas SHAP e LIME.
2. **Explainer**: Classe de alto nível para gerenciar múltiplos modelos e explicações.

## Métodos de Explicabilidade

### SHAP (SHapley Additive exPlanations)

O SHAP é baseado na teoria dos jogos cooperativos e atribui a cada feature um valor de importância para uma previsão específica. Principais características:

- **Consistência**: Garante que uma feature com maior impacto na previsão receba um valor SHAP maior.
- **Precisão Local**: Explica exatamente a saída do modelo para uma previsão específica.
- **Missingness**: Lida corretamente com valores ausentes.

### LIME (Local Interpretable Model-agnostic Explanations)

O LIME cria um modelo interpretável localmente que aproxima o comportamento do modelo original em torno de uma previsão específica. Principais características:

- **Modelo-agnóstico**: Funciona com qualquer tipo de modelo.
- **Interpretabilidade Local**: Explica previsões individuais.
- **Simplicidade**: Usa modelos lineares para aproximar o comportamento local.

## Casos de Uso

### Explicação de Previsões Individuais

```python
from src.interpretability.explainer import Explainer

# Inicializar explicador
explainer = Explainer()

# Registrar modelo
explainer.register_model(
    model_id="my_model",
    model=model,
    model_type="sklearn",
    training_data=X_train,
    feature_names=feature_names
)

# Explicar uma previsão específica com SHAP
shap_explanation = explainer.explain_prediction(
    model_id="my_model",
    data=X_test,
    sample_idx=0,
    method="shap"
)

# Explicar uma previsão específica com LIME
lime_explanation = explainer.explain_prediction(
    model_id="my_model",
    data=X_test,
    sample_idx=0,
    method="lime"
)

# Comparar explicações SHAP e LIME
comparison = explainer.explain_prediction(
    model_id="my_model",
    data=X_test,
    sample_idx=0,
    method="both"
)
```

### Explicação Global do Modelo

```python
# Gerar explicação global do modelo
global_explanation = explainer.explain_model(
    model_id="my_model",
    data=X_test,
    method="shap"
)

# Acessar importância global das features
feature_importance = global_explanation["global_feature_importance"]
```

### Análise de Impacto de Features

```python
# Analisar o impacto de uma feature específica
feature_impact = explainer.explain_feature_impact(
    model_id="my_model",
    feature_name="feature_name",
    data=X_test
)
```

## Integração com Frameworks

### Scikit-learn

```python
# Registrar modelo scikit-learn
explainer.register_model(
    model_id="sklearn_model",
    model=model,
    model_type="sklearn",
    training_data=X_train,
    feature_names=feature_names
)
```

### PyTorch

```python
# Registrar modelo PyTorch
explainer.register_model(
    model_id="pytorch_model",
    model=model,
    model_type="pytorch",
    training_data=X_train,
    feature_names=feature_names
)
```

### TensorFlow

```python
# Registrar modelo TensorFlow
explainer.register_model(
    model_id="tensorflow_model",
    model=model,
    model_type="tensorflow",
    training_data=X_train,
    feature_names=feature_names
)
```

## Melhores Práticas

1. **Dados de Background**: Use um conjunto representativo de dados para o explicador SHAP.
2. **Interpretação de Resultados**: Valores SHAP positivos indicam contribuição positiva para a previsão, valores negativos indicam contribuição negativa.
3. **Comparação de Métodos**: Compare SHAP e LIME para obter uma visão mais completa da explicabilidade.
4. **Visualização**: Use gráficos para facilitar a interpretação das explicações.
5. **Documentação**: Documente as explicações e insights obtidos para referência futura.

## Limitações

1. **Custo Computacional**: SHAP pode ser computacionalmente intensivo para modelos complexos e grandes conjuntos de dados.
2. **Estabilidade**: LIME pode produzir explicações diferentes para a mesma previsão devido à sua natureza estocástica.
3. **Correlação entre Features**: Ambos os métodos podem ter dificuldades com features altamente correlacionadas.

## Referências

- [Documentação SHAP](https://shap.readthedocs.io/en/latest/)
- [Documentação LIME](https://lime-ml.readthedocs.io/en/latest/)
- [Artigo SHAP: A Unified Approach to Interpreting Model Predictions](https://papers.nips.cc/paper/7062-a-unified-approach-to-interpreting-model-predictions)
- [Artigo LIME: "Why Should I Trust You?": Explaining the Predictions of Any Classifier](https://arxiv.org/abs/1602.04938)
```

### Considerações Finais para SHAP e LIME

- **Requisitos Computacionais**: SHAP pode ser computacionalmente intensivo, especialmente para modelos complexos; considere usar amostras menores para análise inicial.
- **Escolha do Método**: SHAP é geralmente mais preciso, mas LIME pode ser mais rápido; use ambos para uma visão mais completa.
- **Interpretação**: Lembre-se que as explicações são aproximações do comportamento do modelo, não representações exatas.
- **Visualização**: Invista em visualizações claras para facilitar a interpretação das explicações.
- **Integração no Fluxo de Trabalho**: Incorpore a explicabilidade desde o início do desenvolvimento do modelo, não apenas como uma etapa final.
