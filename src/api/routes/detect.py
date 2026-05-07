from fastapi import APIRouter
import joblib

from src.api.db import get_logs
from src.detection.engine import run_detection
from src.ml.features.feature_builder import build_feature_dataset

router = APIRouter()

# 🔥 Load trained model + baselines ONCE
MODEL = joblib.load("model.pkl")
BASELINES = joblib.load("baselines.pkl")
FEATURE_COLUMNS = joblib.load("feature_columns.pkl")

@router.post("/detect")
def run_inference():
    # -----------------------------
    # Step 1: get logs from DB
    # -----------------------------
    EVENT_STORE = get_logs()

    if not EVENT_STORE:
        return {"error": "No logs ingested"}

    # -----------------------------
    # Step 2: rule-based detection
    # -----------------------------
    detection_output = run_detection(EVENT_STORE)

    # -----------------------------
    # Step 3: feature building
    # -----------------------------
    df = build_feature_dataset(detection_output, BASELINES)

    if df.empty:
        return {"error": "No features generated"}

    # -----------------------------
    # Step 4: prepare features
    # -----------------------------
    X = df.drop(columns=["label", "user"], errors="ignore")

    # 🔥 ADD missing columns
    for col in FEATURE_COLUMNS:
        if col not in X.columns:
            X[col] = 0

    # 🔥 REMOVE extra columns
    X = X[FEATURE_COLUMNS]

    # -----------------------------
    # Step 5: model prediction
    # -----------------------------
    probs = MODEL.predict_proba(X)[:, 1]
    preds = (probs >= 0.5).astype(int)

    # -----------------------------
    # Step 6: attach results
    # -----------------------------
    df["prediction"] = preds
    df["probability"] = probs

    # -----------------------------
    # Step 7: extract anomalies
    # -----------------------------
    anomalies = df[df["prediction"] == 1].to_dict(orient="records")

    # -----------------------------
    # Step 8: return response
    # -----------------------------
    return {
        "message": "Inference completed",
        "total_records": len(df),
        "total_anomalies": len(anomalies),
        "anomalies": anomalies[:20]  # limit output
    }