import json
import joblib
import pandas as pd
from kafka import KafkaConsumer
from sliding_window import update_window
from risk_scoring import calculate_risk_score
from drift_detection import detect_drift

model = joblib.load("../models/xgboost_fraud_model.pkl")

consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)

for message in consumer:

    transaction = message.value

    velocity = update_window(transaction["user_id"], transaction["timestamp"])

    features = pd.DataFrame(
        [
            {
                "amount": transaction["amount"],
                "is_high_amount": int(transaction["amount"] > 10000),
                "is_suspicious_device": int("SUSPICIOUS" in transaction["device_id"]),
            }
        ]
    )

    prediction = model.predict(features)[0]

    probability = model.predict_proba(features)[0][1]

    risk_score = calculate_risk_score(
        probability, min(velocity / 10, 1), transaction["amount"]
    )

    drift = detect_drift(probability)

    print("=" * 50)

    print("Transaction ID:", transaction["transaction_id"])

    print("Fraud Probability:", round(probability, 2))

    print("Risk Score:", risk_score)

    if prediction == 1:
        print("FRAUD ALERT")

    else:
        print("NORMAL TRANSACTION")

    if drift:
        print("MODEL DRIFT DETECTED")
