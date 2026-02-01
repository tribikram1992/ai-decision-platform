import sys
sys.path.insert(0, ".")

import streamlit as st
from datetime import datetime
import pandas as pd

# Data ingestion
from ingest.load_survey import load_survey
from features.engagement import (
    compute_engagement,
    analyze_engagement_with_context,
    compute_team_engagement,
    compute_engagement_trends,
    recommend_engagement_action
)
from features.ontology import FEATURES, DECISION_RULES, SKILLS

# Neo4j and graph
from decisions.neo4j_database import connect_to_db, get_driver, init_db, is_connected, check_db_initialized
from decisions.knowledge_graph import build_graph, get_employee

# Decision making
from decisions.core import (
    make_decision,
    comprehensive_employee_assessment,
    make_strategic_decision,
    organizational_analytics,
    create_action_plan
)

# Actions
from actions.actions import (
    decide_action,
    execute_engagement_action,
    execute_promotion_action,
    generate_action_execution_report
)

# Page configuration
st.set_page_config(page_title="HR Decision Copilot", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .danger-box {
        background-color: #f8d7da;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None
    st.session_state.graph_built = False
    st.session_state.db_connected = False
    st.session_state.db_initialized = False

# Initialize database connection on startup
if not st.session_state.db_connected:
    st.session_state.db_connected = connect_to_db()

# Sidebar
st.sidebar.title("🚀 HR Decision Copilot")
st.sidebar.markdown("---")

# Load data
with st.sidebar:
    st.subheader("📊 Data Management")
    
    # Database connection status
    if st.session_state.db_connected:
        st.success("✓ Neo4j Connected")
        st.session_state.db_initialized = check_db_initialized()
        if st.session_state.db_initialized:
            st.info("✓ Database Initialized")
    else:
        st.error("❌ Neo4j Not Connected")
        if st.button("🔄 Retry Connection"):
            st.session_state.db_connected = connect_to_db()
            st.rerun()
    
    st.markdown("---")
    
    if st.button("📥 Load Survey Data"):
        with st.spinner("Loading survey data..."):
            try:
                st.session_state.df = load_survey("data/survey.csv")
                st.session_state.df = compute_engagement(st.session_state.df)
                build_graph(st.session_state.df)
                st.session_state.data_loaded = True
                st.session_state.graph_built = True
                st.success("✓ Data loaded successfully!")
            except Exception as e:
                st.error(f"Error loading data: {e}")
    
    if st.session_state.db_connected:
        if st.button("🗄️  Initialize Database"):
            with st.spinner("Initializing Neo4j database..."):
                try:
                    result = init_db(clear_first=True)
                    if result["success"]:
                        st.session_state.db_initialized = True
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                except Exception as e:
                    st.error(f"Error initializing database: {e}")

# Main content
if not st.session_state.data_loaded:
    st.info("👈 Please load survey data from the sidebar to begin")
else:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Dashboard",
        "👤 Employee Analysis",
        "🏢 Organization",
        "📋 Action Plans",
        "📚 Reference"
    ])
    
    # Tab 1: Dashboard
    with tab1:
        st.header("📈 Dashboard Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            engagement_trends = compute_engagement_trends(st.session_state.df)
            st.metric(
                "Total Employees",
                engagement_trends["total_employees"]
            )
        
        with col2:
            high_engagement = engagement_trends["engagement_distribution"]["high"]
            st.metric(
                "High Engagement",
                f"{high_engagement} ({engagement_trends['percentages']['high']}%)"
            )
        
        with col3:
            low_engagement = engagement_trends["engagement_distribution"]["low"]
            st.metric(
                "Low Engagement (At Risk)",
                f"{low_engagement} ({engagement_trends['percentages']['low']}%)"
            )
        
        # Engagement distribution chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Engagement Distribution")
            chart_data = pd.DataFrame({
                "Level": ["High", "Medium", "Low"],
                "Count": [
                    engagement_trends["engagement_distribution"]["high"],
                    engagement_trends["engagement_distribution"]["medium"],
                    engagement_trends["engagement_distribution"]["low"]
                ]
            })
            st.bar_chart(chart_data.set_index("Level"))
        
        with col2:
            st.subheader("Organizational Health")
            st.info(f"Status: {engagement_trends['organizational_health'].upper()}")
            st.write("**Priority Actions:**")
            for action in engagement_trends["priority_actions"]:
                st.warning(f"• {action}")
    
    # Tab 2: Employee Analysis
    with tab2:
        st.header("👤 Individual Employee Analysis")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            employee_id_input = st.selectbox(
                "Select Employee",
                options=st.session_state.df["employee_id"].unique(),
                help="Choose an employee to analyze"
            )
        
        with col2:
            st.write("")  # Spacing
        
        if employee_id_input:
            # Get employee row from CSV
            emp_row = st.session_state.df[st.session_state.df["employee_id"] == int(employee_id_input)].iloc[0]
            engagement = emp_row["engagement"]
            
            # Convert employee_id to Neo4j format (E1, E2, etc.)
            neo4j_emp_id = f"E{int(employee_id_input)}"
            
            # Comprehensive assessment
            assessment = comprehensive_employee_assessment(get_driver(), neo4j_emp_id, engagement)

            # Guard against None or error responses from the assessment
            if not assessment or (isinstance(assessment, dict) and assessment.get("status") == "error"):
                msg = assessment.get("message") if isinstance(assessment, dict) else "Assessment failed or returned no data"
                st.error(f"Error: {msg}")
            else:
                employee = assessment["employee"]
                
                # Header with employee info
                st.subheader(f"👤 {employee['name']} (ID: {employee['id']})")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Level", employee['level'])
                with col2:
                    st.metric("Role", employee['role'])
                with col3:
                    st.metric("Department", employee['department'])
                with col4:
                    st.metric("Engagement", engagement.upper())
                
                # Engagement Analysis
                st.markdown("---")
                st.subheader("💼 Engagement Analysis")
                engagement_analysis = assessment["engagement_analysis"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Interpretation:** {engagement_analysis['interpretation']}")
                    st.write(f"**Skills Count:** {engagement_analysis['skills_count']}")
                
                with col2:
                    if engagement_analysis["risk_factors"]:
                        st.write("**Risk Factors:**")
                        for risk in engagement_analysis["risk_factors"]:
                            st.error(f"⚠️ {risk}")
                
                if engagement_analysis["opportunities"]:
                    st.write("**Opportunities:**")
                    for opp in engagement_analysis["opportunities"]:
                        st.success(f"✓ {opp}")
                
                # Skills
                st.markdown("---")
                st.subheader("🎯 Skills & Expertise")
                skills = assessment["skills"]
                if skills:
                    skills_df = pd.DataFrame([
                        {"Skill": k, "Level": v}
                        for k, v in skills.items()
                    ])
                    st.dataframe(skills_df, use_container_width=True)
                else:
                    st.info("No skills recorded")
                
                # Promotion Eligibility
                st.markdown("---")
                st.subheader("🚀 Career Development")
                promotion = assessment["promotion_eligible"]
                
                if promotion["eligible"]:
                    st.success(f"✅ **Promotion Eligible** - {promotion['reason']}")
                    st.metric("Confidence", f"{promotion.get('confidence', 0):.0%}")
                else:
                    st.warning(f"❌ Not Yet Eligible - {promotion['reason']}")
                
                # Skill Recommendations
                skill_recs = assessment["skill_recommendations"]
                if skill_recs["recommended_skills"]:
                    st.info(f"**Recommended Skills:** {', '.join(skill_recs['recommended_skills'])}")
                
                # Engagement Actions
                if assessment["engagement_actions"]:
                    st.markdown("---")
                    st.subheader("📋 Recommended Actions")
                    for action in assessment["engagement_actions"]["recommended_actions"]:
                        st.write(f"• {action}")
                
                # Action Plan Button
                if st.button("📋 Create Full Action Plan"):
                    driver = get_driver()
                    if driver:
                        action_plan = create_action_plan(driver, neo4j_emp_id, engagement)
                        st.json(action_plan)
                    else:
                        st.error("Database not connected")
    
    # Tab 3: Organization
    with tab3:
        st.header("🏢 Organizational Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔗 Team Structure")
            driver = get_driver()
            if driver:
                analytics = organizational_analytics(driver)
                team_struct = analytics["team_structure"]
                st.metric("Total Reports", team_struct["total_reports"])
                
                if team_struct["structure"]:
                    st.write("**Reporting Relationships:**")
                    for rel in team_struct["structure"]:
                        st.write(f"• {rel['employee']} → {rel['manager']} ({rel['manager_level']})")
            else:
                st.error("Database not connected")
        
        with col2:
            st.subheader("⚠️ Skill Gaps")
            driver = get_driver()
            if driver:
                analytics = organizational_analytics(driver)
                skill_gaps = analytics["skill_gaps"]
                gaps = skill_gaps["critical_skill_gaps"]
                
                st.metric("Total Gaps", skill_gaps["total_gaps"])
            
            if gaps:
                st.write("**Critical Gaps:**")
                for gap in gaps:
                    severity = "🔴" if gap["priority"] == "critical" else "🟡"
                    st.write(f"{severity} **{gap['skill']}** - {gap['experts']} expert(s)")
        
        # Department Engagement
        st.markdown("---")
        st.subheader("📊 Department Engagement")
        
        departments = ["Engineering", "HR", "Sales"]
        dept_cols = st.columns(len(departments))
        
        for idx, dept in enumerate(departments):
            with dept_cols[idx]:
                team_eng = compute_team_engagement(get_driver(), dept)
                st.metric(dept, team_eng["team_health"].upper())
                st.write(f"Avg Score: {team_eng['average_engagement_score']:.2f}")
        
        # Strategic Decisions
        st.markdown("---")
        if st.button("🎯 Generate Strategic Recommendations"):
            decisions = make_strategic_decision(get_driver(), "organizational_health")
            st.subheader("Strategic Recommendations")
            for decision in decisions["strategic_decisions"]:
                st.info(f"**{decision['action'].replace('_', ' ').title()}**: {decision['reason']}")
    
    # Tab 4: Action Plans
    with tab4:
        st.header("📋 Action Execution")
        
        emp_select = st.selectbox(
            "Select Employee for Action Plan",
            options=st.session_state.df["employee_id"].unique(),
            key="action_emp_select"
        )
        
        if emp_select:
            emp_row = st.session_state.df[st.session_state.df["employee_id"] == int(emp_select)].iloc[0]
            neo4j_emp_id = f"E{int(emp_select)}"
            engagement = emp_row["engagement"]
            
            if st.button("Generate Execution Report"):
                # Get assessment data
                driver = get_driver()
                if driver:
                    assessment = comprehensive_employee_assessment(driver, neo4j_emp_id, engagement)

                    # Validate assessment structure before use
                    if not isinstance(assessment, dict):
                        st.error("Assessment failed or returned unexpected result")
                    elif assessment.get("status") == "error":
                        st.error(f"Error: {assessment.get('message', 'Unknown error')}")
                    else:
                        # Execute engagement action
                        engagement_actions = execute_engagement_action(neo4j_emp_id, "engagement_response", engagement)

                        # Generate report
                        report = generate_action_execution_report(
                            neo4j_emp_id,
                            engagement_actions["recommended_actions"]
                        )

                        st.subheader(f"Execution Report: {assessment['employee']['name']}")

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Actions", report["action_summary"]["total_actions"])
                        with col2:
                            st.metric("Immediate", report["action_summary"]["immediate"])
                        with col3:
                            st.metric("High Priority", report["action_summary"]["high_priority"])
                        with col4:
                            st.metric("Critical", report["action_summary"]["critical"])

                        st.markdown("---")
                        st.write("**Actions:**")
                        for action in report["actions"]:
                            st.write(f"• {action.get('type', 'Unknown').upper()}: {action.get('reason', '')}")

                        st.write(f"\n**Next Review:** {report['next_review_date']}")
                else:
                    st.error("Database not connected")
    
    # Tab 5: Reference
    with tab5:
        st.header("📚 System Reference")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Features & Engagement Levels")
            for feature, levels in FEATURES.items():
                st.write(f"**{feature.upper()}:**")
                for level, desc in levels.items():
                    st.write(f"  • {level}: {desc}")
        
        with col2:
            st.subheader("🎯 Skills Inventory")
            for skill, details in SKILLS.items():
                st.write(f"**{skill}** ({details['category']})")
                if details['critical']:
                    st.write("  🔴 Critical")
        
        st.markdown("---")
        st.subheader("📋 Decision Rules")
        for rule_name, rule_details in DECISION_RULES.items():
            st.write(f"**{rule_name.replace('_', ' ').title()}**")
            st.write(f"  {rule_details['description']}")

st.markdown("---")
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
