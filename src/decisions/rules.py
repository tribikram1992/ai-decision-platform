def assess_risk(features):
    if features["engagement"] == "low":
        return {
            "risk": "burnout",
            "priority": "high",
            "confidence": 0.7
        }
    return {
        "risk": "none",
        "priority": "low",
        "confidence": 0.9
    }


# Neo4j-based rules for employee analysis
def analyze_employee_from_db(driver, employee_id):
    """Analyze an employee's skills, role, and department from Neo4j."""
    with driver.session() as session:
        # Get employee details with role and department
        result = session.run(
            '''
            MATCH (e:Employee {id: $emp_id})
            OPTIONAL MATCH (e)-[:HAS_ROLE]->(r:Role)
            OPTIONAL MATCH (e)-[:WORKS_IN]->(d:Department)
            RETURN e.id, e.name, e.level, r.title, d.name
            ''',
            emp_id=employee_id
        )
        
        record = result.single()
        if not record:
            return None
        
        return {
            "id": record[0],
            "name": record[1],
            "level": record[2],
            "role": record[3],
            "department": record[4]
        }


def get_employee_skills(driver, employee_id):
    """Get all skills for an employee with their proficiency levels."""
    with driver.session() as session:
        result = session.run(
            '''
            MATCH (e:Employee {id: $emp_id})-[skill_rel:HAS_SKILL]->(s:Skill)
            RETURN s.name, skill_rel.level
            ''',
            emp_id=employee_id
        )
        
        skills = {}
        for record in result:
            skill_name = record[0]
            level = record[1] if record[1] else "Basic"
            skills[skill_name] = level
        
        return skills


def assess_promotion_eligibility(driver, employee_id):
    """Assess if an employee is eligible for promotion based on skills and level."""
    employee = analyze_employee_from_db(driver, employee_id)
    if not employee:
        return {"eligible": False, "reason": "Employee not found"}
    
    skills = get_employee_skills(driver, employee_id)
    
    # Promotion rule: Senior/Manager level with advanced skills
    level = employee["level"]
    advanced_skills = [s for s, lvl in skills.items() if lvl == "Advanced"]
    
    if level == "Senior" and len(advanced_skills) >= 2:
        return {
            "eligible": True,
            "reason": "Senior level with multiple advanced skills",
            "skills": advanced_skills,
            "confidence": 0.85
        }
    elif level == "Manager" and len(advanced_skills) >= 1:
        return {
            "eligible": True,
            "reason": "Manager level with advanced technical skills",
            "skills": advanced_skills,
            "confidence": 0.7
        }
    else:
        return {
            "eligible": False,
            "reason": f"Current level: {level}, Advanced skills: {len(advanced_skills)}",
            "confidence": 0.9
        }


def recommend_skill_development(driver, employee_id):
    """Recommend skills to develop based on role and current skills."""
    employee = analyze_employee_from_db(driver, employee_id)
    if not employee:
        return {"recommendations": []}
    
    current_skills = get_employee_skills(driver, employee_id)
    role = employee["role"]
    
    # Skill recommendations by role
    role_skills = {
        "Software Engineer": ["Python", "Neo4j"],
        "Engineering Manager": ["Leadership", "Python"],
        "HR Manager": ["Recruitment", "Leadership"],
        "Sales Executive": ["Negotiation"]
    }
    
    recommended = []
    if role in role_skills:
        for skill in role_skills[role]:
            if skill not in current_skills:
                recommended.append(skill)
    
    return {
        "employee": employee["name"],
        "current_role": role,
        "current_skills": current_skills,
        "recommended_skills": recommended,
        "priority": "high" if len(recommended) >= 2 else "medium"
    }


def assess_team_structure(driver):
    """Analyze reporting structure and team organization."""
    with driver.session() as session:
        result = session.run(
            '''
            MATCH (e:Employee)-[:REPORTS_TO]->(manager:Employee)
            RETURN e.id, e.name, manager.id, manager.name, manager.level
            '''
        )
        
        reporting_structure = []
        for record in result:
            reporting_structure.append({
                "employee": record[1],
                "manager": record[3],
                "manager_level": record[4]
            })
        
        return {
            "total_reports": len(reporting_structure),
            "structure": reporting_structure
        }


def identify_skill_gaps(driver):
    """Identify critical skill gaps in the organization."""
    with driver.session() as session:
        # Count employees with critical skills
        result = session.run(
            '''
            MATCH (s:Skill)
            OPTIONAL MATCH (e:Employee)-[skill_rel:HAS_SKILL]->(s)
            WHERE skill_rel.level = "Advanced"
            RETURN s.name, COUNT(DISTINCT e) as expert_count
            '''
        )
        
        skill_gaps = []
        for record in result:
            skill_name = record[0]
            expert_count = record[1]
            
            if expert_count < 2:
                skill_gaps.append({
                    "skill": skill_name,
                    "experts": expert_count,
                    "priority": "critical" if expert_count == 0 else "high"
                })
        
        return {
            "critical_skill_gaps": skill_gaps,
            "total_gaps": len(skill_gaps)
        }
