import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

NUM_TRANSACTIONS = 50000
FRAUD_RATIO = 0.05

transactions = []

users = [f"USER_{i}" for i in range(1000)]
devices = [f"DEV_{i}" for i in range(2000)]

base_time = datetime.now()

for i in range(NUM_TRANSACTIONS):

    user = random.choice(users)

    fraud = 1 if random.random() < FRAUD_RATIO else 0

    if fraud == 0:
        amount = round(np.random.normal(2000, 500), 2)
        device = random.choice(devices)
        ip = fake.ipv4()
        txn_type = random.choice(["UPI", "CARD", "NET_BANKING", "WALLET"])

    else:
        amount = round(np.random.uniform(10000, 100000), 2)
        device = f"SUSPICIOUS_{random.randint(1,100)}"
        ip = fake.ipv4_public()
        txn_type = random.choice(["CARD", "INTERNATIONAL_TRANSFER"])

    transaction = {
        "transaction_id": f"TXN_{i}",
        "user_id": user,
        "amount": amount,
        "device_id": device,
        "ip_address": ip,
        "timestamp": (base_time + timedelta(seconds=i)).strftime("%Y-%m-%d %H:%M:%S"),
        "merchant": fake.company(),
        "location": fake.city(),
        "transaction_type": txn_type,
        "fraud_label": fraud,
    }

    transactions.append(transaction)

df = pd.DataFrame(transactions)

df.to_csv("../data/transactions.csv", index=False)

print(df.head())
