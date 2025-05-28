# Arquivo criado em 2025-05-28T18:23:12.599220
# Primeira sugestão: code-doc-001 - Falta de Documentação no Código
# Código otimizado por IA

import ast
import inspect
from typing import Any, Callable, List, Tuple

class DocstringGenerator:
    """Gera docstrings automaticamente para funções e classes"""

    def __init__(self):
        """Inicializa o gerador de docstrings com os templates"""
        self.templates = {
            'function': '"""\n{description}\n\nArgs:\n{args}\n\nReturns:\n    {returns}\n"""',
            'class': '"""\n{description}\n\nAttributes:\n{attributes}\n"""',
            'method': '"""\n{description}\n\nArgs:\n{args}\n\nReturns:\n    {returns}\n"""'
        }

    def generate_function_docstring(self, func: Callable) -> str:
        """Gera docstring para função

        Args:
            func (Callable): Função para a qual a docstring será gerada

        Returns:
            str: Docstring gerada
        """
        sig = inspect.signature(func)
        args_desc = [f"    {name}: {param.annotation if param.annotation != param.empty else 'Any'}"
                     for name, param in sig.parameters.items() if name != 'self']

        return self.templates['function'].format(
            description=f"{func.__name__} - Função gerada automaticamente",
            args='\n'.join(args_desc) if args_desc else "    None",
            returns=sig.return_annotation if sig.return_annotation != sig.empty else "Any"
        )

    def auto_document_module(self, module_path: str) -> str:
        """Adiciona docstrings a um módulo

        Args:
            module_path (str): Caminho do módulo a ser documentado

        Returns:
            str: Código do módulo com docstrings adicionadas
        """
        try:
            with open(module_path, 'r') as f:
                tree = ast.parse(f.read())
        except FileNotFoundError:
            raise FileNotFoundError(f"O módulo {module_path} não foi encontrado.")
        except Exception as e:
            raise Exception(f"Erro ao abrir o módulo {module_path}: {str(e)}")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                docstring = self._generate_function_docstring_from_ast(node)
                node.body.insert(0, ast.Expr(value=ast.Str(s=docstring)))

        return ast.unparse(tree)

    def _generate_function_docstring_from_ast(self, node: ast.FunctionDef) -> str:
        """Gera docstring a partir do AST

        Args:
            node (ast.FunctionDef): Nó do AST representando uma função

        Returns:
            str: Docstring gerada
        """
        args = [f"    {arg.arg}: Any" for arg in node.args.args if arg.arg != 'self']

        return self.templates['function'].format(
            description=f"{node.name} - Documentação automática",
            args='\n'.join(args) if args else "    None",
            returns="Any"
        )

# Aplicado em 2025-05-28T22:09:43.860648
# Sugestão: code-doc-001 - Falta de Documentação no Código
# Código otimizado por IA
import ast
import inspect
from typing import Any, Callable, List, Tuple

class DocstringGenerator:
    """
    Classe para gerar docstrings automaticamente para funções e classes.
    """
    
    def __init__(self):
        self.templates = {
            'function': '"""\n{description}\n\nArgs:\n{args}\n\nReturns:\n    {returns}\n"""',
            'class': '"""\n{description}\n\nAttributes:\n{attributes}\n"""',
            'method': '"""\n{description}\n\nArgs:\n{args}\n\nReturns:\n    {returns}\n"""'
        }
    
    def generate_function_docstring(self, func: Callable) -> str:
        """
        Gera docstring para função.

        Args:
            func: Função para a qual a docstring será gerada.

        Returns:
            Docstring gerada para a função.
        """
        sig = inspect.signature(func)
        args_desc = [f"    {name}: {param.annotation if param.annotation != param.empty else 'Any'}"
                     for name, param in sig.parameters.items() if name != 'self']
        
        return self.templates['function'].format(
            description=f"{func.__name__} - Função gerada automaticamente",
            args='\n'.join(args_desc) if args_desc else "    None",
            returns=sig.return_annotation if sig.return_annotation != sig.empty else "Any"
        )
    
    def auto_document_module(self, module_path: str) -> str:
        """
        Adiciona docstrings a um módulo.

        Args:
            module_path: Caminho do módulo para o qual as docstrings serão adicionadas.

        Returns:
            Código do módulo com docstrings adicionadas.
        """
        try:
            with open(module_path, 'r') as f:
                tree = ast.parse(f.read())
        except FileNotFoundError:
            raise FileNotFoundError("O módulo especificado não foi encontrado.")
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                docstring = self.generate_function_docstring_from_ast(node)
                node.body.insert(0, ast.Expr(value=ast.Str(s=docstring)))
        
        return ast.unparse(tree)
    
    def generate_function_docstring_from_ast(self, node: ast.FunctionDef) -> str:
        """
        Gera docstring a partir do AST.

        Args:
            node: Nó do AST para o qual a docstring será gerada.

        Returns:
            Docstring gerada para o nó do AST.
        """
        args = [f"    {arg.arg}: Any" for arg in node.args.args if arg.arg != 'self']
        
        return self.templates['function'].format(
            description=f"{node.name} - Documentação automática",
            args='\n'.join(args) if args else "    None",
            returns="Any"
        )

