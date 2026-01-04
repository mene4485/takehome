"""
Mock data for Structured AI - a fictional tech company.
This simulates a realistic operations environment with interconnected data.
"""

from datetime import datetime, timedelta
import random

# Seed for reproducibility
random.seed(42)

DEPARTMENTS = ["engineering", "product", "design", "data", "infrastructure"]

TEAM_MEMBERS = [
    # Engineering
    {"id": "emp_001", "name": "Alice Chen", "email": "alice@structuredai.io", "department": "engineering", "role": "Senior Engineer", "level": "L5", "manager_id": "emp_010"},
    {"id": "emp_002", "name": "Bob Martinez", "email": "bob@structuredai.io", "department": "engineering", "role": "Engineer", "level": "L4", "manager_id": "emp_010"},
    {"id": "emp_003", "name": "Carol Williams", "email": "carol@structuredai.io", "department": "engineering", "role": "Engineer", "level": "L4", "manager_id": "emp_010"},
    {"id": "emp_004", "name": "David Kim", "email": "david@structuredai.io", "department": "engineering", "role": "Junior Engineer", "level": "L3", "manager_id": "emp_001"},
    {"id": "emp_010", "name": "Eva Rodriguez", "email": "eva@structuredai.io", "department": "engineering", "role": "Engineering Manager", "level": "L6", "manager_id": None},

    # Product
    {"id": "emp_005", "name": "Frank Liu", "email": "frank@structuredai.io", "department": "product", "role": "Product Manager", "level": "L5", "manager_id": "emp_011"},
    {"id": "emp_006", "name": "Grace Park", "email": "grace@structuredai.io", "department": "product", "role": "Senior PM", "level": "L6", "manager_id": "emp_011"},
    {"id": "emp_011", "name": "Henry Zhao", "email": "henry@structuredai.io", "department": "product", "role": "Director of Product", "level": "L7", "manager_id": None},

    # Design
    {"id": "emp_007", "name": "Iris Thompson", "email": "iris@structuredai.io", "department": "design", "role": "Senior Designer", "level": "L5", "manager_id": "emp_012"},
    {"id": "emp_008", "name": "Jake Anderson", "email": "jake@structuredai.io", "department": "design", "role": "Designer", "level": "L4", "manager_id": "emp_012"},
    {"id": "emp_012", "name": "Karen Singh", "email": "karen@structuredai.io", "department": "design", "role": "Design Lead", "level": "L6", "manager_id": None},

    # Data
    {"id": "emp_013", "name": "Leo Nakamura", "email": "leo@structuredai.io", "department": "data", "role": "Data Scientist", "level": "L5", "manager_id": "emp_015"},
    {"id": "emp_014", "name": "Maya Patel", "email": "maya@structuredai.io", "department": "data", "role": "Data Engineer", "level": "L4", "manager_id": "emp_015"},
    {"id": "emp_015", "name": "Noah Brown", "email": "noah@structuredai.io", "department": "data", "role": "Data Lead", "level": "L6", "manager_id": None},

    # Infrastructure
    {"id": "emp_016", "name": "Olivia Davis", "email": "olivia@structuredai.io", "department": "infrastructure", "role": "SRE", "level": "L5", "manager_id": "emp_018"},
    {"id": "emp_017", "name": "Peter Wilson", "email": "peter@structuredai.io", "department": "infrastructure", "role": "DevOps Engineer", "level": "L4", "manager_id": "emp_018"},
    {"id": "emp_018", "name": "Quinn Foster", "email": "quinn@structuredai.io", "department": "infrastructure", "role": "Infrastructure Lead", "level": "L6", "manager_id": None},
]

PROJECTS = [
    {"id": "proj_001", "name": "Phoenix API", "team_id": "engineering", "lead_id": "emp_001", "status": "active", "started_at": "2024-01-15"},
    {"id": "proj_002", "name": "Customer Portal v2", "team_id": "engineering", "lead_id": "emp_002", "status": "active", "started_at": "2024-03-01"},
    {"id": "proj_003", "name": "Mobile App Redesign", "team_id": "design", "lead_id": "emp_007", "status": "active", "started_at": "2024-02-10"},
    {"id": "proj_004", "name": "Data Pipeline Overhaul", "team_id": "data", "lead_id": "emp_013", "status": "active", "started_at": "2024-04-01"},
    {"id": "proj_005", "name": "Cloud Migration", "team_id": "infrastructure", "lead_id": "emp_016", "status": "active", "started_at": "2023-11-01"},
    {"id": "proj_006", "name": "Search Infrastructure", "team_id": "engineering", "lead_id": "emp_003", "status": "active", "started_at": "2024-05-15"},
    {"id": "proj_007", "name": "Analytics Dashboard", "team_id": "data", "lead_id": "emp_014", "status": "completed", "started_at": "2024-01-01"},
    {"id": "proj_008", "name": "Design System", "team_id": "design", "lead_id": "emp_008", "status": "active", "started_at": "2024-06-01"},
]

