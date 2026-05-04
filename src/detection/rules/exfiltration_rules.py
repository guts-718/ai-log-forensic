def detect_file_to_usb(events):
    for i in range(len(events) - 1):
        if events[i]["event_type"] == "file" and events[i+1]["event_type"] == "device":
            return {
                "rule": "file_to_usb",
                "category": "data_exfiltration",
                "score": 3
            }


def detect_file_to_email(events):
    for i in range(len(events) - 1):
        if events[i]["event_type"] == "file" and events[i+1]["event_type"] == "email":
            return {
                "rule": "file_to_email",
                "category": "data_exfiltration",
                "score": 3
            }


def detect_multi_exfiltration(events):
    types = [e["event_type"] for e in events]

    if "file" in types and "email" in types and "device" in types:
        return {
            "rule": "multi_channel_exfiltration",
            "category": "data_exfiltration",
            "score": 4
        }
    
def detect_email_spike(events, baseline):
    count = sum(1 for e in events if e["event_type"] == "email")

    avg = baseline.get("avg_email", 1)

    if avg == 0:
        return

    ratio = count / avg

    if ratio > 3:
        return {
            "rule": "email_spike",
            "category": "data_exfiltration",
            "score": 2,
        }