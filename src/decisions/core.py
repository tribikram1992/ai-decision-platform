from .rules import assess_risk

def make_decision(employee_features):
	return assess_risk(employee_features)

