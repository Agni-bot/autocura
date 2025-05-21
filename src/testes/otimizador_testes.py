import os
import json
import subprocess
import openai
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any
import pytest
from pathlib import Path

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
        
        return {
            "exit_code": resultado.returncode,
            "stdout": resultado.stdout,
            "stderr": resultado.stderr
        }

    def analisar_resultados(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Utiliza a API de IA para analisar os resultados dos testes."""
        prompt = f"""
        Analise os resultados dos testes abaixo e forneça:
        1. Resumo dos testes executados
        2. Identificação de problemas críticos
        3. Sugestões de otimização
        4. Priorização de correções

        Resultados:
        {json.dumps(resultados, indent=2)}
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