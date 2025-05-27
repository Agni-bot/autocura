#!/usr/bin/env python3
"""
Script para atualizar a memória compartilhada com as informações da nova estrutura.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AtualizadorMemoria:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.memoria_path = self.base_dir / 'memoria' / 'memoria_compartilhada.json'
        self.memoria: Dict[str, Any] = {}
    
    def carregar_memoria(self):
        """Carrega a memória compartilhada existente."""
        if self.memoria_path.exists():
            with open(self.memoria_path, 'r', encoding='utf-8') as f:
                self.memoria = json.load(f)
        else:
            self.memoria = {
                'versao': '1.0.0',
                'ultima_atualizacao': datetime.now().isoformat(),
                'estrutura': {},
                'modulos': {},
                'configuracoes': {},
                'historico': []
            }
    
    def atualizar_estrutura(self):
        """Atualiza informações sobre a estrutura do projeto."""
        estrutura = {
            'diretorios': {
                'config': {
                    'descricao': 'Configurações do sistema',
                    'arquivos': ['config.yaml', 'logging.yaml', 'security.yaml']
                },
                'docs': {
                    'descricao': 'Documentação do projeto',
                    'arquivos': ['estrutura_diretorios.md', 'arquitetura.md', 'manual.md']
                },
                'src': {
                    'descricao': 'Código fonte',
                    'subdiretorios': {
                        'core': {
                            'descricao': 'Módulos principais',
                            'subdiretorios': [
                                'consciencia',
                                'autocorrecao',
                                'will',
                                'interpretabilidade',
                                'validacao',
                                'sintese',
                                'predicao',
                                'adaptacao'
                            ]
                        },
                        'monitoramento': {
                            'descricao': 'Sistema de monitoramento'
                        },
                        'diagnostico': {
                            'descricao': 'Sistema de diagnóstico'
                        },
                        'gerador': {
                            'descricao': 'Gerador de ações'
                        },
                        'guardiao': {
                            'descricao': 'Guardião cognitivo'
                        },
                        'etica': {
                            'descricao': 'Validação ética'
                        },
                        'memoria': {
                            'descricao': 'Gerenciamento de memória'
                        },
                        'observabilidade': {
                            'descricao': 'Sistema de observabilidade'
                        },
                        'kubernetes': {
                            'descricao': 'Orquestração Kubernetes'
                        },
                        'web': {
                            'descricao': 'Interface web'
                        }
                    }
                }
            }
        }
        self.memoria['estrutura'] = estrutura
    
    def atualizar_modulos(self):
        """Atualiza informações sobre os módulos do sistema."""
        modulos = {
            'core': {
                'consciencia': {
                    'descricao': 'Módulo de consciência situacional',
                    'responsabilidades': [
                        'Monitoramento do ambiente',
                        'Análise de contexto',
                        'Detecção de anomalias'
                    ]
                },
                'autocorrecao': {
                    'descricao': 'Sistema de autocorreção',
                    'responsabilidades': [
                        'Identificação de problemas',
                        'Geração de correções',
                        'Aplicação de mudanças'
                    ]
                },
                'will': {
                    'descricao': 'Sistema de vontade e decisão',
                    'responsabilidades': [
                        'Tomada de decisão',
                        'Priorização de ações',
                        'Execução de tarefas'
                    ]
                }
            },
            'monitoramento': {
                'descricao': 'Sistema de monitoramento',
                'responsabilidades': [
                    'Coleta de métricas',
                    'Análise de desempenho',
                    'Detecção de problemas'
                ]
            },
            'diagnostico': {
                'descricao': 'Sistema de diagnóstico',
                'responsabilidades': [
                    'Análise de problemas',
                    'Identificação de causas',
                    'Geração de relatórios'
                ]
            },
            'gerador': {
                'descricao': 'Gerador de ações',
                'responsabilidades': [
                    'Geração de soluções',
                    'Validação de ações',
                    'Execução de correções'
                ]
            },
            'guardiao': {
                'descricao': 'Guardião cognitivo',
                'responsabilidades': [
                    'Proteção do sistema',
                    'Validação de operações',
                    'Prevenção de falhas'
                ]
            }
        }
        self.memoria['modulos'] = modulos
    
    def atualizar_configuracoes(self):
        """Atualiza informações sobre as configurações do sistema."""
        configuracoes = {
            'global': {
                'nome': 'Sistema Autocura',
                'versao': '1.0.0',
                'ambiente': 'desenvolvimento',
                'log_level': 'INFO'
            },
            'monitoramento': {
                'intervalo_coleta': 60,
                'limite_alertas': 3,
                'retencao_metricas': '30d'
            },
            'diagnostico': {
                'profundidade_analise': 3,
                'limite_historico': 1000,
                'threshold_confianca': 0.8
            },
            'gerador': {
                'max_acoes': 10,
                'timeout_geracao': 30,
                'prioridade_padrao': 'media'
            },
            'guardiao': {
                'nivel_protecao': 'alto',
                'max_tentativas': 3,
                'cooldown': 300
            }
        }
        self.memoria['configuracoes'] = configuracoes
    
    def registrar_historico(self):
        """Registra a atualização no histórico."""
        registro = {
            'data': datetime.now().isoformat(),
            'tipo': 'atualizacao_estrutura',
            'descricao': 'Reorganização da estrutura do projeto',
            'alteracoes': [
                'Padronização de nomes de diretórios',
                'Consolidação de módulos',
                'Centralização de configurações'
            ]
        }
        self.memoria['historico'].append(registro)
    
    def salvar_memoria(self):
        """Salva a memória atualizada."""
        self.memoria['ultima_atualizacao'] = datetime.now().isoformat()
        
        # Garante que o diretório existe
        self.memoria_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Salva o arquivo
        with open(self.memoria_path, 'w', encoding='utf-8') as f:
            json.dump(self.memoria, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Memória atualizada e salva em: {self.memoria_path}")
    
    def executar(self):
        """Executa a atualização completa da memória."""
        try:
            logger.info("Iniciando atualização da memória...")
            
            self.carregar_memoria()
            self.atualizar_estrutura()
            self.atualizar_modulos()
            self.atualizar_configuracoes()
            self.registrar_historico()
            self.salvar_memoria()
            
            logger.info("Atualização da memória concluída com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro durante a atualização da memória: {str(e)}")
            raise

if __name__ == '__main__':
    atualizador = AtualizadorMemoria()
    atualizador.executar() 