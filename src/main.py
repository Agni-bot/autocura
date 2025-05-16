<<<<<<< HEAD
import time
import logging
from monitoramento import MonitoramentoMultidimensional
from diagnostico import RedeNeuralDiagnostico
from gerador import GeradorAcoes

class SistemaAutocuraCognitiva:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitor = MonitoramentoMultidimensional()
        self.diagnostico = RedeNeuralDiagnostico()
        self.gerador = GeradorAcoes()
        
    def executar_ciclo(self):
        """Executa um ciclo completo de monitoramento, diagnóstico e geração de ações"""
        try:
            # 1. Monitoramento
            self.logger.info("Iniciando coleta de métricas...")
            metricas = self.monitor.coletar_metricas()
            
            # 2. Diagnóstico
            self.logger.info("Realizando diagnóstico...")
            resultado_diagnostico = self.diagnostico.gerar_diagnostico(metricas)
            
            # 3. Geração de Ações
            self.logger.info("Gerando ações...")
            acoes = self.gerador.gerar_acoes(resultado_diagnostico, metricas)
            acoes_priorizadas = self.gerador.priorizar_acoes(acoes)
            
            # 4. Exibição de Resultados
            self._exibir_resultados(metricas, resultado_diagnostico, acoes_priorizadas)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro durante o ciclo de autocura: {str(e)}")
            return False
    
    def _exibir_resultados(self, metricas, diagnostico, acoes):
        """Exibe os resultados do ciclo de forma organizada"""
        print("\n" + "="*50)
        print("RESULTADOS DO CICLO DE AUTOCURA COGNITIVA")
        print("="*50)
        
        print("\nMÉTRICAS COLETADAS:")
        print(f"Throughput: {metricas.throughput:.2f} ops/s")
        print(f"Taxa de Erro: {metricas.taxa_erro:.2f}%")
        print(f"Latência: {metricas.latencia:.2f} ms")
        print("Uso de Recursos:")
        for recurso, valor in metricas.uso_recursos.items():
            print(f"  - {recurso}: {valor:.2f}%")
        
        print("\nDIAGNÓSTICO:")
        print(f"Anomalia Detectada: {diagnostico.anomalia_detectada}")
        print(f"Tipo de Anomalia: {diagnostico.tipo_anomalia}")
        print(f"Nível de Gravidade: {diagnostico.nivel_gravidade:.2f}")
        print("\nRecomendações do Diagnóstico:")
        for rec in diagnostico.recomendacoes:
            print(f"  - {rec}")
        
        print("\nAÇÕES PRIORIZADAS:")
        for acao in acoes:
            print(f"\nTipo: {acao.tipo.upper()}")
            print(f"Descrição: {acao.descricao}")
            print(f"Prioridade: {acao.prioridade}")
            print(f"Tempo Estimado: {acao.tempo_estimado}")
            print(f"Recursos Necessários: {', '.join(acao.recursos_necessarios)}")
        
        print("\n" + "="*50)

def main():
    # Configuração do logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicialização do sistema
    sistema = SistemaAutocuraCognitiva()
    
    # Simulação de ciclos contínuos
    while True:
        try:
            sistema.executar_ciclo()
            time.sleep(5)  # Intervalo entre ciclos
        except KeyboardInterrupt:
            print("\nSistema encerrado pelo usuário")
            break
        except Exception as e:
            logging.error(f"Erro fatal: {str(e)}")
            break

if __name__ == "__main__":
    main() 
=======
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

if __name__ == "__main__":
    # Inicia o servidor FastAPI
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 
>>>>>>> origin/main
