import pandas as pd
import numpy as np
import os
import joblib
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score
from xgboost import XGBClassifier

from features import engineer_features

# --------------------------------------------------
# Paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "transactions_dataset.csv")

# --------------------------------------------------
# Load Data
# --------------------------------------------------
df = pd.read_csv(DATA_PATH)
print("✅ Dataset loaded:", df.shape)

# --------------------------------------------------
# Feature Engineering
# --------------------------------------------------
df = engineer_features(df)

# Encode categorical columns
le_location = LabelEncoder()
le_device = LabelEncoder()

df["location"] = le_location.fit_transform(df["location"])
df["device"] = le_device.fit_transform(df["device"])

feature_columns = [
    "amount",
    "amount_log",
    "location",
    "device",
    "high_amount_flag",
    "is_foreign",
    "is_atm",
]

X = df[feature_columns]
y = df["is_fraud"]

# --------------------------------------------------
# Train/Test Split
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------------------------------------
# MLflow Setup
# --------------------------------------------------
mlflow.set_experiment("Fraud Detection")

with mlflow.start_run():

    print("🚀 Training XGBoost model...")

    model = XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1, eval_metric="logloss"
    )

    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)

    print(f"Accuracy: {accuracy}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"AUC: {auc}")

    # --------------------------------------------------
    # Log Parameters
    # --------------------------------------------------
    mlflow.log_param("model_type", "XGBoost")
    mlflow.log_param("n_estimators", 200)
    mlflow.log_param("max_depth", 6)
    mlflow.log_param("learning_rate", 0.1)

    # --------------------------------------------------
    # Log Metrics
    # --------------------------------------------------
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("auc", auc)

    # --------------------------------------------------
    # Log Model
    # --------------------------------------------------
    mlflow.sklearn.log_model(model, "fraud_model")

# --------------------------------------------------
# Save Artifacts Locally
# --------------------------------------------------
joblib.dump(model, os.path.join(BASE_DIR, "fraud_model.pkl"))
joblib.dump(le_location, os.path.join(BASE_DIR, "le_location.pkl"))
joblib.dump(le_device, os.path.join(BASE_DIR, "le_device.pkl"))
joblib.dump(feature_columns, os.path.join(BASE_DIR, "features.pkl"))

print("✅ Model + Encoders + Features saved successfully.")
print("🔥 MLflow run completed.")
