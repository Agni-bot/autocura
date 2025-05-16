# test_strategic_roadmap.py
import pytest
from datetime import datetime, timedelta
# Ajuste para importação relativa
import sys
import os
# Adiciona o diretório src ao sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..")) # Sobe dois níveis de tests/ para src/
sys.path.insert(0, project_root)

from conscienciaSituacional.planejamento.strategic_roadmap import StrategicRoadmapGenerator

@pytest.fixture
def roadmap_generator():
    return StrategicRoadmapGenerator(default_time_unit="weeks")

@pytest.fixture
def sample_goals():
    return [
        "Goal A: Achieve market leadership.",
        "Goal B: Enhance customer satisfaction."
    ]

@pytest.fixture
def sample_initiatives():
    return [
        {
            "name": "Phase 1: Research & Development",
            "description": "Initial R&D for product X.",
            "priority": 1,
            "duration": 4, # weeks
            "dependencies": [],
            "responsible_team": "R&D Team",
            "status": "Planejada",
            "expected_outcomes": ["Feasibility report", "Initial prototype"]
        },
        {
            "name": "Phase 2: Product Development",
            "description": "Full development of product X.",
            "priority": 1,
            "duration": 8, # weeks
            "dependencies": ["Phase 1: Research & Development"],
            "responsible_team": "Engineering Team",
            "status": "Planejada",
            "expected_outcomes": ["Beta version of product X"]
        },
        {
            "name": "Phase 3: Marketing Launch Prep",
            "description": "Prepare marketing materials and strategy.",
            "priority": 2,
            "duration": 6, # weeks
            "dependencies": [], # Can run in parallel with R&D initially
            "responsible_team": "Marketing Team",
            "status": "Planejada",
            "expected_outcomes": ["Marketing plan finalized", "Ad creatives ready"]
        },
        {
            "name": "Phase 4: Product Launch & Marketing",
            "description": "Official launch of product X and marketing campaign execution.",
            "priority": 1,
            "duration": 10, # weeks
            "dependencies": ["Phase 2: Product Development", "Phase 3: Marketing Launch Prep"],
            "responsible_team": "Sales & Marketing",
            "status": "Planejada",
            "expected_outcomes": ["Product launched", "Initial sales targets met"]
        }
    ]

def test_create_roadmap_basic(roadmap_generator, sample_goals, sample_initiatives):
    roadmap = roadmap_generator.create_roadmap(
        project_name="Project Alpha",
        goals=sample_goals,
        initiatives=sample_initiatives,
        start_date_str="2025-07-01"
    )
    assert roadmap is not None
    assert roadmap["project_name"] == "Project Alpha"
    assert roadmap["overall_goals"] == sample_goals
    assert roadmap["start_date"] == "2025-07-01"
    assert len(roadmap["timeline"]) == len(sample_initiatives)
    assert len(roadmap["initiatives_details"]) == len(sample_initiatives)
    # As iniciativas são ordenadas por prioridade, depois pela ordem original se prioridades iguais.
    # Phase 1 e Phase 2 têm prioridade 1. Phase 3 tem prioridade 2.
    # Phase 4 tem prioridade 1.
    # A ordem esperada em initiatives_details seria Phase 1, Phase 2, Phase 4, Phase 3
    assert roadmap["initiatives_details"][0]["name"] == "Phase 1: Research & Development"
    assert roadmap["initiatives_details"][1]["name"] == "Phase 2: Product Development"
    assert roadmap["initiatives_details"][2]["name"] == "Phase 4: Product Launch & Marketing"
    assert roadmap["initiatives_details"][3]["name"] == "Phase 3: Marketing Launch Prep"

def test_create_roadmap_timeline_logic(roadmap_generator, sample_goals, sample_initiatives):
    start_date_str = "2025-07-01"
    roadmap = roadmap_generator.create_roadmap(
        project_name="Project Timeline Test",
        goals=sample_goals,
        initiatives=sample_initiatives,
        start_date_str=start_date_str
    )
    assert roadmap is not None
    timeline = roadmap["timeline"]

    # Phase 1: R&D (4 semanas) - Sem dependências
    # Início: 2025-07-01
    # Fim: 2025-07-01 + 4 semanas - 1 dia = 2025-07-28 (timedelta(weeks=4) adiciona 28 dias, então o fim é 2025-07-28)
    phase1 = next(item for item in timeline if item["initiative_name"] == "Phase 1: Research & Development")
    assert phase1["start_date"] == "2025-07-01"
    assert phase1["end_date"] == "2025-07-28"

    # Phase 3: Marketing Prep (6 semanas) - Sem dependências, mas agendada após a última iniciativa sem dependência (Phase 1)
    # Início: 2025-07-29 (dia seguinte ao fim da Phase 1)
    # Fim: 2025-07-29 + 6 semanas - 1 dia = 2025-09-08
    phase3 = next(item for item in timeline if item["initiative_name"] == "Phase 3: Marketing Launch Prep")
    assert phase3["start_date"] == "2025-07-29"
    assert phase3["end_date"] == "2025-09-08"

    # Phase 2: Product Dev (8 semanas) - Depende da Phase 1
    # Início: 2025-07-29 (dia seguinte ao fim da Phase 1)
    # Fim: 2025-07-29 + 8 semanas - 1 dia = 2025-09-22
    phase2 = next(item for item in timeline if item["initiative_name"] == "Phase 2: Product Development")
    assert phase2["start_date"] == "2025-07-29"
    assert phase2["end_date"] == "2025-09-22"

    # Phase 4: Launch (10 semanas) - Depende da Phase 2 e Phase 3
    # Fim da Phase 2: 2025-09-22
    # Fim da Phase 3: 2025-09-08
    # Início da Phase 4: max(2025-09-22, 2025-09-08) + 1 dia = 2025-09-23
    # Fim: 2025-09-23 + 10 semanas - 1 dia = 2025-12-01
    phase4 = next(item for item in timeline if item["initiative_name"] == "Phase 4: Product Launch & Marketing")
    assert phase4["start_date"] == "2025-09-23"
    assert phase4["end_date"] == "2025-12-01"


