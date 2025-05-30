"""
Módulo de Monitoramento - Aplicação Flask

Este módulo implementa a API REST para o serviço de monitoramento.
"""

from flask import Flask, request, jsonify, render_template
import time
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .metricas import MetricasSistema, MonitoramentoMultidimensional
from .recursos import MonitorRecursos
from .config import CONFIG
from .monitor_sistema import MonitorSistema
from .diagnostico import SistemaDiagnostico, StatusDiagnostico, Severidade
from .visualizacao_4d import Visualizacao4D
from datetime import timedelta

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("Monitoramento")

# Inicializa a aplicação Flask
app = Flask(__name__)

# Inicializa componentes
metricas = MetricasSistema(
    throughput=CONFIG.get('throughput', 100),
    taxa_erro=CONFIG.get('taxa_erro', 0.01),
    latencia=CONFIG.get('latencia', 0.1),
    uso_recursos=CONFIG.get('uso_recursos', {
        'cpu': 0.0,
        'memoria': 0.0,
        'disco': 0.0
    })
)
monitor = MonitorSistema()
recursos = MonitorRecursos()
sistema_diagnostico = SistemaDiagnostico()
visualizador_4d = Visualizacao4D({})

@app.before_first_request
def iniciar_monitor():
    """Inicia o monitoramento antes da primeira requisição."""
    monitor.iniciar()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde."""
    return jsonify({
        'status': 'ok',
        'timestamp': time.time()
    })

@app.route('/ready', methods=['GET'])
def ready_check():
    """
    Verifica se o serviço está pronto para operação.
        
    Returns:
        dict: Status de prontidão
    """
    if not metricas or not monitor or not recursos:
        return jsonify({"status": "not ready", "reason": "Components not initialized"}), 503
    return jsonify({"status": "ready", "timestamp": time.time()})

@app.route('/metrics', methods=['GET'])
def metrics():
    """Endpoint para métricas Prometheus."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/metricas', methods=['GET'])
def obter_metricas():
    """Endpoint para obter métricas atuais."""
    return jsonify(monitor.obter_metricas())

@app.route('/api/historico/<metrica>', methods=['GET'])
def obter_historico(metrica):
    """Endpoint para obter histórico de uma métrica."""
    limite = request.args.get('limite', default=100, type=int)
    return jsonify(monitor.obter_historico(metrica, limite))

@app.route('/api/processos', methods=['GET'])
def obter_processos():
    """Endpoint para obter lista de processos."""
    return jsonify(monitor.obter_processos())

