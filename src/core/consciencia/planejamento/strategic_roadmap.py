from datetime import datetime, timedelta

class StrategicRoadmapGenerator:
    def __init__(self):
        """Inicializa o Gerador de Roadmap Estratégico."""
        print("[StrategicRoadmapGenerator] Gerador de Roadmap Estratégico inicializado.")

    def generate_roadmap(self, project_name: str, start_date: datetime, initiatives: list[dict]) -> dict:
        """Gera um roadmap estratégico com base nas iniciativas fornecidas.

        Args:
            project_name (str): Nome do projeto ou do roadmap.
            start_date (datetime): Data de início do roadmap.
            initiatives (list[dict]): Lista de iniciativas, onde cada iniciativa é um dicionário com:
                - "name" (str): Nome da iniciativa.
                - "duration_weeks" (int): Duração estimada em semanas.
                - "priority" (int): Prioridade (ex: 1-Alta, 2-Média, 3-Baixa).
                - "dependencies" (list[str], optional): Lista de nomes de iniciativas das quais esta depende.
                - "category" (str, optional): Categoria da iniciativa (ex: "Desenvolvimento", "Pesquisa").

        Returns:
            dict: Um dicionário representando o roadmap gerado.
        """
        print(f"[StrategicRoadmapGenerator] Gerando roadmap para: {project_name}")
        print(f"  Data de Início: {start_date.strftime("%Y-%m-%d")}")
        print(f"  Número de Iniciativas: {len(initiatives)}")

        # Ordenar iniciativas por prioridade (e talvez por dependências depois)
        # Esta é uma lógica de agendamento simples. Algoritmos mais complexos (ex: PERT/CPM) podem ser usados.
        # Por simplicidade, vamos agendar sequencialmente baseado na ordem da lista após priorização.
        # Uma melhoria seria construir um grafo de dependências.
        
        # Mapear nomes de iniciativas para seus índices para fácil lookup de dependências
        initiative_map = {init["name"]: i for i, init in enumerate(initiatives)}
        scheduled_initiatives = []
        current_date = start_date
        completed_initiatives_names = set()

        # Ordenar por prioridade primeiro
        sorted_initiatives = sorted(initiatives, key=lambda x: x.get("priority", 3))
        
        # Simples agendamento sequencial com verificação de dependência básica
        # Este loop pode precisar ser mais sofisticado para grafos de dependência complexos
        # e para otimizar o paralelismo.
        processed_indices = set()
        iterations = 0
        max_iterations = len(sorted_initiatives) * 2 # Para evitar loop infinito em caso de dependências circulares não tratadas

        while len(processed_indices) < len(sorted_initiatives) and iterations < max_iterations:
            iterations += 1
            made_progress_this_iteration = False
            temp_current_date_for_iteration = current_date # Data base para esta iteração de agendamento
            
            for i, init_data in enumerate(sorted_initiatives):
                if i in processed_indices:
                    continue

                # Verificar dependências
                dependencies_met = True
                if init_data.get("dependencies"):
                    for dep_name in init_data["dependencies"]:
                        if dep_name not in completed_initiatives_names:
                            dependencies_met = False
                            break
                
                if dependencies_met:
                    duration = timedelta(weeks=init_data.get("duration_weeks", 1))
                    end_date = temp_current_date_for_iteration + duration
                    
                    scheduled_initiatives.append({
                        "name": init_data["name"],
                        "category": init_data.get("category", "Geral"),
                        "priority": init_data.get("priority", 3),
                        "start_date": temp_current_date_for_iteration.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "duration_weeks": init_data.get("duration_weeks", 1),
                        "dependencies": init_data.get("dependencies", [])
                    })
                    
                    # Atualiza a data corrente para a próxima iniciativa *nesta* iteração
                    temp_current_date_for_iteration = end_date 
                    completed_initiatives_names.add(init_data["name"])
                    processed_indices.add(i)
                    made_progress_this_iteration = True
            
            # Se progresso foi feito, a data global avança para o final da última tarefa agendada na iteração
            if made_progress_this_iteration:
                current_date = temp_current_date_for_iteration
            elif len(processed_indices) < len(sorted_initiatives):
                # Se não houve progresso e ainda há tarefas, pode haver dependência circular ou problema
                print("[StrategicRoadmapGenerator] Alerta: Nenhuma iniciativa pôde ser agendada na iteração. Verifique dependências.")
                # Para evitar loop infinito, podemos quebrar ou marcar as restantes como não agendáveis.
                # Por ora, vamos apenas registrar e o loop externo vai parar pelas max_iterations.
                pass 

        if len(processed_indices) < len(sorted_initiatives):
            print("[StrategicRoadmapGenerator] Alerta: Algumas iniciativas não puderam ser agendadas devido a dependências não resolvidas ou complexidade.")
            # Adicionar as não agendadas ao roadmap com um status especial
            for i, init_data in enumerate(sorted_initiatives):
                if i not in processed_indices:
                    scheduled_initiatives.append({
                        "name": init_data["name"],
                        "status": "Não Agendada - Verificar Dependências",
                        "priority": init_data.get("priority", 3),
                        "dependencies": init_data.get("dependencies", [])
                    })

        roadmap_output = {
            "project_name": project_name,
            "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "roadmap_start_date": start_date.strftime("%Y-%m-%d"),
            "initiatives": scheduled_initiatives
        }
        print(f"[StrategicRoadmapGenerator] Roadmap gerado com {len(scheduled_initiatives)} entradas.")
        return roadmap_output

