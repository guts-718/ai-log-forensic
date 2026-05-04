import pandas as pd

def normalize_events(events):
    for e in events:
        # Convert timestamp
        e["timestamp"] = pd.to_datetime(e["timestamp"])
    return events