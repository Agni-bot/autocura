import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from src.monitoramento.coletor_metricas import Metrica

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Diagnostico:
    """Classe que representa um diagnóstico gerado pela rede neural."""
    timestamp: datetime
    anomalia_detectada: bool
    score_anomalia: float
    padrao_detectado: str
    confianca: float
    metricas_relevantes: List[str]
    recomendacoes: List[str]

class RedeNeuralAltaOrdem(nn.Module):
    """Rede neural de alta ordem para diagnóstico de anomalias e padrões."""
    
    def __init__(
        self,
        input_size: int,
        hidden_sizes: List[int] = [128, 64, 32],
        dropout_rate: float = 0.2,
        learning_rate: float = 0.001
    ):
        super().__init__()
        
        # Configuração da rede
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.dropout_rate = dropout_rate
        
        # Construção das camadas
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_size),
                nn.Dropout(dropout_rate)
            ])
            prev_size = hidden_size
        
        # Camadas de saída
        layers.extend([
            nn.Linear(prev_size, 64),  # Camada de features latentes
            nn.ReLU(),
            nn.Linear(64, 32),  # Camada de padrões
            nn.ReLU(),
            nn.Linear(32, 1)   # Saída de anomalia
        ])
        
        self.network = nn.Sequential(*layers)
        
        # Otimizador
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        
        # Critério de perda
        self.criterion = nn.MSELoss()
        
        # Mapeamento de padrões conhecidos
        self.padroes_conhecidos = {
            "alta_cpu": {
                "descricao": "Alto uso de CPU",
                "metricas": ["cpu_usage"],
                "threshold": 0.8
            },
            "alta_memoria": {
                "descricao": "Alto uso de memória",
                "metricas": ["memory_usage"],
                "threshold": 0.85
            },
            "alta_latencia": {
                "descricao": "Alta latência de requisições",
                "metricas": ["request_latency"],
                "threshold": 1.0
            },
            "alta_taxa_erro": {
                "descricao": "Alta taxa de erros",
                "metricas": ["error_rate"],
                "threshold": 0.05
            }
        }
        
        logger.info("Rede neural de alta ordem inicializada")

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass da rede neural."""
        features = self.network[:-2](x)  # Features latentes
        padroes = self.network[-2](features)  # Camada de padrões
        anomalia = self.network[-1](padroes)  # Score de anomalia
        return anomalia, padroes

    def preparar_dados(
        self,
        metricas: List[Metrica]
    ) -> torch.Tensor:
        """Prepara os dados de entrada para a rede neural."""
        # Extrai valores das métricas
        valores = []
        for metrica in metricas:
            if isinstance(metrica.valor, (int, float)):
                valores.append(float(metrica.valor))
            else:
                valores.append(0.0)
        
        # Normaliza os valores
        valores = np.array(valores)
        valores = (valores - np.mean(valores)) / (np.std(valores) + 1e-8)
        
        return torch.FloatTensor(valores)

    def detectar_anomalia(
        self,
        metricas: List[Metrica],
        threshold: float = 0.8
    ) -> Diagnostico:
        """Detecta anomalias nas métricas fornecidas."""
        # Prepara dados
        x = self.preparar_dados(metricas)
        
        # Faz inferência
        with torch.no_grad():
            score_anomalia, padroes = self(x)
            score_anomalia = score_anomalia.item()
        
        # Identifica padrões
        padrao_detectado = self._identificar_padrao(padroes)
        
        # Gera diagnóstico
        anomalia_detectada = score_anomalia > threshold
        confianca = abs(score_anomalia - threshold) / threshold
        
        # Identifica métricas relevantes
        metricas_relevantes = self._identificar_metricas_relevantes(
            metricas,
            padrao_detectado
        )
        
        # Gera recomendações
        recomendacoes = self._gerar_recomendacoes(
            padrao_detectado,
            metricas_relevantes
        )
        
        return Diagnostico(
            timestamp=datetime.now(),
            anomalia_detectada=anomalia_detectada,
            score_anomalia=score_anomalia,
            padrao_detectado=padrao_detectado,
            confianca=confianca,
            metricas_relevantes=metricas_relevantes,
            recomendacoes=recomendacoes
        )

    def _identificar_padrao(
        self,
        padroes: torch.Tensor
    ) -> str:
        """Identifica o padrão mais provável baseado na saída da rede."""
        padroes = padroes.numpy()
        padrao_idx = np.argmax(padroes)
        
        # Mapeia índice para nome do padrão
        padroes_nomes = list(self.padroes_conhecidos.keys())
        return padroes_nomes[padrao_idx]

    def _identificar_metricas_relevantes(
        self,
        metricas: List[Metrica],
        padrao: str
    ) -> List[str]:
        """Identifica as métricas mais relevantes para o padrão detectado."""
        if padrao in self.padroes_conhecidos:
            return self.padroes_conhecidos[padrao]["metricas"]
        return [m.nome for m in metricas]

    def _gerar_recomendacoes(
        self,
        padrao: str,
        metricas_relevantes: List[str]
    ) -> List[str]:
        """Gera recomendações baseadas no padrão detectado."""
        recomendacoes = []
        
        if padrao == "alta_cpu":
            recomendacoes.extend([
                "Verificar processos com alto consumo de CPU",
                "Considerar escalar horizontalmente",
                "Otimizar código de processamento intensivo"
            ])
        elif padrao == "alta_memoria":
            recomendacoes.extend([
                "Verificar vazamentos de memória",
                "Aumentar limite de memória do container",
                "Otimizar uso de memória"
            ])
        elif padrao == "alta_latencia":
            recomendacoes.extend([
                "Verificar gargalos de rede",
                "Otimizar queries de banco de dados",
                "Considerar cache"
            ])
        elif padrao == "alta_taxa_erro":
            recomendacoes.extend([
                "Verificar logs de erro",
                "Implementar retry com backoff",
                "Revisar tratamento de exceções"
            ])
        
        return recomendacoes

    def treinar(
        self,
        dados_treino: List[List[Metrica]],
        epocas: int = 100,
        batch_size: int = 32
    ):
        """Treina a rede neural com dados históricos."""
        self.train()
        
        for epoca in range(epocas):
            total_loss = 0
            batches = 0
            
            # Embaralha dados
            np.random.shuffle(dados_treino)
            
            # Processa em batches
            for i in range(0, len(dados_treino), batch_size):
                batch = dados_treino[i:i + batch_size]
                
                # Prepara batch
                x_batch = torch.stack([
                    self.preparar_dados(metricas)
                    for metricas in batch
                ])
                
                # Forward pass
                anomalia, _ = self(x_batch)
                
                # Calcula loss (usando autoencoder)
                loss = self.criterion(anomalia, x_batch)
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
                batches += 1
            
            # Log do progresso
            if (epoca + 1) % 10 == 0:
                logger.info(
                    f"Época {epoca + 1}/{epocas}, "
                    f"Loss: {total_loss/batches:.4f}"
                )

    def salvar_modelo(self, caminho: str):
        """Salva o modelo treinado."""
        torch.save({
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'input_size': self.input_size,
            'hidden_sizes': self.hidden_sizes,
            'dropout_rate': self.dropout_rate
        }, caminho)
        logger.info(f"Modelo salvo em {caminho}")

    def carregar_modelo(self, caminho: str):
        """Carrega um modelo salvo."""
        checkpoint = torch.load(caminho)
        self.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        logger.info(f"Modelo carregado de {caminho}") 