from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

print("🚀 Starting Financial Transaction Generator...")

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# Valid categories (must match training data)
locations = ["New York", "London", "Mumbai", "Singapore", "Berlin"]
devices = ["Mobile", "Web", "ATM", "POS"]
transaction_types = ["Payment", "Transfer", "Withdrawal", "Deposit"]

while True:
    # -----------------------------
    # Normal Random Transaction
    # -----------------------------
    transaction = {
        "user_id": random.randint(1, 500),
        "amount": round(random.uniform(10, 20000), 2),
        "location": random.choice(locations),
        "device": random.choice(devices),
        "transaction_type": random.choice(transaction_types),
        "timestamp": datetime.utcnow().isoformat(),
    }

    producer.send("financial_transactions", value=transaction)
    print("Sent Normal:", transaction)

    # -----------------------------
    # Controlled High-Risk Injection
    # -----------------------------
    high_risk_transaction = {
        "user_id": 999,
        "amount": 50000,  # Very high amount
        "location": "London",  # MUST be valid label
        "device": "ATM",
        "transaction_type": "Withdrawal",
        "timestamp": datetime.utcnow().isoformat(),
    }

    producer.send("financial_transactions", value=high_risk_transaction)
    print("🔥 Sent High-Risk:", high_risk_transaction)

    producer.flush()

    time.sleep(2)
