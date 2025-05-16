# core.py - Lógica principal do microsserviço Consciência Situacional
import os
import json
import yaml # Para carregar whitelist e api_endpoints
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable
import time

# Importar componentes internos
from .web.data_sources import WebDataMiner
from .web.validation import validar_dados_web
from .web.rate_limiter import APIRateLimiter, RateLimitExceeded
from .shared_utils.cache import global_redis_cache_instance # Usar a instância global ou injetar

KAFKA_BROKER = os.getenv("KAFKA_BROKER_URL", "kafka:9092")
TOPIC_DIAGNOSTICO = os.getenv("TOPIC_DIAGNOSTICO", "autocura.diagnostico")
TOPIC_ESTRATEGIA = os.getenv("TOPIC_ESTRATEGIA", "autocura.estrategia")

# Caminho base para arquivos de configuração montados em produção (via Kubernetes)
PROD_CONFIG_PATH = "/app/config"
# Caminho base para arquivos de configuração em desenvolvimento local
DEV_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config") # Aponta para a pasta config na raiz do projeto Autocura

# Determina o caminho de configuração a ser usado
# Se a variável de ambiente CONFIG_PATH for definida (ex: em K8s), usa ela.
# Senão, verifica se está no modo __main__ (local dev) e usa DEV_CONFIG_PATH.
# Caso contrário (importado como módulo, mas não em __main__ e sem CONFIG_PATH), usa PROD_CONFIG_PATH como fallback.
if os.getenv("CONFIG_PATH"):
    CONFIG_PATH_TO_USE = os.getenv("CONFIG_PATH")
elif "__main__" in __name__ and os.path.basename(__file__) == "core.py": # Verifica se está sendo executado como script principal
    CONFIG_PATH_TO_USE = DEV_CONFIG_PATH
    print(f"Execução local detectada, usando DEV_CONFIG_PATH: {os.path.abspath(CONFIG_PATH_TO_USE)}")
else:
    CONFIG_PATH_TO_USE = PROD_CONFIG_PATH
    print(f"Usando PROD_CONFIG_PATH: {CONFIG_PATH_TO_USE}")

WHITELIST_FILE = os.path.join(CONFIG_PATH_TO_USE, "whitelist.yaml")
API_ENDPOINTS_FILE = os.path.join(CONFIG_PATH_TO_USE, "api_endpoints.yaml")

# Variáveis de ambiente para chaves e endpoints de API (serão injetadas pelo Kubernetes)
NEWS_API_KEY_ENV = "NEWS_API_KEY"
FINANCE_API_KEY_ENV = "FINANCE_API_KEY"
CLIMATE_API_KEY_ENV = "CLIMATE_API_KEY"

NEWS_API_ENDPOINT_ENV = "NEWS_API_ENDPOINT"
FINANCE_API_ENDPOINT_ENV = "FINANCE_API_ENDPOINT"
CLIMATE_API_ENDPOINT_ENV = "CLIMATE_API_ENDPOINT"

# Configurações de Rate Limiting (podem vir de variáveis de ambiente ou config)
NEWS_API_RATE_LIMIT_CALLS = int(os.getenv("NEWS_API_RATE_LIMIT_CALLS", 50))
NEWS_API_RATE_LIMIT_INTERVAL = int(os.getenv("NEWS_API_RATE_LIMIT_INTERVAL", 60))
FINANCE_API_RATE_LIMIT_CALLS = int(os.getenv("FINANCE_API_RATE_LIMIT_CALLS", 30))
FINANCE_API_RATE_LIMIT_INTERVAL = int(os.getenv("FINANCE_API_RATE_LIMIT_INTERVAL", 60))
CLIMATE_API_RATE_LIMIT_CALLS = int(os.getenv("CLIMATE_API_RATE_LIMIT_CALLS", 60))
CLIMATE_API_RATE_LIMIT_INTERVAL = int(os.getenv("CLIMATE_API_RATE_LIMIT_INTERVAL", 60))

