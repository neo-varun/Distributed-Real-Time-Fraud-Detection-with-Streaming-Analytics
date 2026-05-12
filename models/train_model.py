import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from xgboost import XGBClassifier
import joblib

df = pd.read_csv("../data/transactions.csv")

df["is_high_amount"] = (df["amount"] > 10000).astype(int)

df["is_suspicious_device"] = (df["device_id"].str.contains("SUSPICIOUS")).astype(int)

X = df[["amount", "is_high_amount", "is_suspicious_device"]]

y = df["fraud_label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = XGBClassifier(
    n_estimators=200, max_depth=6, learning_rate=0.1, eval_metric="logloss"
)

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print(classification_report(y_test, predictions))

joblib.dump(model, "fraud_model.pkl")
