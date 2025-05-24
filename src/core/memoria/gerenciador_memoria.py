"""
Gerenciador de Memória Compartilhada - Sistema AutoCura
====================================================

Este módulo gerencia a memória compartilhada do sistema, mantendo o contexto
entre diferentes interações e sessões.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class GerenciadorMemoria:
    """
    Gerencia a memória compartilhada do sistema.
    Mantém o contexto entre diferentes interações.
    """
    
    def __init__(self, arquivo_memoria: str = "memoria_compartilhada.json"):
        """
        Inicializa o gerenciador de memória.
        
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
            "historico_interacoes": []
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
    
    def atualizar_estado(self, estado: Dict) -> bool:
        """
        Atualiza o estado atual da memória.
        
        Args:
            estado: Novo estado
            
        Returns:
            bool: True se atualizou com sucesso
        """
        try:
            self.memoria["estado_atual"].update(estado)
            return self.salvar_memoria()
        except Exception as e:
            print(f"Erro ao atualizar estado: {e}")
            return False
    
    def registrar_acao(self, acao: str, detalhes: str) -> bool:
        """
        Registra uma nova ação no histórico.
        
        Args:
            acao: Nome da ação
            detalhes: Detalhes da ação
            
        Returns:
            bool: True se registrou com sucesso
        """
        try:
            self.memoria["historico_interacoes"].append({
                "timestamp": datetime.now().isoformat(),
                "acao": acao,
                "detalhes": detalhes
            })
            return self.salvar_memoria()
        except Exception as e:
            print(f"Erro ao registrar ação: {e}")
            return False
    
    def obter_estado_atual(self) -> Dict:
        """
        Retorna o estado atual da memória.
        
        Returns:
            Dict: Estado atual
        """
        return self.memoria["estado_atual"]
    
    def obter_historico(self, limite: Optional[int] = None) -> List[Dict]:
        """
        Retorna o histórico de interações.
        
        Args:
            limite: Número máximo de interações a retornar
            
        Returns:
            List[Dict]: Histórico de interações
        """
        historico = self.memoria["historico_interacoes"]
        if limite:
            return historico[-limite:]
        return historico
    
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
    
    def atualizar_contexto(self, tarefa: str, status: str, proximos_passos: List[str]) -> bool:
        """
        Atualiza o contexto atual.
        
        Args:
            tarefa: Nome da tarefa atual
            status: Status da tarefa
            proximos_passos: Lista de próximos passos
            
        Returns:
            bool: True se atualizou com sucesso
        """
        try:
            self.memoria["estado_atual"]["contexto_atual"] = {
                "tarefa": tarefa,
                "status": status,
                "proximos_passos": proximos_passos
            }
            return self.salvar_memoria()
        except Exception as e:
            print(f"Erro ao atualizar contexto: {e}")
            return False 