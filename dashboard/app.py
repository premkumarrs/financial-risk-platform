import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# ---------------------------------
# CONFIG
# ---------------------------------
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Fraud Monitoring Dashboard", layout="wide")

# Auto refresh every 5 seconds
st_autorefresh(interval=5000, key="datarefresh")

st.title("💳 Financial Risk Intelligence Dashboard")

# ---------------------------------
# LOAD GLOBAL STATS
# ---------------------------------
try:
    stats = requests.get(f"{API_URL}/stats").json()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Transactions", stats["total_transactions"])
    col2.metric("Fraud Transactions", stats["fraud_transactions"])
    col3.metric("Fraud Rate (%)", stats["fraud_rate_percent"])

except Exception:
    st.error("API not reachable. Make sure FastAPI server is running.")
    st.stop()

st.divider()

# ---------------------------------
# RECENT FRAUD ALERTS
# ---------------------------------
st.subheader("🚨 Recent Fraud Alerts")

fraud_data = requests.get(f"{API_URL}/fraud-alerts").json()

if fraud_data:
    df = pd.DataFrame(fraud_data)
    st.dataframe(df, use_container_width=True)

    # Risk Score Distribution (Matplotlib)
    st.subheader("Risk Score Distribution")

    fig1, ax = plt.subplots()
    ax.hist(df["risk_score"], bins=10)
    ax.set_xlabel("Risk Score")
    ax.set_ylabel("Frequency")

    st.pyplot(fig1)

    # Top Fraud Risk Scores (Plotly)
    st.subheader("Top Fraud Risk Scores")

    fig2 = px.bar(
        df.head(20),
        x="user_id",
        y="risk_score",
        color="risk_score",
        title="Top Fraud Risk Scores",
    )

    st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("No fraud alerts yet.")

st.divider()

# ---------------------------------
# LIVE HIGH RISK USERS (REDIS)
# ---------------------------------
st.subheader("⚡ Live High Risk Users (Redis)")

try:
    live = requests.get(f"{API_URL}/live_high_risk").json()
    live_df = pd.DataFrame(live)

    if not live_df.empty:
        st.dataframe(live_df, use_container_width=True)
    else:
        st.success("No high-risk users in Redis cache.")

except Exception:
    st.warning("Redis endpoint not reachable.")

st.success("🟢 System Running: Kafka + ML + API Active")
