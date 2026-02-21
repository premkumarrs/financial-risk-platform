# 🚀 Real-Time Financial Fraud Detection Platform

An end-to-end real-time fraud detection system built using modern data engineering and machine learning tools.

This project simulates how financial institutions detect, score, and monitor fraudulent transactions in real time.

---

## 📌 Project Overview

The system ingests transaction data, applies a trained ML model to calculate fraud risk scores, stores results in a database, and displays live analytics via a dashboard.

It demonstrates the complete ML lifecycle:

Training → Experiment Tracking → Model Serving → API Layer → Real-Time Monitoring

---

## 🏗 System Architecture

```
Transaction Generator
        ↓
Stream Processor (ML Model)
        ↓
PostgreSQL (Transaction Storage)
        ↓
FastAPI Backend (Analytics APIs)
        ↓
Redis (Live High-Risk Cache)
        ↓
Streamlit Dashboard (Visualization)
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Programming Language | Python |
| Machine Learning | XGBoost |
| Model Tracking | MLflow |
| Backend API | FastAPI |
| Database | PostgreSQL |
| Cache | Redis |
| Dashboard | Streamlit |
| Streaming Logic | Kafka-style simulation |

---

## 📁 Project Structure

```
real-time-fraud-detection-platform/
│
├── api/                  # FastAPI backend
├── consumer/             # Stream processing & scoring
├── producer/             # Transaction generator
├── dashboard/            # Streamlit dashboard
├── ml/                   # Model training & feature engineering
├── data/                 # Dataset
├── docker/               # Docker configuration (optional)
├── screenshots/          # Project screenshots
├── requirements.txt
└── README.md
```

---

## 🧠 Machine Learning Model

Model Type: XGBoost Classifier  
Tracked with: MLflow  

### Example Model Performance:

- Accuracy: 96.9%
- Precision: 1.00
- Recall: 0.81
- AUC: 0.92

The model is trained and logged using MLflow to track:
- Parameters
- Metrics
- Artifacts
- Experiment runs

---

## 🚀 How To Run The Project

### 1️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 2️⃣ Start Backend API

```
uvicorn api.main:app --reload
```

Access Swagger Docs:

```
http://127.0.0.1:8000/docs
```

---

### 3️⃣ Start Dashboard

```
streamlit run dashboard/app.py
```

Access:

```
http://localhost:8501
```

---

### 4️⃣ Start MLflow UI

```
mlflow ui --port 5000
```

Access:

```
http://127.0.0.1:5000
```

---

## 🎯 Key Features

- Real-time fraud risk scoring
- RESTful analytics API
- Experiment tracking with MLflow
- Live high-risk user monitoring via Redis
- Professional dashboard with metrics & visualizations
- Clean modular architecture

