from fastapi import APIRouter
from src.api.state import EVENT_STORE

router = APIRouter()

@router.get("/search")
def search_logs(user: str = None, event_type: str = None): # type: ignore 
    results = EVENT_STORE

    if user:
        results = [e for e in results if e["user"] == user]

    if event_type:
        results = [e for e in results if e["event_type"] == event_type]

    return {
        "count": len(results),
        "results": results[:100]  # limit for safety
    }