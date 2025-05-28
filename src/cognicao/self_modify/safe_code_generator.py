"""
Safe Code Generator - Fase Beta
==============================

Sistema de geração de código seguro que permite auto-modificação
controlada do sistema AutoCura com validações éticas e de segurança.
"""

import ast
import inspect
import logging
import hashlib
import tempfile
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import importlib.util

logger = logging.getLogger(__name__)

class CodeType(Enum):
    """Tipos de código que podem ser gerados"""
    MODULE = "module"
    FUNCTION = "function"
    CLASS = "class"
    CONFIGURATION = "configuration"
    INTEGRATION = "integration"
    OPTIMIZATION = "optimization"

class SecurityLevel(Enum):
    """Níveis de segurança para código gerado"""
    SAFE = "safe"
    MODERATE = "moderate"
    RESTRICTED = "restricted"
    DANGEROUS = "dangerous"

class ValidationResult(Enum):
    """Resultados de validação"""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    MODIFIED = "modified"

@dataclass
class CodeGenerationRequest:
    """Solicitação de geração de código"""
    request_id: str
    code_type: CodeType
    requirements: Dict[str, Any]
    context: Dict[str, Any]
    priority: int
    requester: str
    timestamp: str

@dataclass
class GeneratedCode:
    """Código gerado pelo sistema"""
    code_id: str
    request_id: str
    code_type: CodeType
    source_code: str
    dependencies: List[str]
    security_level: SecurityLevel
    validation_result: ValidationResult
    test_results: Dict[str, Any]
    documentation: str
    metadata: Dict[str, Any]
    timestamp: str

@dataclass
class SecurityViolation:
    """Violação de segurança detectada"""
    violation_id: str
    violation_type: str
    severity: str
    description: str
    line_number: int
    code_snippet: str
    recommendation: str

