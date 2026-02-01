def assess_risk(features):
    if features["engagement"] == "low":
        return {
            "risk": "burnout",
            "priority": "high",
            "confidence": 0.7
        }
    return {
        "risk": "none",
        "priority": "low",
        "confidence": 0.9
    }

