"""
Starter Tools for Mission Control
=================================

These are the 3 example tools provided to get you started.
You will need to design and implement additional tools to complete the challenge.

Hint: Look at the mock data in data/mock_data.py to see what other data is available.
"""

from data.mock_data import get_team_members, get_projects, get_incidents, get_budgets, get_customer_feedback, get_deployments


# =============================================================================
# STARTER TOOL 1: Get Team Members
# =============================================================================
async def tool_get_team_members(department: str | None = None) -> list[dict]:
    """
    Retrieve team members from Structured AI.

    Args:
        department: Optional filter by department.
                   Valid values: "engineering", "product", "design", "data", "infrastructure"

    Returns:
        List of team member objects with id, name, email, department, role, level, manager_id
    """
    return get_team_members(department)


# =============================================================================
# STARTER TOOL 2: Get Projects
# =============================================================================
async def tool_get_projects(team_id: str | None = None) -> list[dict]:
    """
    Retrieve projects from Structured AI.

    Args:
        team_id: Optional filter by team/department.
                Valid values: "engineering", "product", "design", "data", "infrastructure"

    Returns:
        List of project objects with id, name, team_id, lead_id, status, started_at
    """
    return get_projects(team_id)


# =============================================================================
# STARTER TOOL 3: Get Incidents
# =============================================================================
async def tool_get_incidents(
    status: str | None = None,
    severity: str | None = None
) -> list[dict]:
    """
    Retrieve incident reports from Structured AI.

    Args:
        status: Optional filter by status. Valid values: "open", "investigating", "resolved"
        severity: Optional filter by severity. Valid values: "P0", "P1", "P2", "P3"

    Returns:
        List of incident objects with id, title, severity, status, project_id,
        assigned_to, created_at, resolved_at, service
    """
    return get_incidents(status, severity)


# =============================================================================
# TOOL 4: Get Budgets
# =============================================================================
async def tool_get_budgets(department: str | None = None) -> dict:
    """
    Retrieve budget data from Structured AI.

    Args:
        department: Optional filter by department.
                   Valid values: "engineering", "product", "design", "data", "infrastructure"

    Returns:
        Dictionary of budget objects with allocated, spent, q1_spent, q2_spent, q3_spent, q4_spent
    """
    return get_budgets(department)


# =============================================================================
# TOOL 5: Get Customer Feedback
# =============================================================================
async def tool_get_customer_feedback(project_id: str | None = None) -> dict:
    """
    Retrieve customer satisfaction data from Structured AI.

    Args:
        project_id: Optional filter by project ID (e.g., "proj_001")

    Returns:
        Dictionary of feedback objects with nps, responses, trend, recent_comments
    """
    return get_customer_feedback(project_id)


# =============================================================================
# TOOL 6: Get Deployments
# =============================================================================
async def tool_get_deployments(
    project_id: str | None = None,
    status: str | None = None
) -> list[dict]:
    """
    Retrieve deployment history from Structured AI.

    Args:
        project_id: Optional filter by project ID
        status: Optional filter by status. Valid values: "success", "failed"

    Returns:
        List of deployment objects with id, project_id, version, deployed_by,
        deployed_at, status, rollback, environment
    """
    return get_deployments(project_id, status)


# =============================================================================
# TOOL DEFINITIONS FOR CLAUDE API
# =============================================================================
# These are the tool definitions you'll send to the Anthropic API.
# Notice the `allowed_callers` field - this enables Programmatic Tool Calling!

TOOL_DEFINITIONS = [
    {
        "name": "get_team_members",
        "description": "Get team members from Structured AI, optionally filtered by department. Returns employee records with id, name, email, department, role, level, and manager_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Filter by department: engineering, product, design, data, or infrastructure",
                    "enum": ["engineering", "product", "design", "data", "infrastructure"]
                }
            },
            "required": []
        },
        # This enables Programmatic Tool Calling!
        "allowed_callers": ["code_execution_20250825"]
    },
    {
        "name": "get_projects",
        "description": "Get projects from Structured AI, optionally filtered by team. Returns project records with id, name, team_id, lead_id, status, and started_at.",
        "input_schema": {
            "type": "object",
            "properties": {
                "team_id": {
                    "type": "string",
                    "description": "Filter by team/department: engineering, product, design, data, or infrastructure",
                    "enum": ["engineering", "product", "design", "data", "infrastructure"]
                }
            },
            "required": []
        },
        "allowed_callers": ["code_execution_20250825"]
    },
    {
        "name": "get_incidents",
        "description": "Get incident reports from Structured AI, optionally filtered by status and/or severity. Returns incident records with id, title, severity, status, project_id, assigned_to, created_at, resolved_at, and service.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter by status",
                    "enum": ["open", "investigating", "resolved"]
                },
                "severity": {
                    "type": "string",
                    "description": "Filter by severity level",
                    "enum": ["P0", "P1", "P2", "P3"]
                }
            },
            "required": []
        },
        "allowed_callers": ["code_execution_20250825"]
    },
    {
        "name": "get_budgets",
        "description": "Get budget allocation and spending data by department from Structured AI. Returns budget information including allocated amounts, spent amounts, and quarterly spending breakdown.",
        "input_schema": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Filter by department: engineering, product, design, data, or infrastructure",
                    "enum": ["engineering", "product", "design", "data", "infrastructure"]
                }
            },
            "required": []
        },
        "allowed_callers": ["code_execution_20250825"]
    },
    {
        "name": "get_customer_feedback",
        "description": "Get customer satisfaction and NPS scores per project from Structured AI. Returns NPS scores, response counts, satisfaction trends, and recent customer comments.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Filter by project ID (e.g., 'proj_001')"
                }
            },
            "required": []
        },
        "allowed_callers": ["code_execution_20250825"]
    },
    {
        "name": "get_deployments",
        "description": "Get deployment history from Structured AI with optional filters for project and status. Returns deployment records with version, status, timestamp, and rollback information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Filter by project ID"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by deployment status",
                    "enum": ["success", "failed"]
                }
            },
            "required": []
        },
        "allowed_callers": ["code_execution_20250825"]
    }
]

# Map tool names to their implementation functions
TOOL_HANDLERS = {
    "get_team_members": tool_get_team_members,
    "get_projects": tool_get_projects,
    "get_incidents": tool_get_incidents,
    "get_budgets": tool_get_budgets,
    "get_customer_feedback": tool_get_customer_feedback,
    "get_deployments": tool_get_deployments,
}
