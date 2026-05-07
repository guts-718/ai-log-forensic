from fastapi import APIRouter
from src.api.state import EVENT_STORE

router = APIRouter()

@router.get("/timeline")
def get_timeline(user: str):
    events = [e for e in EVENT_STORE if e["user"] == user]

    events.sort(key=lambda x: x["timestamp"])

    return {
        "user": user,
        "event_count": len(events),
        "timeline": events
    }