def load_yaml_config(file_path, default_value=None):
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Arquivo de configuração {file_path} não encontrado. Usando default: {default_value}")
        return default_value
    except Exception as e:
        print(f"Erro ao carregar ou parsear {file_path}: {e}. Usando default: {default_value}")
        return default_value

class ConscienciaSituacionalService:
    def __init__(self):
        print("Iniciando Serviço de Consciência Situacional...")
        self.kafka_connected = False
        try:
            self.consumer = KafkaConsumer(
                TOPIC_DIAGNOSTICO,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="consciencia-situacional-group",
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                consumer_timeout_ms=10000 # Timeout para evitar bloqueio infinito se não houver mensagens
            )
            self.producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda x: json.dumps(x).encode("utf-8")
            )
            self.kafka_connected = True
            print(f"Conectado ao Kafka em {KAFKA_BROKER}. Consumindo de {TOPIC_DIAGNOSTICO}, produzindo para {TOPIC_ESTRATEGIA}.")
        except NoBrokersAvailable:
            print(f"ERRO FATAL: Nenhum broker Kafka disponível em {KAFKA_BROKER}. O serviço não pode iniciar.")
            raise
        except Exception as e:
            print(f"ERRO FATAL ao conectar ao Kafka: {e}")
            raise

        # Usa os caminhos de arquivo definidos globalmente (WHITELIST_FILE, API_ENDPOINTS_FILE)
        self.whitelisted_domains = load_yaml_config(WHITELIST_FILE, {}).get("news_sources", {}).get("allowed_domains", [])
        print(f"Whitelist de domínios carregada de {WHITELIST_FILE}: {self.whitelisted_domains}")
        
        self.api_endpoints_config = load_yaml_config(API_ENDPOINTS_FILE, {}).get("apis", {})
        print(f"Configuração de endpoints de API carregada de {API_ENDPOINTS_FILE}: {self.api_endpoints_config}")

        api_keys = {
            "news": os.getenv(NEWS_API_KEY_ENV),
            "finance": os.getenv(FINANCE_API_KEY_ENV),
            "climate": os.getenv(CLIMATE_API_KEY_ENV)
        }
        
        configured_api_endpoints = {
            "news": os.getenv(NEWS_API_ENDPOINT_ENV, self.api_endpoints_config.get("news", {}).get("primary_endpoint")),
            "finance": os.getenv(FINANCE_API_ENDPOINT_ENV, self.api_endpoints_config.get("finance", {}).get("primary_endpoint")),
            "climate": os.getenv(CLIMATE_API_ENDPOINT_ENV, self.api_endpoints_config.get("climate", {}).get("primary_endpoint"))
        }

        rate_limiters = {
            "news": APIRateLimiter(NEWS_API_RATE_LIMIT_CALLS, NEWS_API_RATE_LIMIT_INTERVAL),
            "finance": APIRateLimiter(FINANCE_API_RATE_LIMIT_CALLS, FINANCE_API_RATE_LIMIT_INTERVAL),
            "climate": APIRateLimiter(CLIMATE_API_RATE_LIMIT_CALLS, CLIMATE_API_RATE_LIMIT_INTERVAL)
        }

        self.web_miner = WebDataMiner(
            api_keys=api_keys,
            api_endpoints=configured_api_endpoints,
            rate_limiters=rate_limiters
        )
        
        if not global_redis_cache_instance.enabled:
            print("AVISO: Cache Redis não está funcionando. O desempenho pode ser afetado.")

        print("Serviço de Consciência Situacional configurado e pronto.")

    def _buscar_contexto_web(self, contexto_diagnostico):
        palavras_chave = contexto_diagnostico.get("palavras_chave", [])
        localizacao = contexto_diagnostico.get("localizacao", "global")
        print(f"Buscando contexto web para palavras-chave: {palavras_chave}, localização: {localizacao}")
        
        dados_web = {}
        try:
            dados_web["eventos_globais"] = self.web_miner.get_global_events(keywords=palavras_chave)
            dados_web["economia"] = self.web_miner.get_economic_indicators(indicador_key=localizacao)
            dados_web["clima"] = self.web_miner.get_climate_data(location=localizacao)
            
            if validar_dados_web(dados_web, whitelisted_domains_list=self.whitelisted_domains):
                print("Dados web validados com sucesso.")
                return dados_web
            else:
                print("AVISO: Falha na validação dos dados web. Retornando dados não validados ou parciais.")
                return dados_web
        except RateLimitExceeded as rle:
            print(f"Erro de Rate Limit ao buscar contexto web: {rle}")
            return {"erro": "Rate limit excedido", "detalhes": str(rle)}
        except requests.exceptions.RequestException as re:
            print(f"Erro de Request (HTTP) ao buscar contexto web: {re}")
            return {"erro": "Falha na comunicação com API externa", "detalhes": str(re)}
        except Exception as e:
            print(f"Erro inesperado ao buscar contexto web: {e}")
            return {"erro": "Erro interno ao processar dados web", "detalhes": str(e)}

    def processar_mensagem(self, mensagem_diagnostico):
        if not mensagem_diagnostico or not isinstance(mensagem_diagnostico, dict):
            print(f"Mensagem de diagnóstico inválida recebida: {mensagem_diagnostico}. Ignorando.")
            return

        print(f"Recebido diagnóstico: {json.dumps(mensagem_diagnostico, indent=2)}")
        
        contexto_para_web = {
            "palavras_chave": mensagem_diagnostico.get("entidades_detectadas", []) or mensagem_diagnostico.get("termos_relevantes", []),
            "localizacao": mensagem_diagnostico.get("local_afetado", "global")
        }

        dados_web_enriquecidos = self._buscar_contexto_web(contexto_para_web)
        
        mensagem_para_estrategia = mensagem_diagnostico.copy()
        if dados_web_enriquecidos and not dados_web_enriquecidos.get("erro"):
            mensagem_para_estrategia["contexto_web"] = dados_web_enriquecidos
            print("Diagnóstico enriquecido com contexto web.")
        elif dados_web_enriquecidos and dados_web_enriquecidos.get("erro"):
            mensagem_para_estrategia["contexto_web"] = {"status": "falha_coleta", "detalhes_erro": dados_web_enriquecidos}
            print(f"Falha ao coletar contexto web: {dados_web_enriquecidos.get('detalhes_erro')}")
        else:
            mensagem_para_estrategia["contexto_web"] = {"status": "nao_disponivel"}
            print("Não foi possível enriquecer diagnóstico com contexto web (dados nulos ou falha na validação crítica).")

        try:
            self.producer.send(TOPIC_ESTRATEGIA, value=mensagem_para_estrategia)
            self.producer.flush()
            print(f"Mensagem enviada para {TOPIC_ESTRATEGIA}")
        except Exception as e:
            print(f"ERRO ao enviar mensagem para Kafka ({TOPIC_ESTRATEGIA}): {e}")

    def run(self):
        if not self.kafka_connected:
            print("Serviço não pode rodar pois não está conectado ao Kafka.")
            return

        print(f"Escutando mensagens no tópico {TOPIC_DIAGNOSTICO}...")
        try:
            for mensagem in self.consumer:
                if mensagem and mensagem.value:
                    self.processar_mensagem(mensagem.value)
                else:
                    print("Mensagem vazia ou inválida recebida do Kafka.")
        except KeyboardInterrupt:
            print("Serviço interrompido pelo usuário.")
        except Exception as e:
            print(f"Erro crítico no loop de consumo do Kafka: {e}")
        finally:
            print("Fechando conexões Kafka...")
            if hasattr(self, 'consumer') and self.consumer:
                self.consumer.close()
            if hasattr(self, 'producer') and self.producer:
                self.producer.close()
            print("Serviço de Consciência Situacional encerrado.")

