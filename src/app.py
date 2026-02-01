from ingest.load_survey import load_survey
from features.engagement import compute_engagement
from decisions.knowledge_graph import build_graph, get_employee
from decisions.core import make_decision
from actions.actions import decide_action

import streamlit as st

data = load_survey("data/survey.csv")
data = compute_engagement(data)
build_graph(data)

st.title("HR Decision Copilot")

employee_id = st.number_input("Employee ID", min_value=1)

if st.button("Analyze"):
    features = get_employee(employee_id)
    if features is None:
        st.warning("Employee not found in data")
    else:
        decision = make_decision(features)
        action = decide_action(decision)

        st.write("Decision:", decision)
        st.write("Recommended Action:", action)
