import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import json
import os
from pathlib import Path
import yaml
from prometheus_client import Counter, Gauge, Histogram, Summary

@dataclass
class Metrica:
    """Representa uma métrica do sistema."""
    id: str
    nome: str
    tipo: str
    valor: Any
    timestamp: datetime
    labels: Dict[str, str]
    descricao: str
    unidade: str

class GerenciadorMetricas:
    """Módulo Gerenciador de Métricas para gerenciar métricas do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializa o gerenciador de métricas.
        
        Args:
            config: Configuração do gerenciador
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Diretório base para arquivos de métricas
        self.base_dir = Path(config.get("base_dir", "metricas"))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache de métricas
        self.metricas: Dict[str, Metrica] = {}
        
        # Histórico de valores
        self.historico: Dict[str, List[Metrica]] = {}
        
        # Configuração de tipos
        self.tipos = {
            "counter": Counter,
            "gauge": Gauge,
            "histogram": Histogram,
            "summary": Summary
        }
        
        # Métricas Prometheus
        self.metricas_prometheus = {
            "metricas_criadas": Counter(
                "metricas_criadas_total",
                "Total de métricas criadas",
                ["tipo"]
            ),
            "metricas_atualizadas": Counter(
                "metricas_atualizadas_total",
                "Total de métricas atualizadas",
                ["tipo"]
            ),
            "tempo_operacao": Histogram(
                "tempo_operacao_metricas_seconds",
                "Tempo de operações nas métricas",
                ["operacao"]
            )
        }
        
        # Configuração de alertas
        self.alertas = {
            "limite_superior": {},
            "limite_inferior": {},
            "tendencia": {},
            "anomalia": {}
        }
        
        # Handlers de alerta
        self.handlers_alerta = {
            "log": self._handler_alerta_log,
            "email": self._handler_alerta_email,
            "slack": self._handler_alerta_slack,
            "webhook": self._handler_alerta_webhook
        }
        
        self.logger.info("Gerenciador de Métricas inicializado")
    
    async def criar_metrica(self, nome: str, tipo: str, valor: Any,
                          labels: Dict[str, str] = None, descricao: str = "",
                          unidade: str = "") -> Optional[Metrica]:
        """Cria uma nova métrica.
        
        Args:
            nome: Nome da métrica
            tipo: Tipo da métrica
            valor: Valor inicial
            labels: Labels da métrica
            descricao: Descrição da métrica
            unidade: Unidade da métrica
            
        Returns:
            Métrica criada ou None em caso de erro
        """
        if tipo not in self.tipos:
            self.logger.error(f"Tipo de métrica desconhecido: {tipo}")
            return None
        
        try:
            with self.metricas_prometheus["tempo_operacao"].labels(operacao="criar").time():
                # Gera ID único
                metrica_id = f"{tipo}_{nome}"
                
                # Cria métrica
                metrica = Metrica(
                    id=metrica_id,
                    nome=nome,
                    tipo=tipo,
                    valor=valor,
                    timestamp=datetime.now(),
                    labels=labels or {},
                    descricao=descricao,
                    unidade=unidade
                )
                
                # Cria métrica Prometheus
                prom_metrica = self.tipos[tipo](
                    metrica_id,
                    descricao,
                    list(labels.keys()) if labels else []
                )
                
                # Inicializa com valor
                if labels:
                    prom_metrica.labels(**labels).set(float(valor))
                else:
                    prom_metrica.set(float(valor))
                
                # Adiciona ao cache
                self.metricas[metrica_id] = metrica
                
                # Inicializa histórico
                self.historico[metrica_id] = [metrica]
                
                # Atualiza métricas
                self.metricas_prometheus["metricas_criadas"].labels(tipo=tipo).inc()
                
                self.logger.info(f"Métrica criada: {metrica_id}")
                return metrica
                
        except Exception as e:
            self.logger.error(f"Erro ao criar métrica: {e}")
            return None
    
    async def atualizar_metrica(self, metrica_id: str, valor: Any) -> bool:
        """Atualiza uma métrica existente.
        
        Args:
            metrica_id: ID da métrica
            valor: Novo valor
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            with self.metricas_prometheus["tempo_operacao"].labels(operacao="atualizar").time():
                # Obtém métrica
                metrica = self.metricas.get(metrica_id)
                if not metrica:
                    return False
                
                # Cria nova versão
                nova_metrica = Metrica(
                    id=metrica.id,
                    nome=metrica.nome,
                    tipo=metrica.tipo,
                    valor=valor,
                    timestamp=datetime.now(),
                    labels=metrica.labels,
                    descricao=metrica.descricao,
                    unidade=metrica.unidade
                )
                
                # Atualiza métrica Prometheus
                prom_metrica = self.tipos[metrica.tipo](
                    metrica_id,
                    metrica.descricao,
                    list(metrica.labels.keys()) if metrica.labels else []
                )
                
                if metrica.labels:
                    prom_metrica.labels(**metrica.labels).set(float(valor))
                else:
                    prom_metrica.set(float(valor))
                
                # Atualiza cache
                self.metricas[metrica_id] = nova_metrica
                
                # Adiciona ao histórico
                self.historico[metrica_id].append(nova_metrica)
                
                # Verifica alertas
                await self._verificar_alertas(nova_metrica)
                
                # Atualiza métricas
                self.metricas_prometheus["metricas_atualizadas"].labels(tipo=metrica.tipo).inc()
                
                self.logger.info(f"Métrica atualizada: {metrica_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar métrica: {e}")
            return False
    
    async def _verificar_alertas(self, metrica: Metrica) -> None:
        """Verifica alertas para uma métrica.
        
        Args:
            metrica: Métrica a ser verificada
        """
        try:
            # Verifica limite superior
            limite = self.alertas["limite_superior"].get(metrica.id)
            if limite and float(metrica.valor) > limite:
                await self._disparar_alerta(metrica, "limite_superior", limite)
            
            # Verifica limite inferior
            limite = self.alertas["limite_inferior"].get(metrica.id)
            if limite and float(metrica.valor) < limite:
                await self._disparar_alerta(metrica, "limite_inferior", limite)
            
            # Verifica tendência
            if metrica.id in self.alertas["tendencia"]:
                historico = self.historico[metrica.id][-10:]  # Últimas 10 medições
                if len(historico) >= 3:
                    valores = [float(m.valor) for m in historico]
                    tendencia = (valores[-1] - valores[0]) / len(valores)
                    limite = self.alertas["tendencia"][metrica.id]
                    if abs(tendencia) > limite:
                        await self._disparar_alerta(metrica, "tendencia", tendencia)
            
            # Verifica anomalia
            if metrica.id in self.alertas["anomalia"]:
                historico = self.historico[metrica.id][-100:]  # Últimas 100 medições
                if len(historico) >= 10:
                    valores = [float(m.valor) for m in historico]
                    media = sum(valores) / len(valores)
                    desvio = (sum((v - media) ** 2 for v in valores) / len(valores)) ** 0.5
                    limite = self.alertas["anomalia"][metrica.id]
                    if abs(float(metrica.valor) - media) > limite * desvio:
                        await self._disparar_alerta(metrica, "anomalia", float(metrica.valor))
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar alertas: {e}")
    
    async def _disparar_alerta(self, metrica: Metrica, tipo: str, valor: Any) -> None:
        """Dispara alertas para uma métrica.
        
        Args:
            metrica: Métrica que gerou o alerta
            tipo: Tipo do alerta
            valor: Valor que disparou o alerta
        """
        try:
            # Formata mensagem
            mensagem = {
                "metrica": metrica.id,
                "tipo": tipo,
                "valor": valor,
                "timestamp": datetime.now().isoformat(),
                "labels": metrica.labels
            }
            
            # Processa handlers
            for handler in self.handlers_alerta.values():
                await handler(mensagem)
                
        except Exception as e:
            self.logger.error(f"Erro ao disparar alerta: {e}")
    
    async def _handler_alerta_log(self, mensagem: Dict[str, Any]) -> None:
        """Handler de alerta para log.
        
        Args:
            mensagem: Mensagem do alerta
        """
        self.logger.warning(f"Alerta: {mensagem}")
    
    async def _handler_alerta_email(self, mensagem: Dict[str, Any]) -> None:
        """Handler de alerta para email.
        
        Args:
            mensagem: Mensagem do alerta
        """
        # TODO: Implementar envio de email
        pass
    
    async def _handler_alerta_slack(self, mensagem: Dict[str, Any]) -> None:
        """Handler de alerta para Slack.
        
        Args:
            mensagem: Mensagem do alerta
        """
        # TODO: Implementar integração com Slack
        pass
    
    async def _handler_alerta_webhook(self, mensagem: Dict[str, Any]) -> None:
        """Handler de alerta para webhook.
        
        Args:
            mensagem: Mensagem do alerta
        """
        # TODO: Implementar chamada de webhook
        pass
    
    async def obter_metrica(self, metrica_id: str) -> Optional[Metrica]:
        """Obtém uma métrica pelo ID.
        
        Args:
            metrica_id: ID da métrica
            
        Returns:
            Métrica ou None se não encontrada
        """
        return self.metricas.get(metrica_id)
    
    async def buscar_metricas(self, tipo: Optional[str] = None,
                            labels: Optional[Dict[str, str]] = None) -> List[Metrica]:
        """Busca métricas por critérios.
        
        Args:
            tipo: Tipo da métrica (opcional)
            labels: Labels da métrica (opcional)
            
        Returns:
            Lista de métricas encontradas
        """
        metricas = []
        
        for metrica in self.metricas.values():
            # Filtra por tipo
            if tipo and metrica.tipo != tipo:
                continue
            
            # Filtra por labels
            if labels and not all(metrica.labels.get(k) == v for k, v in labels.items()):
                continue
            
            metricas.append(metrica)
        
        return metricas
    
    async def obter_historico(self, metrica_id: str,
                            inicio: Optional[datetime] = None,
                            fim: Optional[datetime] = None) -> List[Metrica]:
        """Obtém o histórico de valores de uma métrica.
        
        Args:
            metrica_id: ID da métrica
            inicio: Data/hora inicial (opcional)
            fim: Data/hora final (opcional)
            
        Returns:
            Lista de valores históricos
        """
        historico = self.historico.get(metrica_id, [])
        
        if inicio:
            historico = [m for m in historico if m.timestamp >= inicio]
        if fim:
            historico = [m for m in historico if m.timestamp <= fim]
        
        return historico
    
    async def configurar_alerta(self, metrica_id: str, tipo: str,
                              valor: Any) -> bool:
        """Configura um alerta para uma métrica.
        
        Args:
            metrica_id: ID da métrica
            tipo: Tipo do alerta
            valor: Valor do alerta
            
        Returns:
            True se configurado com sucesso
        """
        if tipo not in self.alertas:
            self.logger.error(f"Tipo de alerta desconhecido: {tipo}")
            return False
        
        try:
            self.alertas[tipo][metrica_id] = valor
            self.logger.info(f"Alerta configurado: {metrica_id} - {tipo}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar alerta: {e}")
            return False
    
    async def obter_estatisticas(self) -> Dict[str, Any]:
        """Obtém estatísticas das métricas.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            "timestamp": datetime.now(),
            "total_metricas": len(self.metricas),
            "por_tipo": {},
            "por_label": {},
            "total_alertas": 0
        }
        
        # Conta métricas por tipo e label
        for metrica in self.metricas.values():
            if metrica.tipo not in stats["por_tipo"]:
                stats["por_tipo"][metrica.tipo] = 0
            stats["por_tipo"][metrica.tipo] += 1
            
            for label, valor in metrica.labels.items():
                if label not in stats["por_label"]:
                    stats["por_label"][label] = {}
                if valor not in stats["por_label"][label]:
                    stats["por_label"][label][valor] = 0
                stats["por_label"][label][valor] += 1
        
        # Conta total de alertas
        for alertas in self.alertas.values():
            stats["total_alertas"] += len(alertas)
        
        return stats 