if __name__ == "__main__":
    print("Executando ConscienciaSituacionalService em modo de desenvolvimento local...")
    print(f"Verifique se o Kafka ({KAFKA_BROKER}) e o Redis ({os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}) estão acessíveis.")
    print("Certifique-se de que as variáveis de ambiente para chaves de API estão configuradas (ex: NEWS_API_KEY).")
    
    # Usar DEV_CONFIG_PATH para arquivos de configuração em modo local
    local_whitelist_file = os.path.join(DEV_CONFIG_PATH, "whitelist.yaml")
    local_api_endpoints_file = os.path.join(DEV_CONFIG_PATH, "api_endpoints.yaml") 
    print(f"Arquivos de configuração esperados em (desenvolvimento local): {os.path.abspath(DEV_CONFIG_PATH)}")

    os.environ.setdefault("NEWS_API_KEY", "dummy_news_key")
    os.environ.setdefault("FINANCE_API_KEY", "dummy_finance_key")
    os.environ.setdefault("CLIMATE_API_KEY", "dummy_climate_key")
    os.environ.setdefault("NEWS_API_ENDPOINT", "https://newsapi.org/v2/everything")
    os.environ.setdefault("FINANCE_API_ENDPOINT", "https://www.alphavantage.co/query")
    os.environ.setdefault("CLIMATE_API_ENDPOINT", "https://api.openweathermap.org/data/2.5/weather")

    # Garante que o diretório de configuração de desenvolvimento exista
    if not os.path.exists(DEV_CONFIG_PATH):
        try:
            os.makedirs(DEV_CONFIG_PATH)
            print(f"Diretório de configuração de desenvolvimento criado em: {os.path.abspath(DEV_CONFIG_PATH)}")
        except OSError as e:
            print(f"ERRO ao criar diretório de configuração de desenvolvimento {os.path.abspath(DEV_CONFIG_PATH)}: {e}. Verifique as permissões.")
            # Não prosseguir se não puder criar o diretório de config local
            exit(1) 

    # Cria arquivos de config dummy se não existirem no DEV_CONFIG_PATH
    if not os.path.exists(local_whitelist_file):
        with open(local_whitelist_file, "w") as wf:
            yaml.dump({"news_sources": {"allowed_domains": ["newsapi.org", "alphavantage.co", "openweathermap.org"]}}, wf)
        print(f"Arquivo de whitelist dummy criado em {local_whitelist_file}")
    
    if not os.path.exists(local_api_endpoints_file):
        with open(local_api_endpoints_file, "w") as aef:
            yaml.dump({"apis": {
                "news": {"primary_endpoint": os.getenv("NEWS_API_ENDPOINT")},
                "finance": {"primary_endpoint": os.getenv("FINANCE_API_ENDPOINT")},
                "climate": {"primary_endpoint": os.getenv("CLIMATE_API_ENDPOINT")}
            }}, aef)
        print(f"Arquivo de endpoints dummy criado em {local_api_endpoints_file}")

    # Sobrescreve WHITELIST_FILE e API_ENDPOINTS_FILE para usar os caminhos locais
    # Esta é uma forma de garantir que a classe ConscienciaSituacionalService use os arquivos corretos
    # quando instanciada a partir deste bloco __main__.
    # No entanto, a lógica de CONFIG_PATH_TO_USE já deve lidar com isso se __main__ for detectado corretamente.
    # Para garantir, podemos redefinir aqui explicitamente para o teste local.
    # Ou melhor, a classe ConscienciaSituacionalService já usará CONFIG_PATH_TO_USE que foi definido como DEV_CONFIG_PATH.

    try:
        service = ConscienciaSituacionalService() # Ela usará CONFIG_PATH_TO_USE que é DEV_CONFIG_PATH aqui
        service.run()
    except NoBrokersAvailable:
        print("Falha ao iniciar o serviço: Kafka não disponível. Verifique a configuração e o status do Kafka.")
    except Exception as e:
        print(f"Erro ao executar o serviço em modo local: {e}")

