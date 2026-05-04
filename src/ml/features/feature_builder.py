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

    # -----------------------------
    # Transitions
    # -----------------------------
    transitions = extract_transitions(events)

    # Only key transitions (avoid feature explosion)
    for t in [
        "file->device",
        "file->email",
        "email->device",
        "logon->file",
        "device->logon",
    ]:
        feature[f"transition_{t}"] = transitions.get(t, 0)

    # -----------------------------
    # Pattern flags
    # -----------------------------
    feature.update(extract_pattern_flags(events))

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
                window.get("raw_events", [])  # we will add this shortly
            )

            # -----------------------------
            # Label (weak supervision)
            # -----------------------------
            # label = 1 if window["score"] >= 5 else 0
            
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
    # Encode sequence_signature
    # -----------------------------
    df = pd.get_dummies(df, columns=["sequence_signature"])

    return df