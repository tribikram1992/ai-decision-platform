"""Neo4j Database Connection and Initialization Module.

This module handles:
1. Loading credentials from environment file
2. Establishing connection to Neo4j database
3. Initializing database with schema and sample data
4. Providing connection management utilities
"""

import dotenv
import os
from neo4j import GraphDatabase

# Global driver instance
driver = None
_connection_initialized = False
_connection_error = None


def _load_credentials():
    """Load Neo4j credentials from environment file.
    
    Returns:
        tuple: (uri, username, password) or (None, None, None) if failed
    """
    global _connection_error
    
    # Try multiple possible paths for the credentials file
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "../connection/Neo4j-165925b5-Created-2026-02-01.txt"),
        "src/connection/Neo4j-165925b5-Created-2026-02-01.txt",
        "../connection/Neo4j-165925b5-Created-2026-02-01.txt",
        "connection/Neo4j-165925b5-Created-2026-02-01.txt",
    ]
    
    cred_file = None
    for path in possible_paths:
        if os.path.exists(path):
            cred_file = path
            break
    
    if not cred_file:
        _connection_error = f"Credentials file not found in any of these locations: {possible_paths}"
        return None, None, None
    
    try:
        load_status = dotenv.load_dotenv(cred_file)
        
        if not load_status:
            _connection_error = f"Failed to load credentials from: {cred_file}"
            return None, None, None
        
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not all([uri, username, password]):
            _connection_error = "Missing required environment variables (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)"
            return None, None, None
        
        return uri, username, password
    
    except Exception as e:
        _connection_error = f"Error loading credentials: {str(e)}"
        return None, None, None


def connect_to_db():
    """Establish connection to Neo4j database.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    global driver, _connection_initialized, _connection_error
    
    if _connection_initialized:
        return driver is not None
    
    uri, username, password = _load_credentials()
    
    if not all([uri, username, password]):
        print(f"⚠️  Neo4j Connection Failed: {_connection_error}")
        _connection_initialized = True
        return False
    
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        print("✓ Neo4j Connection established successfully.")
        _connection_initialized = True
        return True
    
    except Exception as e:
        _connection_error = f"Could not connect to Neo4j: {str(e)}"
        print(f"⚠️  Neo4j Connection Failed: {_connection_error}")
        driver = None
        _connection_initialized = True
        return False


def get_driver():
    """Get the Neo4j driver instance.
    
    Returns:
        GraphDatabase.driver or None if not connected
    """
    global driver
    
    if not _connection_initialized:
        connect_to_db()
    
    return driver


def is_connected():
    """Check if database is connected.
    
    Returns:
        bool: True if connected, False otherwise
    """
    global driver
    return driver is not None


def disconnect_db():
    """Close database connection."""
    global driver, _connection_initialized
    
    if driver:
        try:
            driver.close()
            print("✓ Neo4j Connection closed.")
        except Exception as e:
            print(f"Error closing connection: {e}")
        finally:
            driver = None
            _connection_initialized = False
    else:
        print("No active connection to close.")



# Initialize database with nodes and relationships
def check_db_initialized():
    """Check if database has been initialized with schema.
    
    Returns:
        bool: True if schema exists, False otherwise
    """
    db = get_driver()
    if not db:
        return False
    
    try:
        with db.session() as session:
            result = session.run("MATCH (n:Employee) RETURN COUNT(n) as count")
            count = result.single()[0]
            return count > 0
    except Exception as e:
        print(f"Error checking database: {e}")
        return False


def init_db(clear_first=False):
    """Initialize database with schema and sample data.
    
    Args:
        clear_first (bool): If True, clear all existing data before initialization
    
    Returns:
        dict: Status information {"success": bool, "message": str}
    """
    from .neo4j_client import (
        clear_all,
        create_department, create_role, create_skill, create_employee,
        create_works_in_relationship, create_has_role_relationship,
        create_has_skill_relationship, create_reports_to_relationship
    )
    
    # Ensure connection exists
    db = get_driver()
    if not db:
        return {"success": False, "message": "Database not connected. Cannot initialize."}
    
    try:
        # Clear existing data if requested
        if clear_first:
            print("Clearing existing data...")
            clear_all(db)
            print("✓ Database cleared")
        
        # Create Departments
        create_department(db, "D1", "Engineering")
        create_department(db, "D2", "HR")
        create_department(db, "D3", "Sales")
        print("✓ Departments created")
        
        # Create Roles
        create_role(db, "R1", "Software Engineer")
        create_role(db, "R2", "Engineering Manager")
        create_role(db, "R3", "HR Manager")
        create_role(db, "R4", "Sales Executive")
        print("✓ Roles created")
        
        # Create Skills
        create_skill(db, "Python")
        create_skill(db, "Neo4j")
        create_skill(db, "Leadership")
        create_skill(db, "Recruitment")
        create_skill(db, "Negotiation")
        print("✓ Skills created")
        
        # Create Employees
        create_employee(db, "E1", "Alice", "Senior")
        create_employee(db, "E2", "Bob", "Manager")
        create_employee(db, "E3", "Carol", "Senior")
        create_employee(db, "E4", "David", "Junior")
        print("✓ Employees created")
        
        # Create WORKS_IN relationships
        create_works_in_relationship(db, "E1", "Engineering")
        create_works_in_relationship(db, "E2", "Engineering")
        create_works_in_relationship(db, "E3", "HR")
        create_works_in_relationship(db, "E4", "Sales")
        print("✓ WORKS_IN relationships created")
        
        # Create HAS_ROLE relationships
        create_has_role_relationship(db, "E1", "Software Engineer")
        create_has_role_relationship(db, "E2", "Engineering Manager")
        create_has_role_relationship(db, "E3", "HR Manager")
        create_has_role_relationship(db, "E4", "Sales Executive")
        print("✓ HAS_ROLE relationships created")
        
        # Create HAS_SKILL relationships
        create_has_skill_relationship(db, "E1", "Python", "Advanced")
        create_has_skill_relationship(db, "E1", "Neo4j", "Intermediate")
        create_has_skill_relationship(db, "E2", "Leadership")
        create_has_skill_relationship(db, "E3", "Recruitment")
        create_has_skill_relationship(db, "E4", "Negotiation")
        print("✓ HAS_SKILL relationships created")
        
        # Create REPORTS_TO relationship
        create_reports_to_relationship(db, "E1", "E2")
        print("✓ REPORTS_TO relationship created")
        
        print("\n✓ Database initialization complete!")
        return {"success": True, "message": "Database initialized successfully"}
    
    except Exception as e:
        error_msg = f"Database initialization failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {"success": False, "message": error_msg}
