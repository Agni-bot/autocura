import requests
import json

class CrowdfundingIntegrator:
    def __init__(self, api_key: str = None, platform_base_url: str = "https://api.kickstarter.com"):
        """Inicializa o integrador de crowdfunding.

        Args:
            api_key (str, optional): Chave de API para a plataforma de crowdfunding, se necessária.
                                     Muitas plataformas podem não exigir para dados públicos.
            platform_base_url (str): URL base da API da plataforma (ex: Kickstarter, Indiegogo).
        """
        self.api_key = api_key
        self.platform_base_url = platform_base_url
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "AutocuraCrowdfundingIntegrator/1.0"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}" # Exemplo, pode variar
        print(f"[CrowdfundingIntegrator] Integrador de Crowdfunding inicializado para: {self.platform_base_url}")

    def search_projects(self, query: str, category: str = None, sort: str = "magic", limit: int = 5) -> list[dict]:
        """Busca por projetos em uma plataforma de crowdfunding.

        Args:
            query (str): Termo de busca para os projetos.
            category (str, optional): Categoria para filtrar os projetos.
            sort (str, optional): Critério de ordenação (ex: 'magic', 'popularity', 'end_date').
            limit (int): Número máximo de projetos a retornar.

        Returns:
            Lista de dicionários, cada um representando um projeto encontrado, ou lista vazia.
        """
        # Este é um exemplo genérico. A API real do Kickstarter ou Indiegogo pode ser diferente.
        # Kickstarter V1 API é mais complexa e usa GraphQL.
        # Vamos simular uma API RESTful mais simples para fins de demonstração.
        endpoint = f"{self.platform_base_url}/v1/projects/search.json"
        params = {
            "term": query,
            "sort": sort,
            "per_page": limit
        }
        if category:
            params["category_id"] = category # Supondo que a API aceita ID de categoria
        if self.api_key:
             params["client_id"] = self.api_key # Algumas APIs usam client_id na query

        print(f"[CrowdfundingIntegrator] Buscando projetos com query: 	{query}	, params: {params}")
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            projects = data.get("projects", [])
            print(f"[CrowdfundingIntegrator] {len(projects)} projetos encontrados para 	{query}	.")
            return projects
        except requests.RequestException as e:
            print(f"[CrowdfundingIntegrator] Erro na requisição para buscar projetos: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"[CrowdfundingIntegrator] Erro ao decodificar JSON da resposta: {e}")
            return []
        except Exception as e:
            print(f"[CrowdfundingIntegrator] Erro inesperado ao buscar projetos: {e}")
            return []

    def get_project_details(self, project_id: str) -> dict | None:
        """Obtém detalhes de um projeto específico pelo seu ID.

        Args:
            project_id (str): ID do projeto na plataforma.

        Returns:
            Dicionário com os detalhes do projeto, ou None em caso de falha.
        """
        # Simulação, pois a estrutura exata da API varia.
        endpoint = f"{self.platform_base_url}/v1/projects/{project_id}.json"
        params = {}
        if self.api_key:
             params["client_id"] = self.api_key

        print(f"[CrowdfundingIntegrator] Buscando detalhes do projeto ID: {project_id}")
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            project_data = response.json()
            print(f"[CrowdfundingIntegrator] Detalhes do projeto 	{project_id}	 recuperados.")
            return project_data.get("project", project_data) # Algumas APIs aninham sob 'project'
        except requests.RequestException as e:
            print(f"[CrowdfundingIntegrator] Erro na requisição para obter detalhes do projeto {project_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"[CrowdfundingIntegrator] Erro ao decodificar JSON dos detalhes do projeto {project_id}: {e}")
            return None
        except Exception as e:
            print(f"[CrowdfundingIntegrator] Erro inesperado ao obter detalhes do projeto {project_id}: {e}")
            return None

# Exemplo de uso (simulado, pois depende de uma API real e possivelmente de chaves)
if __name__ == '__main__':
    # Para Kickstarter, a API pública é limitada. Este é um exemplo conceitual.
    # Você pode precisar de web scraping ou usar APIs não oficiais se uma oficial robusta não estiver disponível.
    integrator = CrowdfundingIntegrator(platform_base_url="https://api.examplekickstarter.com") # URL Fictícia

    print("\n--- Buscando Projetos de IA Verde ---")
    # Simulação de resposta da API para busca
    def mock_search_projects(self, query, category=None, sort="magic", limit=5):
        print(f"[Mock] Buscando projetos: {query}, Categoria: {category}, Limite: {limit}")
        if "IA Verde" in query:
            return [
                {"id": "proj_123", "name": "Sistema Inteligente de Irrigação Solar", "goal": 50000, "pledged": 25000, "backers_count": 300, "state": "live"},
                {"id": "proj_456", "name": "Monitoramento Ambiental com Drones IA", "goal": 75000, "pledged": 80000, "backers_count": 500, "state": "successful"}
            ]
        return []
    CrowdfundingIntegrator.search_projects = mock_search_projects # Monkey patch para simulação
    
    projects = integrator.search_projects(query="IA Verde", category="tecnologia")
    if projects:
        for proj in projects:
            print(f"  - ID: {proj.get(	'id	')}, Nome: {proj.get(	'name	')}, Arrecadado: ${proj.get(	'pledged	', 0)}, Meta: ${proj.get(	'goal	', 0)}")
        
        # Tentar obter detalhes do primeiro projeto encontrado (simulado)
        first_project_id = projects[0].get("id")
        if first_project_id:
            print(f"\n--- Buscando Detalhes do Projeto {first_project_id} ---")
            # Simulação de resposta da API para detalhes
            def mock_get_project_details(self, project_id):
                print(f"[Mock] Buscando detalhes do projeto: {project_id}")
                if project_id == "proj_123":
                    return {"id": "proj_123", "name": "Sistema Inteligente de Irrigação Solar", "blurb": "Usa IA para otimizar o uso de água.", "currency": "USD", "goal": 50000, "pledged": 25000, "state": "live", "country": "US", "deadline": 1700000000, "creator": {"name": "EcoTech Innovations"}}
                return None
            CrowdfundingIntegrator.get_project_details = mock_get_project_details # Monkey patch

            details = integrator.get_project_details(first_project_id)
            if details:
                print(f"  Detalhes de 	'{details.get('name')}	':")
                print(f"    Descrição Curta: {details.get('blurb')}")
                print(f"    Criador: {details.get('creator', {}).get('name')}")
                print(f"    Status: {details.get('state')}")
    else:
        print("Nenhum projeto encontrado para 'IA Verde'.")
