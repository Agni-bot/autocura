"""
SafeCodeGenerator - Sistema de Geração de Código Seguro com IA
============================================================

Gerador de código seguro que utiliza OpenAI para análise cognitiva
e validação ética de código auto-gerado.
"""

import ast
import json
import hashlib
import tempfile
import subprocess
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
import openai
import os

logger = logging.getLogger(__name__)

class SafetyLevel(Enum):
    """Níveis de segurança para geração de código"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAssessment(Enum):
    """Avaliação de risco do código"""
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"
    BLOCKED = "blocked"

@dataclass
class CodeAnalysis:
    """Resultado da análise de código"""
    syntax_valid: bool
    security_score: float  # 0.0 a 1.0
    risk_assessment: RiskAssessment
    ethical_compliance: bool
    complexity_score: float
    openai_analysis: Dict
    recommendations: List[str]
    warnings: List[str]
    timestamp: str

class SafeCodeGenerator:
    """
    Gerador de código seguro com análise cognitiva via OpenAI
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Inicializa o gerador de código seguro
        
        Args:
            openai_api_key: Chave da API OpenAI (ou usa variável de ambiente)
        """
        # Configuração OpenAI
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY') or os.getenv('AI_API_KEY')
        
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
            self.simulation_mode = False
            logger.info("SafeCodeGenerator inicializado com OpenAI")
        else:
            self.openai_client = None
            self.simulation_mode = True
            logger.warning("SafeCodeGenerator inicializado em modo simulação (sem OpenAI)")
        
        # Configurações de segurança
        self.allowed_imports = {
            'typing', 'datetime', 'json', 'math', 'random', 'uuid',
            'asyncio', 'logging', 'dataclasses', 'enum', 'collections',
            'itertools', 'functools', 'operator', 'copy', 'time'
        }
        
        self.forbidden_imports = {
            'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib',
            'requests', 'pickle', '__import__', 'eval', 'exec',
            'compile', 'open', 'file', 'input', 'raw_input'
        }
        
        self.dangerous_functions = {
            'exec', 'eval', 'compile', 'open', 'file', 'input',
            'raw_input', '__import__', 'globals', 'locals', 'vars',
            'dir', 'getattr', 'setattr', 'delattr', 'hasattr'
        }
        
        # Histórico de gerações
        self.generation_history = []
        
    async def generate_module(self, requirements: Dict) -> Tuple[str, CodeAnalysis]:
        """
        Gera módulo Python com análise cognitiva via OpenAI
        
        Args:
            requirements: {
                "function_name": str,
                "description": str,
                "inputs": List[Dict],
                "outputs": List[Dict],
                "logic_description": str,
                "safety_level": str,
                "context": str (opcional)
            }
        
        Returns:
            Tuple[str, CodeAnalysis]: Código gerado e análise
        """
        try:
            logger.info(f"Gerando código para: {requirements.get('function_name', 'unknown')}")
            
            # 1. Gera código usando OpenAI
            generated_code = await self._generate_code_with_openai(requirements)
            
            # 2. Análise de segurança local
            local_analysis = self._analyze_code_locally(generated_code)
            
            # 3. Análise cognitiva via OpenAI
            openai_analysis = await self._analyze_code_with_openai(generated_code, requirements)
            
            # 4. Combina análises
            final_analysis = self._combine_analyses(local_analysis, openai_analysis)
            
            # 5. Aplica melhorias se necessário
            if final_analysis.risk_assessment in [RiskAssessment.CAUTION, RiskAssessment.DANGEROUS]:
                improved_code = await self._improve_code_safety(generated_code, final_analysis)
                if improved_code:
                    generated_code = improved_code
                    # Reanalisa o código melhorado
                    local_analysis_improved = self._analyze_code_locally(generated_code)
                    openai_analysis_improved = await self._analyze_code_with_openai(generated_code, requirements)
                    final_analysis = self._combine_analyses(local_analysis_improved, openai_analysis_improved)
            
            # 6. Registra no histórico
            self._record_generation(requirements, generated_code, final_analysis)
            
            return generated_code, final_analysis
            
        except Exception as e:
            logger.error(f"Erro na geração de código: {e}")
            raise
    
    async def _generate_code_with_openai(self, requirements: Dict) -> str:
        """Gera código usando OpenAI GPT"""
        
        if self.simulation_mode:
            # Modo simulação: gera código básico baseado nos requisitos
            function_name = requirements.get('function_name', 'generated_function')
            description = requirements.get('description', 'Função gerada automaticamente')
            
            simulated_code = f'''
def {function_name}(*args, **kwargs):
    """
    {description}
    
    Esta é uma função gerada em modo simulação.
    Para funcionalidade completa, configure a chave OpenAI.
    """
    # Implementação simulada
    print("Função executada em modo simulação")
    return "resultado_simulado"

# Exemplo de uso
if __name__ == "__main__":
    result = {function_name}()
    print(f"Resultado: {{result}}")
'''
            logger.info("Código gerado em modo simulação")
            return simulated_code.strip()
        
        prompt = self._build_generation_prompt(requirements)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um especialista em geração de código Python seguro.
                        Gere código que seja:
                        1. Sintaticamente correto
                        2. Seguro (sem operações perigosas)
                        3. Eficiente e legível
                        4. Bem documentado
                        5. Testável
                        
                        NUNCA use: os, sys, subprocess, socket, eval, exec, open, file
                        SEMPRE inclua: type hints, docstrings, tratamento de erros"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Baixa criatividade para mais segurança
                max_tokens=2000
            )
            
            generated_code = response.choices[0].message.content
            
            # Remove markdown se presente
            if "```python" in generated_code:
                generated_code = generated_code.split("```python")[1].split("```")[0]
            elif "```" in generated_code:
                generated_code = generated_code.split("```")[1].split("```")[0]
            
            return generated_code.strip()
            
        except Exception as e:
            logger.error(f"Erro na geração OpenAI: {e}")
            raise
    
    def _build_generation_prompt(self, requirements: Dict) -> str:
        """Constrói prompt para geração de código"""
        
        prompt = f"""