# Generate incidents with realistic patterns
def generate_incidents():
    incidents = []
    severities = ["P0", "P1", "P2", "P3"]
    statuses = ["open", "investigating", "resolved"]

    incident_templates = [
        {"title": "API latency spike in {service}", "service": "Phoenix API", "project_id": "proj_001"},
        {"title": "Database connection pool exhausted", "service": "Core DB", "project_id": "proj_001"},
        {"title": "Customer Portal login failures", "service": "Auth Service", "project_id": "proj_002"},
        {"title": "Search indexing delay", "service": "Search", "project_id": "proj_006"},
        {"title": "Pipeline job failures", "service": "Data Pipeline", "project_id": "proj_004"},
        {"title": "CDN cache invalidation issues", "service": "CDN", "project_id": "proj_005"},
        {"title": "Memory leak in worker nodes", "service": "Workers", "project_id": "proj_005"},
        {"title": "SSL certificate expiration warning", "service": "Infrastructure", "project_id": "proj_005"},
    ]

    engineers = [e for e in TEAM_MEMBERS if e["department"] in ["engineering", "infrastructure"]]

    base_date = datetime.now()

    for i in range(25):
        template = random.choice(incident_templates)
        days_ago = random.randint(0, 30)
        created = base_date - timedelta(days=days_ago, hours=random.randint(0, 23))
        severity = random.choices(severities, weights=[5, 15, 40, 40])[0]

        # P0s are more likely to be resolved, P3s might still be open
        if severity == "P0":
            status = random.choices(statuses, weights=[10, 20, 70])[0]
        elif severity == "P1":
            status = random.choices(statuses, weights=[15, 25, 60])[0]
        else:
            status = random.choices(statuses, weights=[30, 20, 50])[0]

        resolved_at = None
        if status == "resolved":
            resolution_hours = random.randint(1, 48) if severity in ["P0", "P1"] else random.randint(4, 168)
            resolved_at = (created + timedelta(hours=resolution_hours)).isoformat()

        incidents.append({
            "id": f"inc_{i+1:03d}",
            "title": template["title"].format(service=template["service"]),
            "severity": severity,
            "status": status,
            "project_id": template["project_id"],
            "assigned_to": random.choice(engineers)["id"],
            "created_at": created.isoformat(),
            "resolved_at": resolved_at,
            "service": template["service"],
        })

    return sorted(incidents, key=lambda x: x["created_at"], reverse=True)

INCIDENTS = generate_incidents()

# Budget data per department (in thousands)
BUDGETS = {
    "engineering": {"allocated": 2500, "spent": 2340, "q1_spent": 580, "q2_spent": 620, "q3_spent": 590, "q4_spent": 550},
    "product": {"allocated": 800, "spent": 720, "q1_spent": 180, "q2_spent": 190, "q3_spent": 175, "q4_spent": 175},
    "design": {"allocated": 600, "spent": 680, "q1_spent": 160, "q2_spent": 170, "q3_spent": 180, "q4_spent": 170},  # Over budget!
    "data": {"allocated": 1200, "spent": 1100, "q1_spent": 270, "q2_spent": 280, "q3_spent": 275, "q4_spent": 275},
    "infrastructure": {"allocated": 3000, "spent": 3200, "q1_spent": 780, "q2_spent": 800, "q3_spent": 820, "q4_spent": 800},  # Over budget!
}

