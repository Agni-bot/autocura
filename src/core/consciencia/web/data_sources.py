# src/conscienciaSituacional/web/data_sources.py
import os
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
# Importar o cache do shared_utils
from ..shared_utils.cache import cache

class WebDataMiner:
    def __init__(self, api_keys, api_endpoints, rate_limiters=None):
        """
        api_keys: Dicionário com chaves para NEWS_API_KEY, FINANCE_API_KEY, CLIMATE_API_KEY.
        api_endpoints: Dicionário com chaves para news, finance, climate.
        rate_limiters: Dicionário opcional com instâncias de APIRateLimiter para cada API.
        """
        self.api_keys = api_keys
        self.api_endpoints = api_endpoints
        self.rate_limiters = rate_limiters if rate_limiters else {}
        print(f"WebDataMiner inicializado com endpoints: {self.api_endpoints}")

    def _call_with_rate_limit(self, api_name, func, *args, **kwargs):
        limiter = self.rate_limiters.get(api_name)
        if limiter:
            print(f"Usando rate limiter para API: {api_name}")
            # A função call_api do limiter deve chamar a `func` com seus args e kwargs
            return limiter.call_api(func, *args, **kwargs) # Ou call_api_blocking
        else:
            print(f"Nenhum rate limiter configurado para API: {api_name}. Chamando diretamente.")
            return func(*args, **kwargs)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @cache(key_prefix="web_miner_global_events", ttl_seconds=600) # TTL de 10 minutos
    def get_global_events(self, keywords):
        if not keywords or not isinstance(keywords, list):
            print("WebDataMiner: Keywords inválidos ou não fornecidos para get_global_events.")
            return []
        
        news_endpoint = self.api_endpoints.get("news")
        news_api_key = self.api_keys.get("news")
        
        if not news_endpoint or not news_api_key:
            print(f"WebDataMiner: Endpoint de Notícias ({news_endpoint}) ou Chave de API de Notícias não configurada.")
            return []

        print(f"WebDataMiner: Buscando eventos globais para keywords: {keywords} no endpoint: {news_endpoint}")
        
        def api_call():
            response = requests.get(
                news_endpoint,
                params={
                    "q": " OR ".join(keywords),
                    "lang": "pt",
                    "sortBy": "relevance",
                    "pageSize": 5,
                    "apiKey": news_api_key
                },
                timeout=5 
            )
            response.raise_for_status()
            return self._parse_news(response.json())
        
        return self._call_with_rate_limit("news", api_call)

    def _parse_news(self, raw_data):
        parsed_articles = []
        articles = raw_data.get("articles", [])
        for item in articles[:3]:
            try:
                parsed_articles.append({
                    "titulo": item.get("title"),
                    "fonte": item.get("source", {}).get("name"),
                    "data": item.get("publishedAt"),
                    "relevancia": item.get("relevanceScore", 0.0) 
                })
            except Exception as e:
                print(f"WebDataMiner: Erro ao fazer parse de um artigo de notícia: {e} - Item: {item}")
        return parsed_articles

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @cache(key_prefix="web_miner_economic_indicators", ttl_seconds=43200) # TTL de 12 horas
    def get_economic_indicators(self, indicador_key="default"):
        finance_endpoint = self.api_endpoints.get("finance")
        finance_api_key = self.api_keys.get("finance")

        if not finance_endpoint or not finance_api_key:
            print(f"WebDataMiner: Endpoint Financeiro ({finance_endpoint}) ou Chave de API Financeira não configurada.")
            return {}
        
        # Correção da linha 88: String f-string corrigida para uma única linha.
        print(f"WebDataMiner: Buscando indicadores econômicos (key: {indicador_key}) no endpoint: {finance_endpoint}")
        
        def api_call():
            response = requests.get(
                finance_endpoint,
                params={"apiKey": finance_api_key, "indicator": indicador_key},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            # Adapte o parsing conforme a API real (FMI, Banco Mundial)
            return {
                "preco_painel_solar": {"atual": data.get("solar_panel_price", {}).get("current", 0.38), "tendencia": data.get("solar_panel_price", {}).get("trend", "queda 2% a.a.")},
                "regulacao_nuclear": {"status": data.get("nuclear_regulation", {}).get("status", "em revisão"), "paises": data.get("nuclear_regulation", {}).get("countries", ["BR", "US", "DE"])}
            }
        return self._call_with_rate_limit("finance", api_call)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @cache(key_prefix="web_miner_climate_data", ttl_seconds=3600) # TTL de 1 hora
    def get_climate_data(self, location="global"):
        climate_endpoint = self.api_endpoints.get("climate")
        climate_api_key = self.api_keys.get("climate")

        if not climate_endpoint or not climate_api_key:
            print(f"WebDataMiner: Endpoint Climático ({climate_endpoint}) ou Chave de API Climática não configurada.")
            return {}

        # Correção similar para consistência, se houver quebra de linha no print.
        print(f"WebDataMiner: Buscando dados climáticos para (location: {location}) no endpoint: {climate_endpoint}")
        
        def api_call():
            response = requests.get(
                climate_endpoint,
                params={"key": climate_api_key, "q": location},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            # Adapte o parsing conforme a API real (OpenWeatherMap, NOAA)
            return {
                "temperatura_media_global": data.get("global_avg_temp", 15.5),
                "alerta_evento_extremo": data.get("extreme_event_alert", None)
            }
        return self._call_with_rate_limit("climate", api_call)

