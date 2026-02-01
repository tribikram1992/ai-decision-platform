from neo4j import GraphDatabase


def get_driver(uri, user, password):
    """Create and return a Neo4j driver."""
    return GraphDatabase.driver(uri, auth=(user, password))


def close_driver(driver):
    driver.close()


def _create_employee_tx(tx, emp_id, engagement):
    tx.run(
        "MERGE (e:Employee {employee_id: $id}) SET e.engagement = $engagement",
        id=int(emp_id),
        engagement=engagement,
    )


def create_employee_node(driver, emp_id, engagement):
    with driver.session() as session:
        session.write_transaction(_create_employee_tx, emp_id, engagement)


def clear_all(driver):
    with driver.session() as session:
        session.write_transaction(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))


def sync_df(driver, df):
    with driver.session() as session:
        for _, row in df.iterrows():
            session.write_transaction(_create_employee_tx, int(row["employee_id"]), row["engagement"])
