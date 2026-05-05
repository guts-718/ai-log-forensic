import pandas as pd
from collections import Counter


# -----------------------------
# Helper: transitions
# -----------------------------
def extract_transitions(events):
    transitions = Counter()

    for i in range(len(events) - 1):
        a = events[i]["event_type"]
        b = events[i + 1]["event_type"]

        transitions[f"{a}->{b}"] += 1

    return transitions


# -----------------------------
# Helper: pattern flags
# -----------------------------
def extract_pattern_flags(events):
    types = [e["event_type"] for e in events]

    return {
        "has_file_to_usb": int("file" in types and "device" in types),
        "has_file_to_email": int("file" in types and "email" in types),
        "has_multi_exfil": int(
            "file" in types and "email" in types and "device" in types
        ),
    }


# -----------------------------
# Helper: sequence signature
# -----------------------------
def extract_sequence_signature(events, max_len=5):
    mapping = {
        "logon": "L",
        "file": "F",
        "email": "E",
        "device": "D",
    }

    seq = [mapping.get(e["event_type"], "X") for e in events[:max_len]]

    # pad if short
    while len(seq) < max_len:
        seq.append("PAD")

    return "-".join(seq)


# -----------------------------
# Main Feature Builder
# -----------------------------
def build_features_for_window(events):
    feature = {}

    types = [e["event_type"] for e in events]

    # -----------------------------
    # Basic counts
    # -----------------------------
    feature["event_count"] = len(events)
    feature["file_count"] = types.count("file")
    feature["email_count"] = types.count("email")
    feature["logon_count"] = types.count("logon")
    feature["device_count"] = types.count("device")

    # -----------------------------
    # Diversity
    # -----------------------------
    feature["unique_event_types"] = len(set(types))

    timestamps = [e["timestamp"] for e in events]
    times = pd.to_datetime(timestamps)

    feature["window_duration"] = (times.max() - times.min()).total_seconds()
    feature["events_per_min"] = len(events) / (feature["window_duration"] / 60 + 1e-5)
    feature["active_hours"] = len(set(times.hour))

    total = len(events) + 1e-5

    feature["file_ratio"] = feature["file_count"] / total
    feature["email_ratio"] = feature["email_count"] / total
    feature["device_ratio"] = feature["device_count"] / total

    time_diffs = sorted(times)
    diffs = [(time_diffs[i + 1] - time_diffs[i]).total_seconds() for i in range(len(time_diffs) - 1)]

    if diffs:
        feature["avg_time_gap"] = sum(diffs) / len(diffs)
        feature["min_time_gap"] = min(diffs)
    else:
        feature["avg_time_gap"] = 0
        feature["min_time_gap"] = 0

    from math import log2
    counts = Counter(types)
    probs = [c / len(types) for c in counts.values()]
    entropy = -sum(p * log2(p) for p in probs)

    feature["event_entropy"] = entropy

    feature["first_event"] = events[0]["event_type"]
    feature["last_event"] = events[-1]["event_type"]

    # -----------------------------
    # Transitions (FIXED ORDER)
    # -----------------------------
    transitions = extract_transitions(events)

    feature["num_transitions"] = sum(transitions.values())
    feature["transition_diversity"] = len(transitions)

    # -----------------------------
    # Transitions (safe subset)
    # -----------------------------
    for t in [
        "logon->file",
        "file->file",
        "email->email",
        "device->logon"
    ]:
        feature[f"transition_{t}"] = transitions.get(t, 0)

    # -----------------------------
    # Pattern flags (kept as-is)
    # -----------------------------
    # feature.update(extract_pattern_flags(events))

    # -----------------------------
    # Sequence signature
    # -----------------------------
    feature["sequence_signature"] = extract_sequence_signature(events)

    return feature


# -----------------------------
# Convert all windows → dataframe
# -----------------------------
def build_feature_dataset(detection_output):
    """
    detection_output = output from rule engine
    """

    rows = []

    for user, data in detection_output.items():
        for window in data["windows"]:
            features = build_features_for_window(
                window.get("raw_events", [])
            )

            # -----------------------------
            # Label (weak supervision)
            # -----------------------------
            if window["score"] >= 7:
                label = 1
            elif window["score"] <= 2:
                label = 0
            else:
                continue  # skip ambiguous windows

            features["label"] = label
            features["user"] = user

            rows.append(features)

    df = pd.DataFrame(rows)

    # -----------------------------
    # Encode categorical
    # -----------------------------
    df = pd.get_dummies(df, columns=["sequence_signature", "first_event", "last_event"])

    return df