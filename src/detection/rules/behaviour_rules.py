def detect_long_session(events):
    if len(events) > 100:
        return {
            "rule": "long_session",
            "category": "behavior_anomaly",
            "score": 2
        }


def detect_event_switching(events):
    types = [e["event_type"] for e in events]

    unique = len(set(types))

    if unique >= 4:
        return {
            "rule": "rapid_event_switching",
            "category": "behavior_anomaly",
            "score": 2
        }


def detect_suspicious_transition(events):
    for i in range(len(events) - 2):
        if (
            events[i]["event_type"] == "device"
            and events[i+1]["event_type"] == "logon"
            and events[i+2]["event_type"] == "file"
        ):
            return {
                "rule": "suspicious_transition",
                "category": "behavior_anomaly",
                "score": 3
            }