@app.route('/api/analise', methods=['GET'])
def analisar_metricas():
    """
    Realiza análise das métricas coletadas.
    
    Returns:
        dict: Resultados da análise
    """
    try:
        resultados = monitor.analisar_metricas()
        return jsonify(resultados), 200
    except Exception as e:
        logger.error(f"Erro ao analisar métricas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/alertas', methods=['GET'])
def gerar_alertas():
    """
    Gera alertas baseados na análise de métricas.
    
    Returns:
        dict: Lista de alertas gerados
    """
    try:
        alertas = recursos.gerar_alertas()
        return jsonify(alertas), 200
    except Exception as e:
        logger.error(f"Erro ao gerar alertas: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Endpoint para o dashboard de monitoramento."""
    metricas = monitor.obter_metricas()
    analise = metricas.get('analise', {})
    alertas = monitor.monitor.verificar_alertas(metricas.get('metricas', {}))
    
    return render_template(
        'dashboard.html',
        metricas=metricas.get('metricas', {}),
        analise=analise,
        alertas=alertas
    )

@app.route('/api/diagnostico/problemas', methods=['GET'])
def listar_problemas():
    """Lista problemas detectados com filtros opcionais."""
    try:
        status = request.args.get('status')
        severidade = request.args.get('severidade')
        
        if status:
            status = StatusDiagnostico(status)
        if severidade:
            severidade = Severidade(severidade)
            
        problemas = sistema_diagnostico.listar_problemas(status, severidade)
        return jsonify([{
            "id": p.id,
            "titulo": p.titulo,
            "descricao": p.descricao,
            "causa_raiz": p.causa_raiz,
            "recomendacoes": p.recomendacoes,
            "timestamp": p.timestamp.isoformat(),
            "status": p.status.value,
            "severidade": p.severidade.value,
            "componentes_afetados": p.componentes_afetados,
            "metricas": p.metricas,
            "logs": p.logs,
            "metadata": p.metadata
        } for p in problemas])
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/diagnostico/problemas/<problema_id>', methods=['GET'])
def obter_problema(problema_id):
    """Obtém detalhes de um problema específico."""
    try:
        problema = sistema_diagnostico.obter_problema(problema_id)
        if not problema:
            return jsonify({"erro": "Problema não encontrado"}), 404
            
        return jsonify({
            "id": problema.id,
            "titulo": problema.titulo,
            "descricao": problema.descricao,
            "causa_raiz": problema.causa_raiz,
            "recomendacoes": problema.recomendacoes,
            "timestamp": problema.timestamp.isoformat(),
            "status": problema.status.value,
            "severidade": problema.severidade.value,
            "componentes_afetados": problema.componentes_afetados,
            "metricas": problema.metricas,
            "logs": problema.logs,
            "metadata": problema.metadata
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/diagnostico/analisar', methods=['POST'])
def analisar_problemas():
    """Inicia uma nova análise de diagnóstico."""
    try:
        metricas = monitor.obter_metricas()
        problemas = sistema_diagnostico.analisar_metricas(metricas)
        
        for problema in problemas:
            sistema_diagnostico.registrar_problema(problema)
            
        return jsonify({
            "mensagem": "Análise concluída",
            "problemas_detectados": len(problemas)
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/diagnostico/historico', methods=['GET'])
def historico_diagnostico():
    """Retorna histórico de diagnósticos."""
    try:
        inicio = request.args.get('inicio')
        fim = request.args.get('fim')
        
        historico = sistema_diagnostico.obter_historico(inicio, fim)
        return jsonify(historico)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/diagnostico/problemas/<problema_id>/status', methods=['PUT'])
def atualizar_status_problema(problema_id):
    """Atualiza o status de um problema."""
    try:
        novo_status = request.json.get('status')
        if not novo_status:
            return jsonify({"erro": "Status não fornecido"}), 400
            
        sistema_diagnostico.atualizar_status(problema_id, StatusDiagnostico(novo_status))
        return jsonify({"mensagem": "Status atualizado com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/diagnostico/problemas/<problema_id>/recomendacoes', methods=['POST'])
def adicionar_recomendacao(problema_id):
    """Adiciona uma nova recomendação a um problema."""
    try:
        recomendacao = request.json.get('recomendacao')
        if not recomendacao:
            return jsonify({"erro": "Recomendação não fornecida"}), 400
            
        sistema_diagnostico.adicionar_recomendacao(problema_id, recomendacao)
        return jsonify({"mensagem": "Recomendação adicionada com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/diagnostico/problemas/<problema_id>/logs', methods=['POST'])
def adicionar_log(problema_id):
    """Adiciona um novo log a um problema."""
    try:
        log = request.json.get('log')
        if not log:
            return jsonify({"erro": "Log não fornecido"}), 400
            
        sistema_diagnostico.adicionar_log(problema_id, log)
        return jsonify({"mensagem": "Log adicionado com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/visualizacao/dimensoes/<nome>', methods=['GET'])
def obter_dimensao(nome):
    """Obtém dados de uma dimensão 4D."""
    try:
        periodo = request.args.get('periodo')
        if periodo:
            periodo = timedelta(minutes=int(periodo))
            
        dimensoes = visualizador_4d.obter_dimensao(nome, periodo)
        return jsonify([{
            "nome": d.nome,
            "valor": d.valor,
            "timestamp": d.timestamp.isoformat(),
            "contexto": d.contexto
        } for d in dimensoes])
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/visualizacao/dimensoes/<nome>/estatisticas', methods=['GET'])
def estatisticas_dimensao(nome):
    """Obtém estatísticas de uma dimensão 4D."""
    try:
        periodo = request.args.get('periodo')
        if periodo:
            periodo = timedelta(minutes=int(periodo))
            
        estatisticas = visualizador_4d.calcular_estatisticas(nome, periodo)
        return jsonify(estatisticas)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/visualizacao/dimensoes/<nome>/anomalias', methods=['GET'])
def anomalias_dimensao(nome):
    """Obtém anomalias detectadas em uma dimensão 4D."""
    try:
        periodo = request.args.get('periodo')
        if periodo:
            periodo = timedelta(minutes=int(periodo))
            
        anomalias = visualizador_4d.detectar_anomalias(nome, periodo)
        return jsonify(anomalias)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/visualizacao/correlacoes', methods=['GET'])
def correlacoes():
    """Obtém matriz de correlação entre dimensões."""
    try:
        periodo = request.args.get('periodo')
        if periodo:
            periodo = timedelta(minutes=int(periodo))
            
        matriz = visualizador_4d.gerar_matriz_correlacao(periodo)
        return jsonify(matriz)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/visualizacao/dimensoes/<nome>/tendencias', methods=['GET'])
def tendencias_dimensao(nome):
    """Obtém tendências detectadas em uma dimensão 4D."""
    try:
        periodo = request.args.get('periodo')
        if periodo:
            periodo = timedelta(minutes=int(periodo))
            
        tendencias = visualizador_4d.detectar_tendencias(nome, periodo)
        return jsonify(tendencias)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/visualizacao/relatorio', methods=['GET'])
def relatorio_visualizacao():
    """Gera relatório completo de visualização."""
    try:
        periodo = request.args.get('periodo')
        if periodo:
            periodo = timedelta(minutes=int(periodo))
            
        relatorio = visualizador_4d.gerar_relatorio(periodo)
        return jsonify(relatorio)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(
        host=CONFIG.HOST,
        port=CONFIG.PORT,
        debug=CONFIG.DEBUG
    ) 