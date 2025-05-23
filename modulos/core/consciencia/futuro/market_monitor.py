import requests
from bs4 import BeautifulSoup
import time

class MarketMonitor:
    def __init__(self):
        self.gartner_url = "https://www.gartner.com/en/research" # Exemplo, URL real pode variar
        self.mckinsey_url = "https://www.mckinsey.com/insights" # Exemplo, URL real pode variar
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print("[MarketMonitor] Monitor de mercado inicializado.")

    def _fetch_report_titles(self, url: str, site_name: str) -> list[str]:
        """Busca títulos de relatórios de uma URL específica."""
        titles = []
        try:
            print(f"[MarketMonitor] Buscando relatórios em: {url} ({site_name})")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status() # Levanta exceção para códigos de erro HTTP
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Esta parte é altamente dependente da estrutura HTML do site alvo
            # O exemplo abaixo é genérico e precisaria ser adaptado
            if site_name == "Gartner":
                # Exemplo: Supondo que os títulos estão em tags <h2> com classe 'report-title'
                for header in soup.find_all('h2', class_='report-title', limit=5):
                    titles.append(header.get_text(strip=True))
            elif site_name == "McKinsey":
                # Exemplo: Supondo que os títulos estão em tags <h3> dentro de artigos
                for article in soup.find_all('article', limit=5):
                    title_tag = article.find('h3')
                    if title_tag:
                        titles.append(title_tag.get_text(strip=True))
            else:
                # Fallback genérico (menos preciso)
                 for header in soup.find_all(['h1', 'h2', 'h3'], limit=5):
                    titles.append(header.get_text(strip=True))
            
            print(f"[MarketMonitor] Títulos encontrados em {site_name}: {titles}")
        except requests.RequestException as e:
            print(f"[MarketMonitor] Erro ao buscar relatórios de {site_name} ({url}): {e}")
        except Exception as e:
            print(f"[MarketMonitor] Erro inesperado ao processar {site_name} ({url}): {e}")
        return titles

    def get_latest_market_reports(self) -> dict:
        """Coleta os últimos relatórios de mercado de fontes como Gartner e McKinsey."""
        print("[MarketMonitor] Coletando últimos relatórios de mercado...")
        reports = {
            'gartner': [],
            'mckinsey': []
        }
        
        reports['gartner'] = self._fetch_report_titles(self.gartner_url, "Gartner")
        time.sleep(1) # Pequena pausa para evitar sobrecarregar os servidores
        reports['mckinsey'] = self._fetch_report_titles(self.mckinsey_url, "McKinsey")
        
        print(f"[MarketMonitor] Relatórios coletados: {reports}")
        return reports

# Exemplo de uso (pode ser removido ou comentado em produção)
if __name__ == '__main__':
    monitor = MarketMonitor()
    latest_reports = monitor.get_latest_market_reports()
    
    if latest_reports['gartner']:
        print("\n--- Relatórios Recentes da Gartner ---")
        for i, title in enumerate(latest_reports['gartner']):
            print(f"{i+1}. {title}")
    else:
        print("\nNenhum relatório da Gartner encontrado ou erro na busca.")
        
    if latest_reports['mckinsey']:
        print("\n--- Relatórios Recentes da McKinsey ---")
        for i, title in enumerate(latest_reports['mckinsey']):
            print(f"{i+1}. {title}")
    else:
        print("\nNenhum relatório da McKinsey encontrado ou erro na busca.")
