def detect_login_burst(events, baseline):
    count = sum(1 for e in events if e["event_type"] == "logon")

    avg = baseline.get("avg_logon", 1)

    if avg == 0:
        return

    ratio = count / avg

    if ratio > 3:
        return {
            "rule": "login_burst",
            "category": "brute_force",
            "score": 2 if ratio < 5 else 3,
            "details": {
                "count": count,
                "baseline": avg
            }
        }

def detect_off_hours(events):
    for e in events:
        if e["event_type"] == "logon":
            hour = e["timestamp"].hour
            if hour < 6 or hour > 20:
                return {
                    "rule": "off_hours_login",
                    "category": "authentication",
                    "score": 2
                }