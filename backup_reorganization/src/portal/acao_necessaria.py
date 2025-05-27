"""
Módulo responsável por gerenciar e executar ações necessárias no sistema.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

class GerenciadorAcoes:
    def __init__(self):
        """
        Inicializa o gerenciador de ações.
        Configura logging e carrega configurações necessárias.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Configuração do handler de arquivo
        fh = logging.FileHandler('logs/acoes.log')
        fh.setLevel(logging.INFO)
        
        # Configuração do formato do log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        
        # Carrega configurações de ações
        self.config_acoes = self._carregar_configuracoes()
        
        self.acoes_pendentes = []
        self.acoes_executadas = []
        self.acoes_falhas = []

    def _carregar_configuracoes(self) -> Dict:
        """
        Carrega configurações de ações do arquivo de configuração.
        
        Returns:
            Dict: Configurações carregadas
        """
        try:
            config_path = os.path.join('config', 'acoes.json')
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {str(e)}")
            return {}

    def registrar_acao(self, acao: Dict) -> bool:
        """
        Registra uma nova ação a ser executada.
        
        Args:
            acao (Dict): Dados da ação a ser registrada
            
        Returns:
            bool: True se o registro foi bem sucedido, False caso contrário
        """
        try:
            self.logger.info(f"Registrando nova ação: {acao}")
            
            # Validação básica da ação
            if not self._validar_acao(acao):
                self.logger.error("Ação inválida")
                return False
            
            # Adiciona metadados
            acao['id'] = self._gerar_id_acao()
            acao['timestamp_registro'] = datetime.now().isoformat()
            acao['status'] = 'pendente'
            
            self.acoes_pendentes.append(acao)
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao registrar ação: {str(e)}")
            return False

    def _validar_acao(self, acao: Dict) -> bool:
        """
        Valida se uma ação possui todos os campos necessários.
        
        Args:
            acao (Dict): Ação a ser validada
            
        Returns:
            bool: True se a ação é válida, False caso contrário
        """
        campos_obrigatorios = ['tipo', 'descricao', 'prioridade']
        
        for campo in campos_obrigatorios:
            if campo not in acao:
                self.logger.error(f"Campo obrigatório ausente: {campo}")
                return False
        
        return True

    def _gerar_id_acao(self) -> str:
        """
        Gera um ID único para a ação.
        
        Returns:
            str: ID gerado
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"acao_{timestamp}"

    def executar_acao(self, id_acao: str) -> bool:
        """
        Executa uma ação pendente.
        
        Args:
            id_acao (str): ID da ação a ser executada
            
        Returns:
            bool: True se a execução foi bem sucedida, False caso contrário
        """
        try:
            # Encontra a ação
            acao = next((a for a in self.acoes_pendentes if a['id'] == id_acao), None)
            if not acao:
                self.logger.error(f"Ação não encontrada: {id_acao}")
                return False
            
            self.logger.info(f"Executando ação: {acao}")
            
            # Executa a ação
            sucesso = self._executar_acao_especifica(acao)
            
            if sucesso:
                acao['status'] = 'executada'
                acao['timestamp_execucao'] = datetime.now().isoformat()
                self.acoes_executadas.append(acao)
                self.acoes_pendentes.remove(acao)
            else:
                acao['status'] = 'falha'
                acao['timestamp_falha'] = datetime.now().isoformat()
                self.acoes_falhas.append(acao)
                self.acoes_pendentes.remove(acao)
            
            return sucesso
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ação: {str(e)}")
            return False

    def _executar_acao_especifica(self, acao: Dict) -> bool:
        """
        Executa uma ação específica baseada em seu tipo.
        
        Args:
            acao (Dict): Ação a ser executada
            
        Returns:
            bool: True se a execução foi bem sucedida, False caso contrário
        """
        try:
            tipo_acao = acao['tipo']
            
            # TODO: Implementar lógica específica para cada tipo de ação
            # - Reiniciar serviço
            # - Limpar cache
            # - Atualizar configuração
            # - etc.
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ação específica: {str(e)}")
            return False

    def listar_acoes_pendentes(self) -> List[Dict]:
        """
        Lista todas as ações pendentes.
        
        Returns:
            List[Dict]: Lista de ações pendentes
        """
        return self.acoes_pendentes

    def listar_acoes_executadas(self) -> List[Dict]:
        """
        Lista todas as ações já executadas.
        
        Returns:
            List[Dict]: Lista de ações executadas
        """
        return self.acoes_executadas

    def listar_acoes_falhas(self) -> List[Dict]:
        """
        Lista todas as ações que falharam.
        
        Returns:
            List[Dict]: Lista de ações com falha
        """
        return self.acoes_falhas

    def obter_status_acao(self, id_acao: str) -> Optional[Dict]:
        """
        Obtém o status atual de uma ação específica.
        
        Args:
            id_acao (str): ID da ação
            
        Returns:
            Optional[Dict]: Status da ação ou None se não encontrada
        """
        # Procura em todas as listas
        for lista in [self.acoes_pendentes, self.acoes_executadas, self.acoes_falhas]:
            acao = next((a for a in lista if a['id'] == id_acao), None)
            if acao:
                return {
                    'id': acao['id'],
                    'status': acao['status'],
                    'timestamp': acao.get('timestamp_execucao') or 
                                acao.get('timestamp_falha') or 
                                acao.get('timestamp_registro')
                }
        
        return None 