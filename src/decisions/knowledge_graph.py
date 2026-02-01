graph = {}

def add_employee(emp_id, features):
    graph[emp_id] = features

def get_employee(emp_id):
    return graph.get(emp_id)

def build_graph(df):
    """Populate the in-memory graph from a DataFrame."""
    for _, row in df.iterrows():
        add_employee(row["employee_id"], {
            "engagement": row["engagement"]
        })
    return graph
