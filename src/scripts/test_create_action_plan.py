import sys
sys.path.insert(0, 'src')
from decisions.neo4j_database import get_driver
from decisions.core import create_action_plan
import json

driver = get_driver()
print('Driver:', 'available' if driver else 'None')
plan = create_action_plan(driver, 'E1', 'low')
print('RESULT:')
print(json.dumps(plan, indent=2))
