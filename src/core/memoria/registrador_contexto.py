"""
Registrador de Contexto - Sistema AutoCura
=======================================

Este módulo gerencia o registro automático de contexto,
salvando todas as interações e instruções no arquivo de memória.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class RegistradorContexto:
    """
    Gerencia o registro automático de contexto do sistema.
    Salva todas as interações e instruções no arquivo de memória.
    """
    
    def __init__(self, arquivo_memoria: str = "memoria_compartilhada.json"):
        """
        Inicializa o registrador de contexto.
        
        Args:
            arquivo_memoria: Caminho do arquivo de memória compartilhada
        """
        self.arquivo_memoria = arquivo_memoria
        self.memoria = self._carregar_memoria()
    
    def _carregar_memoria(self) -> Dict:
        """
        Carrega a memória compartilhada do arquivo.
        
        Returns:
            Dict: Memória carregada
        """
        try:
            if os.path.exists(self.arquivo_memoria):
                with open(self.arquivo_memoria, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self._criar_memoria_inicial()
        except Exception as e:
            print(f"Erro ao carregar memória: {e}")
            return self._criar_memoria_inicial()
    
    def _criar_memoria_inicial(self) -> Dict:
        """
        Cria uma memória inicial vazia.
        
        Returns:
            Dict: Memória inicial
        """
        return {
            "ultima_atualizacao": datetime.now().isoformat(),
            "estado_atual": {
                "configuracoes": {},
                "estrutura_diretorios": {},
                "ultimas_acoes": [],
                "contexto_atual": {
                    "tarefa": "",
                    "status": "inicial",
                    "proximos_passos": []
                }
            },
            "historico_interacoes": [],
            "instrucoes_ia": [],
            "log_eventos": []
        }
    
    def salvar_memoria(self) -> bool:
        """
        Salva a memória compartilhada no arquivo.
        
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            self.memoria["ultima_atualizacao"] = datetime.now().isoformat()
            with open(self.arquivo_memoria, 'w', encoding='utf-8') as f:
                json.dump(self.memoria, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar memória: {e}")
            return False
    
    def registrar_interacao(self, tipo: str, conteudo: str, detalhes: Optional[Dict] = None) -> bool:
        """
        Registra uma nova interação no histórico.
        
        Args:
            tipo: Tipo da interação (comando, resposta, erro, etc)
            conteudo: Conteúdo da interação
            detalhes: Detalhes adicionais da interação
            
        Returns:
            bool: True se registrou com sucesso
        """
        try:
            interacao = {
                "timestamp": datetime.now().isoformat(),
                "tipo": tipo,
                "conteudo": conteudo
            }
            
            if detalhes:
                interacao["detalhes"] = detalhes
            
            self.memoria["historico_interacoes"].append(interacao)
            return self.salvar_memoria()
        except Exception as e:
            print(f"Erro ao registrar interação: {e}")
            return False
    
    def registrar_instrucao(self, instrucao: str, contexto: str, prioridade: int = 1) -> bool:
        """
        Registra uma nova instrução para IAs.
        
        Args:
            instrucao: Instrução a ser registrada
            contexto: Contexto da instrução
            prioridade: Prioridade da instrução (1-5)
            
        Returns:
            bool: True se registrou com sucesso
        """
        try:
            self.memoria["instrucoes_ia"].append({
                "timestamp": datetime.now().isoformat(),
                "instrucao": instrucao,
                "contexto": contexto,
                "prioridade": prioridade,
                "status": "pendente"
            })
            return self.salvar_memoria()
        except Exception as e:
            print(f"Erro ao registrar instrução: {e}")
            return False
    
    def registrar_evento(self, evento: str, detalhes: str) -> bool:
        """
        Registra um novo evento no log.
        
        Args:
            evento: Nome do evento
            detalhes: Detalhes do evento
            
        Returns:
            bool: True se registrou com sucesso
        """
        try:
            self.memoria["log_eventos"].append({
                "data": datetime.now().isoformat(),
                "evento": evento,
                "detalhes": detalhes
            })
            return self.salvar_memoria()
        except Exception as e:
            print(f"Erro ao registrar evento: {e}")
            return False
    
    def obter_instrucoes_pendentes(self) -> List[Dict]:
        """
        Retorna as instruções pendentes para IAs.
        
        Returns:
            List[Dict]: Lista de instruções pendentes
        """
        return [
            inst for inst in self.memoria["instrucoes_ia"]
            if inst["status"] == "pendente"
        ]
    
    def marcar_instrucao_concluida(self, timestamp: str) -> bool:
        """
        Marca uma instrução como concluída.
        
        Args:
            timestamp: Timestamp da instrução
            
        Returns:
            bool: True se marcou com sucesso
        """
        try:
            for inst in self.memoria["instrucoes_ia"]:
                if inst["timestamp"] == timestamp:
                    inst["status"] = "concluida"
                    return self.salvar_memoria()
            return False
        except Exception as e:
            print(f"Erro ao marcar instrução: {e}")
            return False
    
    def obter_historico_recente(self, limite: int = 10) -> List[Dict]:
        """
        Retorna o histórico recente de interações.
        
        Args:
            limite: Número máximo de interações
            
        Returns:
            List[Dict]: Histórico recente
        """
        return self.memoria["historico_interacoes"][-limite:]
    
    def obter_eventos_recentes(self, limite: int = 10) -> List[Dict]:
        """
        Retorna os eventos recentes.
        
        Args:
            limite: Número máximo de eventos
            
        Returns:
            List[Dict]: Eventos recentes
        """
        return self.memoria["log_eventos"][-limite:]
    
    def limpar_historico(self) -> bool:
        """
        Limpa o histórico de interações.
        
        Returns:
            bool: True se limpou com sucesso
        """
        try:
            self.memoria["historico_interacoes"] = []
            return self.salvar_memoria()
        except Exception as e:
            print(f"Erro ao limpar histórico: {e}")
            return False
    
    def exportar_contexto(self, arquivo: str) -> bool:
        """
        Exporta o contexto atual para um arquivo.
        
        Args:
            arquivo: Caminho do arquivo de saída
            
        Returns:
            bool: True se exportou com sucesso
        """
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(self.memoria, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao exportar contexto: {e}")
            return False 