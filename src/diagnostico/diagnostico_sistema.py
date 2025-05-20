#!/usr/bin/env python3
"""
Implementação do diagnóstico do sistema.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import json
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DiagnosticoSistema:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.memoria_path = self.base_dir / 'memoria' / 'memoria_compartilhada.json'
        self.estado: Dict[str, Any] = {
            'ciclo_atual': 0,
            'ultima_execucao': None,
            'diagnosticos': [],
            'modelos': {},
            'historico': []
        }
        self.modelos = {
            'anomalia': None,
            'tendencia': None
        }
        self.scaler = StandardScaler()
    
    async def carregar_memoria(self):
        """Carrega o estado atual da memória compartilhada."""
        try:
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
                    self.estado.update(memoria.get('estado_diagnostico', {}))
            logger.info("Memória do diagnóstico carregada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar memória do diagnóstico: {str(e)}")
            raise
    
    async def extrair_features(self, metricas: Dict[str, Any]) -> np.ndarray:
        """Extrai features das métricas para análise."""
        try:
            features = []
            
            # Features do sistema
            sistema = metricas['sistema']
            features.extend([
                sistema['cpu']['uso_percentual'],
                sistema['memoria']['uso_percentual'],
                sistema['disco']['uso_percentual'],
                sistema['memoria']['swap_usado'] / sistema['memoria']['swap_total'] if sistema['memoria']['swap_total'] > 0 else 0
            ])
            
            # Features da aplicação
            aplicacao = metricas['aplicacao']
            features.extend([
                aplicacao['requisicoes']['latencia_media'],
                aplicacao['requisicoes']['erro'] / aplicacao['requisicoes']['total'] if aplicacao['requisicoes']['total'] > 0 else 0,
                aplicacao['recursos']['conexoes_ativas'],
                aplicacao['recursos']['threads_ativas'],
                aplicacao['processamento']['tarefas_pendentes']
            ])
            
            return np.array(features).reshape(1, -1)
        except Exception as e:
            logger.error(f"Erro ao extrair features: {str(e)}")
            raise
    
    async def treinar_modelo_anomalia(self, historico: List[Dict[str, Any]]):
        """Treina o modelo de detecção de anomalias."""
        try:
            if len(historico) < 10:  # Mínimo de amostras para treinar
                logger.warning("Histórico insuficiente para treinar modelo de anomalia")
                return
            
            # Extrair features do histórico
            X = []
            for entrada in historico:
                features = await self.extrair_features(entrada['metricas'])
                X.append(features[0])
            
            X = np.array(X)
            
            # Normalizar features
            X_scaled = self.scaler.fit_transform(X)
            
            # Treinar modelo
            self.modelos['anomalia'] = IsolationForest(
                contamination=0.1,  # 10% de anomalias esperadas
                random_state=42
            )
            self.modelos['anomalia'].fit(X_scaled)
            
            logger.info("Modelo de anomalia treinado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao treinar modelo de anomalia: {str(e)}")
            raise
    
    async def detectar_anomalias(self, metricas: Dict[str, Any]) -> bool:
        """Detecta anomalias nas métricas atuais."""
        try:
            if self.modelos['anomalia'] is None:
                logger.warning("Modelo de anomalia não treinado")
                return False
            
            # Extrair features
            features = await self.extrair_features(metricas)
            
            # Normalizar features
            features_scaled = self.scaler.transform(features)
            
            # Prever anomalia
            predicao = self.modelos['anomalia'].predict(features_scaled)
            
            # -1 indica anomalia, 1 indica normal
            return predicao[0] == -1
        except Exception as e:
            logger.error(f"Erro ao detectar anomalias: {str(e)}")
            raise
    
    async def analisar_tendencias(self, historico: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analisa tendências no histórico de métricas."""
        try:
            if len(historico) < 10:
                logger.warning("Histórico insuficiente para análise de tendências")
                return []
            
            tendencias = []
            
            # Análise de tendência de CPU
            cpu_values = [h['metricas']['sistema']['cpu']['uso_percentual'] for h in historico]
            if np.mean(cpu_values[-5:]) > np.mean(cpu_values[-10:-5]) * 1.2:  # Aumento de 20%
                tendencias.append({
                    'tipo': 'cpu',
                    'direcao': 'aumento',
                    'magnitude': 'significativa',
                    'mensagem': 'Tendência de aumento no uso de CPU'
                })
            
            # Análise de tendência de Memória
            memoria_values = [h['metricas']['sistema']['memoria']['uso_percentual'] for h in historico]
            if np.mean(memoria_values[-5:]) > np.mean(memoria_values[-10:-5]) * 1.2:
                tendencias.append({
                    'tipo': 'memoria',
                    'direcao': 'aumento',
                    'magnitude': 'significativa',
                    'mensagem': 'Tendência de aumento no uso de memória'
                })
            
            # Análise de tendência de Latência
            latencia_values = [h['metricas']['aplicacao']['requisicoes']['latencia_media'] for h in historico]
            if np.mean(latencia_values[-5:]) > np.mean(latencia_values[-10:-5]) * 1.2:
                tendencias.append({
                    'tipo': 'latencia',
                    'direcao': 'aumento',
                    'magnitude': 'significativa',
                    'mensagem': 'Tendência de aumento na latência'
                })
            
            return tendencias
        except Exception as e:
            logger.error(f"Erro ao analisar tendências: {str(e)}")
            raise
    
    async def gerar_diagnostico(self, metricas: Dict[str, Any], historico: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera diagnóstico completo do sistema."""
        try:
            diagnostico = {
                'timestamp': datetime.now().isoformat(),
                'anomalia_detectada': await self.detectar_anomalias(metricas),
                'tendencias': await self.analisar_tendencias(historico),
                'metricas_criticas': [],
                'recomendacoes': []
            }
            
            # Análise de métricas críticas
            if metricas['sistema']['cpu']['uso_percentual'] > 90:
                diagnostico['metricas_criticas'].append({
                    'tipo': 'cpu',
                    'valor': metricas['sistema']['cpu']['uso_percentual'],
                    'limite': 90,
                    'mensagem': 'Uso de CPU crítico'
                })
                diagnostico['recomendacoes'].append('Considerar escalonamento horizontal')
            
            if metricas['sistema']['memoria']['uso_percentual'] > 90:
                diagnostico['metricas_criticas'].append({
                    'tipo': 'memoria',
                    'valor': metricas['sistema']['memoria']['uso_percentual'],
                    'limite': 90,
                    'mensagem': 'Uso de memória crítico'
                })
                diagnostico['recomendacoes'].append('Otimizar uso de memória e considerar aumento de recursos')
            
            if metricas['aplicacao']['requisicoes']['latencia_media'] > 2000:
                diagnostico['metricas_criticas'].append({
                    'tipo': 'latencia',
                    'valor': metricas['aplicacao']['requisicoes']['latencia_media'],
                    'limite': 2000,
                    'mensagem': 'Latência crítica'
                })
                diagnostico['recomendacoes'].append('Investigar gargalos de performance')
            
            return diagnostico
        except Exception as e:
            logger.error(f"Erro ao gerar diagnóstico: {str(e)}")
            raise
    
    async def atualizar_historico(self, diagnostico: Dict[str, Any]):
        """Atualiza o histórico de diagnósticos."""
        try:
            self.estado['historico'].append(diagnostico)
            
            # Manter apenas as últimas 1000 entradas
            if len(self.estado['historico']) > 1000:
                self.estado['historico'] = self.estado['historico'][-1000:]
            
            logger.info("Histórico de diagnósticos atualizado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao atualizar histórico: {str(e)}")
            raise
    
    async def atualizar_memoria(self):
        """Atualiza a memória compartilhada com o novo estado."""
        try:
            self.estado['ultima_execucao'] = datetime.now().isoformat()
            self.estado['ciclo_atual'] += 1
            
            # Carrega memória existente
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
            else:
                memoria = {}
            
            # Atualiza estado do diagnóstico
            memoria['estado_diagnostico'] = self.estado
            
            # Salva memória atualizada
            with open(self.memoria_path, 'w', encoding='utf-8') as f:
                json.dump(memoria, f, indent=2, ensure_ascii=False)
            
            logger.info("Memória do diagnóstico atualizada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao atualizar memória do diagnóstico: {str(e)}")
            raise
    
    async def ciclo_diagnostico(self):
        """Executa um ciclo completo de diagnóstico."""
        try:
            logger.info("Iniciando ciclo de diagnóstico...")
            
            await self.carregar_memoria()
            
            # Carregar métricas atuais
            if self.memoria_path.exists():
                with open(self.memoria_path, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
                    metricas = memoria.get('estado_monitoramento', {}).get('metricas', {})
                    historico = memoria.get('estado_monitoramento', {}).get('historico', [])
            
            # Treinar modelo se necessário
            if self.modelos['anomalia'] is None:
                await self.treinar_modelo_anomalia(historico)
            
            # Gerar diagnóstico
            diagnostico = await self.gerar_diagnostico(metricas, historico)
            self.estado['diagnosticos'].append(diagnostico)
            
            # Atualizar histórico e memória
            await self.atualizar_historico(diagnostico)
            await self.atualizar_memoria()
            
            logger.info("Ciclo de diagnóstico concluído com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro durante o ciclo de diagnóstico: {str(e)}")
            raise
    
    async def executar_continuamente(self, intervalo: int = 300):  # 5 minutos
        """Executa ciclos de diagnóstico continuamente."""
        while True:
            try:
                await self.ciclo_diagnostico()
                await asyncio.sleep(intervalo)
            except Exception as e:
                logger.error(f"Erro no ciclo contínuo de diagnóstico: {str(e)}")
                await asyncio.sleep(intervalo)  # Aguarda antes de tentar novamente

async def main():
    """Função principal."""
    diagnostico = DiagnosticoSistema()
    await diagnostico.executar_continuamente()

if __name__ == '__main__':
    asyncio.run(main()) 