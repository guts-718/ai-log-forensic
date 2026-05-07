from fastapi import APIRouter
from typing import List
from src.api.state import EVENT_STORE
from src.api.db import insert_log

router = APIRouter()

@router.post("/ingest")
def ingest_logs(logs: List[dict]):
    for log in logs:
        insert_log(log)
    return {"message": "Stored in DB"}
   