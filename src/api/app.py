from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

from src.services.ingestion_service import ingest_events, get_sequences
from src.services.detection_service import detect_anomaly
from src.detection.engine import run_detection
from src.services.ingestion_service import EVENT_STORE


app = FastAPI()


# ------------------------
# Models
# ------------------------

class Event(BaseModel):
    timestamp: str
    user: str
    event_type: str
    resource: str | None = None
    device: str | None = None
    metadata: Dict = {}


# ------------------------
# Endpoints
# ------------------------

@app.get("/")
def root():
    return {"status": "running"}


@app.post("/ingest")
def ingest(events: List[Event]):
    events_dict = [e.dict() for e in events]

    result = ingest_events(events_dict)

    return {
        "message": "ingested",
        "stats": result
    }


@app.get("/users")
def users():
    sequences = get_sequences()
    return {"users": list(sequences.keys())}


@app.get("/detect")
def detect_all():
    return run_detection(EVENT_STORE)

@app.get("/detect/{user}")
def detect(user: str):
    sequences = get_sequences()

    if user not in sequences:
        return {"error": "user not found"}

    result = detect_anomaly(sequences[user])

    return {
        "user": user,
        "result": result
    }