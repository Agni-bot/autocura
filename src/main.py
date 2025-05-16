"""
Sistema de Autocura Cognitiva - Arquivo Principal

Este arquivo serve como ponto de entrada do sistema, orquestrando todos os componentes
e gerenciando o fluxo de autocura. Ele integra:
- Monitoramento Multidimensional
- Diagnóstico Neural
- Gerador de Ações
- Interface Web (Portal)
"""

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from datetime import datetime
import argparse
import json
import os
import re

# Importação dos módulos principais do sistema
from monitoramento import Monitoramento  # Coleta dados multidimensionais
from diagnostico import Diagnostico      # Analisa dados e identifica anomalias
from gerador import GeradorAcoes         # Gera ações corretivas
from portal.routes.acao_necessaria import router as acao_router  # Interface de ações

# Configuração de logging para rastreamento de operações
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização da aplicação FastAPI
app = FastAPI(title="Sistema de Autocura Cognitiva")

# Configuração de arquivos estáticos e templates
app.mount("/static", StaticFiles(directory="src/portal/static"), name="static")
templates = Jinja2Templates(directory="src/portal/templates")

# Inicialização dos componentes principais do sistema
monitoramento = Monitoramento()  # Responsável pela coleta de dados
diagnostico = Diagnostico()      # Responsável pela análise
gerador = GeradorAcoes()         # Responsável pela geração de ações

# Integração da interface de ações necessárias
app.include_router(acao_router)

# Função utilitária de dry-run (baseada no main2.py)
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
MAPPING_FILE = os.path.join(PROJECT_ROOT, "../directory_mapping.json")
DRY_RUN_REPORT_FILE = os.path.join(PROJECT_ROOT, "../dry_run_report.md")
RELEVANT_EXTENSIONS = [
    ".py", ".go", ".md", ".txt", ".yaml", ".yml", ".json", ".sh", ".cmd", 
    "Dockerfile", ".tf", ".hcl", ".js", ".html", ".css"
]
IGNORE_FILES = ["generate_mapping.py", "dry_run_script.py", "directory_mapping.json", "dry_run_report.md"]
IGNORE_DIRS = [".git", ".pytest_cache", "__pycache__", "venv", "node_modules", "build", "dist"]

def is_binary_string(bytes_content):
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
        return False
    changed_mappings = [m for m in path_mappings if m["original_full_path"] != m["new_full_path"]]
    if not changed_mappings:
        report_content += "Nenhuma alteração de nome de diretório foi mapeada. Nenhuma referência seria alterada.\n"
        with open(DRY_RUN_REPORT_FILE, "w") as f_report:
            f_report.write(report_content)
        print(f"Relatório de dry-run salvo em {DRY_RUN_REPORT_FILE}")
        return True
    report_content += "## Mapeamento de Diretórios a Serem Renomeados:\n\n"
    for mapping_item in changed_mappings:
        report_content += f"- **Original**: `{mapping_item['original_full_path']}`\n"
        report_content += f"  - **Novo (Simulado)**: `{mapping_item['new_full_path']}`\n"
        report_content += f"  - **Tipo de Transformação**: {mapping_item['transformation_type']}\n\n"
    report_content += "## Arquivos que Seriam Afetados por Atualizações de Referência:\n\n"
    for root, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file_name in files:
            if file_name in IGNORE_FILES:
                continue
            file_path = os.path.join(root, file_name)
            file_ext = os.path.splitext(file_name)[1]
            base_name_no_ext = os.path.splitext(file_name)[0]
            if not (file_ext.lower() in RELEVANT_EXTENSIONS or base_name_no_ext in RELEVANT_EXTENSIONS or file_ext == ""):
                continue
            try:
                with open(file_path, "rb") as f_bin_check:
                    if is_binary_string(f_bin_check.read(1024)):
                        continue
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f_content:
                    lines = f_content.readlines()
            except Exception as e:
                continue
            for i, line_content in enumerate(lines):
                for mapping_item in changed_mappings:
                    original_path_str = mapping_item["original_full_path"].replace(PROJECT_ROOT + "/", "")
                    new_path_str = mapping_item["new_full_path"].replace(PROJECT_ROOT + "/", "")
                    original_basename = os.path.basename(mapping_item["original_full_path"])
                    new_basename = os.path.basename(mapping_item["new_full_path"])
                    search_patterns = [
                        re.escape(mapping_item["original_full_path"]),
                        re.escape(original_path_str),
                        re.escape(original_basename)
                    ]
                    for pattern in search_patterns:
                        if re.search(pattern, line_content):
                            report_content += f"- Arquivo: `{file_path}` (linha {i+1})\n"
                            report_content += f"  - Ocorrência: `{line_content.strip()}`\n"
    with open(DRY_RUN_REPORT_FILE, "w") as f_report:
        f_report.write(report_content)
    print(f"Relatório de dry-run salvo em {DRY_RUN_REPORT_FILE}")
    return True

@app.get("/")
async def home(request: Request):
    """
    Página inicial do sistema.
    Renderiza o dashboard principal com status dos componentes.
    """
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "timestamp": datetime.now()
        }
    )

@app.post("/api/ciclo-autocura")
async def iniciar_ciclo_autocura():
    """
    Inicia um novo ciclo de autocura.
    
    Fluxo de execução:
    1. Coleta dados do monitoramento
    2. Realiza diagnóstico dos dados coletados
    3. Gera ações corretivas baseadas no diagnóstico
    
    Retorna:
        dict: Resultado do ciclo com status e diagnóstico
    """
    try:
        # 1. Coleta dados do monitoramento
        dados = monitoramento.coletar_dados()
        
        # 2. Realiza diagnóstico
        resultado_diagnostico = diagnostico.analisar(dados)
        
        # 3. Gera ações baseadas no diagnóstico
        if resultado_diagnostico['necessita_acao']:
            # Gera ações para cada tipo (hotfix, refatoracao, redesign)
            for tipo in ['hotfix', 'refatoracao', 'redesign']:
                if resultado_diagnostico['prioridade_' + tipo] > 0:
                    acao = gerador.gerar_acao(resultado_diagnostico, tipo)
                    logger.info(f"Ação gerada: {acao.id} - {acao.tipo}")
        
        return {
            "success": True,
            "message": "Ciclo de autocura iniciado com sucesso",
            "diagnostico": resultado_diagnostico
        }
    
    except Exception as e:
        logger.error(f"Erro no ciclo de autocura: {str(e)}")
        return {
            "success": False,
            "message": f"Erro no ciclo de autocura: {str(e)}"
        }

@app.post("/api/dry-run")
async def dry_run_endpoint():
    try:
        result = generate_dry_run_report()
        if result:
            return {"success": True, "message": "Relatório de dry-run gerado com sucesso."}
        else:
            return {"success": False, "message": "Erro ao gerar relatório de dry-run."}
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sistema de Autocura Cognitiva")
    parser.add_argument("--dry-run", action="store_true", help="Executa o utilitário de dry-run de renomeação de diretórios")
    args = parser.parse_args()
    if args.dry_run:
        generate_dry_run_report()
    else:
        # Inicia o servidor FastAPI normalmente
        uvicorn.run(app, host="0.0.0.0", port=8000)
