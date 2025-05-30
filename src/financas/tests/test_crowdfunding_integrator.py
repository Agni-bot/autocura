# test_crowdfunding_integrator.py
import pytest
from unittest.mock import patch, MagicMock

import sys
import os
# Adiciona o diretório src ao sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..")) # Sobe dois níveis de tests/ para src/
sys.path.insert(0, project_root)

from financas.crowdfunding_integrator import CrowdfundingIntegrator

@pytest.fixture
def integrator():
    # Mock API keys for testing
    api_keys = {
        "kickstarter": "dummy_kickstarter_key",
        "indiegogo": "dummy_indiegogo_key"
    }
    return CrowdfundingIntegrator(api_keys=api_keys, default_platform="kickstarter")

@pytest.fixture
def mock_kickstarter_client():
    client = MagicMock()
    mock_project_data = [
        MagicMock(
            id="ks_proj_123", name="Awesome Tech Gadget", category="Technology", 
            goal_usd=50000, pledged_usd=60000, backers=700, status="successful",
            url="https://kickstarter.com/projects/test/awesome-gadget",
            to_dict=lambda: { 
                "id": "ks_proj_123", "name": "Awesome Tech Gadget", "category": "Technology",
                "goal_usd": 50000, "pledged_usd": 60000, "backers": 700, "status": "successful",
                "url": "https://kickstarter.com/projects/test/awesome-gadget"
            }
        ),
        MagicMock(
            id="ks_proj_456", name="Indie Game Adventure", category="Games",
            goal_usd=20000, pledged_usd=15000, backers=300, status="live",
            url="https://kickstarter.com/projects/test/indie-game",
            to_dict=lambda: {
                "id": "ks_proj_456", "name": "Indie Game Adventure", "category": "Games",
                "goal_usd": 20000, "pledged_usd": 15000, "backers": 300, "status": "live",
                "url": "https://kickstarter.com/projects/test/indie-game"
            }
        )
    ]
    client.projects.search.return_value = mock_project_data
    client.campaigns.create.return_value = MagicMock(id="new_camp_789", url="https://kickstarter.com/projects/test/new-campaign")
    client.campaigns.get.return_value = MagicMock(id="camp_abc", status="live", pledged_usd=5000)
    return client

def test_crowdfunding_integrator_initialization(integrator):
    assert integrator.default_platform == "kickstarter"
    assert "kickstarter" in integrator.api_keys

def test_search_projects_simulated(integrator):
    projects = integrator.search_projects(category="Technology", keywords="AI Gadget")
    assert projects is not None
    assert len(projects) > 0
    assert any(p["name"] == "Revolutionary AI-Powered Gadget" for p in projects)
    assert all(p["platform"] == "kickstarter" for p in projects)

    projects_indiegogo = integrator.search_projects(platform="indiegogo", category="Games")
    assert projects_indiegogo is not None
    assert any(p["name"] == "Epic Fantasy RPG Adventure" for p in projects_indiegogo)
    assert all(p["platform"] == "indiegogo" for p in projects_indiegogo)

    high_goal_projects = integrator.search_projects(min_goal_usd=60000)
    assert len(high_goal_projects) == 0 
    medium_goal_projects = integrator.search_projects(min_goal_usd=20000)
    assert len(medium_goal_projects) >= 2

    all_kickstarter_projects = integrator.search_projects(platform="kickstarter")
    assert len(all_kickstarter_projects) == 3 

def test_launch_campaign_simulated(integrator):
    project_details = {
        "name": "My New Awesome Project",
        "description": "This project will change the world!",
        "goal_usd": 30000,
        "duration_days": 45
    }
    result = integrator.launch_campaign(project_details=project_details)
    assert result is not None
    assert "campaign_id" in result
    assert "campaign_url" in result
    assert result["status"] == "submitted_for_review"
    assert project_details["name"].lower().replace(" ", "-") in result["campaign_url"]

    incomplete_details = {"description": "Only description"}
    assert integrator.launch_campaign(project_details=incomplete_details) is None

def test_get_campaign_status_simulated(integrator):
    project_details = {"name": "Status Check Campaign", "goal_usd": 5000}
    launch_result = integrator.launch_campaign(project_details=project_details)
    assert launch_result and "campaign_id" in launch_result
    campaign_id = launch_result["campaign_id"]

    status_result = integrator.get_campaign_status(campaign_id=campaign_id)
    assert status_result is not None
    assert status_result["id"] == campaign_id
    assert status_result["status"] == "live" 
    assert "pledged_usd" in status_result

    non_existent_status = integrator.get_campaign_status(campaign_id="non_existent_camp_id")
    assert non_existent_status is not None
    assert non_existent_status["status"] == "not_found"
