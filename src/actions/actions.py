def decide_action(decision):
    if decision["priority"] == "high":
        return "Notify manager"
    return "Observe"
