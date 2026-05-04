def create_event(timestamp, user, event_type, resource=None, device=None, metadata=None):
    return {
        "timestamp": timestamp,
        "user": user,
        "event_type": event_type,
        "resource": resource,
        "device": device,
        "metadata": metadata or {}
    }