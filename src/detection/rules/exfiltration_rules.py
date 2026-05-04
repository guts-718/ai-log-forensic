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