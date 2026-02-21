from kafka import KafkaConsumer, KafkaProducer
import json
import psycopg2
import joblib
import os
import pandas as pd
import redis

from ml.features import engineer_features

print("🚀 Starting Risk Stream Processor...")

# ----------------------------
# Load Model + Encoders + Features
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "ml")

model = joblib.load(os.path.join(MODEL_PATH, "fraud_model.pkl"))
le_location = joblib.load(os.path.join(MODEL_PATH, "le_location.pkl"))
le_device = joblib.load(os.path.join(MODEL_PATH, "le_device.pkl"))
feature_columns = joblib.load(os.path.join(MODEL_PATH, "features.pkl"))

print("✅ ML Model Loaded.")
print("📊 Feature Columns:", feature_columns)

# ----------------------------
# Kafka Consumer
# ----------------------------
consumer = KafkaConsumer(
    "financial_transactions",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="risk-consumer-v5",
)

print("✅ Connected to Kafka.")

# ----------------------------
# Kafka Producer (for predictions + alerts)
# ----------------------------
prediction_producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

print("✅ Prediction Producer Ready.")

# ----------------------------
# PostgreSQL Connection
# ----------------------------
conn = psycopg2.connect(
    host="localhost",
    port="5433",
    database="riskdb",
    user="prem",
    password="prem",
)

cursor = conn.cursor()
print("✅ Connected to PostgreSQL.")

# ----------------------------
# Redis Connection
# ----------------------------
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
print("✅ Connected to Redis.")

# ----------------------------
# Streaming Loop
# ----------------------------
for message in consumer:

    transaction = message.value
    print("\n📥 Incoming TX:", transaction)

    try:
        # Convert to DataFrame
        input_df = pd.DataFrame([transaction])

        # Apply feature engineering
        input_df = engineer_features(input_df)

        # Encode categorical features
        input_df["location"] = le_location.transform(input_df["location"])
        input_df["device"] = le_device.transform(input_df["device"])

        # Ensure correct feature order
        input_df = input_df[feature_columns]

        print("🔎 Model Input:")
        print(input_df)

        # Predict probability
        probability = model.predict_proba(input_df)[0][1]
        probability = float(probability)

        risk_score = round(probability, 2)
        is_fraud = bool(probability > 0.5)

        print(f"📊 Probability: {probability}")

        # ----------------------------
        # Publish Prediction Event
        # ----------------------------
        prediction_producer.send(
            "fraud_predictions",
            {
                "user_id": transaction["user_id"],
                "risk_score": risk_score,
                "is_fraud": is_fraud,
                "timestamp": transaction["timestamp"],
            },
        )

        # ----------------------------
        # High-Risk Handling
        # ----------------------------
        if risk_score > 0.8:
            print("⚠ High Risk Detected — Publishing Alert + Writing to Redis")

            prediction_producer.send("fraud_alerts", transaction)

            # Redis with TTL (5 minutes)
            r.setex(f"fraud_user:{transaction['user_id']}", 300, risk_score)

            print("✔ Alert published & cached in Redis")

        # ----------------------------
        # Insert into PostgreSQL
        # ----------------------------
        cursor.execute(
            """
            INSERT INTO transactions
            (user_id, amount, location, device, is_fraud, risk_score)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                int(transaction["user_id"]),
                float(transaction["amount"]),
                str(transaction["location"]),
                str(transaction["device"]),
                bool(is_fraud),
                float(risk_score),
            ),
        )

        conn.commit()

        print(f"✅ Processed TX | Risk: {risk_score} | Fraud: {is_fraud}")

    except Exception as e:
        print("❌ Processing Error:", e)
        continue
