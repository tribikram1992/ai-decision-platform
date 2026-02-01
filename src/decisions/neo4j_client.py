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


# Database initialization functions
def create_department(driver, dept_id, name):
    """Create a Department node."""
    with driver.session() as session:
        session.run(
            'CREATE (:Department {id: $id, name: $name})',
            id=dept_id,
            name=name
        )


def create_role(driver, role_id, title):
    """Create a Role node."""
    with driver.session() as session:
        session.run(
            'CREATE (:Role {id: $id, title: $title})',
            id=role_id,
            title=title
        )


def create_skill(driver, name):
    """Create a Skill node."""
    with driver.session() as session:
        session.run(
            'CREATE (:Skill {name: $name})',
            name=name
        )


def create_employee(driver, emp_id, name, level):
    """Create an Employee node."""
    with driver.session() as session:
        session.run(
            'CREATE (:Employee {id: $id, name: $name, level: $level})',
            id=emp_id,
            name=name,
            level=level
        )


def create_works_in_relationship(driver, employee_id, department_name):
    """Create WORKS_IN relationship between Employee and Department."""
    with driver.session() as session:
        session.run(
            'MATCH (a:Employee {id: $emp_id}), (d:Department {name: $dept_name}) '
            'CREATE (a)-[:WORKS_IN]->(d)',
            emp_id=employee_id,
            dept_name=department_name
        )


def create_has_role_relationship(driver, employee_id, role_title):
    """Create HAS_ROLE relationship between Employee and Role."""
    with driver.session() as session:
        session.run(
            'MATCH (a:Employee {id: $emp_id}), (r:Role {title: $role_title}) '
            'CREATE (a)-[:HAS_ROLE]->(r)',
            emp_id=employee_id,
            role_title=role_title
        )


def create_has_skill_relationship(driver, employee_id, skill_name, level=None):
    """Create HAS_SKILL relationship between Employee and Skill."""
    with driver.session() as session:
        if level:
            session.run(
                'MATCH (a:Employee {id: $emp_id}), (s:Skill {name: $skill_name}) '
                'CREATE (a)-[:HAS_SKILL {level: $level}]->(s)',
                emp_id=employee_id,
                skill_name=skill_name,
                level=level
            )
        else:
            session.run(
                'MATCH (a:Employee {id: $emp_id}), (s:Skill {name: $skill_name}) '
                'CREATE (a)-[:HAS_SKILL]->(s)',
                emp_id=employee_id,
                skill_name=skill_name
            )


def create_reports_to_relationship(driver, employee_id, manager_id):
    """Create REPORTS_TO relationship between Employee and Manager."""
    with driver.session() as session:
        session.run(
            'MATCH (a:Employee {id: $emp_id}), (b:Employee {id: $mgr_id}) '
            'CREATE (a)-[:REPORTS_TO]->(b)',
            emp_id=employee_id,
            mgr_id=manager_id
        )