Gere uma função Python com as seguintes especificações:

**Nome da Função:** {requirements.get('function_name', 'generated_function')}

**Descrição:** {requirements.get('description', 'Função gerada automaticamente')}

**Entradas:**
{json.dumps(requirements.get('inputs', []), indent=2)}

**Saídas:**
{json.dumps(requirements.get('outputs', []), indent=2)}

**Lógica Desejada:**
{requirements.get('logic_description', 'Implementar lógica básica')}

**Nível de Segurança:** {requirements.get('safety_level', 'medium')}

**Contexto Adicional:**
{requirements.get('context', 'Nenhum contexto adicional')}

**Requisitos Obrigatórios:**
1. Use apenas imports seguros (typing, datetime, json, math, etc.)
2. Inclua type hints completos
3. Adicione docstring detalhada
4. Implemente tratamento de erros
5. Mantenha complexidade baixa
6. Código deve ser testável

**Formato de Resposta:**
Retorne APENAS o código Python, sem explicações adicionais.
"""
        return prompt
    
    async def _analyze_code_with_openai(self, code: str, requirements: Dict) -> Dict:
        """Análise cognitiva do código via OpenAI"""
        
        if self.simulation_mode:
            # Modo simulação: retorna análise básica simulada
            return {
                "security_assessment": {
                    "score": 0.8, 
                    "risks": [], 
                    "recommendations": ["Análise completa requer chave OpenAI"]
                },
                "ethical_assessment": {
                    "compliant": True, 
                    "concerns": [], 
                    "recommendations": []
                },
                "quality_assessment": {
                    "score": 0.7, 
                    "strengths": ["Código gerado em modo simulação"], 
                    "weaknesses": ["Funcionalidade limitada sem OpenAI"]
                },
                "functionality_assessment": {
                    "meets_requirements": True, 
                    "missing_features": [], 
                    "suggestions": ["Configure OpenAI para análise completa"]
                },
                "overall_recommendation": "IMPROVE",
                "summary": "Análise simulada - Configure OpenAI para análise completa"
            }
        
        analysis_prompt = f"""
Analise o seguinte código Python em termos de:

1. **Segurança**: Identifique riscos de segurança
2. **Ética**: Avalie conformidade ética
3. **Qualidade**: Avalie qualidade do código
4. **Funcionalidade**: Verifica se atende aos requisitos
5. **Manutenibilidade**: Facilidade de manutenção

**Código a Analisar:**
```python
{code}
```

**Requisitos Originais:**
{json.dumps(requirements, indent=2)}

