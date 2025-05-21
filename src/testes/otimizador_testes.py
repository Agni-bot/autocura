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

# Carregar variáveis de ambiente
load_dotenv()

class OtimizadorTestes:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('AI_API_KEY'),
            base_url=os.getenv('AI_API_ENDPOINT')
        )
        self.modelo = os.getenv('AI_API_PRIMARY_MODEL')
        self.resultados = []
        self.memoria_path = Path('memoria_compartilhada.json')

    def executar_testes(self) -> Dict[str, Any]:
        """Executa os testes e coleta os resultados."""
        print("🚀 Iniciando execução dos testes...")
        
        # Executar pytest com cobertura
        resultado = subprocess.run(
            ["pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing"],
            capture_output=True,
            text=True
        )
        
        # Processar a saída para extrair informações relevantes
        saida_processada = self._processar_saida_teste(resultado.stdout)
        
        return {
            "exit_code": resultado.returncode,
            "resumo": saida_processada,
            "erros": resultado.stderr if resultado.stderr else "Nenhum erro encontrado"
        }

    def _processar_saida_teste(self, saida: str) -> Dict[str, Any]:
        """Processa a saída dos testes para extrair informações relevantes."""
        linhas = saida.split('\n')
        resumo = {
            "total_testes": 0,
            "testes_passaram": 0,
            "testes_falharam": 0,
            "cobertura": {},
            "testes_falhos": []
        }
        
        # Padrão para encontrar o número total de testes
        padrao_total = re.compile(r'collected (\d+) items')
        
        for linha in linhas:
            # Verificar total de testes
            match_total = padrao_total.search(linha)
            if match_total:
                resumo["total_testes"] = int(match_total.group(1))
            
            # Verificar testes passados/falhados
            if "PASSED" in linha:
                resumo["testes_passaram"] += 1
            elif "FAILED" in linha:
                resumo["testes_falharam"] += 1
                resumo["testes_falhos"].append(linha)
            
            # Verificar cobertura
            if "TOTAL" in linha and "COVERAGE" in linha:
                partes = linha.split()
                if len(partes) >= 2:
                    resumo["cobertura"] = {
                        "total": partes[-1],
                        "detalhes": []
                    }
        
        return resumo

    def analisar_resultados(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Utiliza a API de IA para analisar os resultados dos testes."""
        # Criar um resumo conciso dos resultados
        resumo = {
            "total_testes": resultados["resumo"]["total_testes"],
            "testes_passaram": resultados["resumo"]["testes_passaram"],
            "testes_falharam": resultados["resumo"]["testes_falharam"],
            "cobertura": resultados["resumo"]["cobertura"],
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
            print(f"❌ Erro ao analisar resultados: {str(e)}")
            return {
                "erro": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def registrar_analise(self, analise: Dict[str, Any]):
        """Registra a análise na memória compartilhada."""
        try:
            with open(self.memoria_path, 'r+', encoding='utf-8') as f:
                memoria = json.load(f)
                
                # Adicionar evento de análise
                memoria['log_eventos'].append({
                    "data": analise['timestamp'],
                    "evento": "Análise de Testes com IA",
                    "detalhes": analise.get('analise', analise.get('erro', 'Erro desconhecido'))
                })
                
                # Atualizar métricas de teste
                if 'memoria_tecnica' not in memoria:
                    memoria['memoria_tecnica'] = {}
                if 'metricas' not in memoria['memoria_tecnica']:
                    memoria['memoria_tecnica']['metricas'] = {}
                
                memoria['memoria_tecnica']['metricas']['ultima_analise_testes'] = analise
                
                f.seek(0)
                json.dump(memoria, f, indent=2, ensure_ascii=False)
                f.truncate()
                
            print("✅ Análise registrada na memória compartilhada")
        except Exception as e:
            print(f"❌ Erro ao registrar análise: {str(e)}")

    def executar_otimizacao(self):
        """Executa o processo completo de otimização de testes."""
        print("🔄 Iniciando processo de otimização de testes...")
        
        # Executar testes
        resultados = self.executar_testes()
        
        # Analisar resultados com IA
        print("🤖 Analisando resultados com IA...")
        analise = self.analisar_resultados(resultados)
        
        # Registrar análise
        self.registrar_analise(analise)
        
        # Exibir resultados
        print("\n📊 Resultados da Análise:")
        print(analise.get('analise', analise.get('erro', 'Erro na análise')))
        
        return analise

if __name__ == "__main__":
    otimizador = OtimizadorTestes()
    otimizador.executar_otimizacao() 