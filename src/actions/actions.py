import datetime


def decide_action(decision):
    """Legacy function: decide action based on risk priority."""
    if decision["priority"] == "high":
        return "Notify manager"
    return "Observe"


# Action types and categories
ACTION_TYPES = {
    "engagement": ["one_on_one_meeting", "skill_development", "mentorship", "promotion", "role_change"],
    "skill_gap": ["training_program", "hire_external", "knowledge_transfer", "project_assignment"],
    "team": ["restructure", "add_resource", "cross_train", "establish_reporting"],
    "organizational": ["policy_change", "strategic_initiative", "culture_change"]
}

# Action templates
ACTION_TEMPLATES = {
    "one_on_one_meeting": {
        "description": "Schedule one-on-one discussion with employee",
        "priority": "immediate",
        "duration": "60 minutes",
        "participants": ["HR Manager", "Direct Manager", "Employee"]
    },
    "skill_development": {
        "description": "Enroll employee in skill development program",
        "priority": "high",
        "duration": "30-60 days",
        "budget_required": True
    },
    "mentorship": {
        "description": "Pair employee with mentor",
        "priority": "medium",
        "duration": "ongoing",
        "budget_required": False
    },
    "promotion": {
        "description": "Promote employee to next level",
        "priority": "high",
        "duration": "immediate",
        "requires_approval": True
    },
    "role_change": {
        "description": "Transfer employee to different role",
        "priority": "medium",
        "duration": "1-2 weeks",
        "requires_approval": True
    },
    "training_program": {
        "description": "Enroll in specialized training",
        "priority": "high",
        "duration": "varies",
        "budget_required": True
    },
    "hire_external": {
        "description": "Hire external expert or contractor",
        "priority": "critical",
        "duration": "2-4 weeks",
        "budget_required": True,
        "requires_approval": True
    },
    "knowledge_transfer": {
        "description": "Facilitate knowledge transfer session",
        "priority": "high",
        "duration": "2-3 hours",
        "budget_required": False
    }
}


def execute_engagement_action(employee_id, action_type, engagement_level):
    """Execute engagement-related actions."""
    
    if engagement_level == "low":
        actions = [
            {
                "type": "one_on_one_meeting",
                "target": employee_id,
                "urgency": "immediate",
                "reason": "High burnout risk - needs intervention",
                "template": ACTION_TEMPLATES["one_on_one_meeting"]
            },
            {
                "type": "workload_review",
                "target": employee_id,
                "urgency": "immediate",
                "reason": "Assess and rebalance workload",
                "action_items": ["Review current projects", "Identify bottlenecks", "Rebalance priorities"]
            }
        ]
    elif engagement_level == "medium":
        actions = [
            {
                "type": "engagement_check",
                "target": employee_id,
                "urgency": "high",
                "reason": "Monitor for further decline",
                "frequency": "bi-weekly"
            },
            {
                "type": "growth_opportunity",
                "target": employee_id,
                "urgency": "medium",
                "reason": "Provide new challenges",
                "template": ACTION_TEMPLATES["skill_development"]
            }
        ]
    else:  # high
        actions = [
            {
                "type": "recognition",
                "target": employee_id,
                "urgency": "high",
                "reason": "Recognize and reward high engagement",
                "action_items": ["Public recognition", "Bonus/raise consideration", "Leadership opportunity"]
            },
            {
                "type": "retention",
                "target": employee_id,
                "urgency": "medium",
                "reason": "Ensure retention of top performer",
                "action_items": ["Career development discussion", "Advancement pathway", "Mentorship opportunity"]
            }
        ]
    
    return {
        "employee_id": employee_id,
        "engagement_level": engagement_level,
        "recommended_actions": actions,
        "execution_date": datetime.datetime.now().isoformat(),
        "status": "pending_approval"
    }


