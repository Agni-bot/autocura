import logging
from typing import Dict, Any, List, Callable
from datetime import datetime, time
import schedule
import time as time_module
import pytz
import json
from pathlib import Path
import threading

from ..memoria.gerenciador_memoria import GerenciadorMemoria
from ..monitoramento.coletor_metricas import ColetorMetricas
from ..core.diagnostico_autocura import SistemaDiagnosticoAutocura

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("agendador")

class Agendador:
    """Sistema de agendamento de tarefas"""
    
    def __init__(self, gerenciador_memoria: GerenciadorMemoria,
                 coletor_metricas: ColetorMetricas,
                 sistema_diagnostico: SistemaDiagnosticoAutocura):
        self.gerenciador_memoria = gerenciador_memoria
        self.coletor_metricas = coletor_metricas
        self.sistema_diagnostico = sistema_diagnostico
        self.config = self._carregar_config()
        self.tarefas_agendadas = {}
        self.thread_agendador = None
        self.running = False
        logger.info("Sistema de Agendamento inicializado")
    
    def _carregar_config(self) -> Dict[str, Any]:
        """Carrega a configuração do agendador"""
        try:
            caminho_config = Path("config/agendador.json")
            if caminho_config.exists():
                with open(caminho_config, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Arquivo de configuração não encontrado. Usando configuração padrão.")
                return self._criar_config_padrao()
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {str(e)}")
            return self._criar_config_padrao()
    
    def _criar_config_padrao(self) -> Dict[str, Any]:
        """Cria configuração padrão do agendador"""
        return {
            "tarefas": {
                "coleta_metricas": {
                    "intervalo": 60,
                    "horario_inicio": "00:00",
                    "horario_fim": "23:59",
                    "dias_semana": [1, 2, 3, 4, 5, 6, 7],
                    "timezone": "America/Sao_Paulo"
                },
                "diagnostico": {
                    "intervalo": 300,
                    "horario_inicio": "00:00",
                    "horario_fim": "23:59",
                    "dias_semana": [1, 2, 3, 4, 5, 6, 7],
                    "timezone": "America/Sao_Paulo"
                },
                "limpeza_logs": {
                    "intervalo": 86400,
                    "horario_inicio": "00:00",
                    "horario_fim": "23:59",
                    "dias_semana": [1],
                    "timezone": "America/Sao_Paulo"
                }
            },
            "configuracoes": {
                "max_tarefas_concorrentes": 5,
                "timeout_tarefa": 300,
                "retry": {
                    "max_tentativas": 3,
                    "intervalo_entre_tentativas": 60
                }
            }
        }
    
    def iniciar(self) -> None:
        """Inicia o agendador de tarefas"""
        try:
            if self.running:
                logger.warning("Agendador já está em execução")
                return
            
            self.running = True
            self.thread_agendador = threading.Thread(target=self._executar_agendador)
            self.thread_agendador.start()
            
            logger.info("Agendador iniciado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar agendador: {str(e)}")
            self.running = False
    
    def parar(self) -> None:
        """Para o agendador de tarefas"""
        try:
            if not self.running:
                logger.warning("Agendador não está em execução")
                return
            
            self.running = False
            if self.thread_agendador:
                self.thread_agendador.join()
            
            logger.info("Agendador parado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao parar agendador: {str(e)}")
    
    def _executar_agendador(self) -> None:
        """Executa o loop principal do agendador"""
        try:
            # Configura timezone
            timezone = pytz.timezone(self.config["tarefas"]["coleta_metricas"]["timezone"])
            
            # Agenda tarefas
            self._agendar_tarefas()
            
            # Loop principal
            while self.running:
                schedule.run_pending()
                time_module.sleep(1)
            
        except Exception as e:
            logger.error(f"Erro no loop do agendador: {str(e)}")
            self.running = False
    
    def _agendar_tarefas(self) -> None:
        """Agenda todas as tarefas configuradas"""
        try:
            # Agenda coleta de métricas
            self._agendar_tarefa(
                "coleta_metricas",
                self._tarefa_coleta_metricas,
                self.config["tarefas"]["coleta_metricas"]
            )
            
            # Agenda diagnóstico
            self._agendar_tarefa(
                "diagnostico",
                self._tarefa_diagnostico,
                self.config["tarefas"]["diagnostico"]
            )
            
            # Agenda limpeza de logs
            self._agendar_tarefa(
                "limpeza_logs",
                self._tarefa_limpeza_logs,
                self.config["tarefas"]["limpeza_logs"]
            )
            
            logger.info("Tarefas agendadas com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao agendar tarefas: {str(e)}")
    
    def _agendar_tarefa(self, nome: str, funcao: Callable, config: Dict[str, Any]) -> None:
        """Agenda uma tarefa específica"""
        try:
            # Configura timezone
            timezone = pytz.timezone(config["timezone"])
            
            # Agenda tarefa
            if config["intervalo"] > 0:
                schedule.every(config["intervalo"]).seconds.do(
                    self._executar_tarefa_com_retry,
                    nome=nome,
                    funcao=funcao
                )
            
            # Registra tarefa
            self.tarefas_agendadas[nome] = {
                "config": config,
                "ultima_execucao": None,
                "proxima_execucao": None,
                "status": "agendada"
            }
            
            logger.info(f"Tarefa '{nome}' agendada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao agendar tarefa '{nome}': {str(e)}")
    
    def _executar_tarefa_com_retry(self, nome: str, funcao: Callable) -> None:
        """Executa uma tarefa com retry em caso de falha"""
        try:
            max_tentativas = self.config["configuracoes"]["retry"]["max_tentativas"]
            intervalo = self.config["configuracoes"]["retry"]["intervalo_entre_tentativas"]
            
            for tentativa in range(max_tentativas):
                try:
                    # Atualiza status
                    self.tarefas_agendadas[nome]["status"] = "executando"
                    self.tarefas_agendadas[nome]["ultima_execucao"] = datetime.now().isoformat()
                    
                    # Executa tarefa
                    funcao()
                    
                    # Atualiza status
                    self.tarefas_agendadas[nome]["status"] = "concluida"
                    break
                    
                except Exception as e:
                    logger.error(f"Erro na tentativa {tentativa + 1} da tarefa '{nome}': {str(e)}")
                    
                    if tentativa < max_tentativas - 1:
                        time_module.sleep(intervalo)
                    else:
                        self.tarefas_agendadas[nome]["status"] = "falha"
                        raise
            
        except Exception as e:
            logger.error(f"Erro ao executar tarefa '{nome}': {str(e)}")
            self.tarefas_agendadas[nome]["status"] = "falha"
    
    def _tarefa_coleta_metricas(self) -> None:
        """Tarefa de coleta de métricas"""
        try:
            # Coleta métricas do sistema
            metricas_sistema = self.coletor_metricas.coletar_metricas_sistema()
            
            # Coleta métricas da aplicação
            metricas_aplicacao = self.coletor_metricas.coletar_metricas_aplicacao()
            
            # Verifica limites
            alertas = self.coletor_metricas.verificar_limites(metricas_sistema)
            
            logger.info("Coleta de métricas executada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro na tarefa de coleta de métricas: {str(e)}")
            raise
    
    def _tarefa_diagnostico(self) -> None:
        """Tarefa de diagnóstico do sistema"""
        try:
            # Executa diagnóstico
            resultado = self.sistema_diagnostico.executar_diagnostico()
            
            # Executa correções se necessário
            if resultado["status"] == "completo" and resultado["diagnosticos"]:
                for diagnostico in resultado["diagnosticos"]:
                    self.sistema_diagnostico.executar_correcao(diagnostico)
            
            logger.info("Diagnóstico executado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro na tarefa de diagnóstico: {str(e)}")
            raise
    
    def _tarefa_limpeza_logs(self) -> None:
        """Tarefa de limpeza de logs"""
        try:
            # Limpa memória antiga
            self.gerenciador_memoria.limpar_memoria_antiga()
            
            logger.info("Limpeza de logs executada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro na tarefa de limpeza de logs: {str(e)}")
            raise
    
    def obter_status_tarefas(self) -> Dict[str, Any]:
        """Retorna o status atual das tarefas"""
        return {
            "tarefas": self.tarefas_agendadas,
            "status": "running" if self.running else "stopped",
            "timestamp": datetime.now().isoformat()
        } 