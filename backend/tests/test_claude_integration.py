"""
Tests for Claude AI integration with Programmatic Tool Calling.

This test file verifies that:
1. Tools work correctly when called directly
2. Data exists for all 5 challenge questions

Note: With PTC, Claude executes code in its own secure environment,
so we no longer need sandbox tests. We only test our tool implementations.
"""

import pytest
from services.tools import TOOL_HANDLERS


# =============================================================================
# Test 1: Integration Test - Simple Tool Call
# =============================================================================

@pytest.mark.asyncio
async def test_simple_tool_integration():
    """Test that tools work correctly when called directly."""
    # Test get_team_members
    members = await TOOL_HANDLERS["get_team_members"]()
    assert isinstance(members, list)
    assert len(members) > 0
    assert "name" in members[0]
    assert "department" in members[0]
    
    # Test get_incidents
    incidents = await TOOL_HANDLERS["get_incidents"](severity="P0")
    assert isinstance(incidents, list)
    
    # Test get_budgets
    budgets = await TOOL_HANDLERS["get_budgets"]()
    assert isinstance(budgets, dict)


# =============================================================================
# Test 2: Challenge Question Data Verification
# =============================================================================

@pytest.mark.asyncio
async def test_challenge_q1_data_departments_over_budget():
    """Verify data exists for Q1: Which departments are over budget?"""
    budgets = await TOOL_HANDLERS["get_budgets"]()
    
    # Check that we have budget data
    assert len(budgets) > 0
    
    # Find departments over budget
    over_budget = []
    for dept, data in budgets.items():
        if data["spent"] > data["allocated"]:
            over_budget.append(dept)
    
    # Should have at least one department over budget
    assert len(over_budget) > 0
    print(f"Departments over budget: {over_budget}")


@pytest.mark.asyncio
async def test_challenge_q2_data_declining_satisfaction():
    """Verify data exists for Q2: Projects with declining satisfaction."""
    feedback = await TOOL_HANDLERS["get_customer_feedback"]()
    
    # Check that we have feedback data
    assert len(feedback) > 0
    
    # Find projects with declining trend
    declining = []
    for project_id, data in feedback.items():
        if data.get("trend") == "declining":
            declining.append(project_id)
    
    # Should have projects with declining satisfaction
    assert len(declining) > 0
    print(f"Projects with declining satisfaction: {declining}")


@pytest.mark.asyncio
async def test_challenge_q3_data_engineers_with_p1_incidents():
    """Verify data exists for Q3: Engineers with unresolved P1+ incidents."""
    # Get P0 and P1 incidents that are not resolved
    incidents = await TOOL_HANDLERS["get_incidents"]()
    
    # Filter for P0/P1 and open/investigating status
    high_priority = [
        inc for inc in incidents
        if inc["severity"] in ["P0", "P1"] and inc["status"] in ["open", "investigating"]
    ]
    
    # Should have some high priority unresolved incidents
    assert len(high_priority) > 0
    
    # Get assigned engineers
    assigned_engineers = set(inc["assigned_to"] for inc in high_priority if inc["assigned_to"])
    assert len(assigned_engineers) > 0
    
    print(f"Engineers with P1+ incidents: {assigned_engineers}")


@pytest.mark.asyncio
async def test_challenge_q4_data_incident_deployment_ratio():
    """Verify data exists for Q4: Worst incident-to-deployment ratio."""
    incidents = await TOOL_HANDLERS["get_incidents"]()
    deployments = await TOOL_HANDLERS["get_deployments"]()
    
    # Group by project
    project_incidents = {}
    project_deployments = {}
    
    for inc in incidents:
        project_id = inc["project_id"]
        project_incidents[project_id] = project_incidents.get(project_id, 0) + 1
    
    for dep in deployments:
        project_id = dep["project_id"]
        project_deployments[project_id] = project_deployments.get(project_id, 0) + 1
    
    # Calculate ratios
    ratios = {}
    for project_id in project_incidents:
        if project_id in project_deployments and project_deployments[project_id] > 0:
            ratios[project_id] = project_incidents[project_id] / project_deployments[project_id]
    
    assert len(ratios) > 0
    print(f"Project incident/deployment ratios: {ratios}")


@pytest.mark.asyncio
async def test_challenge_q5_data_infrastructure_summary():
    """Verify data exists for Q5: Infrastructure project summary."""
    # Get infrastructure project
    projects = await TOOL_HANDLERS["get_projects"](team_id="infrastructure")
    assert len(projects) > 0
    
    # For first infrastructure project, get all related data
    project_id = projects[0]["id"]
    
    incidents = await TOOL_HANDLERS["get_incidents"]()
    deployments = await TOOL_HANDLERS["get_deployments"](project_id=project_id)
    feedback = await TOOL_HANDLERS["get_customer_feedback"](project_id=project_id)
    
    # Filter incidents for this project
    project_incidents = [inc for inc in incidents if inc["project_id"] == project_id]
    
    print(f"Infrastructure project {project_id}:")
    print(f"  - Incidents: {len(project_incidents)}")
    print(f"  - Deployments: {len(deployments)}")
    print(f"  - Feedback: {feedback}")
    
    # Should have some data
    assert len(deployments) > 0 or len(project_incidents) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

