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


def sync_to_neo4j(df, uri, user, password, clear_first=False):
    """Synchronize the DataFrame into a Neo4j instance.

    Args:
        df: pandas DataFrame with `employee_id` and `engagement` columns.
        uri: Neo4j bolt/http uri, e.g. "bolt://localhost:7687".
        user: Neo4j username.
        password: Neo4j password or token.
        clear_first: if True, delete all nodes before syncing.
    """
    from .neo4j_client import get_driver, close_driver, clear_all, sync_df

    driver = get_driver(uri, user, password)
    try:
        if clear_first:
            clear_all(driver)
        sync_df(driver, df)
    finally:
        close_driver(driver)
