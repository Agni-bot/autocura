#!/usr/bin/env python3
"""
Script de Consolidação da Estrutura de Módulos
==============================================

Este script verifica e consolida a estrutura dos módulos do sistema AutoCura,
resolvendo conflitos entre diretórios /modulos/ e /src/modulos/.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any

class ModuleStructureConsolidator:
    """Consolidador da estrutura de módulos"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.modules_path = self.root_path / "modulos"
        self.src_modules_path = self.root_path / "src" / "modulos"
        self.report = {
            "modules_found": {},
            "conflicts": [],
            "actions_taken": [],
            "recommendations": []
        }
    
    def scan_modules(self) -> Dict[str, Any]:
        """Escaneia e mapeia todos os módulos encontrados"""
        modules_map = {}
        
        # Escaneia /modulos/
        if self.modules_path.exists():
            for item in self.modules_path.iterdir():
                if item.is_dir() and not item.name.startswith("__"):
                    modules_map[item.name] = {
                        "main_location": str(item),
                        "has_src": (item / "src").exists(),
                        "has_tests": (item / "tests").exists(),
                        "has_readme": (item / "README.md").exists(),
                        "files": list(item.rglob("*.py"))
                    }
        
        # Escaneia /src/modulos/
        if self.src_modules_path.exists():
            for item in self.src_modules_path.iterdir():
                if item.is_dir() and not item.name.startswith("__"):
                    if item.name in modules_map:
                        # Conflito detectado
                        modules_map[item.name]["conflict_location"] = str(item)
                        modules_map[item.name]["has_conflict"] = True
                        self.report["conflicts"].append({
                            "module": item.name,
                            "main": modules_map[item.name]["main_location"],
                            "conflict": str(item)
                        })
                    else:
                        modules_map[item.name] = {
                            "main_location": str(item),
                            "has_src": False,
                            "has_tests": False,
                            "has_readme": False,
                            "files": list(item.rglob("*.py")),
                            "in_src_only": True
                        }
        
        self.report["modules_found"] = modules_map
        return modules_map
    
    def consolidate_modules(self) -> None:
        """Consolida módulos resolvendo conflitos"""
        modules_map = self.scan_modules()
        
        for module_name, module_info in modules_map.items():
            if module_info.get("has_conflict"):
                self._resolve_conflict(module_name, module_info)
            elif module_info.get("in_src_only"):
                self._move_from_src(module_name, module_info)
            else:
                self._validate_structure(module_name, module_info)
    
    def _resolve_conflict(self, module_name: str, module_info: Dict[str, Any]) -> None:
        """Resolve conflito entre /modulos/ e /src/modulos/"""
        main_path = Path(module_info["main_location"])
        conflict_path = Path(module_info["conflict_location"])
        
        # Analisa qual tem mais conteúdo
        main_files = len(module_info["files"])
        conflict_files = len(list(conflict_path.rglob("*.py")))
        
        if conflict_files > main_files:
            # Move conteúdo do conflito para o principal
            self._merge_directories(conflict_path, main_path)
            action = f"Merged {conflict_path} into {main_path}"
        else:
            action = f"Kept {main_path}, removed {conflict_path}"
        
        # Remove diretório de conflito
        shutil.rmtree(conflict_path)
        
        self.report["actions_taken"].append({
            "action": "resolve_conflict",
            "module": module_name,
            "details": action
        })
    
    def _move_from_src(self, module_name: str, module_info: Dict[str, Any]) -> None:
        """Move módulo de /src/modulos/ para /modulos/"""
        src_path = Path(module_info["main_location"])
        dest_path = self.modules_path / module_name
        
        # Cria diretório destino se não existir
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move o módulo
        shutil.move(str(src_path), str(dest_path))
        
        self.report["actions_taken"].append({
            "action": "move_from_src",
            "module": module_name,
            "from": str(src_path),
            "to": str(dest_path)
        })
    
    def _merge_directories(self, source: Path, dest: Path) -> None:
        """Merge de diretórios preservando conteúdo"""
        for item in source.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(source)
                dest_file = dest / rel_path
                
                # Cria diretório pai se necessário
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Move arquivo
                if not dest_file.exists():
                    shutil.copy2(item, dest_file)
                else:
                    # Arquivo existe, backup antes de sobrescrever
                    backup_file = dest_file.with_suffix(f"{dest_file.suffix}.backup")
                    shutil.copy2(dest_file, backup_file)
                    shutil.copy2(item, dest_file)
    
    def _validate_structure(self, module_name: str, module_info: Dict[str, Any]) -> None:
        """Valida e corrige estrutura do módulo"""
        module_path = Path(module_info["main_location"])
        
        # Estrutura esperada
        expected_dirs = ["src", "tests", "docs"]
        expected_files = ["README.md", "__init__.py"]
        
        for dir_name in expected_dirs:
            dir_path = module_path / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True)
                self.report["actions_taken"].append({
                    "action": "create_directory",
                    "module": module_name,
                    "directory": str(dir_path)
                })
        
        for file_name in expected_files:
            file_path = module_path / file_name
            if not file_path.exists():
                if file_name == "__init__.py":
                    file_path.write_text('"""Módulo do Sistema AutoCura"""')
                elif file_name == "README.md":
                    file_path.write_text(f"# Módulo {module_name.title()}\n\nDescrição do módulo.")
                
                self.report["actions_taken"].append({
                    "action": "create_file",
                    "module": module_name,
                    "file": str(file_path)
                })
    
    def update_imports(self) -> None:
        """Atualiza importações no código para refletir nova estrutura"""
        # Padrões de importação a corrigir
        import_patterns = [
            ("from modulos.", "from modulos."),
            ("import modulos.", "import modulos."),
        ]
        
        # Arquivos a verificar
        files_to_check = list(self.root_path.rglob("*.py"))
        
        for file_path in files_to_check:
            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content
                
                for old_pattern, new_pattern in import_patterns:
                    content = content.replace(old_pattern, new_pattern)
                
                if content != original_content:
                    file_path.write_text(content, encoding="utf-8")
                    self.report["actions_taken"].append({
                        "action": "update_imports",
                        "file": str(file_path),
                        "changes": len([p for p in import_patterns if p[0] in original_content])
                    })
            except Exception as e:
                print(f"Erro ao processar {file_path}: {e}")
    
    def generate_recommendations(self) -> None:
        """Gera recomendações para melhorar a estrutura"""
        modules_map = self.report["modules_found"]
        
        for module_name, module_info in modules_map.items():
            recommendations = []
            
            if not module_info.get("has_tests"):
                recommendations.append("Criar suite de testes")
            
            if not module_info.get("has_readme"):
                recommendations.append("Criar documentação README.md")
            
            if not module_info.get("has_src"):
                recommendations.append("Organizar código em diretório src/")
            
            if len(module_info.get("files", [])) == 0:
                recommendations.append("Módulo vazio - implementar funcionalidades")
            
            if recommendations:
                self.report["recommendations"].append({
                    "module": module_name,
                    "recommendations": recommendations
                })
    
    def save_report(self) -> None:
        """Salva relatório da consolidação"""
        report_path = self.root_path / "reports" / "module_consolidation_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Relatório salvo em: {report_path}")
    
    def run(self) -> Dict[str, Any]:
        """Executa processo completo de consolidação"""
        print("🔍 Escaneando módulos...")
        self.scan_modules()
        
        print("🔧 Consolidando estrutura...")
        self.consolidate_modules()
        
        print("📝 Atualizando importações...")
        self.update_imports()
        
        print("💡 Gerando recomendações...")
        self.generate_recommendations()
        
        print("💾 Salvando relatório...")
        self.save_report()
        
        return self.report

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 CONSOLIDADOR DE ESTRUTURA DE MÓDULOS")
    print("Sistema AutoCura - Organização e Correção")
    print("=" * 60)
    
    consolidator = ModuleStructureConsolidator()
    report = consolidator.run()
    
    print("\n📊 RESUMO DA CONSOLIDAÇÃO:")
    print(f"Módulos encontrados: {len(report['modules_found'])}")
    print(f"Conflitos resolvidos: {len(report['conflicts'])}")
    print(f"Ações executadas: {len(report['actions_taken'])}")
    print(f"Recomendações geradas: {len(report['recommendations'])}")
    
    if report["conflicts"]:
        print("\n⚠️  CONFLITOS RESOLVIDOS:")
        for conflict in report["conflicts"]:
            print(f"  - {conflict['module']}: {conflict['main']} vs {conflict['conflict']}")
    
    if report["recommendations"]:
        print("\n💡 RECOMENDAÇÕES:")
        for rec in report["recommendations"]:
            print(f"  - {rec['module']}: {', '.join(rec['recommendations'])}")
    
    print("\n✅ Consolidação concluída!")

if __name__ == "__main__":
    main() 