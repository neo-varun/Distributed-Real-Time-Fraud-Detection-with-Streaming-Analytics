def calculate_risk_score(fraud_probability, velocity, amount):

    amount_risk = min(amount / 100000, 1)

    score = fraud_probability * 50 + velocity * 30 + amount_risk * 20

    return round(score, 2)