def test_create_roadmap_invalid_inputs(roadmap_generator, sample_goals, sample_initiatives):
    assert roadmap_generator.create_roadmap(project_name=None, goals=sample_goals, initiatives=sample_initiatives) is None
    assert roadmap_generator.create_roadmap(project_name="Test", goals=[], initiatives=sample_initiatives) is None
    assert roadmap_generator.create_roadmap(project_name="Test", goals=sample_goals, initiatives=[]) is None
    assert roadmap_generator.create_roadmap(project_name="Test", goals=sample_goals, initiatives=sample_initiatives, start_date_str="invalid-date") is None

def test_create_roadmap_different_time_units(sample_goals, sample_initiatives):
    generator_months = StrategicRoadmapGenerator(default_time_unit="months")
    # Ajustar duração para meses (ex: 4 semanas ~ 1 mês, 8 semanas ~ 2 meses)
    initiatives_months_adj = []
    for init in sample_initiatives:
        new_init = dict(init)
        if new_init["duration"] == 4: new_init["duration"] = 1
        elif new_init["duration"] == 8: new_init["duration"] = 2
        elif new_init["duration"] == 6: new_init["duration"] = 1 # Aprox 1.5, arredondar para 1 ou 2
        elif new_init["duration"] == 10: new_init["duration"] = 2 # Aprox 2.5
        initiatives_months_adj.append(new_init)

    roadmap_months = generator_months.create_roadmap(
        project_name="Project Months", 
        goals=sample_goals, 
        initiatives=initiatives_months_adj, 
        start_date_str="2025-01-01"
    )
    assert roadmap_months is not None
    assert roadmap_months["time_unit"] == "months"
    phase1_m = next(item for item in roadmap_months["timeline"] if item["initiative_name"] == "Phase 1: Research & Development")
    assert phase1_m["start_date"] == "2025-01-01"
    # 1 mês a partir de 2025-01-01 (usando timedelta(days=1*30)) -> 2025-01-31
    assert phase1_m["end_date"] == "2025-01-30" 

    generator_quarters = StrategicRoadmapGenerator(default_time_unit="quarters")
    # Ajustar duração para trimestres (ex: 4,6,8 semanas < 1 trimestre, 10,12 semanas ~ 1 trimestre)
    initiatives_quarters_adj = []
    for init in sample_initiatives:
        new_q_init = dict(init)
        if new_q_init["duration"] <= 12 : new_q_init["duration"] = 1 # Tudo é 1 trimestre ou menos
        else: new_q_init["duration"] = 2
        initiatives_quarters_adj.append(new_q_init)

    roadmap_quarters = generator_quarters.create_roadmap(
        project_name="Project Quarters", 
        goals=sample_goals, 
        initiatives=initiatives_quarters_adj, 
        start_date_str="2025-01-01"
    )
    assert roadmap_quarters is not None
    assert roadmap_quarters["time_unit"] == "quarters"
    phase1_q = next(item for item in roadmap_quarters["timeline"] if item["initiative_name"] == "Phase 1: Research & Development")
    assert phase1_q["start_date"] == "2025-01-01"
    # 1 trimestre a partir de 2025-01-01 (usando timedelta(days=1*90)) -> 2025-03-31
    assert phase1_q["end_date"] == "2025-03-31"

def test_visualize_roadmap_text(capsys, roadmap_generator, sample_goals, sample_initiatives):
    roadmap = roadmap_generator.create_roadmap(
        project_name="Visualization Test",
        goals=sample_goals,
        initiatives=sample_initiatives,
        start_date_str="2025-08-01"
    )
    roadmap_generator.visualize_roadmap_text(roadmap)
    captured = capsys.readouterr()
    assert "--- Roadmap Estratégico: Visualization Test ---" in captured.out
    assert "Goal A: Achieve market leadership." in captured.out
    assert "Phase 1: Research & Development" in captured.out
    assert "Phase 4: Product Launch & Marketing" in captured.out

    roadmap_generator.visualize_roadmap_text(None)
    captured_none = capsys.readouterr()
    assert "Nenhum dado de roadmap para visualizar." in captured_none.out