# Exemplo de uso
if __name__ == "__main__":
    generator = StrategicRoadmapGenerator()
    
    today = datetime.today()

    sample_initiatives = [
        {
            "name": "Pesquisa de Mercado para Produto X", 
            "duration_weeks": 4, 
            "priority": 1, 
            "category": "Pesquisa"
        },
        {
            "name": "Desenvolvimento do Protótipo MVP", 
            "duration_weeks": 8, 
            "priority": 1, 
            "dependencies": ["Pesquisa de Mercado para Produto X"], 
            "category": "Desenvolvimento"
        },
        {
            "name": "Planejamento de Marketing", 
            "duration_weeks": 3, 
            "priority": 2, 
            "dependencies": ["Pesquisa de Mercado para Produto X"], 
            "category": "Marketing"
        },
        {
            "name": "Testes Alfa com Usuários", 
            "duration_weeks": 4, 
            "priority": 2, 
            "dependencies": ["Desenvolvimento do Protótipo MVP"], 
            "category": "Testes"
        },
        {
            "name": "Lançamento Beta", 
            "duration_weeks": 2, 
            "priority": 1, 
            "dependencies": ["Testes Alfa com Usuários", "Planejamento de Marketing"], 
            "category": "Lançamento"
        },
        {
            "name": "Treinamento da Equipe de Vendas",
            "duration_weeks": 2,
            "priority": 3,
            "category": "Operações"
            # Sem dependências explícitas, pode rodar em paralelo ou ser agendado por prioridade
        }
    ]

    print("\n--- Gerando Roadmap para Lançamento do Produto X ---")
    roadmap = generator.generate_roadmap(
        project_name="Lançamento do Produto X",
        start_date=today,
        initiatives=sample_initiatives
    )

    print("\nRoadmap Gerado:")
    print(f"Projeto: {roadmap["project_name"]}")
    print(f"Gerado em: {roadmap["generated_on"]}")
    print(f"Início do Roadmap: {roadmap["roadmap_start_date"]}")
    print("Iniciativas Agendadas:")
    for init in roadmap["initiatives"]:
        if init.get("status") == "Não Agendada - Verificar Dependências":
            print(f"  - {init["name"]} (Prioridade: {init["priority"]}) - STATUS: {init["status"]}")
        else:
            print(f"  - {init["name"]} (Prioridade: {init["priority"]})")
            print(f"    Categoria: {init["category"]}")
            print(f"    Duração: {init["duration_weeks"]} semanas")
            print(f"    Início: {init["start_date"]}, Fim: {init["end_date"]}")
            if init["dependencies"]:
                print(f"    Depende de: {', '.join(init["dependencies"])}")
        print("---")

