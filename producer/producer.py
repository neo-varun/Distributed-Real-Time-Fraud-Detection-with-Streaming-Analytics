import json
import time
import random
from kafka import KafkaProducer
from faker import Faker
from datetime import datetime

fake = Faker()

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

users = [f"USER_{i}" for i in range(1000)]

devices = [f"DEV_{i}" for i in range(2000)]

transaction_count = 0

while True:

    fraud = 1 if random.random() < 0.05 else 0

    if fraud == 0:

        amount = round(random.uniform(100, 5000), 2)

        device = random.choice(devices)

        txn_type = random.choice(["UPI", "CARD", "NET_BANKING", "WALLET"])

    else:

        amount = round(random.uniform(10000, 100000), 2)

        device = f"SUSPICIOUS_" f"{random.randint(1,100)}"

        txn_type = random.choice(["CARD", "INTERNATIONAL_TRANSFER"])

    transaction = {
        "transaction_id": f"TXN_{transaction_count}",
        "user_id": random.choice(users),
        "amount": amount,
        "device_id": device,
        "ip_address": fake.ipv4(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "merchant": fake.company(),
        "location": fake.city(),
        "transaction_type": txn_type,
    }

    producer.send("transactions", value=transaction)

    print(transaction)

    transaction_count += 1

    time.sleep(1)
