def detect_device_usage(events, seen_devices):
    for e in events:
        if e["event_type"] == "device":
            device = e.get("device")

            if device not in seen_devices:
                seen_devices.add(device)
                return {
                    "rule": "new_device_usage",
                    "category": "device_anomaly",
                    "score": 2
                }