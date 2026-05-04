from collections import defaultdict
from src.sequence.builder import build_sequences

# in-memory store
EVENT_STORE = []
SEQUENCE_STORE = {}

def ingest_events(events):
    global EVENT_STORE, SEQUENCE_STORE

    EVENT_STORE.extend(events)

    # rebuild sequences
    SEQUENCE_STORE = build_sequences(EVENT_STORE)

    return {
        "total_events": len(EVENT_STORE),
        "total_users": len(SEQUENCE_STORE)
    }

def get_sequences():
    return SEQUENCE_STORE