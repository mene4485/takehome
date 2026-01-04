"""
Tests for Tool API Endpoints
=============================

This module tests all tool endpoints including the newly added budgets,
customer feedback, and deployments endpoints.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# =============================================================================
# Tests for Budgets Endpoint
# =============================================================================

def test_get_all_budgets():
    """Test retrieving all budget data."""
    response = client.get("/tools/budgets")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 5
    
    # Verify all departments are present
    departments = ["engineering", "product", "design", "data", "infrastructure"]
    for dept in departments:
        assert dept in data["data"]
        assert "allocated" in data["data"][dept]
        assert "spent" in data["data"][dept]
        assert "q1_spent" in data["data"][dept]
        assert "q2_spent" in data["data"][dept]
        assert "q3_spent" in data["data"][dept]
        assert "q4_spent" in data["data"][dept]


def test_get_budget_by_department():
    """Test retrieving budget data filtered by department."""
    response = client.get("/tools/budgets?department=engineering")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert "engineering" in data["data"]
    assert data["data"]["engineering"]["allocated"] == 2500
    assert data["data"]["engineering"]["spent"] == 2340


def test_budgets_over_budget():
    """Test identifying departments that are over budget."""
    response = client.get("/tools/budgets")
    assert response.status_code == 200
    data = response.json()
    
    # Design department is over budget
    design = data["data"]["design"]
    assert design["spent"] > design["allocated"]
    
    # Infrastructure department is over budget
    infrastructure = data["data"]["infrastructure"]
    assert infrastructure["spent"] > infrastructure["allocated"]


# =============================================================================
# Tests for Customer Feedback Endpoint
# =============================================================================

def test_get_all_customer_feedback():
    """Test retrieving all customer feedback data."""
    response = client.get("/tools/customer-feedback")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 8
    
    # Verify structure of feedback data
    for project_id, feedback in data["data"].items():
        assert "nps" in feedback
        assert "responses" in feedback
        assert "trend" in feedback
        assert "recent_comments" in feedback
        assert isinstance(feedback["nps"], int)
        assert isinstance(feedback["responses"], int)
        assert isinstance(feedback["trend"], str)
        assert isinstance(feedback["recent_comments"], list)


def test_get_feedback_by_project():
    """Test retrieving customer feedback filtered by project."""
    response = client.get("/tools/customer-feedback?project_id=proj_002")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert "proj_002" in data["data"]
    
    # Verify Customer Portal v2 has declining trend
    proj_002 = data["data"]["proj_002"]
    assert proj_002["nps"] == 28
    assert proj_002["trend"] == "declining"
    assert proj_002["responses"] == 567


def test_feedback_trends():
    """Test analyzing feedback trends across projects."""
    response = client.get("/tools/customer-feedback")
    assert response.status_code == 200
    data = response.json()
    
    # Check that proj_003 (Mobile App Redesign) has improving trend
    assert data["data"]["proj_003"]["trend"] == "improving"
    assert data["data"]["proj_003"]["nps"] == 62
    
    # Check that proj_006 (Search Infrastructure) has improving trend and high NPS
    assert data["data"]["proj_006"]["trend"] == "improving"
    assert data["data"]["proj_006"]["nps"] == 72


# =============================================================================
# Tests for Deployments Endpoint
# =============================================================================

def test_get_all_deployments():
    """Test retrieving all deployments."""
    response = client.get("/tools/deployments")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == data["count"]
    assert data["count"] > 0
    
    # Verify structure of deployment data
    if len(data["data"]) > 0:
        deployment = data["data"][0]
        assert "id" in deployment
        assert "project_id" in deployment
        assert "version" in deployment
        assert "deployed_by" in deployment
        assert "deployed_at" in deployment
        assert "status" in deployment
        assert "rollback" in deployment
        assert "environment" in deployment


def test_deployments_filter_by_project():
    """Test filtering deployments by project."""
    response = client.get("/tools/deployments?project_id=proj_001")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    
    # Verify all deployments are for the requested project
    for deployment in data["data"]:
        assert deployment["project_id"] == "proj_001"


def test_deployments_filter_by_status():
    """Test filtering deployments by status."""
    # Test filtering for successful deployments
    response = client.get("/tools/deployments?status=success")
    assert response.status_code == 200
    data = response.json()
    
    for deployment in data["data"]:
        assert deployment["status"] == "success"
    
    # Test filtering for failed deployments
    response = client.get("/tools/deployments?status=failed")
    assert response.status_code == 200
    data = response.json()
    
    for deployment in data["data"]:
        assert deployment["status"] == "failed"


def test_deployments_combined_filters():
    """Test filtering deployments with both project_id and status."""
    response = client.get("/tools/deployments?project_id=proj_001&status=success")
    assert response.status_code == 200
    data = response.json()
    
    # Verify all deployments match both filters
    for deployment in data["data"]:
        assert deployment["project_id"] == "proj_001"
        assert deployment["status"] == "success"


# =============================================================================
# Tests for Tool Definitions
# =============================================================================

def test_tool_definitions():
    """Test that all tool definitions are properly registered."""
    response = client.get("/tools/definitions")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) == 6
    
    # Verify all tool names are present
    tool_names = [tool["name"] for tool in data["tools"]]
    assert "get_team_members" in tool_names
    assert "get_projects" in tool_names
    assert "get_incidents" in tool_names
    assert "get_budgets" in tool_names
    assert "get_customer_feedback" in tool_names
    assert "get_deployments" in tool_names
    
    # Verify new tools have allowed_callers for PTC
    for tool in data["tools"]:
        if tool["name"] in ["get_budgets", "get_customer_feedback", "get_deployments"]:
            assert "allowed_callers" in tool
            assert "code_execution_20250825" in tool["allowed_callers"]


# =============================================================================
# Tests for Existing Endpoints (Smoke Tests)
# =============================================================================

def test_get_team_members():
    """Smoke test for team members endpoint."""
    response = client.get("/tools/team-members")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data


def test_get_projects():
    """Smoke test for projects endpoint."""
    response = client.get("/tools/projects")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data


def test_get_incidents():
    """Smoke test for incidents endpoint."""
    response = client.get("/tools/incidents")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data

