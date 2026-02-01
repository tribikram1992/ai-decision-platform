FEATURES = {
    "engagement": {
        "low": "Employee shows disengagement",
        "medium": "Employee is neutral",
        "high": "Employee is engaged"
    }
}
# Node types and their properties
NODE_TYPES = {
    "Employee": {
        "properties": ["id", "name", "level", "engagement", "employee_id"],
        "levels": ["Junior", "Senior", "Manager"],
        "description": "Represents an employee in the organization"
    },
    "Department": {
        "properties": ["id", "name"],
        "description": "Represents a department or team"
    },
    "Role": {
        "properties": ["id", "title"],
        "description": "Represents a job role or position"
    },
    "Skill": {
        "properties": ["name"],
        "description": "Represents a professional skill"
    }
}

# Relationship types and their semantics
RELATIONSHIPS = {
    "WORKS_IN": {
        "from": "Employee",
        "to": "Department",
        "properties": [],
        "description": "Employee is part of a department"
    },
    "HAS_ROLE": {
        "from": "Employee",
        "to": "Role",
        "properties": [],
        "description": "Employee holds a specific role"
    },
    "HAS_SKILL": {
        "from": "Employee",
        "to": "Skill",
        "properties": ["level"],
        "levels": ["Basic", "Intermediate", "Advanced"],
        "description": "Employee possesses a skill at a certain level"
    },
    "REPORTS_TO": {
        "from": "Employee",
        "to": "Employee",
        "properties": [],
        "description": "Employee reports to a manager"
    }
}

# Departments
DEPARTMENTS = {
    "D1": {"name": "Engineering", "description": "Software development and technical teams"},
    "D2": {"name": "HR", "description": "Human resources and talent management"},
    "D3": {"name": "Sales", "description": "Sales and business development"}
}

# Roles
ROLES = {
    "R1": {"title": "Software Engineer", "seniority": 1, "department": "Engineering"},
    "R2": {"title": "Engineering Manager", "seniority": 2, "department": "Engineering"},
    "R3": {"title": "HR Manager", "seniority": 2, "department": "HR"},
    "R4": {"title": "Sales Executive", "seniority": 1, "department": "Sales"}
}

# Skills inventory
SKILLS = {
    "Python": {"category": "Technical", "critical": True},
    "Neo4j": {"category": "Technical", "critical": True},
    "Leadership": {"category": "Soft", "critical": False},
    "Recruitment": {"category": "Functional", "critical": False},
    "Negotiation": {"category": "Soft", "critical": False}
}

# Decision rules based on ontology
DECISION_RULES = {
    "promotion_eligibility": {
        "description": "Rules for employee promotion assessment",
        "conditions": [
            {"level": "Senior", "advanced_skills_required": 2},
            {"level": "Manager", "advanced_skills_required": 1}
        ]
    },
    "burnout_risk": {
        "description": "Rules for identifying burnout risk",
        "conditions": [
            {"engagement": "low", "priority": "high", "confidence": 0.7},
            {"engagement": "medium", "priority": "low", "confidence": 0.9}
        ]
    },
    "skill_gap": {
        "description": "Rules for identifying skill gaps in organization",
        "conditions": [
            {"critical_skill": True, "experts": 0, "priority": "critical"},
            {"critical_skill": True, "experts": 1, "priority": "high"},
            {"critical_skill": False, "experts": 0, "priority": "medium"}
        ]
    },
    "team_structure": {
        "description": "Rules for analyzing team composition",
        "conditions": [
            {"reports_to_manager": True, "manager_level": "Manager"}
        ]
    }
}

# Employee attributes and their interpretations
EMPLOYEE_ATTRIBUTES = {
    "level": {
        "Junior": "Entry-level, requires mentorship",
        "Senior": "Advanced skills, can lead projects",
        "Manager": "Leadership role, manages team"
    },
    "engagement": {
        "low": "At-risk, requires intervention",
        "medium": "Stable, normal performance",
        "high": "Highly motivated, potential leader"
    }
}