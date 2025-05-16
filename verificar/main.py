
import json
import os
import re

PROJECT_ROOT = "/home/ubuntu/Autocura_project/Autocura"
MAPPING_FILE = "/home/ubuntu/directory_mapping.json"
DRY_RUN_REPORT_FILE = "/home/ubuntu/dry_run_report.md"

# Tipos de arquivos a serem verificados (extensões comuns)
# Adicionar mais conforme necessário para o projeto Autocura
RELEVANT_EXTENSIONS = [
    ".py", ".go", ".md", ".txt", ".yaml", ".yml", ".json", ".sh", ".cmd", 
    "Dockerfile", ".tf", ".hcl", ".js", ".html", ".css"
]
# Arquivos a serem ignorados (nomes exatos ou padrões)
IGNORE_FILES = ["generate_mapping.py", "dry_run_script.py", "directory_mapping.json", "dry_run_report.md"]
IGNORE_DIRS = [".git", ".pytest_cache", "__pycache__", "venv", "node_modules", "build", "dist"]

def is_binary_string(bytes_content):
    """Heurística simples para detectar se um conteúdo é binário."""
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    return bool(bytes_content.translate(None, textchars))

def generate_dry_run_report():
    report_content = "# Relatório de Dry-Run - Refatoração de Nomes de Diretório\n\n"
    report_content += "Este relatório simula as alterações que seriam feitas nos nomes dos diretórios e nas referências a esses diretórios em arquivos do projeto. **Nenhuma alteração real foi aplicada.**\n\n"
    
    try:
        with open(MAPPING_FILE, "r") as f:
            path_mappings = json.load(f)
    except FileNotFoundError:
        report_content += "**ERRO: Arquivo de mapeamento `directory_mapping.json` não encontrado.**\n"
        with open(DRY_RUN_REPORT_FILE, "w") as f_report:
            f_report.write(report_content)
        print(f"Relatório de dry-run (com erro) salvo em {DRY_RUN_REPORT_FILE}")
        return

    changed_mappings = [m for m in path_mappings if m["original_full_path"] != m["new_full_path"]]

    if not changed_mappings:
        report_content += "Nenhuma alteração de nome de diretório foi mapeada. Nenhuma referência seria alterada.\n"
        with open(DRY_RUN_REPORT_FILE, "w") as f_report:
            f_report.write(report_content)
        print(f"Relatório de dry-run salvo em {DRY_RUN_REPORT_FILE}")
        return

    report_content += "## Mapeamento de Diretórios a Serem Renomeados:\n\n"
    for mapping_item in changed_mappings:
        report_content += f"- **Original**: `{mapping_item['original_full_path']}`\n"
        report_content += f"  - **Novo (Simulado)**: `{mapping_item['new_full_path']}`\n"
        report_content += f"  - **Tipo de Transformação**: {mapping_item['transformation_type']}\n\n"

    report_content += "## Arquivos que Seriam Afetados por Atualizações de Referência:\n\n"
    files_with_potential_changes = {}

    for root, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
        # Ignorar diretórios especificados
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        # Ignorar diretórios que são eles próprios os originais (serão "movidos", não lidos para substituição interna)
        # ou que já são os novos (para evitar reprocessamento em um dry-run repetido)
        original_paths_basenames = [os.path.basename(m["original_full_path"]) for m in changed_mappings]
        new_paths_basenames = [os.path.basename(m["new_full_path"]) for m in changed_mappings]
        dirs[:] = [d for d in dirs if d not in original_paths_basenames and d not in new_paths_basenames]

        for file_name in files:
            if file_name in IGNORE_FILES:
                continue
            
            file_path = os.path.join(root, file_name)
            file_ext = os.path.splitext(file_name)[1]
            base_name_no_ext = os.path.splitext(file_name)[0]

            # Verifica se a extensão é relevante ou se é um arquivo sem extensão mas com nome relevante (ex: Dockerfile)
            if not (file_ext.lower() in RELEVANT_EXTENSIONS or base_name_no_ext in RELEVANT_EXTENSIONS or file_ext == ""):
                continue

            try:
                with open(file_path, "rb") as f_bin_check: # Abre em modo binário para checar
                    if is_binary_string(f_bin_check.read(1024)): # Lê primeiros 1KB
                        # print(f"Ignorando arquivo binário: {file_path}")
                        continue
                
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f_content:
                    lines = f_content.readlines()
            except Exception as e:
                # print(f"Não foi possível ler o arquivo {file_path}: {e}")
                continue

            for i, line_content in enumerate(lines):
                for mapping_item in changed_mappings:
                    original_path_str = mapping_item["original_full_path"].replace(PROJECT_ROOT + "/", "") # Caminho relativo ao projeto
                    new_path_str = mapping_item["new_full_path"].replace(PROJECT_ROOT + "/", "")
                    
                    # Variações de caminhos a serem buscadas (absoluto, relativo ao projeto, apenas o basename)
                    # É importante ser cuidadoso para não fazer substituições incorretas.
                    # Por simplicidade no dry-run, vamos focar em ocorrências do caminho completo ou relativo ao projeto.
                    # E também o basename da pasta original.
                    original_basename = os.path.basename(mapping_item["original_full_path"])
                    new_basename = os.path.basename(mapping_item["new_full_path"])

                    # Padrões de busca mais específicos para evitar falsos positivos
                    # Ex: /path/to/dir, path/to/dir, 'path/to/dir', "path/to/dir"
                    # E também apenas o nome da pasta, ex: 'dir_name'
                    search_patterns = [
                        re.escape(mapping_item["original_full_path"]),
                        re.escape(original_path_str), 
                        r"([\"']|^|\s|/|=)
