from fastapi import APIRouter

from src.api.db import clear_logs, clear_anomalies

router = APIRouter()


@router.post("/reset")
def reset_system():

    clear_logs()
    clear_anomalies()

    return {
        "message": "System reset successful"
    }