from fastapi import APIRouter
from src.api.state import DETECTION_RESULTS

router = APIRouter()

@router.get("/anomalies")
def get_anomalies():
    if "output" not in DETECTION_RESULTS:
        return {"error": "Run detection first"}

    output = DETECTION_RESULTS["output"]

    anomalies = []

    for user, data in output.items():
        for window in data["windows"]:
            if window["risk_level"] in ["MEDIUM", "HIGH"]:
                anomalies.append({
                    "user": user,
                    "window_id": window["window_id"],
                    "risk": window["risk_level"],
                    "score": window["score"]
                })

    return {
        "total_anomalies": len(anomalies),
        "anomalies": anomalies
    }