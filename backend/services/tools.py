"""
Starter Tools for Mission Control
=================================

These are the 3 example tools provided to get you started.
You will need to design and implement additional tools to complete the challenge.

Hint: Look at the mock data in data/mock_data.py to see what other data is available.
"""

from data.mock_data import get_team_members, get_projects, get_incidents


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
    }
]

# Map tool names to their implementation functions
TOOL_HANDLERS = {
    "get_team_members": tool_get_team_members,
    "get_projects": tool_get_projects,
    "get_incidents": tool_get_incidents,
}
