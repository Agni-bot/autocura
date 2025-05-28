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