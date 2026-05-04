def detect_login_burst(events):
    logins = [e for e in events if e["event_type"] == "logon"]

    if len(logins) > 5:
        return {
            "rule": "login_burst",
            "category": "brute_force",
            "score": 2
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