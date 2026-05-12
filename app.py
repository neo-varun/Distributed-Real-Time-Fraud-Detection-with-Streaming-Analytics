import os
import sys
import subprocess
import streamlit as st
import pandas as pd
import joblib
import json
from kafka import KafkaConsumer
from consumer.risk_scoring import calculate_risk_score

os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

st.set_page_config(page_title="Real-Time Fraud Detection", layout="wide")

DATASET_PATH = "data/transactions.csv"

MODEL_PATH = "models/fraud_model.pkl"

if not os.path.exists(DATASET_PATH):
    subprocess.run([sys.executable, "generate_dataset.py"], cwd="producer")

if not os.path.exists(MODEL_PATH):
    subprocess.run([sys.executable, "train_model.py"], cwd="models")

subprocess.Popen([sys.executable, "producer.py"], cwd="producer")

model = joblib.load(MODEL_PATH)

st.title("Distributed Real-Time Fraud Detection")

consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
)

if "live_transactions" not in st.session_state:
    st.session_state.live_transactions = []

if "high_risk_transactions" not in st.session_state:
    st.session_state.high_risk_transactions = []

transaction_placeholder = st.empty()

high_risk_placeholder = st.empty()

metrics_placeholder = st.empty()

fraud_chart_placeholder = st.empty()

risk_chart_placeholder = st.empty()

fraud_probabilities = []

risk_scores = []

for message in consumer:

    transaction = message.value

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

    risk_score = calculate_risk_score(probability, 0.5, transaction["amount"])

    transaction["fraud_probability"] = round(probability, 2)

    transaction["risk_score"] = round(risk_score, 2)

    transaction["prediction"] = "FRAUD" if prediction == 1 else "NORMAL"

    fraud_probabilities.append(probability)

    risk_scores.append(risk_score)

    st.session_state.live_transactions.append(transaction)

    st.session_state.live_transactions = st.session_state.live_transactions[-10:]

    if risk_score > 70:

        st.session_state.high_risk_transactions.append(transaction)

    live_df = pd.DataFrame(st.session_state.live_transactions)

    high_risk_df = pd.DataFrame(st.session_state.high_risk_transactions)

    total_transactions = len(fraud_probabilities)

    fraud_count = len(high_risk_df)

    normal_count = total_transactions - fraud_count

    with metrics_placeholder.container():

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Transactions", total_transactions)

        col2.metric("Fraud Transactions", fraud_count)

        col3.metric("Normal Transactions", normal_count)

    with transaction_placeholder.container():

        st.subheader("Live Transaction Stream")

        st.dataframe(live_df, width="content")

    with high_risk_placeholder.container():

        st.subheader("High Risk Transactions")

        st.dataframe(high_risk_df, width="content")

    with fraud_chart_placeholder.container():

        st.subheader("Fraud Probability Distribution")

        st.bar_chart(fraud_probabilities)

    with risk_chart_placeholder.container():

        st.subheader("Risk Score Distribution")

        st.line_chart(risk_scores)
