from fastapi import APIRouter
import joblib
import json
from src.api.db import cursor, conn

from src.api.db import get_logs
from src.detection.engine import run_detection
from src.ml.features.feature_builder import build_feature_dataset
from src.api.db import clear_anomalies

router = APIRouter()

# load once
MODEL = joblib.load("model.pkl")
BASELINES = joblib.load("baselines.pkl")
FEATURE_COLUMNS = joblib.load("feature_columns.pkl")


def get_risk(probability: float) -> str:
    if probability >= 0.8:
        return "HIGH"
    elif probability >= 0.5:
        return "MEDIUM"
    return "LOW"



@router.post("/predict")
def predict_anomalies():
    EVENT_STORE = get_logs()

    if not EVENT_STORE:
        return {"error": "No logs available"}

    # Step 1 — rule engine (for feature building)
    detection_output = run_detection(EVENT_STORE)

    # Step 2 — features
    df = build_feature_dataset(detection_output, BASELINES)

    if df.empty:
        return {"error": "No features generated"}

    X = df.drop(columns=["label", "user"], errors="ignore")

    # 🔥 ADD missing columns
    for col in FEATURE_COLUMNS:
        if col not in X.columns:
            X[col] = 0

    # 🔥 REMOVE extra columns
    X = X[FEATURE_COLUMNS]

    # Step 3 — ML inference
    probs = MODEL.predict_proba(X)[:, 1]
    preds = (probs >= 0.35).astype(int)   # use your tuned threshold

    df["prediction"] = preds
    df["probability"] = probs

    anomaly_rows = df[df["prediction"] == 1]

    anomalies = []
    # remove previous prediction results
    clear_anomalies()
    for _, row in anomaly_rows.iterrows():
        record = row.to_dict()
        record["reasons"] = explain_anomaly(row)
        anomalies.append(record)

        cursor.execute(
    """
    INSERT INTO anomalies (user, probability, risk, reasons)
    VALUES (?, ?, ?, ?)
    """,
    (
        record.get("user"),
        float(record.get("probability", 0)),
        get_risk(record.get("probability", 0)),
        json.dumps(record.get("reasons", []))
    )
    )

    conn.commit()


    return {
        "total_records": len(df),
        "total_anomalies": len(anomalies),
        "anomalies": anomalies[:20] # type: ignore
    }

def explain_anomaly(row):
    reasons = []

    if row.get("file_dev_norm", 0) > 2:
        reasons.append("Unusual file activity")

    if row.get("device_count", 0) > 2:
        reasons.append("Multiple device interactions")

    if row.get("burst_ratio", 0) > 0.5:
        reasons.append("Burst activity detected")

    if row.get("event_entropy", 0) > 1.5:
        reasons.append("High behavioral randomness")

    return reasons