def detect_file_spike(events, baseline):
    file_count = sum(1 for e in events if e["event_type"] == "file")

    avg = baseline.get("avg_file", 1)

    if avg == 0:
        return

    ratio = file_count / avg

    if ratio > 3:
        score = 3 if ratio > 5 else 2

        return {
            "rule": "file_spike",
            "category": "data_access",
            "score": score,
            "details": {
                "count": file_count,
                "baseline": avg,
                "ratio": ratio
            }
        }