import json
from pathlib import Path

CAMINHO_MEMORIA = Path(__file__).parent / "memoria_compartilhada.json"

def carregar_memoria():
    if not CAMINHO_MEMORIA.exists():
        return {
            "decisoes_recentes": [],
            "feedback_modelo": [],
            "erros_criticos": [],
            "etapas_concluidas": [],
            "documentacao_chave": [],
            "alertas_eticos": []
        }
    with open(CAMINHO_MEMORIA, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_memoria(memoria):
    with open(CAMINHO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, indent=4, ensure_ascii=False)

def registrar(item, categoria):
    memoria = carregar_memoria()
    if categoria not in memoria:
        raise ValueError(f"Categoria '{categoria}' não encontrada na memória.")
    if item not in memoria[categoria]:
        memoria[categoria].append(item)
        salvar_memoria(memoria)
        print(f"✅ Item registrado em '{categoria}'.")
    else:
        print(f"⚠️ Item já existente em '{categoria}'.")

def consultar(categoria):
    memoria = carregar_memoria()
    if categoria not in memoria:
        raise ValueError(f"Categoria '{categoria}' não encontrada na memória.")
    return memoria[categoria]

def listar_categorias():
    memoria = carregar_memoria()
    return list(memoria.keys())

def atualizar_item(categoria, index, novo_valor):
    memoria = carregar_memoria()
    if categoria not in memoria:
        raise ValueError(f"Categoria '{categoria}' não encontrada na memória.")
    if index >= len(memoria[categoria]):
        raise IndexError("Índice fora do intervalo.")
    memoria[categoria][index] = novo_valor
    salvar_memoria(memoria)
    print(f"🔄 Item na posição {index} de '{categoria}' atualizado.")