**Formato de Resposta (JSON):**
{{
    "security_assessment": {{
        "score": 0.0-1.0,
        "risks": ["lista de riscos"],
        "recommendations": ["recomendações de segurança"]
    }},
    "ethical_assessment": {{
        "compliant": true/false,
        "concerns": ["preocupações éticas"],
        "recommendations": ["recomendações éticas"]
    }},
    "quality_assessment": {{
        "score": 0.0-1.0,
        "strengths": ["pontos fortes"],
        "weaknesses": ["pontos fracos"]
    }},
    "functionality_assessment": {{
        "meets_requirements": true/false,
        "missing_features": ["recursos faltantes"],
        "suggestions": ["sugestões de melhoria"]
    }},
    "overall_recommendation": "APPROVE/IMPROVE/REJECT",
    "summary": "Resumo da análise"
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em análise de código Python, segurança e ética em IA. Forneça análises detalhadas e precisas."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.1,  # Muito baixa para análise consistente
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Tenta extrair JSON da resposta
            try:
                if "```json" in analysis_text:
                    json_part = analysis_text.split("```json")[1].split("```")[0]
                elif "```" in analysis_text:
                    json_part = analysis_text.split("```")[1].split("```")[0]
                else:
                    json_part = analysis_text
                
                return json.loads(json_part.strip())
                
            except json.JSONDecodeError:
                # Fallback: análise básica
                return {
                    "security_assessment": {"score": 0.5, "risks": [], "recommendations": []},
                    "ethical_assessment": {"compliant": True, "concerns": [], "recommendations": []},
                    "quality_assessment": {"score": 0.5, "strengths": [], "weaknesses": []},
                    "functionality_assessment": {"meets_requirements": True, "missing_features": [], "suggestions": []},
                    "overall_recommendation": "IMPROVE",
                    "summary": "Análise automática básica"
                }
                
        except Exception as e:
            logger.error(f"Erro na análise OpenAI: {e}")
            return {"error": str(e)}
    
    def _analyze_code_locally(self, code: str) -> Dict:
        """Análise local de segurança do código"""
        
        analysis = {
            "syntax_valid": False,
            "security_score": 0.0,
            "forbidden_imports": [],
            "dangerous_functions": [],
            "complexity_score": 0.0,
            "line_count": len(code.split('\n'))
        }
        
        try:
            # 1. Validação sintática
            tree = ast.parse(code)
            analysis["syntax_valid"] = True
            
            # 2. Análise de imports
            forbidden_found = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.forbidden_imports:
                            forbidden_found.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self.forbidden_imports:
                        forbidden_found.append(node.module)
            
            analysis["forbidden_imports"] = forbidden_found
            
            # 3. Análise de funções perigosas
            dangerous_found = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in self.dangerous_functions:
                            dangerous_found.append(node.func.id)
            
            analysis["dangerous_functions"] = dangerous_found
            
            # 4. Cálculo de complexidade (simplificado)
            complexity = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.For, ast.While, ast.If, ast.Try)):
                    complexity += 1
            
            analysis["complexity_score"] = min(complexity / 10.0, 1.0)
            
            # 5. Score de segurança
            security_score = 1.0
            security_score -= len(forbidden_found) * 0.3
            security_score -= len(dangerous_found) * 0.2
            security_score -= analysis["complexity_score"] * 0.1
            
            analysis["security_score"] = max(security_score, 0.0)
            
        except SyntaxError as e:
            analysis["syntax_error"] = str(e)
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    def _combine_analyses(self, local_analysis: Dict, openai_analysis: Dict) -> CodeAnalysis:
        """Combina análises local e OpenAI"""
        
        # Determina risk assessment
        risk = RiskAssessment.SAFE
        
        if not local_analysis.get("syntax_valid", False):
            risk = RiskAssessment.BLOCKED
        elif local_analysis.get("forbidden_imports") or local_analysis.get("dangerous_functions"):
            risk = RiskAssessment.DANGEROUS
        elif local_analysis.get("security_score", 0) < 0.7:
            risk = RiskAssessment.CAUTION
        elif openai_analysis.get("overall_recommendation") == "REJECT":
            risk = RiskAssessment.DANGEROUS
        elif openai_analysis.get("overall_recommendation") == "IMPROVE":
            risk = RiskAssessment.CAUTION
        
        # Combina recomendações
        recommendations = []
        recommendations.extend(local_analysis.get("recommendations", []))
        recommendations.extend(
            openai_analysis.get("security_assessment", {}).get("recommendations", [])
        )
        recommendations.extend(
            openai_analysis.get("ethical_assessment", {}).get("recommendations", [])
        )
        
        # Combina warnings
        warnings = []
        warnings.extend([f"Import proibido: {imp}" for imp in local_analysis.get("forbidden_imports", [])])
        warnings.extend([f"Função perigosa: {func}" for func in local_analysis.get("dangerous_functions", [])])
        warnings.extend(openai_analysis.get("security_assessment", {}).get("risks", []))
        
        return CodeAnalysis(
            syntax_valid=local_analysis.get("syntax_valid", False),
            security_score=local_analysis.get("security_score", 0.0),
            risk_assessment=risk,
            ethical_compliance=openai_analysis.get("ethical_assessment", {}).get("compliant", True),
            complexity_score=local_analysis.get("complexity_score", 0.0),
            openai_analysis=openai_analysis,
            recommendations=recommendations,
            warnings=warnings,
            timestamp=datetime.now().isoformat()
        )
    
    async def _improve_code_safety(self, code: str, analysis: CodeAnalysis) -> Optional[str]:
        """Melhora segurança do código usando OpenAI"""
        
        if analysis.risk_assessment == RiskAssessment.BLOCKED:
            return None
        
        if self.simulation_mode:
            # Modo simulação: retorna código com comentários de melhoria
            improved_code = f"""
# CÓDIGO MELHORADO EM MODO SIMULAÇÃO
# Para melhorias reais, configure a chave OpenAI

{code}

# Melhorias sugeridas (modo simulação):
# - Análise de segurança completa
# - Validação ética avançada
# - Otimizações de performance
# - Documentação aprimorada
"""
            logger.info("Melhoria de código simulada")
            return improved_code.strip()
        
        improvement_prompt = f"""
Melhore a segurança do seguinte código Python:

**Código Original:**
```python
{code}
```

**Problemas Identificados:**
{json.dumps(analysis.warnings, indent=2)}

**Recomendações:**
{json.dumps(analysis.recommendations, indent=2)}

**Instruções:**
1. Corrija todos os problemas de segurança
2. Remova imports proibidos
3. Substitua funções perigosas por alternativas seguras
4. Mantenha a funcionalidade original
5. Melhore a documentação

**Formato de Resposta:**
Retorne APENAS o código Python melhorado, sem explicações.
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em segurança de código Python. Melhore o código mantendo funcionalidade."
                    },
                    {
                        "role": "user",
                        "content": improvement_prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            improved_code = response.choices[0].message.content
            
            # Remove markdown se presente
            if "```python" in improved_code:
                improved_code = improved_code.split("```python")[1].split("```")[0]
            elif "```" in improved_code:
                improved_code = improved_code.split("```")[1].split("```")[0]
            
            return improved_code.strip()
            
        except Exception as e:
            logger.error(f"Erro na melhoria de código: {e}")
            return None
    
    def _record_generation(self, requirements: Dict, code: str, analysis: CodeAnalysis):
        """Registra geração no histórico"""
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "requirements": requirements,
            "code_hash": hashlib.sha256(code.encode()).hexdigest(),
            "analysis": {
                "syntax_valid": analysis.syntax_valid,
                "security_score": analysis.security_score,
                "risk_assessment": analysis.risk_assessment.value,
                "ethical_compliance": analysis.ethical_compliance,
                "complexity_score": analysis.complexity_score
            },
            "warnings_count": len(analysis.warnings),
            "recommendations_count": len(analysis.recommendations)
        }
        
        self.generation_history.append(record)
        
        # Mantém apenas últimas 100 gerações
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-100:]
    
    def get_generation_stats(self) -> Dict:
        """Retorna estatísticas de geração"""
        
        if not self.generation_history:
            return {"total_generations": 0}
        
        total = len(self.generation_history)
        safe_count = sum(1 for r in self.generation_history 
                        if r["analysis"]["risk_assessment"] == "safe")
        
        avg_security = sum(r["analysis"]["security_score"] for r in self.generation_history) / total
        
        return {
            "total_generations": total,
            "safe_generations": safe_count,
            "safety_rate": safe_count / total,
            "average_security_score": avg_security,
            "last_generation": self.generation_history[-1]["timestamp"] if self.generation_history else None
        }
    
    async def validate_existing_code(self, code: str, context: str = "") -> CodeAnalysis:
        """Valida código existente"""
        
        requirements = {
            "description": "Validação de código existente",
            "context": context,
            "safety_level": "high"
        }
        
        local_analysis = self._analyze_code_locally(code)
        openai_analysis = await self._analyze_code_with_openai(code, requirements)
        
        return self._combine_analyses(local_analysis, openai_analysis) 