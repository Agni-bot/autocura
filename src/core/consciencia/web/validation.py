# src/conscienciaSituacional/web/validation.py
import re
from urllib.parse import urlparse

# Carregar whitelist de um arquivo de configuração
# Em um cenário real, isso seria carregado de forma mais robusta, ex: ao iniciar o serviço.
# WHITELISTED_DOMAINS = ["reuters.com", "bloomberg.com", "gov.uk", "data.worldbank.org", "api.example-events.com", "api.finance-data.com", "api.climate-service.com"]
# A whitelist será carregada do config/whitelist.yaml posteriormente

def _check_fontes_whitelist(sources_data, whitelisted_domains):
    """Verifica se as fontes dos dados estão em uma whitelist de domínios."""
    if not isinstance(sources_data, list):
        print("Validation: sources_data não é uma lista.")
        return False # Ou True se a ausência de fontes for aceitável

    for source_entry in sources_data:
        # A estrutura de source_entry pode variar. Ex: URL direta ou um objeto com um campo URL/fonte.
        # Adaptar conforme a estrutura real dos dados de fontes.
        url_str = None
        if isinstance(source_entry, str):
            url_str = source_entry
        elif isinstance(source_entry, dict) and "url" in source_entry:
            url_str = source_entry["url"]
        elif isinstance(source_entry, dict) and "fonte" in source_entry: # Como no _parse_news
            # Se a "fonte" for apenas um nome, não uma URL, esta checagem pode não ser aplicável diretamente aqui.
            # Precisaria de uma URL associada ou um mapeamento de nomes de fontes para domínios.
            # Por ora, vamos assumir que se "fonte" existe, é um nome e confiamos nele se a API de origem é confiável.
            # Ou, a whitelist poderia incluir nomes de fontes conhecidas.
            # print(f"Validation: Fonte 
            pass # Não há URL para verificar diretamente aqui para o formato de _parse_news

        if url_str:
            try:
                domain = urlparse(url_str).netloc
                if domain not in whitelisted_domains:
                    print(f"Validation: Domínio {domain} não está na whitelist.")
                    return False
            except Exception as e:
                print(f"Validation: Erro ao parsear URL da fonte {url_str}: {e}")
                return False
    return True

def _check_anomalias_temporais(data):
    """Verifica anomalias temporais básicas, como datas futuras para eventos passados."""
    # Exemplo: verificar se datas em eventos_globais não são do futuro.
    # Esta é uma lógica placeholder e precisaria ser adaptada aos dados reais.
    if "eventos_globais" in data and isinstance(data["eventos_globais"], list):
        for evento in data["eventos_globais"]:
            if "data" in evento:
                # Lógica para comparar data do evento com data atual
                # from datetime import datetime, timezone
                # try:
                #     event_date = datetime.fromisoformat(evento["data"].replace("Z", "+00:00"))
                #     if event_date > datetime.now(timezone.utc):
                #         print(f"Validation: Evento com data futura encontrado: {evento}")
                #         return False
                # except ValueError:
                #     print(f"Validation: Formato de data inválido para o evento: {evento}")
                #     return False
                pass # Implementação real da checagem de data
    return True

def _crosscheck_fontes(data):
    """Realiza um cruzamento básico entre fontes, se aplicável."""
    # Placeholder: Lógica para comparar dados de diferentes fontes se houver sobreposição.
    # Ex: Se duas fontes de notícias reportam o mesmo evento, há consistência?
    return True

def validar_dados_web(raw_data: dict, whitelisted_domains_list: list = None) -> bool:
    """Valida consistência básica dos dados externos agregados."""
    if not raw_data: # Se não há dados, considera válido (ou inválido, dependendo da política)
        print("Validation: Nenhum dado web para validar.")
        return True 

    # Carregar whitelist se não fornecida (idealmente, isso é feito uma vez na inicialização do serviço)
    if whitelisted_domains_list is None:
        # Esta é uma forma simplificada. Em produção, carregar de um arquivo de config.
        # whitelisted_domains_list = ["reuters.com", "bloomberg.com", "news.google.com", "api.example-events.com"]
        # print("Validation: Usando whitelist de domínios padrão.")
        # A whitelist deve ser carregada a partir do config/whitelist.yaml
        # Por enquanto, vamos assumir que ela é passada ou o _check_fontes_whitelist lida com isso.
        pass 

    # A estrutura de raw_data["sources"] não está clara no exemplo fornecido.
    # Vamos assumir que raw_data pode ter uma chave "sources" ou que cada sub-dado (eventos, economia, clima)
    # tem sua própria estrutura de fontes.
    # Para o exemplo de _parse_news, a "fonte" é um nome, não uma URL.
    # A validação de whitelist de domínios precisaria ser adaptada.
    # Por ora, focaremos nas outras checagens ou assumiremos que a API de origem é confiável.

    checks = [
        _check_anomalias_temporais(raw_data), # Verifica datas em eventos
        # _check_fontes_whitelist(raw_data.get("sources", []), whitelisted_domains_list), # Desabilitado temporariamente até a estrutura de "sources" ser clara
        _crosscheck_fontes(raw_data) # Placeholder para cruzamento de dados
    ]
    
    print(f"Validation: Resultados das checagens: {checks}")
    return all(checks)

# Exemplo de como carregar a whitelist (a ser usado no core.py ou similar)
# import yaml
# def load_whitelist(config_path="config/whitelist.yaml"):
#     try:
#         with open(config_path, "r") as f:
#             config = yaml.safe_load(f)
#         return config.get("news_sources", {}).get("allowed_domains", [])
#     except FileNotFoundError:
#         print(f"Arquivo de whitelist {config_path} não encontrado.")
#         return []
#     except Exception as e:
#         print(f"Erro ao carregar whitelist: {e}")
#         return []

