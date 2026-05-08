from datetime import datetime


# -----------------------------
# TEMPORAL WEIGHT
# -----------------------------
def temporal_weight(t1, t2):
    if not t1 or not t2:
        return 0

    diff = abs((t2 - t1).total_seconds())

    if diff <= 60:
        return 4

    if diff <= 300:
        return 3

    if diff <= 1800:
        return 1

    return 0


# -----------------------------
# SHARED ENTITY WEIGHTS
# -----------------------------
def shared_entity_weight(e1, e2):
    score = 0

    if e1.get("user") == e2.get("user"):
        score += 2

    if e1.get("device") and e1.get("device") == e2.get("device"):
        score += 5

    if e1.get("resource") and e1.get("resource") == e2.get("resource"):
        score += 5

    return score


# -----------------------------
# SUSPICIOUS TRANSITIONS
# -----------------------------
def suspicious_transition_weight(e1, e2):
    score = 0

    t1 = e1.get("event_type")
    t2 = e2.get("event_type")

    # file -> usb
    if t1 == "file_access" and t2 == "usb_insert":
        score += 8

    # usb -> email
    if t1 == "usb_insert" and t2 == "email_sent":
        score += 9

    # failed -> success
    if t1 == "failed_logon" and t2 == "logon":
        score += 6

    # privilege escalation
    if t2 == "privilege_escalation":
        score += 9

    # ransomware style burst
    if t1 == "process_start" and t2 == "mass_file_modification":
        score += 10

    return score


# -----------------------------
# TOTAL EDGE WEIGHT
# -----------------------------
def compute_edge_weight(e1, e2):
    total = 0

    total += temporal_weight(
        e1.get("timestamp"),
        e2.get("timestamp")
    )

    total += shared_entity_weight(e1, e2)

    total += suspicious_transition_weight(e1, e2)

    return total