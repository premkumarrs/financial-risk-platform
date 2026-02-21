import os
import logging
import psycopg2
import redis
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

# ==============================
# Load Environment Variables
# ==============================
load_dotenv()

# ==============================
# Logging Setup
# ==============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fraud_api")

logger.info("Starting Financial Risk Intelligence API...")

# ==============================
# App Initialization
# ==============================
app = FastAPI(title="Financial Risk Intelligence API")


# ==============================
# Database Connection
# ==============================
def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


# ==============================
# Redis Connection (Global)
# ==============================
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=os.getenv("REDIS_PORT", 6379),
    decode_responses=True,
)


# ==============================
# Health Check
# ==============================
@app.get("/health")
def health():
    return {"status": "API running"}


# ==============================
# Global Stats
# ==============================
@app.get("/stats")
def get_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM transactions;")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM transactions WHERE is_fraud = TRUE;")
    fraud_count = cursor.fetchone()[0]

    fraud_rate = round((fraud_count / total) * 100, 2) if total > 0 else 0

    conn.close()

    return {
        "total_transactions": total,
        "fraud_transactions": fraud_count,
        "fraud_rate_percent": fraud_rate,
    }


# ==============================
# Recent Fraud Alerts
# ==============================
@app.get("/fraud-alerts")
def get_fraud_alerts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id, amount, location, device, risk_score
        FROM transactions
        WHERE is_fraud = TRUE
        ORDER BY transaction_id DESC
        LIMIT 20
        """
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "user_id": r[0],
            "amount": float(r[1]),
            "location": r[2],
            "device": r[3],
            "risk_score": float(r[4]),
        }
        for r in rows
    ]


# ==============================
# Fraud by Device
# ==============================
@app.get("/fraud_by_device")
def fraud_by_device():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT device, COUNT(*) 
        FROM transactions
        WHERE is_fraud = TRUE
        GROUP BY device
        """
    )

    data = cursor.fetchall()
    conn.close()

    return [{"device": d[0], "fraud_count": d[1]} for d in data]


# ==============================
# Fraud by Location
# ==============================
@app.get("/fraud_by_location")
def fraud_by_location():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT location, COUNT(*) 
        FROM transactions
        WHERE is_fraud = TRUE
        GROUP BY location
        """
    )

    data = cursor.fetchall()
    conn.close()

    return [{"location": d[0], "fraud_count": d[1]} for d in data]


# ==============================
# Fraud Trend Over Time
# ==============================
@app.get("/fraud_trend")
def fraud_trend():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DATE(timestamp), 
               COUNT(*) as total,
               SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) as fraud_count
        FROM transactions
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp)
        """
    )

    data = cursor.fetchall()
    conn.close()

    return [
        {
            "date": str(d[0]),
            "total_transactions": d[1],
            "fraud_transactions": d[2] if d[2] else 0,
        }
        for d in data
    ]


# ==============================
# Risk Score Distribution
# ==============================
@app.get("/risk_distribution")
def risk_distribution():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT risk_score FROM transactions;")

    data = cursor.fetchall()
    conn.close()

    return [float(d[0]) for d in data]


# ==============================
# Top Risky Users
# ==============================
@app.get("/top_risky_users")
def top_risky_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id, AVG(risk_score) as avg_risk
        FROM transactions
        GROUP BY user_id
        ORDER BY avg_risk DESC
        LIMIT 10
        """
    )

    data = cursor.fetchall()
    conn.close()

    return [{"user_id": d[0], "average_risk": round(float(d[1]), 3)} for d in data]


# ==============================
# Live High Risk (Redis)
# ==============================
@app.get("/live_high_risk")
def live_high_risk():
    keys = redis_client.keys("fraud_user:*")
    results = []

    for key in keys:
        user_id = key.split(":")[1]
        score = redis_client.get(key)
        results.append({"user_id": int(user_id), "risk_score": float(score)})

    return results