def execute_skill_action(employee_id, skill_gap):
    """Execute skill development actions."""
    
    skill_name = skill_gap["skill"]
    priority = skill_gap["priority"]
    
    if priority == "critical":
        actions = [
            {
                "type": "hire_external",
                "target": skill_name,
                "urgency": "critical",
                "reason": f"No internal experts in {skill_name}",
                "template": ACTION_TEMPLATES["hire_external"],
                "estimated_timeline": "2-4 weeks"
            },
            {
                "type": "emergency_training",
                "target": skill_name,
                "urgency": "critical",
                "reason": "Urgent need for internal capability",
                "training_type": "accelerated"
            }
        ]
    elif priority == "high":
        actions = [
            {
                "type": "training_program",
                "target": skill_name,
                "urgency": "high",
                "reason": f"Limited expertise in {skill_name}",
                "template": ACTION_TEMPLATES["training_program"],
                "estimated_timeline": "30-60 days"
            },
            {
                "type": "knowledge_transfer",
                "target": skill_name,
                "urgency": "high",
                "reason": "Share knowledge among team members",
                "template": ACTION_TEMPLATES["knowledge_transfer"]
            }
        ]
    else:
        actions = [
            {
                "type": "training_program",
                "target": skill_name,
                "urgency": "medium",
                "reason": f"Develop internal capability in {skill_name}",
                "estimated_timeline": "60-90 days"
            }
        ]
    
    return {
        "skill": skill_name,
        "priority": priority,
        "recommended_actions": actions,
        "execution_date": datetime.datetime.now().isoformat(),
        "status": "pending_approval"
    }


def execute_promotion_action(employee_id, promotion_eligibility):
    """Execute promotion-related actions."""
    
    if not promotion_eligibility["eligible"]:
        return {
            "employee_id": employee_id,
            "promotion_eligible": False,
            "reason": promotion_eligibility["reason"],
            "recommended_actions": [
                {
                    "type": "skill_development",
                    "reason": promotion_eligibility["reason"],
                    "next_review_date": (datetime.datetime.now() + datetime.timedelta(days=90)).isoformat()
                }
            ]
        }
    
    actions = [
        {
            "type": "promotion",
            "target": employee_id,
            "urgency": "high",
            "reason": promotion_eligibility["reason"],
            "template": ACTION_TEMPLATES["promotion"],
            "required_approvals": ["HR Manager", "Department Head", "Executive Leadership"]
        },
        {
            "type": "role_transition",
            "target": employee_id,
            "urgency": "high",
            "reason": "Support successful transition to new role",
            "action_items": [
                "Prepare new position briefing",
                "Arrange executive coaching",
                "Plan team introduction",
                "Set 30-60-90 day goals"
            ]
        }
    ]
    
    return {
        "employee_id": employee_id,
        "promotion_eligible": True,
        "confidence": promotion_eligibility.get("confidence", 0.8),
        "recommended_actions": actions,
        "execution_date": datetime.datetime.now().isoformat(),
        "status": "pending_approval"
    }


def generate_action_execution_report(employee_id, actions_list):
    """Generate comprehensive action execution report."""
    
    total_actions = len(actions_list)
    immediate_actions = sum(1 for a in actions_list if a.get("urgency") == "immediate")
    high_priority = sum(1 for a in actions_list if a.get("urgency") == "high")
    critical_actions = sum(1 for a in actions_list if a.get("urgency") == "critical")
    
    budget_required = sum(1 for a in actions_list if ACTION_TEMPLATES.get(a.get("type"), {}).get("budget_required"))
    approvals_needed = sum(1 for a in actions_list if ACTION_TEMPLATES.get(a.get("type"), {}).get("requires_approval"))
    
    report = {
        "employee_id": employee_id,
        "report_date": datetime.datetime.now().isoformat(),
        "action_summary": {
            "total_actions": total_actions,
            "immediate": immediate_actions,
            "high_priority": high_priority,
            "critical": critical_actions
        },
        "resource_requirements": {
            "budget_items": budget_required,
            "approvals_required": approvals_needed
        },
        "actions": actions_list,
        "next_review_date": (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
    }
    
    return report


def execute_comprehensive_action_plan(driver, employee_id, decision_data):
    """Execute comprehensive action plan based on decision data."""
    
    all_actions = []
    
    # Engagement actions
    if "engagement" in decision_data:
        engagement_actions = execute_engagement_action(
            employee_id,
            "engagement_response",
            decision_data["engagement"]
        )
        all_actions.extend(engagement_actions["recommended_actions"])
    
    # Promotion actions
    if "promotion_eligible" in decision_data:
        promotion_actions = execute_promotion_action(
            employee_id,
            decision_data["promotion_eligible"]
        )
        all_actions.extend(promotion_actions["recommended_actions"])
    
    # Skill gap actions
    if "skill_gaps" in decision_data:
        for gap in decision_data["skill_gaps"]:
            skill_actions = execute_skill_action(employee_id, gap)
            all_actions.extend(skill_actions["recommended_actions"])
    
    # Generate execution report
    report = generate_action_execution_report(employee_id, all_actions)
    
    return report
