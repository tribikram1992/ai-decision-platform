from features.ontology import EMPLOYEE_ATTRIBUTES, DECISION_RULES, NODE_TYPES


def engagement_level(score):
    """Map survey score to engagement level."""
    if score <= 2:
        return "low"
    elif score == 3:
        return "medium"
    return "high"


def compute_engagement(df):
    """Compute engagement levels for employees from survey data."""
    df["engagement"] = df["score"].apply(engagement_level)
    return df


def get_engagement_interpretation(engagement):
    """Get human-readable interpretation of engagement level."""
    return EMPLOYEE_ATTRIBUTES["engagement"].get(engagement, "Unknown")


def analyze_engagement_with_context(driver, employee_id, engagement):
    """Analyze engagement in context of employee's role, skills, and team."""
    from decisions.rules import (
        analyze_employee_from_db,
        get_employee_skills,
        assess_promotion_eligibility
    )
    
    employee = analyze_employee_from_db(driver, employee_id)
    if not employee:
        return {"status": "employee_not_found"}
    
    skills = get_employee_skills(driver, employee_id)
    promotion_eligible = assess_promotion_eligibility(driver, employee_id)
    
    # Contextual engagement analysis
    engagement_context = {
        "employee": employee["name"],
        "employee_id": employee_id,
        "engagement_level": engagement,
        "interpretation": get_engagement_interpretation(engagement),
        "role": employee["role"],
        "department": employee["department"],
        "level": employee["level"],
        "skills_count": len(skills),
        "promotion_eligible": promotion_eligible["eligible"],
        "risk_factors": [],
        "opportunities": []
    }
    
    # Identify risk factors
    if engagement == "low":
        engagement_context["risk_factors"].append("High burnout risk - intervention needed")
        if employee["level"] == "Senior":
            engagement_context["risk_factors"].append("Senior-level employee at risk of leaving")
    
    if engagement == "medium" and employee["level"] == "Senior":
        engagement_context["risk_factors"].append("Senior employee with moderate engagement - monitor closely")
    
    # Identify opportunities
    if engagement == "high" and promotion_eligible["eligible"]:
        engagement_context["opportunities"].append("Strong candidate for promotion")
    
    if engagement == "high" and len(skills) >= 2:
        engagement_context["opportunities"].append("Potential mentor for junior team members")
    
    if engagement == "low" and len(skills) >= 2:
        engagement_context["opportunities"].append("Consider skill-development project to boost engagement")
    
    return engagement_context


def compute_team_engagement(driver, department_name):
    """Compute aggregate engagement metrics for a team/department."""
    with driver.session() as session:
        result = session.run(
            '''
            MATCH (e:Employee)-[:WORKS_IN]->(d:Department {name: $dept})
            RETURN e.id, e.name, e.engagement
            ''',
            dept=department_name
        )
        
        employees = []
        engagement_counts = {"high": 0, "medium": 0, "low": 0}
        
        for record in result:
            emp_id, name, engagement_val = record
            if engagement_val:
                employees.append({"id": emp_id, "name": name, "engagement": engagement_val})
                engagement_counts[engagement_val] += 1
        
        total = len(employees)
        avg_engagement = (
            (engagement_counts["high"] * 3 + engagement_counts["medium"] * 2 + engagement_counts["low"] * 1) / total
            if total > 0 else 0
        )
        
        return {
            "department": department_name,
            "total_employees": total,
            "engagement_distribution": engagement_counts,
            "average_engagement_score": round(avg_engagement, 2),
            "team_health": "healthy" if avg_engagement >= 2.5 else "at_risk",
            "employees": employees
        }


def compute_engagement_trends(df):
    """Identify engagement trends and patterns in the data."""
    if df.empty:
        return {"status": "no_data"}
    
    engagement_dist = df["engagement"].value_counts().to_dict()
    total = len(df)
    
    trends = {
        "total_employees": total,
        "engagement_distribution": {
            "high": engagement_dist.get("high", 0),
            "medium": engagement_dist.get("medium", 0),
            "low": engagement_dist.get("low", 0)
        },
        "percentages": {
            "high": round((engagement_dist.get("high", 0) / total) * 100, 1),
            "medium": round((engagement_dist.get("medium", 0) / total) * 100, 1),
            "low": round((engagement_dist.get("low", 0) / total) * 100, 1)
        },
        "organizational_health": "good" if engagement_dist.get("high", 0) >= total * 0.5 else "needs_attention",
        "priority_actions": []
    }
    
    # Add priority actions based on distribution
    if trends["percentages"]["low"] > 25:
        trends["priority_actions"].append("High number of disengaged employees - urgent intervention needed")
    
    if trends["percentages"]["high"] < 30:
        trends["priority_actions"].append("Low high-engagement rate - review compensation and growth opportunities")
    
    if trends["percentages"]["medium"] > 50:
        trends["priority_actions"].append("Large neutral population - tailor engagement initiatives")
    
    return trends


def recommend_engagement_action(engagement, employee_level, role):
    """Recommend actions based on engagement level, employee level, and role."""
    actions = {
        "low": {
            "Junior": ["Schedule mentorship meeting", "Review role fit", "Discuss career growth"],
            "Senior": ["One-on-one leadership discussion", "Explore new challenges", "Consider sabbatical"],
            "Manager": ["Discuss team dynamics", "Executive coaching", "Rebalance responsibilities"]
        },
        "medium": {
            "Junior": ["Provide growth opportunities", "Skill development plan", "Peer collaboration"],
            "Senior": ["Leadership development program", "Project ownership", "Cross-team initiatives"],
            "Manager": ["Manager effectiveness review", "Team engagement assessment", "Strategic planning"]
        },
        "high": {
            "Junior": ["Recognize achievements", "Increase responsibilities", "Mentorship opportunities"],
            "Senior": ["Leadership opportunities", "Promotion pathway", "Innovation projects"],
            "Manager": ["Expand portfolio", "Strategic initiatives", "Succession planning"]
        }
    }
    
    return {
        "engagement": engagement,
        "level": employee_level,
        "role": role,
        "recommended_actions": actions.get(engagement, {}).get(employee_level, [])
    }
