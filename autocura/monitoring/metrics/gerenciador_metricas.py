import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import json
import os
from pathlib import Path
import yaml

# Usar singleton do Prometheus
from .prometheus_singleton import get_counter, get_gauge, get_histogram, get_registry

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
    """
    Gerenciador avançado de métricas do sistema AutoCura.
    Utiliza Prometheus singleton para evitar conflitos.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.logger = logging.getLogger(__name__)
        
        # Inicializa storage
        self.storage_path = Path(self.config.get("base_dir", "data/metricas"))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Métricas Prometheus usando singleton (evita duplicatas)
        self.metrics_created = get_counter("metricas_criadas", "Total de métricas criadas")
        self.metrics_processed = get_counter("metricas_processadas", "Total de métricas processadas")
        self.system_health = get_gauge("system_health_score", "Score de saúde do sistema")
        self.processing_duration = get_histogram("metrics_processing_duration", "Duração do processamento de métricas")
        
        # Cache interno
        self._metrics_cache: Dict[str, Metrica] = {}
        self._alerts: List[Dict[str, Any]] = []
        
        self.logger.info("Gerenciador de Métricas inicializado")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuração padrão do gerenciador"""
        return {
            "base_dir": "data/metricas",
            "retention_days": 30,
            "batch_size": 100,
            "alert_thresholds": {
                "cpu": 80.0,
                "memoria": 85.0,
                "disco": 90.0
            }
        }
    
    def criar_metrica(self, 
                     nome: str, 
                     valor: Any, 
                     tipo: str = "gauge",
                     labels: Optional[Dict[str, str]] = None,
                     descricao: str = "",
                     unidade: str = "") -> str:
        """
        Cria uma nova métrica no sistema.
        
        Returns:
            str: ID da métrica criada
        """
        try:
            metric_id = f"{nome}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            metrica = Metrica(
                id=metric_id,
                nome=nome,
                tipo=tipo,
                valor=valor,
                timestamp=datetime.now(),
                labels=labels or {},
                descricao=descricao,
                unidade=unidade
            )
            
            # Armazena no cache
            self._metrics_cache[metric_id] = metrica
            
            # Atualiza Prometheus
            self._update_prometheus_metric(metrica)
            
            # Incrementa contador
            self.metrics_created.inc()
            
            self.logger.debug(f"Métrica criada: {nome} = {valor}")
            return metric_id
            
        except Exception as e:
            self.logger.error(f"Erro ao criar métrica {nome}: {e}")
            raise
    
    def _update_prometheus_metric(self, metrica: Metrica):
        """Atualiza métrica no Prometheus"""
        try:
            if metrica.tipo == "gauge":
                gauge = get_gauge(f"autocura_{metrica.nome}", metrica.descricao, list(metrica.labels.keys()))
                if metrica.labels:
                    gauge.labels(**metrica.labels).set(float(metrica.valor))
                else:
                    gauge.set(float(metrica.valor))
                    
            elif metrica.tipo == "counter":
                counter = get_counter(f"autocura_{metrica.nome}", metrica.descricao, list(metrica.labels.keys()))
                if metrica.labels:
                    counter.labels(**metrica.labels).inc(float(metrica.valor))
                else:
                    counter.inc(float(metrica.valor))
                    
        except Exception as e:
            self.logger.warning(f"Erro ao atualizar Prometheus para {metrica.nome}: {e}")
    
    def obter_metrica(self, metric_id: str) -> Optional[Metrica]:
        """Obtém métrica por ID"""
        return self._metrics_cache.get(metric_id)
    
    def listar_metricas(self, filtros: Optional[Dict[str, Any]] = None) -> List[Metrica]:
        """Lista métricas com filtros opcionais"""
        metricas = list(self._metrics_cache.values())
        
        if filtros:
            # Aplica filtros
            if "tipo" in filtros:
                metricas = [m for m in metricas if m.tipo == filtros["tipo"]]
            if "nome" in filtros:
                metricas = [m for m in metricas if filtros["nome"] in m.nome]
        
        return metricas
    
    def calcular_estatisticas(self) -> Dict[str, Any]:
        """Calcula estatísticas das métricas"""
        try:
            metricas = list(self._metrics_cache.values())
            
            if not metricas:
                return {"total": 0, "tipos": {}, "ultima_atualizacao": None}
            
            tipos_count = {}
            for metrica in metricas:
                tipos_count[metrica.tipo] = tipos_count.get(metrica.tipo, 0) + 1
            
            ultima_atualizacao = max(m.timestamp for m in metricas)
            
            return {
                "total": len(metricas),
                "tipos": tipos_count,
                "ultima_atualizacao": ultima_atualizacao.isoformat(),
                "periodo": {
                    "inicio": min(m.timestamp for m in metricas).isoformat(),
                    "fim": ultima_atualizacao.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}
    
    def verificar_alertas(self) -> List[Dict[str, Any]]:
        """Verifica e retorna alertas baseados em thresholds"""
        alertas = []
        thresholds = self.config["alert_thresholds"]
        
        try:
            for metrica in self._metrics_cache.values():
                if metrica.nome == "cpu_usage" and float(metrica.valor) > thresholds["cpu"]:
                    alertas.append({
                        "tipo": "cpu_high",
                        "metrica": metrica.nome,
                        "valor": metrica.valor,
                        "threshold": thresholds["cpu"],
                        "timestamp": metrica.timestamp.isoformat(),
                        "severidade": "warning" if float(metrica.valor) < thresholds["cpu"] * 1.2 else "critical"
                    })
                    
                elif metrica.nome == "memory_usage" and float(metrica.valor) > thresholds["memoria"]:
                    alertas.append({
                        "tipo": "memory_high", 
                        "metrica": metrica.nome,
                        "valor": metrica.valor,
                        "threshold": thresholds["memoria"],
                        "timestamp": metrica.timestamp.isoformat(),
                        "severidade": "warning" if float(metrica.valor) < thresholds["memoria"] * 1.2 else "critical"
                    })
            
            self._alerts = alertas
            return alertas
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar alertas: {e}")
            return []
    
    def salvar_metricas(self, formato: str = "json") -> bool:
        """Salva métricas em arquivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if formato == "json":
                arquivo = self.storage_path / f"metricas_{timestamp}.json"
                data = {
                    "timestamp": datetime.now().isoformat(),
                    "total_metricas": len(self._metrics_cache),
                    "metricas": [
                        {
                            "id": m.id,
                            "nome": m.nome,
                            "tipo": m.tipo,
                            "valor": m.valor,
                            "timestamp": m.timestamp.isoformat(),
                            "labels": m.labels,
                            "descricao": m.descricao,
                            "unidade": m.unidade
                        }
                        for m in self._metrics_cache.values()
                    ]
                }
                
                with open(arquivo, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
                self.logger.info(f"Métricas salvas em: {arquivo}")
                return True
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar métricas: {e}")
            return False
    
    def carregar_metricas(self, arquivo: str) -> bool:
        """Carrega métricas de arquivo"""
        try:
            arquivo_path = Path(arquivo)
            if not arquivo_path.exists():
                self.logger.warning(f"Arquivo não encontrado: {arquivo}")
                return False
                
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for metric_data in data.get("metricas", []):
                metrica = Metrica(
                    id=metric_data["id"],
                    nome=metric_data["nome"],
                    tipo=metric_data["tipo"],
                    valor=metric_data["valor"],
                    timestamp=datetime.fromisoformat(metric_data["timestamp"]),
                    labels=metric_data.get("labels", {}),
                    descricao=metric_data.get("descricao", ""),
                    unidade=metric_data.get("unidade", "")
                )
                self._metrics_cache[metrica.id] = metrica
                
            self.logger.info(f"Métricas carregadas de: {arquivo}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar métricas: {e}")
            return False
    
    def limpar_metricas_antigas(self, dias: int = None) -> int:
        """Remove métricas mais antigas que X dias"""
        try:
            dias = dias or self.config["retention_days"]
            cutoff_date = datetime.now() - timedelta(days=dias)
            
            metricas_removidas = 0
            for metric_id, metrica in list(self._metrics_cache.items()):
                if metrica.timestamp < cutoff_date:
                    del self._metrics_cache[metric_id]
                    metricas_removidas += 1
            
            self.logger.info(f"Removidas {metricas_removidas} métricas antigas (>{dias} dias)")
            return metricas_removidas
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar métricas antigas: {e}")
            return 0
    
    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do gerenciador"""
        try:
            stats = self.calcular_estatisticas()
            alertas = self.verificar_alertas()
            
            # Calcula score de saúde
            health_score = 1.0
            if alertas:
                critical_alerts = [a for a in alertas if a.get("severidade") == "critical"]
                warning_alerts = [a for a in alertas if a.get("severidade") == "warning"]
                health_score -= (len(critical_alerts) * 0.3 + len(warning_alerts) * 0.1)
                health_score = max(0.0, health_score)
            
            # Atualiza gauge Prometheus
            self.system_health.set(health_score)
            
            return {
                "status": "healthy" if health_score > 0.8 else "degraded" if health_score > 0.5 else "unhealthy",
                "health_score": health_score,
                "total_metricas": stats.get("total", 0),
                "alertas_ativas": len(alertas),
                "ultima_atualizacao": stats.get("ultima_atualizacao"),
                "prometheus_metrics": len(self._metrics_cache)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status de saúde: {e}")
            return {"status": "error", "error": str(e)} 