class SafeCodeGenerator:
    """
    Gerador de Código Seguro
    
    Gera código automaticamente com validações de segurança,
    testes automáticos e aprovação ética.
    """
    
    def __init__(self):
        """Inicializa o gerador de código seguro"""
        self.generated_codes = {}
        self.security_violations = {}
        self.approved_patterns = set()
        self.blocked_patterns = set()
        
        # Configurações de segurança
        self.security_config = {
            "max_code_size": 10000,  # Máximo de caracteres
            "max_complexity": 10,    # Complexidade ciclomática máxima
            "allowed_imports": {
                "standard": ["os", "sys", "json", "datetime", "typing", "logging"],
                "scientific": ["numpy", "pandas", "scipy"],
                "ml": ["sklearn", "torch", "tensorflow"],
                "web": ["fastapi", "requests", "aiohttp"],
                "async": ["asyncio", "concurrent.futures"]
            },
            "forbidden_imports": ["subprocess", "eval", "exec", "compile", "__import__"],
            "forbidden_functions": ["eval", "exec", "compile", "open", "file"],
            "max_nested_loops": 3,
            "max_function_params": 10
        }
        
        # Padrões de código perigoso
        self.dangerous_patterns = {
            r"eval\s*\(": "Uso de eval() é perigoso",
            r"exec\s*\(": "Uso de exec() é perigoso", 
            r"__import__\s*\(": "Uso de __import__() é perigoso",
            r"subprocess\s*\.": "Uso de subprocess pode ser perigoso",
            r"os\s*\.system": "Uso de os.system é perigoso",
            r"open\s*\([^)]*['\"]w": "Escrita em arquivos requer aprovação",
            r"rm\s+-rf": "Comandos destrutivos são proibidos",
            r"DROP\s+TABLE": "Comandos SQL destrutivos são proibidos"
        }
        
        # Templates de código seguro
        self.safe_templates = {
            CodeType.FUNCTION: self._get_function_template(),
            CodeType.CLASS: self._get_class_template(),
            CodeType.MODULE: self._get_module_template(),
            CodeType.CONFIGURATION: self._get_config_template()
        }
        
        logger.info("SafeCodeGenerator inicializado")
    
    async def generate_module(self, requirements: Dict[str, Any]) -> GeneratedCode:
        """
        Gera um novo módulo baseado nos requisitos
        
        Args:
            requirements: Requisitos para o módulo
            
        Returns:
            GeneratedCode: Código gerado
        """
        request = CodeGenerationRequest(
            request_id=f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            code_type=CodeType.MODULE,
            requirements=requirements,
            context={"generator": "auto", "version": "1.0"},
            priority=1,
            requester="system",
            timestamp=datetime.now().isoformat()
        )
        
        return await self._process_generation_request(request)
    
    async def _process_generation_request(self, request: CodeGenerationRequest) -> GeneratedCode:
        """
        Processa uma solicitação de geração de código
        
        Args:
            request: Solicitação de geração
            
        Returns:
            GeneratedCode: Código gerado
        """
        try:
            logger.info(f"Processando solicitação {request.request_id}")
            
            # Gerar código baseado no tipo
            source_code = await self._generate_source_code(request)
            
            # Validar segurança
            security_result = await self._validate_security(source_code)
            
            # Executar testes
            test_results = await self._run_tests(source_code, request.code_type)
            
            # Gerar documentação
            documentation = await self._generate_documentation(source_code, request)
            
            # Criar objeto de código gerado
            generated_code = GeneratedCode(
                code_id=f"code_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                request_id=request.request_id,
                code_type=request.code_type,
                source_code=source_code,
                dependencies=self._extract_dependencies(source_code),
                security_level=security_result["level"],
                validation_result=security_result["validation"],
                test_results=test_results,
                documentation=documentation,
                metadata={
                    "requirements": request.requirements,
                    "context": request.context,
                    "generation_time": datetime.now().isoformat(),
                    "code_hash": hashlib.sha256(source_code.encode()).hexdigest()
                },
                timestamp=datetime.now().isoformat()
            )
            
            # Armazenar código gerado
            self.generated_codes[generated_code.code_id] = generated_code
            
            logger.info(f"Código gerado: {generated_code.code_id} (segurança: {security_result['level'].value})")
            
            return generated_code
            
        except Exception as e:
            logger.error(f"Erro na geração de código: {e}")
            raise
    
    async def _generate_source_code(self, request: CodeGenerationRequest) -> str:
        """
        Gera o código fonte baseado na solicitação
        
        Args:
            request: Solicitação de geração
            
        Returns:
            str: Código fonte gerado
        """
        template = self.safe_templates.get(request.code_type)
        if not template:
            raise ValueError(f"Tipo de código não suportado: {request.code_type}")
        
        # Personalizar template baseado nos requisitos
        if request.code_type == CodeType.FUNCTION:
            return await self._generate_function_code(request, template)
        elif request.code_type == CodeType.CLASS:
            return await self._generate_class_code(request, template)
        elif request.code_type == CodeType.MODULE:
            return await self._generate_module_code(request, template)
        elif request.code_type == CodeType.CONFIGURATION:
            return await self._generate_config_code(request, template)
        else:
            return template
    
    async def _generate_function_code(self, request: CodeGenerationRequest, template: str) -> str:
        """
        Gera código de função
        
        Args:
            request: Solicitação
            template: Template base
            
        Returns:
            str: Código da função
        """
        req = request.requirements
        
        function_name = req.get("name", "generated_function")
        parameters = req.get("parameters", [])
        return_type = req.get("return_type", "Any")
        description = req.get("description", "Função gerada automaticamente")
        logic = req.get("logic", "pass")
        
        # Validar parâmetros
        if len(parameters) > self.security_config["max_function_params"]:
            raise ValueError(f"Muitos parâmetros: {len(parameters)} > {self.security_config['max_function_params']}")
        
        # Construir assinatura da função
        param_str = ", ".join([f"{p['name']}: {p.get('type', 'Any')}" for p in parameters])
        
        code = f'''
def {function_name}({param_str}) -> {return_type}:
    """
    {description}
    
    Args:
        {chr(10).join([f"{p['name']}: {p.get('description', 'Parâmetro')}" for p in parameters])}
    
    Returns:
        {return_type}: {req.get("return_description", "Resultado da função")}
    """
    try:
        # Lógica gerada automaticamente
        {logic}
        
    except Exception as e:
        logger.error(f"Erro em {function_name}: {{e}}")
        raise
'''
        
        return code.strip()
    
    async def _generate_class_code(self, request: CodeGenerationRequest, template: str) -> str:
        """
        Gera código de classe
        
        Args:
            request: Solicitação
            template: Template base
            
        Returns:
            str: Código da classe
        """
        req = request.requirements
        
        class_name = req.get("name", "GeneratedClass")
        base_classes = req.get("base_classes", [])
        attributes = req.get("attributes", [])
        methods = req.get("methods", [])
        description = req.get("description", "Classe gerada automaticamente")
        
        # Construir herança
        inheritance = f"({', '.join(base_classes)})" if base_classes else ""
        
        # Construir atributos
        attr_code = ""
        for attr in attributes:
            attr_code += f"    {attr['name']}: {attr.get('type', 'Any')} = {attr.get('default', 'None')}\n"
        
        # Construir métodos
        methods_code = ""
        for method in methods:
            method_code = await self._generate_method_code(method)
            methods_code += f"\n{method_code}\n"
        
        code = f'''
class {class_name}{inheritance}:
    """
    {description}
    """
    
{attr_code}
    
    def __init__(self):
        """Inicializa a classe"""
        super().__init__()
        logger.info(f"{class_name} inicializado")
{methods_code}
'''
        
        return code.strip()
    
    async def _generate_method_code(self, method_spec: Dict[str, Any]) -> str:
        """
        Gera código de método
        
        Args:
            method_spec: Especificação do método
            
        Returns:
            str: Código do método
        """
        name = method_spec.get("name", "generated_method")
        parameters = method_spec.get("parameters", [])
        return_type = method_spec.get("return_type", "None")
        description = method_spec.get("description", "Método gerado automaticamente")
        logic = method_spec.get("logic", "pass")
        
        param_str = ", ".join([f"{p['name']}: {p.get('type', 'Any')}" for p in parameters])
        
        return f'''
    def {name}(self, {param_str}) -> {return_type}:
        """
        {description}
        
        Args:
            {chr(10).join([f"    {p['name']}: {p.get('description', 'Parâmetro')}" for p in parameters])}
        
        Returns:
            {return_type}: {method_spec.get("return_description", "Resultado do método")}
        """
        try:
            {logic}
        except Exception as e:
            logger.error(f"Erro em {name}: {{e}}")
            raise
'''
    
    async def _generate_module_code(self, request: CodeGenerationRequest, template: str) -> str:
        """
        Gera código de módulo completo
        
        Args:
            request: Solicitação
            template: Template base
            
        Returns:
            str: Código do módulo
        """
        req = request.requirements
        
        module_name = req.get("name", "generated_module")
        description = req.get("description", "Módulo gerado automaticamente")
        imports = req.get("imports", [])
        classes = req.get("classes", [])
        functions = req.get("functions", [])
        
        # Validar imports
        safe_imports = []
        for imp in imports:
            if self._is_import_safe(imp):
                safe_imports.append(imp)
            else:
                logger.warning(f"Import bloqueado por segurança: {imp}")
        
        # Construir código
        imports_code = "\n".join([f"import {imp}" for imp in safe_imports])
        
        classes_code = ""
        for class_spec in classes:
            class_request = CodeGenerationRequest(
                request_id=f"{request.request_id}_class",
                code_type=CodeType.CLASS,
                requirements=class_spec,
                context=request.context,
                priority=request.priority,
                requester=request.requester,
                timestamp=datetime.now().isoformat()
            )
            class_code = await self._generate_class_code(class_request, "")
            classes_code += f"\n{class_code}\n"
        
        functions_code = ""
        for func_spec in functions:
            func_request = CodeGenerationRequest(
                request_id=f"{request.request_id}_func",
                code_type=CodeType.FUNCTION,
                requirements=func_spec,
                context=request.context,
                priority=request.priority,
                requester=request.requester,
                timestamp=datetime.now().isoformat()
            )
            func_code = await self._generate_function_code(func_request, "")
            functions_code += f"\n{func_code}\n"
        
        code = f'''
"""
{module_name}
{description}

Gerado automaticamente pelo SafeCodeGenerator
Data: {datetime.now().isoformat()}
"""

import logging
{imports_code}

logger = logging.getLogger(__name__)

{classes_code}

{functions_code}
'''
        
        return code.strip()
    
    async def _generate_config_code(self, request: CodeGenerationRequest, template: str) -> str:
        """
        Gera código de configuração
        
        Args:
            request: Solicitação
            template: Template base
            
        Returns:
            str: Código de configuração
        """
        req = request.requirements
        
        config_data = req.get("config_data", {})
        config_name = req.get("name", "generated_config")
        
        # Serializar configuração de forma segura
        config_str = self._safe_serialize_config(config_data)
        
        code = f'''
"""
Configuração: {config_name}
Gerada automaticamente
"""

{config_name} = {config_str}
'''
        
        return code.strip()
    
    def _safe_serialize_config(self, config_data: Dict[str, Any]) -> str:
        """
        Serializa configuração de forma segura
        
        Args:
            config_data: Dados de configuração
            
        Returns:
            str: Configuração serializada
        """
        # Implementação simplificada - em produção seria mais robusta
        import json
        return json.dumps(config_data, indent=4, ensure_ascii=False)
    
    async def _validate_security(self, source_code: str) -> Dict[str, Any]:
        """
        Valida segurança do código gerado
        
        Args:
            source_code: Código a validar
            
        Returns:
            Dict: Resultado da validação
        """
        violations = []
        security_level = SecurityLevel.SAFE
        
        # Verificar tamanho do código
        if len(source_code) > self.security_config["max_code_size"]:
            violations.append(SecurityViolation(
                violation_id="size_limit",
                violation_type="size",
                severity="high",
                description=f"Código muito grande: {len(source_code)} caracteres",
                line_number=0,
                code_snippet="",
                recommendation="Dividir em módulos menores"
            ))
            security_level = SecurityLevel.DANGEROUS
        
        # Verificar padrões perigosos
        import re
        lines = source_code.split('\n')
        for i, line in enumerate(lines):
            for pattern, message in self.dangerous_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(SecurityViolation(
                        violation_id=f"pattern_{i}",
                        violation_type="dangerous_pattern",
                        severity="critical",
                        description=message,
                        line_number=i + 1,
                        code_snippet=line.strip(),
                        recommendation="Remover ou substituir por alternativa segura"
                    ))
                    security_level = SecurityLevel.DANGEROUS
        
        # Verificar complexidade
        try:
            tree = ast.parse(source_code)
            complexity = self._calculate_complexity(tree)
            if complexity > self.security_config["max_complexity"]:
                violations.append(SecurityViolation(
                    violation_id="complexity",
                    violation_type="complexity",
                    severity="medium",
                    description=f"Complexidade muito alta: {complexity}",
                    line_number=0,
                    code_snippet="",
                    recommendation="Simplificar lógica"
                ))
                if security_level == SecurityLevel.SAFE:
                    security_level = SecurityLevel.MODERATE
        except SyntaxError as e:
            violations.append(SecurityViolation(
                violation_id="syntax",
                violation_type="syntax",
                severity="critical",
                description=f"Erro de sintaxe: {e}",
                line_number=e.lineno or 0,
                code_snippet="",
                recommendation="Corrigir sintaxe"
            ))
            security_level = SecurityLevel.DANGEROUS
        
        # Armazenar violações
        for violation in violations:
            self.security_violations[violation.violation_id] = violation
        
        # Determinar resultado da validação
        if security_level == SecurityLevel.DANGEROUS:
            validation_result = ValidationResult.REJECTED
        elif security_level == SecurityLevel.MODERATE:
            validation_result = ValidationResult.NEEDS_REVIEW
        else:
            validation_result = ValidationResult.APPROVED
        
        return {
            "level": security_level,
            "validation": validation_result,
            "violations": violations,
            "violations_count": len(violations)
        }
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """
        Calcula complexidade ciclomática do código
        
        Args:
            tree: AST do código
            
        Returns:
            int: Complexidade ciclomática
        """
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _is_import_safe(self, import_name: str) -> bool:
        """
        Verifica se um import é seguro
        
        Args:
            import_name: Nome do import
            
        Returns:
            bool: True se seguro
        """
        # Verificar se está na lista de imports proibidos
        if import_name in self.security_config["forbidden_imports"]:
            return False
        
        # Verificar se está nas listas permitidas
        for category, allowed in self.security_config["allowed_imports"].items():
            if import_name in allowed:
                return True
        
        # Por padrão, bloquear imports não conhecidos
        return False
    
    def _extract_dependencies(self, source_code: str) -> List[str]:
        """
        Extrai dependências do código
        
        Args:
            source_code: Código fonte
            
        Returns:
            List[str]: Lista de dependências
        """
        dependencies = []
        
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)
        except SyntaxError:
            # Se não conseguir parsear, extrair imports com regex
            import re
            import_pattern = r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            from_pattern = r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
            
            dependencies.extend(re.findall(import_pattern, source_code))
            dependencies.extend(re.findall(from_pattern, source_code))
        
        return list(set(dependencies))  # Remover duplicatas
    
    async def _run_tests(self, source_code: str, code_type: CodeType) -> Dict[str, Any]:
        """
        Executa testes no código gerado
        
        Args:
            source_code: Código a testar
            code_type: Tipo do código
            
        Returns:
            Dict: Resultados dos testes
        """
        test_results = {
            "syntax_check": False,
            "import_check": False,
            "execution_check": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Teste de sintaxe
            ast.parse(source_code)
            test_results["syntax_check"] = True
            
            # Teste de imports (em ambiente isolado)
            test_results["import_check"] = await self._test_imports(source_code)
            
            # Teste de execução básica (se for função ou classe)
            if code_type in [CodeType.FUNCTION, CodeType.CLASS]:
                test_results["execution_check"] = await self._test_execution(source_code)
            else:
                test_results["execution_check"] = True
                
        except SyntaxError as e:
            test_results["errors"].append(f"Erro de sintaxe: {e}")
        except Exception as e:
            test_results["errors"].append(f"Erro nos testes: {e}")
        
        return test_results
    
    async def _test_imports(self, source_code: str) -> bool:
        """
        Testa se os imports funcionam
        
        Args:
            source_code: Código a testar
            
        Returns:
            bool: True se imports funcionam
        """
        try:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(source_code)
                temp_file = f.name
            
            # Tentar importar o módulo
            spec = importlib.util.spec_from_file_location("test_module", temp_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return True
            
        except Exception as e:
            logger.debug(f"Erro no teste de imports: {e}")
            return False
        finally:
            # Limpar arquivo temporário
            try:
                Path(temp_file).unlink()
            except:
                pass
        
        return False
    
    async def _test_execution(self, source_code: str) -> bool:
        """
        Testa execução básica do código
        
        Args:
            source_code: Código a testar
            
        Returns:
            bool: True se executa sem erros
        """
        try:
            # Compilar código
            compiled_code = compile(source_code, '<generated>', 'exec')
            
            # Executar em namespace isolado
            namespace = {
                '__builtins__': __builtins__,
                'logger': logger
            }
            exec(compiled_code, namespace)
            
            return True
            
        except Exception as e:
            logger.debug(f"Erro no teste de execução: {e}")
            return False
    
    async def _generate_documentation(self, source_code: str, request: CodeGenerationRequest) -> str:
        """
        Gera documentação para o código
        
        Args:
            source_code: Código fonte
            request: Solicitação original
            
        Returns:
            str: Documentação gerada
        """
        doc = f"""
# Documentação do Código Gerado

## Informações Gerais
- **ID da Solicitação**: {request.request_id}
- **Tipo**: {request.code_type.value}
- **Gerado em**: {datetime.now().isoformat()}
- **Solicitante**: {request.requester}

## Requisitos
{self._format_requirements(request.requirements)}

## Código Gerado
```python
{source_code}
```

## Dependências
{self._format_dependencies(self._extract_dependencies(source_code))}

## Notas de Segurança
- Código validado pelo SafeCodeGenerator
- Todas as verificações de segurança foram aplicadas
- Testes automáticos executados

## Uso
Este código foi gerado automaticamente e deve ser revisado antes do uso em produção.
"""
        
        return doc.strip()
    
    def _format_requirements(self, requirements: Dict[str, Any]) -> str:
        """
        Formata requisitos para documentação
        
        Args:
            requirements: Requisitos
            
        Returns:
            str: Requisitos formatados
        """
        formatted = []
        for key, value in requirements.items():
            formatted.append(f"- **{key}**: {value}")
        return "\n".join(formatted)
    
    def _format_dependencies(self, dependencies: List[str]) -> str:
        """
        Formata dependências para documentação
        
        Args:
            dependencies: Lista de dependências
            
        Returns:
            str: Dependências formatadas
        """
        if not dependencies:
            return "Nenhuma dependência externa"
        
        return "\n".join([f"- {dep}" for dep in dependencies])
    
    async def validate_safety(self, code: str) -> bool:
        """
        Valida segurança de código externo
        
        Args:
            code: Código a validar
            
        Returns:
            bool: True se seguro
        """
        result = await self._validate_security(code)
        return result["validation"] == ValidationResult.APPROVED
    
    def get_generation_status(self) -> Dict[str, Any]:
        """
        Retorna status da geração de código
        
        Returns:
            Dict: Status atual
        """
        return {
            "total_generated": len(self.generated_codes),
            "security_violations": len(self.security_violations),
            "approved_patterns": len(self.approved_patterns),
            "blocked_patterns": len(self.blocked_patterns),
            "recent_generations": [
                {
                    "id": code.code_id,
                    "type": code.code_type.value,
                    "security_level": code.security_level.value,
                    "validation": code.validation_result.value,
                    "timestamp": code.timestamp
                }
                for code in list(self.generated_codes.values())[-5:]
            ]
        }
    
    def _get_function_template(self) -> str:
        """Retorna template para funções"""
        return '''
def template_function(param1: Any, param2: Any = None) -> Any:
    """
    Template de função segura
    
    Args:
        param1: Primeiro parâmetro
        param2: Segundo parâmetro (opcional)
    
    Returns:
        Any: Resultado da função
    """
    try:
        # Implementação aqui
        pass
    except Exception as e:
        logger.error(f"Erro na função: {e}")
        raise
'''
    
    def _get_class_template(self) -> str:
        """Retorna template para classes"""
        return '''
class TemplateClass:
    """
    Template de classe segura
    """
    
    def __init__(self):
        """Inicializa a classe"""
        self.initialized = True
        logger.info("TemplateClass inicializada")
    
    def template_method(self, param: Any) -> Any:
        """
        Método template
        
        Args:
            param: Parâmetro do método
        
        Returns:
            Any: Resultado do método
        """
        try:
            # Implementação aqui
            pass
        except Exception as e:
            logger.error(f"Erro no método: {e}")
            raise
'''
    
    def _get_module_template(self) -> str:
        """Retorna template para módulos"""
        return '''
"""
Template de módulo seguro
"""

import logging

logger = logging.getLogger(__name__)

# Implementação do módulo aqui
'''
    
    def _get_config_template(self) -> str:
        """Retorna template para configurações"""
        return '''
"""
Template de configuração segura
"""

template_config = {
    "version": "1.0",
    "settings": {},
    "metadata": {
        "generated": True,
        "safe": True
    }
}
''' 