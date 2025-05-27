"""
Registrador de Contexto Automático - Sistema AutoCura
=====================================================

Este módulo mantém registro automático de todas as interações e eventos do sistema.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from .gerenciador_memoria import GerenciadorMemoria

class RegistradorContexto:
    """
    Registra automaticamente o contexto e eventos do sistema.
    """
    
    def __init__(self, arquivo_memoria: str = "memoria_compartilhada.json"):
        """
        Inicializa o registrador de contexto.
        
        Args:
            arquivo_memoria: Caminho do arquivo de memória compartilhada
        """
        self.gerenciador_memoria = GerenciadorMemoria(arquivo_memoria)
        self.eventos_recentes = []
        self.instrucoes_pendentes = []
    
    def registrar_evento(self, tipo_evento: str, descricao: str, dados_extras: Optional[Dict] = None) -> bool:
        """
        Registra um evento no sistema.
        
        Args:
            tipo_evento: Tipo do evento
            descricao: Descrição do evento
            dados_extras: Dados adicionais opcionais
            
        Returns:
            bool: True se registrou com sucesso
        """
        try:
            evento = {
                "timestamp": datetime.now().isoformat(),
                "tipo": tipo_evento,
                "descricao": descricao,
                "dados": dados_extras or {}
            }
            
            self.eventos_recentes.append(evento)
            
            # Mantém apenas os últimos 100 eventos na memória
            if len(self.eventos_recentes) > 100:
                self.eventos_recentes.pop(0)
            
            # Registra no gerenciador de memória
            return self.gerenciador_memoria.registrar_acao(tipo_evento, descricao)
            
        except Exception as e:
            print(f"Erro ao registrar evento: {e}")
            return False
    
    def registrar_instrucao(self, titulo: str, descricao: str, prioridade: int = 1) -> bool:
        """
        Registra uma instrução para outras IAs.
        
        Args:
            titulo: Título da instrução
            descricao: Descrição detalhada
            prioridade: Prioridade (1-5)
            
        Returns:
            bool: True se registrou com sucesso
        """
        try:
            instrucao = {
                "id": len(self.instrucoes_pendentes) + 1,
                "timestamp": datetime.now().isoformat(),
                "titulo": titulo,
                "descricao": descricao,
                "prioridade": prioridade,
                "status": "pendente"
            }
            
            self.instrucoes_pendentes.append(instrucao)
            
            return self.registrar_evento("instrucao_criada", f"Instrução criada: {titulo}")
            
        except Exception as e:
            print(f"Erro ao registrar instrução: {e}")
            return False
    
    def obter_eventos_recentes(self, limit: int = 20) -> List[Dict]:
        """
        Retorna eventos recentes.
        
        Args:
            limit: Número máximo de eventos a retornar
            
        Returns:
            List[Dict]: Lista de eventos recentes
        """
        return self.eventos_recentes[-limit:]
    
    def obter_instrucoes_pendentes(self) -> List[Dict]:
        """
        Retorna instruções pendentes.
        
        Returns:
            List[Dict]: Lista de instruções pendentes
        """
        return [i for i in self.instrucoes_pendentes if i["status"] == "pendente"]
    
    def marcar_instrucao_concluida(self, instrucao_id: int) -> bool:
        """
        Marca uma instrução como concluída.
        
        Args:
            instrucao_id: ID da instrução
            
        Returns:
            bool: True se marcou com sucesso
        """
        try:
            for instrucao in self.instrucoes_pendentes:
                if instrucao["id"] == instrucao_id:
                    instrucao["status"] = "concluida"
                    instrucao["concluida_em"] = datetime.now().isoformat()
                    
                    return self.registrar_evento(
                        "instrucao_concluida", 
                        f"Instrução {instrucao_id} concluída: {instrucao['titulo']}"
                    )
            
            return False
            
        except Exception as e:
            print(f"Erro ao marcar instrução como concluída: {e}")
            return False
    
    def obter_estado_atual(self) -> Dict:
        """
        Retorna o estado atual do sistema.
        
        Returns:
            Dict: Estado atual
        """
        try:
            estado = self.gerenciador_memoria.obter_estado_atual()
            
            # Adiciona informações do registrador
            estado["eventos_recentes_count"] = len(self.eventos_recentes)
            estado["instrucoes_pendentes_count"] = len(self.obter_instrucoes_pendentes())
            estado["ultima_atualizacao"] = datetime.now().isoformat()
            
            return estado
            
        except Exception as e:
            print(f"Erro ao obter estado atual: {e}")
            return {}
    
    def exportar_contexto(self, arquivo_destino: str) -> bool:
        """
        Exporta todo o contexto para um arquivo.
        
        Args:
            arquivo_destino: Caminho do arquivo de destino
            
        Returns:
            bool: True se exportou com sucesso
        """
        try:
            contexto_completo = {
                "timestamp_exportacao": datetime.now().isoformat(),
                "estado_sistema": self.obter_estado_atual(),
                "eventos_recentes": self.eventos_recentes,
                "instrucoes_pendentes": self.instrucoes_pendentes,
                "historico_interacoes": self.gerenciador_memoria.obter_historico()
            }
            
            with open(arquivo_destino, 'w', encoding='utf-8') as f:
                json.dump(contexto_completo, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao exportar contexto: {e}")
            return False
    
    def limpar_historico(self) -> bool:
        """
        Limpa o histórico de eventos e instruções.
        
        Returns:
            bool: True se limpou com sucesso
        """
        try:
            self.eventos_recentes.clear()
            self.instrucoes_pendentes.clear()
            
            return self.gerenciador_memoria.limpar_historico()
            
        except Exception as e:
            print(f"Erro ao limpar histórico: {e}")
            return False 