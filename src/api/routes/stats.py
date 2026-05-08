from fastapi import APIRouter
from src.api.db import cursor

router = APIRouter()

@router.get("/stats")
def get_stats():

    total_logs = cursor.execute(
        "SELECT COUNT(*) FROM logs"
    ).fetchone()[0]

    total_anomalies = cursor.execute(
        "SELECT COUNT(*) FROM anomalies"
    ).fetchone()[0]

    high_risk = cursor.execute(
        "SELECT COUNT(*) FROM anomalies WHERE probability >= 0.8"
    ).fetchone()[0]

    users = cursor.execute(
        "SELECT COUNT(DISTINCT user) FROM anomalies"
    ).fetchone()[0]

    return {
        "total_logs": total_logs,
        "total_anomalies": total_anomalies,
        "high_risk_events": high_risk,
        "users_investigated": users
    }