import json
from pathlib import Path
import re
from datetime import datetime

# Caminhos dos arquivos
BASE_DIR = Path(__file__).parent.parent.parent
MEMORIA_PATH = BASE_DIR / 'memoria_compartilhada.json'
STATUS_PATH = BASE_DIR / 'docs' / 'status_sistema.md'

# Função utilitária para formatar eventos

def formatar_eventos(eventos):
    linhas = []
    for ev in eventos:
        data = ev.get('data', '')
        evento = ev.get('evento', '')
        detalhes = ev.get('detalhes', '')
        linhas.append(f"- **{data}** — {evento} ({detalhes})")
    return '\n'.join(linhas)

# Função utilitária para formatar progresso dos agentes
def formatar_progresso(memoria):
    progresso = []
    op = memoria.get('memoria_operacional', {})
    progresso.append(f"- **Engenharia de Software:** {op.get('acoes', ['Sem registro'])[0] if op.get('acoes') else 'Sem registro'}")
    progresso.append(f"- **ML/Dados:** {op.get('acoes', ['Sem registro'])[1] if len(op.get('acoes', [])) > 1 else 'Sem registro'}")
    progresso.append(f"- **Ética/Security:** {memoria.get('memoria_etica', {}).get('principios', ['Sem registro'])[0] if memoria.get('memoria_etica', {}).get('principios') else 'Sem registro'}")
    progresso.append(f"- **Pesquisa I.A.:** {memoria.get('memoria_cognitiva', {}).get('heuristicas', ['Sem registro'])[0] if memoria.get('memoria_cognitiva', {}).get('heuristicas') else 'Sem registro'}")
    progresso.append(f"- **Orquestrador:** Consolidação e versionamento do status.")
    return '\n'.join(progresso)

# Função utilitária para formatar bloqueios
def formatar_bloqueios(memoria):
    alertas = memoria.get('estado_sistema', {}).get('alertas_ativos', [])
    if not alertas:
        return "- Nenhum bloqueio registrado até o momento."
    return '\n'.join(f"- {a}" for a in alertas)

def atualizar_logs_realtime():
    # Carregar memória compartilhada
    with open(MEMORIA_PATH, 'r', encoding='utf-8') as f:
        memoria = json.load(f)
    # Extrair eventos
    eventos = memoria.get('log_eventos', [])
    eventos_md = formatar_eventos(eventos)
    progresso_md = formatar_progresso(memoria)
    bloqueios_md = formatar_bloqueios(memoria)
    # Ler status_sistema.md
    with open(STATUS_PATH, 'r', encoding='utf-8') as f:
        status_md = f.read()
    # Regex para encontrar a seção de logs em tempo real
    padrao = r'(## 🟢 Acompanhamento de Logs em Tempo Real \(Sprint 1\)[\s\S]+?)(?=## |$)'
    nova_secao = f"## 🟢 Acompanhamento de Logs em Tempo Real (Sprint 1)\n\nEsta seção consolida os eventos, decisões e progresso dos agentes durante o Sprint 1, com base nos registros da `memoria_compartilhada.json`.\n\n---\n\n### ⏳ Últimos Eventos\n\n{eventos_md if eventos_md else '- Nenhum evento registrado.'}\n\n---\n\n### 📈 Progresso dos Agentes\n\n{progresso_md}\n\n---\n\n### 🚩 Bloqueios e Alertas\n\n{bloqueios_md}\n\n---\n\n### 🔄 Instruções para Atualização Contínua\n\n- Cada agente deve registrar eventos relevantes em `memoria_compartilhada.json`.\n- O orquestrador deve atualizar esta seção ao final de cada ciclo ou quando houver eventos críticos.\n- Bloqueios e alertas devem ser sinalizados imediatamente.\n\n---\n\n### 📚 Referência\n\n- Todos os eventos e decisões são rastreados em `memoria_compartilhada.json` (campos: `log_eventos`, `decisoes_recentes`, `memoria_operacional`).\n"
    # Substituir a seção antiga pela nova
    status_md_novo = re.sub(padrao, nova_secao + '\n', status_md, flags=re.MULTILINE)
    # Salvar arquivo atualizado
    with open(STATUS_PATH, 'w', encoding='utf-8') as f:
        f.write(status_md_novo)
    print(f"[OK] Logs em tempo real atualizados em {STATUS_PATH}")

if __name__ == "__main__":
    atualizar_logs_realtime() 