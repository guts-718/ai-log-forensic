from fastapi import APIRouter
from typing import List
from src.api.state import EVENT_STORE

router = APIRouter()

@router.post("/ingest")
def ingest_logs(logs: List[dict]):
    EVENT_STORE.extend(logs)

    return {
        "message": "Logs ingested successfully",
        "total_events": len(EVENT_STORE)
    }