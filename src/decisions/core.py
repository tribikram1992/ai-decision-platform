from decisions.rules import (
    assess_risk,
    analyze_employee_from_db,
    get_employee_skills,
    assess_promotion_eligibility,
    recommend_skill_development,
    assess_team_structure,
    identify_skill_gaps
)
from features.engagement import (
    analyze_engagement_with_context,
    recommend_engagement_action
)
from features.ontology import DECISION_RULES


def make_decision(employee_features):
    """Make a risk-based decision from employee engagement features."""
    return assess_risk(employee_features)


def comprehensive_employee_assessment(driver, employee_id, engagement=None):
    """Comprehensive assessment of an employee across multiple dimensions."""
    
    employee = analyze_employee_from_db(driver, employee_id)
    if not employee:
        return {"status": "error", "message": "Employee not found"}
    
    skills = get_employee_skills(driver, employee_id)
    promotion_eligible = assess_promotion_eligibility(driver, employee_id)
    skill_recommendations = recommend_skill_development(driver, employee_id)
    
    # Engagement-based analysis if provided
    engagement_analysis = None
    engagement_actions = None
    if engagement:
        engagement_analysis = analyze_engagement_with_context(driver, employee_id, engagement)
        engagement_actions = recommend_engagement_action(engagement, employee["level"], employee["role"])
    
    return {
        "employee_id": employee_id,
        "employee": employee,
        "skills": skills,
        "promotion_eligible": promotion_eligible,
        "skill_recommendations": skill_recommendations,
        "engagement_analysis": engagement_analysis,
        "engagement_actions": engagement_actions,
        "assessment_timestamp": __import__("datetime").datetime.now().isoformat()
    }


def organizational_analytics(driver):
    """Analyze organization-wide metrics and identify strategic issues."""
    
    team_structure = assess_team_structure(driver)
    skill_gaps = identify_skill_gaps(driver)
    
    return {
        "team_structure": team_structure,
        "skill_gaps": skill_gaps,
        "analytics_timestamp": __import__("datetime").datetime.now().isoformat()
    }


def make_strategic_decision(driver, decision_type, target_id=None):
    """Make strategic HR decisions based on rules and data."""
    
    if decision_type == "promotion":
        if not target_id:
            return {"status": "error", "message": "Employee ID required for promotion decision"}
        
        assessment = comprehensive_employee_assessment(driver, target_id)
        if not isinstance(assessment, dict):
            return {"status": "error", "message": "Assessment failed or returned unexpected result"}
        if assessment.get("status") == "error":
            return assessment
        
        promotion_result = assessment["promotion_eligible"]
        
        return {
            "decision": "promote" if promotion_result["eligible"] else "do_not_promote",
            "reason": promotion_result["reason"],
            "confidence": promotion_result.get("confidence", 0),
            "employee": assessment["employee"],
            "details": assessment
        }
    
    elif decision_type == "skill_development":
        if not target_id:
            return {"status": "error", "message": "Employee ID required for skill development decision"}
        
        assessment = comprehensive_employee_assessment(driver, target_id)
        if not isinstance(assessment, dict):
            return {"status": "error", "message": "Assessment failed or returned unexpected result"}
        if assessment.get("status") == "error":
            return assessment
        
        return {
            "decision": "initiate_training",
            "recommendations": assessment["skill_recommendations"],
            "employee": assessment["employee"],
            "priority": assessment["skill_recommendations"].get("priority")
        }
    
    elif decision_type == "organizational_health":
        analytics = organizational_analytics(driver)
        skill_gaps = analytics["skill_gaps"]["critical_skill_gaps"]
        
        decisions = []
        
        # Strategic decisions based on skill gaps
        for gap in skill_gaps:
            if gap["priority"] == "critical":
                decisions.append({
                    "action": "hire_external_expert",
                    "skill": gap["skill"],
                    "reason": f"Critical gap: only {gap['experts']} expert(s) in {gap['skill']}"
                })
            elif gap["priority"] == "high":
                decisions.append({
                    "action": "develop_internal_talent",
                    "skill": gap["skill"],
                    "reason": f"High gap: limited expertise in {gap['skill']}"
                })
        
        # Team structure decisions
        if analytics["team_structure"]["total_reports"] == 0:
            decisions.append({
                "action": "establish_reporting_structure",
                "reason": "No clear reporting relationships defined"
            })
        
        return {
            "decision_type": "organizational_strategy",
            "strategic_decisions": decisions,
            "analytics": analytics
        }
    
    else:
        return {"status": "error", "message": f"Unknown decision type: {decision_type}"}


def create_action_plan(driver, employee_id, engagement=None):
    """Create a detailed action plan for an employee."""
    
    assessment = comprehensive_employee_assessment(driver, employee_id, engagement)
    if not isinstance(assessment, dict):
        return {"status": "error", "message": "Assessment failed or returned unexpected result"}
    if assessment.get("status") == "error":
        return assessment
    
    action_plan = {
        "employee_id": employee_id,
        "employee": assessment["employee"],
        "current_state": {
            "skills": assessment["skills"],
            "engagement": engagement,
            "promotion_eligible": assessment["promotion_eligible"]["eligible"]
        },
        "planned_actions": [],
        "timeline": "90 days"
    }
    
    # Add skill development actions
    if assessment["skill_recommendations"]["recommended_skills"]:
        action_plan["planned_actions"].append({
            "type": "skill_development",
            "skills": assessment["skill_recommendations"]["recommended_skills"],
            "priority": assessment["skill_recommendations"]["priority"],
            "timeline": "30-60 days"
        })
    
    # Add engagement-based actions
    if assessment["engagement_actions"]:
        action_plan["planned_actions"].append({
            "type": "engagement_action",
            "actions": assessment["engagement_actions"]["recommended_actions"],
            "priority": "high" if engagement == "low" else "medium",
            "timeline": "immediate"
        })
    
    # Add promotion pathway if eligible
    if assessment["promotion_eligible"]["eligible"]:
        action_plan["planned_actions"].append({
            "type": "promotion_pathway",
            "target_role": f"Senior {assessment['employee']['role']}",
            "timeline": "6-12 months"
        })
    
    return action_plan