# Customer satisfaction scores per project (NPS-style, -100 to 100)
CUSTOMER_FEEDBACK = {
    "proj_001": {"nps": 45, "responses": 234, "trend": "stable", "recent_comments": [
        {"score": 9, "comment": "API is fast and reliable"},
        {"score": 7, "comment": "Good but documentation could be better"},
        {"score": 8, "comment": "Love the new endpoints"},
    ]},
    "proj_002": {"nps": 28, "responses": 567, "trend": "declining", "recent_comments": [
        {"score": 5, "comment": "Login is slow sometimes"},
        {"score": 6, "comment": "UI is confusing"},
        {"score": 4, "comment": "Can't find basic features"},
    ]},
    "proj_003": {"nps": 62, "responses": 189, "trend": "improving", "recent_comments": [
        {"score": 9, "comment": "Beautiful new design!"},
        {"score": 10, "comment": "So much easier to use"},
        {"score": 8, "comment": "Great improvements"},
    ]},
    "proj_004": {"nps": 51, "responses": 45, "trend": "stable", "recent_comments": [
        {"score": 8, "comment": "Data is more reliable now"},
        {"score": 7, "comment": "Reports are faster"},
    ]},
    "proj_005": {"nps": 38, "responses": 123, "trend": "declining", "recent_comments": [
        {"score": 6, "comment": "Some downtime recently"},
        {"score": 5, "comment": "Performance issues"},
        {"score": 7, "comment": "Generally stable"},
    ]},
    "proj_006": {"nps": 72, "responses": 312, "trend": "improving", "recent_comments": [
        {"score": 10, "comment": "Search is blazing fast now"},
        {"score": 9, "comment": "Finally finds what I need"},
        {"score": 9, "comment": "Huge improvement"},
    ]},
    "proj_007": {"nps": 55, "responses": 89, "trend": "stable", "recent_comments": [
        {"score": 8, "comment": "Dashboards are useful"},
        {"score": 7, "comment": "Good data visualization"},
    ]},
    "proj_008": {"nps": 41, "responses": 67, "trend": "stable", "recent_comments": [
        {"score": 7, "comment": "Components are consistent"},
        {"score": 6, "comment": "Some components missing"},
    ]},
}

# Deployments per project
def generate_deployments():
    deployments = []
    base_date = datetime.now()

    for project in PROJECTS:
        # Each project has 5-15 deployments in the last 30 days
        num_deployments = random.randint(5, 15)
        engineers = [e for e in TEAM_MEMBERS if e["department"] == project["team_id"]]

        for i in range(num_deployments):
            days_ago = random.randint(0, 30)
            deployed_at = base_date - timedelta(days=days_ago, hours=random.randint(9, 18))
            success = random.random() > 0.1  # 90% success rate

            deployments.append({
                "id": f"deploy_{project['id']}_{i+1:03d}",
                "project_id": project["id"],
                "version": f"v{random.randint(1,9)}.{random.randint(0,99)}.{random.randint(0,999)}",
                "deployed_by": random.choice(engineers)["id"] if engineers else "emp_001",
                "deployed_at": deployed_at.isoformat(),
                "status": "success" if success else "failed",
                "rollback": not success and random.random() > 0.5,
                "environment": random.choice(["production", "staging"]),
            })

    return sorted(deployments, key=lambda x: x["deployed_at"], reverse=True)

DEPLOYMENTS = generate_deployments()




def get_team_members(department: str | None = None) -> list[dict]:
    """Get team members, optionally filtered by department."""
    if department:
        return [m for m in TEAM_MEMBERS if m["department"] == department.lower()]
    return TEAM_MEMBERS


def get_projects(team_id: str | None = None) -> list[dict]:
    """Get projects, optionally filtered by team."""
    if team_id:
        return [p for p in PROJECTS if p["team_id"] == team_id.lower()]
    return PROJECTS


def get_incidents(status: str | None = None, severity: str | None = None) -> list[dict]:
    """Get incidents, optionally filtered by status and/or severity."""
    results = INCIDENTS
    if status:
        results = [i for i in results if i["status"] == status.lower()]
    if severity:
        results = [i for i in results if i["severity"] == severity.upper()]
    return results


def get_budgets(department: str | None = None) -> dict:
    """Get budget data, optionally filtered by department."""
    if department:
        return {department.lower(): BUDGETS[department.lower()]}
    return BUDGETS


def get_customer_feedback(project_id: str | None = None) -> dict:
    """Get customer satisfaction data, optionally filtered by project."""
    if project_id:
        return {project_id: CUSTOMER_FEEDBACK[project_id]}
    return CUSTOMER_FEEDBACK


def get_deployments(project_id: str | None = None, status: str | None = None) -> list[dict]:
    """Get deployments, optionally filtered by project and/or status."""
    results = DEPLOYMENTS
    if project_id:
        results = [d for d in results if d["project_id"] == project_id]
    if status:
        results = [d for d in results if d["status"] == status.lower()]
    return results
