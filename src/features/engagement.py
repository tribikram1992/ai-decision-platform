def engagement_level(score):
    if score <= 2:
        return "low"
    elif score == 3:
        return "medium"
    return "high"

def compute_engagement(df):
    df["engagement"] = df["score"].apply(engagement_level)
    return df
