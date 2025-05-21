#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import logging
import subprocess
import platform
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ProblemaDependencia:
    pacote: str
    versao: str
    erro: str
    solucao: str
    data_ocorrencia: datetime
    resolvido: bool = False

class GerenciadorDependencias:
    def __init__(self, arquivo_historico: str = "memoria/dependencias.json"):
        self.arquivo_historico = arquivo_historico
        self.logger = logging.getLogger(__name__)
        self.historico: List[ProblemaDependencia] = []
        self._carregar_historico()
        
    def _carregar_historico(self):
        """Carrega o histórico de problemas de dependências."""
        if os.path.exists(self.arquivo_historico):
            try:
                with open(self.arquivo_historico, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                    self.historico = [
                        ProblemaDependencia(
                            pacote=p['pacote'],
                            versao=p['versao'],
                            erro=p['erro'],
                            solucao=p['solucao'],
                            data_ocorrencia=datetime.fromisoformat(p['data_ocorrencia']),
                            resolvido=p['resolvido']
                        )
                        for p in dados
                    ]
            except Exception as e:
                self.logger.error(f"Erro ao carregar histórico: {e}")
                self.historico = []
    
    def _salvar_historico(self):
        """Salva o histórico de problemas de dependências."""
        try:
            os.makedirs(os.path.dirname(self.arquivo_historico), exist_ok=True)
            with open(self.arquivo_historico, 'w', encoding='utf-8') as f:
                json.dump(
                    [
                        {
                            'pacote': p.pacote,
                            'versao': p.versao,
                            'erro': p.erro,
                            'solucao': p.solucao,
                            'data_ocorrencia': p.data_ocorrencia.isoformat(),
                            'resolvido': p.resolvido
                        }
                        for p in self.historico
                    ],
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico: {e}")
    
    def registrar_problema(self, pacote: str, versao: str, erro: str, solucao: str):
        """Registra um novo problema de dependência."""
        problema = ProblemaDependencia(
            pacote=pacote,
            versao=versao,
            erro=erro,
            solucao=solucao,
            data_ocorrencia=datetime.now()
        )
        self.historico.append(problema)
        self._salvar_historico()
        self.logger.info(f"Problema registrado para {pacote} {versao}")
    
    def verificar_compatibilidade_python(self) -> bool:
        """Verifica se a versão do Python é compatível com o sistema."""
        versao_atual = sys.version_info
        versao_minima = (3, 10)
        versao_maxima = (3, 13)
        
        if versao_atual < versao_minima:
            self.logger.warning(f"Python {versao_minima[0]}.{versao_minima[1]} é recomendado para este projeto. Versão atual: {versao_atual[0]}.{versao_atual[1]}")
            return False
            
        if versao_atual > versao_maxima:
            self.logger.warning(f"Python {versao_maxima[0]}.{versao_maxima[1]} é a versão máxima suportada. Versão atual: {versao_atual[0]}.{versao_atual[1]}")
            return False
            
        """Verifica se a versão do Python é compatível com as dependências."""
        versao_python = platform.python_version_tuple()
        versao_major = int(versao_python[0])
        versao_minor = int(versao_python[1])
        
        if versao_major > 3 or (versao_major == 3 and versao_minor > 10):
            self.logger.warning(
                "Python 3.10 é recomendado para este projeto. "
                f"Versão atual: {platform.python_version()}"
            )
            return False
        return True
    
    def verificar_dependencias_sistema(self) -> Dict[str, bool]:
        """Verifica dependências do sistema operacional."""
        dependencias = {
            'pg_config': False,
            'gcc': False,
            'make': False
        }
        
        try:
            # Verifica pg_config
            subprocess.run(['pg_config', '--version'], capture_output=True)
            dependencias['pg_config'] = True
        except FileNotFoundError:
            self.logger.warning("pg_config não encontrado. Necessário para psycopg2-binary")
        
        try:
            # Verifica gcc
            subprocess.run(['gcc', '--version'], capture_output=True)
            dependencias['gcc'] = True
        except FileNotFoundError:
            self.logger.warning("gcc não encontrado. Necessário para compilação de pacotes")
        
        try:
            # Verifica make
            subprocess.run(['make', '--version'], capture_output=True)
            dependencias['make'] = True
        except FileNotFoundError:
            self.logger.warning("make não encontrado. Necessário para compilação de pacotes")
        
        return dependencias
    
    def sugerir_solucao(self, pacote: str, versao: str) -> Optional[str]:
        """Sugere uma solução baseada no histórico de problemas."""
        for problema in self.historico:
            if problema.pacote == pacote and problema.versao == versao:
                return problema.solucao
        return None
    
    def executar_autocura(self):
        """Executa o processo de autocura de dependências."""
        self.logger.info("Iniciando processo de autocura de dependências...")
        
        # Verifica versão do Python
        if not self.verificar_compatibilidade_python():
            self.logger.error("Versão do Python incompatível")
            return False
        
        # Verifica dependências do sistema
        dependencias = self.verificar_dependencias_sistema()
        if not all(dependencias.values()):
            self.logger.error("Dependências do sistema faltando")
            return False
        
        # Tenta instalar dependências
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                check=True
            )
            self.logger.info("Dependências instaladas com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Erro ao instalar dependências: {e}")
            return False

def main():
    """Função principal para execução do script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    gerenciador = GerenciadorDependencias()
    sucesso = gerenciador.executar_autocura()
    
    if not sucesso:
        sys.exit(1)

if __name__ == '__main__':
    main() 