# Instância da classe DocstringGenerator para uso.
doc_generator = DocstringGenerator()

# Aplicado em 2025-05-28T22:16:57.066114
# Sugestão: code-doc-001 - Falta de Documentação no Código
# Código otimizado por IA
# Importando as bibliotecas necessárias
import ast
import inspect
from typing import Any, Callable, Union

class DocstringGenerator:
    """
    Classe para gerar docstrings automaticamente para funções e classes.
    """
    
    def __init__(self):
        """
        Inicializa a classe com os templates de docstrings.
        """
        self.templates = {
            'function': '"""\n{description}\n\nArgs:\n{args}\n\nReturns:\n    {returns}\n"""',
            'class': '"""\n{description}\n\nAttributes:\n{attributes}\n"""',
            'method': '"""\n{description}\n\nArgs:\n{args}\n\nReturns:\n    {returns}\n"""'
        }
    
    def generate_function_docstring(self, func: Callable) -> str:
        """
        Gera docstring para função.
        
        Args:
            func (Callable): Função para a qual a docstring será gerada.
        
        Returns:
            str: Docstring gerada.
        """
        sig = inspect.signature(func)
        args_desc = [f"    {name}: {param.annotation if param.annotation != param.empty else 'Any'}" 
                     for name, param in sig.parameters.items() if name != 'self']
        
        return self.templates['function'].format(
            description=f"{func.__name__} - Função gerada automaticamente",
            args='\n'.join(args_desc) if args_desc else "    None",
            returns=sig.return_annotation if sig.return_annotation != sig.empty else "Any"
        )
    
    def auto_document_module(self, module_path: str) -> str:
        """
        Adiciona docstrings a um módulo.
        
        Args:
            module_path (str): Caminho do módulo a ser documentado.
        
        Returns:
            str: Código do módulo com docstrings adicionadas.
        """
        try:
            with open(module_path, 'r') as f:
                tree = ast.parse(f.read())
        except FileNotFoundError:
            raise FileNotFoundError(f"O módulo {module_path} não foi encontrado.")
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node):
                docstring = self.generate_function_docstring_from_ast(node)
                node.body.insert(0, ast.Expr(value=ast.Str(s=docstring)))
        
        return ast.unparse(tree)
    
    def generate_function_docstring_from_ast(self, node: Union[ast.FunctionDef, ast.ClassDef]) -> str:
        """
        Gera docstring a partir do AST.
        
        Args:
            node (Union[ast.FunctionDef, ast.ClassDef]): Nó do AST para o qual a docstring será gerada.
        
        Returns:
            str: Docstring gerada.
        """
        args = [f"    {arg.arg}: Any" for arg in node.args.args if arg.arg != 'self']
        
        return self.templates['function'].format(
            description=f"{node.name} - Documentação automática",
            args='\n'.join(args) if args else "    None",
            returns="Any"
        )

# Instância do gerador de docstrings
doc_generator = DocstringGenerator()