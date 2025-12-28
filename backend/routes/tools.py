"""
Tool API Routes
===============

These endpoints expose the starter tools via REST API.
The candidate's agent will call these endpoints when Claude's code execution
requests tool results.
"""

from fastapi import APIRouter, Query
from typing import Optional

from services.tools import (
    tool_get_team_members,
    tool_get_projects,
    tool_get_incidents,
    TOOL_DEFINITIONS,
)

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/definitions")
async def get_tool_definitions():
    """
    Get all tool definitions for the Claude API.
    These include the `allowed_callers` field for Programmatic Tool Calling.
    """
    return {"tools": TOOL_DEFINITIONS}


@router.get("/team-members")
async def get_team_members(
    department: Optional[str] = Query(None, description="Filter by department")
):
    """Get team members, optionally filtered by department."""
    members = await tool_get_team_members(department)
    return {"data": members, "count": len(members)}


@router.get("/projects")
async def get_projects(
    team_id: Optional[str] = Query(None, description="Filter by team/department")
):
    """Get projects, optionally filtered by team."""
    projects = await tool_get_projects(team_id)
    return {"data": projects, "count": len(projects)}


@router.get("/incidents")
async def get_incidents(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity")
):
    """Get incidents, optionally filtered by status and/or severity."""
    incidents = await tool_get_incidents(status, severity)
    return {"data": incidents, "count": len(incidents)}
