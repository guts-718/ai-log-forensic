def detect_file_spike(events):
    files = [e for e in events if e["event_type"] == "file"]

    if len(files) > 20:
        return {
            "rule": "file_spike",
            "category": "data_access",
            "score": 2
        }