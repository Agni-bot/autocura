import os
import json
import subprocess
import openai
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any
import pytest
from pathlib import Path
import re
import logging
import sys
from dataclasses import dataclass, asdict
from enum import Enum

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('testes.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('OtimizadorTestes')

class StatusTeste(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
    XFAIL = "XFAIL"
    XPASS = "XPASS"

    def __str__(self):
        return self.value

@dataclass
class ResultadoTeste:
    nome: str
    status: StatusTeste
    duracao: float
    mensagem_erro: str = ""
    traceback: str = ""

    def to_dict(self):
        return {
            "nome": self.nome,
            "status": str(self.status),
            "duracao": self.duracao,
            "mensagem_erro": self.mensagem_erro,
            "traceback": self.traceback
        }

class OtimizadorTestes:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('AI_API_KEY'),
            base_url=os.getenv('AI_API_ENDPOINT')
        )
        self.modelo = os.getenv('AI_API_PRIMARY_MODEL')
        self.resultados = []
        self.memoria_path = Path('memoria_compartilhada.json')
        self.testes_detalhados = []

    def executar_testes(self) -> Dict[str, Any]:
        """Executa os testes e coleta os resultados."""
        logger.info("Iniciando execução dos testes...")
        
        # Executar pytest com cobertura e relatório detalhado
        resultado = subprocess.run(
            [
                "pytest", 
                "tests/", 
                "-v", 
                "--cov=src", 
                "--cov-report=term-missing",
                "--cov-report=html",
                "--cov-report=xml",
                "--junitxml=test-results.xml",
                "--tb=long"
            ],
            capture_output=True,
            text=True
        )
        
        # Processar a saída para extrair informações relevantes
        saida_processada = self._processar_saida_teste(resultado.stdout)
        
        # Registrar resultados detalhados
        self._registrar_resultados_detalhados(resultado.stdout)
        
        return {
            "exit_code": resultado.returncode,
            "resumo": saida_processada,
            "erros": resultado.stderr if resultado.stderr else "Nenhum erro encontrado",
            "testes_detalhados": [teste.to_dict() for teste in self.testes_detalhados]
        }

    def _processar_saida_teste(self, saida: str) -> Dict[str, Any]:
        """Processa a saída dos testes para extrair informações relevantes."""
        linhas = saida.split('\n')
        resumo = {
            "total_testes": 0,
            "testes_passaram": 0,
            "testes_falharam": 0,
            "testes_erro": 0,
            "testes_pulados": 0,
            "cobertura": {
                "total": "0%",
                "detalhes": []
            },
            "testes_falhos": [],
            "duracao_total": 0.0
        }
        
        # Padrões para extração de informações
        padrao_total = re.compile(r'collected (\d+) items')
        padrao_duracao = re.compile(r'(\d+\.\d+)s')
        padrao_cobertura = re.compile(r'TOTAL.*?(\d+)%')
        
        for linha in linhas:
            # Verificar total de testes
            match_total = padrao_total.search(linha)
            if match_total:
                resumo["total_testes"] = int(match_total.group(1))
                logger.info(f"Total de testes coletados: {resumo['total_testes']}")
            
            # Verificar duração
            match_duracao = padrao_duracao.search(linha)
            if match_duracao:
                resumo["duracao_total"] = float(match_duracao.group(1))
            
            # Verificar cobertura
            match_cobertura = padrao_cobertura.search(linha)
            if match_cobertura:
                resumo["cobertura"]["total"] = f"{match_cobertura.group(1)}%"
                logger.info(f"Cobertura total: {resumo['cobertura']['total']}")
            
            # Processar resultados de testes individuais
            if any(status.value in linha for status in StatusTeste):
                partes = linha.split()
                if len(partes) >= 2:
                    nome_teste = partes[0]
                    status = next(s for s in StatusTeste if s.value in linha)
                    
                    # Corrigir parser de duração
                    duracao = 0.0
                    if len(partes) > 1 and partes[-1].endswith('s'):
                        try:
                            duracao = float(partes[-1].replace('s', ''))
                        except ValueError:
                            duracao = 0.0
                    
                    resultado = ResultadoTeste(
                        nome=nome_teste,
                        status=status,
                        duracao=duracao
                    )
                    
                    if status == StatusTeste.FAILED:
                        resumo["testes_falharam"] += 1
                        resumo["testes_falhos"].append({
                            "nome": nome_teste,
                            "status": str(status),
                            "duracao": resultado.duracao
                        })
                    elif status == StatusTeste.PASSED:
                        resumo["testes_passaram"] += 1
                    elif status == StatusTeste.ERROR:
                        resumo["testes_erro"] += 1
                    elif status == StatusTeste.SKIPPED:
                        resumo["testes_pulados"] += 1
                    
                    self.testes_detalhados.append(resultado)
        
        return resumo

    def _registrar_resultados_detalhados(self, saida: str):
        """Registra resultados detalhados dos testes."""
        try:
            # Criar backup do arquivo atual
            if self.memoria_path.exists():
                backup_path = self.memoria_path.with_suffix('.json.bak')
                self.memoria_path.rename(backup_path)
            
            # Criar novo arquivo com os resultados
            memoria = {
                "memoria_tecnica": {
                    "testes": {
                        "ultima_execucao": {
                            "timestamp": datetime.now().isoformat(),
                            "resultados": [teste.to_dict() for teste in self.testes_detalhados]
                        }
                    }
                }
            }
            
            with open(self.memoria_path, 'w', encoding='utf-8') as f:
                json.dump(memoria, f, indent=2, ensure_ascii=False)
            
            logger.info("Resultados detalhados registrados na memória compartilhada")
        except Exception as e:
            logger.error(f"Erro ao registrar resultados detalhados: {str(e)}")

    def analisar_resultados(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Utiliza a API de IA para analisar os resultados dos testes."""
        # Criar um resumo conciso dos resultados
        resumo = {
            "total_testes": resultados["resumo"]["total_testes"],
            "testes_passaram": resultados["resumo"]["testes_passaram"],
            "testes_falharam": resultados["resumo"]["testes_falharam"],
            "testes_erro": resultados["resumo"]["testes_erro"],
            "testes_pulados": resultados["resumo"]["testes_pulados"],
            "cobertura": resultados["resumo"]["cobertura"],
            "duracao_total": resultados["resumo"]["duracao_total"],
            "erros_principais": resultados["resumo"]["testes_falhos"][:5] if resultados["resumo"]["testes_falhos"] else []
        }

        prompt = f"""
        Analise os resultados dos testes abaixo e forneça:
        1. Resumo dos testes executados
        2. Identificação de problemas críticos
        3. Sugestões de otimização
        4. Priorização de correções

        Resultados:
        {json.dumps(resumo, indent=2)}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": "Você é um especialista em testes de software e otimização de código."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                "analise": response.choices[0].message.content,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao analisar resultados: {str(e)}")
            return {
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def registrar_analise(self, analise: Dict[str, Any]):
        """Registra a análise na memória compartilhada."""
        try:
            # Criar backup do arquivo atual
            if self.memoria_path.exists():
                backup_path = self.memoria_path.with_suffix('.json.bak')
                self.memoria_path.rename(backup_path)
            
            # Criar novo arquivo com a análise
            memoria = {
                "log_eventos": [{
                    "data": analise['timestamp'],
                    "evento": "Análise de Testes com IA",
                    "detalhes": analise.get('analise', analise.get('erro', 'Erro desconhecido'))
                }],
                "memoria_tecnica": {
                    "metricas": {
                        "ultima_analise_testes": analise
                    }
                }
            }
            
            with open(self.memoria_path, 'w', encoding='utf-8') as f:
                json.dump(memoria, f, indent=2, ensure_ascii=False)
            
            logger.info("Análise registrada na memória compartilhada")
        except Exception as e:
            logger.error(f"Erro ao registrar análise: {str(e)}")

    def executar_otimizacao(self):
        """Executa o processo completo de otimização de testes."""
        logger.info("Iniciando processo de otimização de testes...")
        
        # Executar testes
        resultados = self.executar_testes()
        
        # Analisar resultados com IA
        logger.info("Analisando resultados com IA...")
        analise = self.analisar_resultados(resultados)
        
        # Registrar análise
        self.registrar_analise(analise)
        
        # Exibir resultados
        logger.info("\nResultados da Análise:")
        logger.info(analise.get('analise', analise.get('erro', 'Erro na análise')))
        
        return analise

if __name__ == "__main__":
    otimizador = OtimizadorTestes()
    otimizador.executar_otimizacao() 