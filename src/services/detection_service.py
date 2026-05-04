def detect_anomaly(sequence):
    """
    Simple baseline:
    anomaly if sequence too short or too long
    """

    length = len(sequence)

    if length < 3:
        return {"anomaly": True, "reason": "too few events"}

    if length > 1000:
        return {"anomaly": True, "reason": "too many events"}

    return {"anomaly": False, "reason": "normal baseline"}