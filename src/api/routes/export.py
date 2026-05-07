from fastapi import APIRouter
from fastapi.responses import FileResponse
import pandas as pd
import joblib
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from src.api.db import get_logs
from src.detection.engine import run_detection
from src.ml.features.feature_builder import build_feature_dataset

router = APIRouter()

# load assets
MODEL = joblib.load("model.pkl")
BASELINES = joblib.load("baselines.pkl")
FEATURE_COLUMNS = joblib.load("feature_columns.pkl")


# -----------------------------
# Helper: get anomalies
# -----------------------------
def get_anomaly_dataframe():
    EVENT_STORE = get_logs()

    if not EVENT_STORE:
        return None

    detection_output = run_detection(EVENT_STORE)
    df = build_feature_dataset(detection_output, BASELINES)

    if df.empty:
        return None

    X = df.drop(columns=["label", "user"], errors="ignore")

    # align features
    for col in FEATURE_COLUMNS:
        if col not in X.columns:
            X[col] = 0

    X = X[FEATURE_COLUMNS]

    probs = MODEL.predict_proba(X)[:, 1]
    preds = (probs >= 0.35).astype(int)

    df["prediction"] = preds
    df["probability"] = probs

    anomalies = df[df["prediction"] == 1]

    return anomalies


# -----------------------------
# CSV EXPORT
# -----------------------------
@router.get("/export/csv")
def export_csv():
    anomalies = get_anomaly_dataframe()

    if anomalies is None or anomalies.empty:
        return {"error": "No anomalies found"}

    file_path = "anomaly_report.csv"

    anomalies.to_csv(file_path, index=False)

    return FileResponse(
        file_path,
        media_type="text/csv",
        filename="anomaly_report.csv"
    )


# -----------------------------
# PDF EXPORT
# -----------------------------
@router.get("/export/pdf")
def export_pdf():
    anomalies = get_anomaly_dataframe()

    if anomalies is None or anomalies.empty:
        return {"error": "No anomalies found"}

    file_path = "anomaly_report.pdf"

    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Anomaly Detection Report", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Total Anomalies: {len(anomalies)}", styles["Normal"]))
    content.append(Spacer(1, 12))

    # add top anomalies
    for i, (_, row) in enumerate(anomalies.head(10).iterrows()):
        text = f"""
        User: {row.get('user')} <br/>
        Probability: {round(row.get('probability', 0), 3)} <br/>
        File Count: {row.get('file_count', 0)} <br/>
        Device Count: {row.get('device_count', 0)} <br/>
        """
        content.append(Paragraph(text, styles["Normal"]))
        content.append(Spacer(1, 10))

    doc.build(content)

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename="anomaly_report.pdf"
    )