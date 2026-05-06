import pandas as pd
import numpy as np
import random

from collections import Counter
from math import log2


# -----------------------------
# Transition extraction
# -----------------------------
def extract_transitions(events):
    transitions = Counter()

    for i in range(len(events) - 1):
        a = events[i]["event_type"]
        b = events[i + 1]["event_type"]

        transitions[f"{a}->{b}"] += 1

    return transitions


# -----------------------------
# Sequence signature
# -----------------------------
def extract_sequence_signature(events, max_len=5):
    mapping = {
        "logon": "L",
        "file": "F",
        "email": "E",
        "device": "D",
    }

    seq = [mapping.get(e["event_type"], "X") for e in events[:max_len]]

    while len(seq) < max_len:
        seq.append("PAD")

    return "-".join(seq)


# -----------------------------
# Main Feature Builder
# -----------------------------
def build_features_for_window(events, baselines):
    feature = {}

    if not events:
        return None

    user = events[0]["user"]

    # -----------------------------
    # Extract types
    # -----------------------------
    types = [e["event_type"] for e in events]

    # -----------------------------
    # Basic counts
    # -----------------------------
    feature["event_count"] = len(events)
    feature["file_count"] = types.count("file")
    feature["email_count"] = types.count("email")
    feature["logon_count"] = types.count("logon")
    feature["device_count"] = types.count("device")

    feature["unique_event_types"] = len(set(types))

    # -----------------------------
    # Time features
    # -----------------------------
    timestamps = [e["timestamp"] for e in events]
    times = pd.to_datetime(timestamps)

    if len(times) > 1:
        window_duration = (times.max() - times.min()).total_seconds()
    else:
        window_duration = 1

    feature["window_duration"] = window_duration

    # stable intensity
    feature["activity_intensity"] = feature["event_count"] / max(window_duration, 60)

    # -----------------------------
    # Time gaps
    # -----------------------------
    if len(times) > 1:
        diffs = [(times[i+1] - times[i]).total_seconds() for i in range(len(times)-1)]

        feature["avg_time_gap"] = np.mean(diffs)
        feature["min_time_gap"] = np.min(diffs)
        feature["time_gap_std"] = np.std(diffs)

        short_gaps = sum(1 for d in diffs if d < 60)
        feature["burst_ratio"] = short_gaps / (len(diffs) + 1e-5)
    else:
        feature["avg_time_gap"] = 0
        feature["min_time_gap"] = 0
        feature["time_gap_std"] = 0
        feature["burst_ratio"] = 0

    # -----------------------------
    # Ratios
    # -----------------------------
    total = len(events) + 1e-5

    feature["file_ratio"] = feature["file_count"] / total
    feature["email_ratio"] = feature["email_count"] / total
    feature["device_ratio"] = feature["device_count"] / total

    # -----------------------------
    # Entropy
    # -----------------------------
    counts = Counter(types)
    probs = [c / len(types) for c in counts.values()]
    feature["event_entropy"] = -sum(p * log2(p) for p in probs)

    # -----------------------------
    # Transitions
    # -----------------------------
    transitions = extract_transitions(events)

    for t in [
        "logon->file",
        "file->file",
        "email->email",
        "device->logon"
    ]:
        feature[f"transition_{t}"] = transitions.get(t, 0)

    feature["num_transitions"] = sum(transitions.values())
    feature["transition_diversity"] = len(transitions)

    # -----------------------------
    # Sequence features
    # -----------------------------
    feature["sequence_signature"] = extract_sequence_signature(events)

    feature["first_event"] = events[0]["event_type"]
    feature["last_event"] = events[-1]["event_type"]

    feature["event_switch_rate"] = feature["transition_diversity"] / (feature["event_count"] + 1e-5)

    # -----------------------------
    # Repetition
    # -----------------------------
    feature["max_event_repeat"] = max(Counter(types).values())

    # -----------------------------
    # Weak sequential signal
    # -----------------------------
    feature["file_then_device_proximity"] = 0

    for i in range(len(events) - 1):
        if events[i]["event_type"] == "file" and events[i+1]["event_type"] == "device":
            feature["file_then_device_proximity"] += 1

    # -----------------------------
    # 🔥 BASELINE DEVIATION (KEY FEATURE)
    # -----------------------------
    baseline = baselines.get(user, {})

    feature["file_dev_norm"] = (
    feature["file_count"] - baseline.get("avg_file", 0)
    ) / (baseline.get("std_file", 1) + 1e-5)

    feature["email_dev_norm"] = (
        feature["email_count"] - baseline.get("avg_email", 0)
    ) / (baseline.get("std_email", 1) + 1e-5)

    feature["logon_dev_norm"] = (
        feature["logon_count"] - baseline.get("avg_logon", 0)
    ) / (baseline.get("std_logon", 1) + 1e-5)


    feature["total_dev"] = (
    abs(feature["file_dev_norm"]) +
    abs(feature["email_dev_norm"]) +
    abs(feature["logon_dev_norm"])


)
    feature["extreme_file_dev"] = 1 if abs(feature["file_dev_norm"]) > 2 else 0
    feature["extreme_email_dev"] = 1 if abs(feature["email_dev_norm"]) > 2 else 0
    feature["extreme_logon_dev"] = 1 if abs(feature["logon_dev_norm"]) > 2 else 0
    feature["file_x_device"] = feature["file_count"] * feature["device_count"]

    feature["any_extreme_dev"] = (
    feature["extreme_file_dev"] +
    feature["extreme_email_dev"] +
    feature["extreme_logon_dev"]
)

    return feature


# -----------------------------
# Dataset Builder
# -----------------------------
def build_feature_dataset(detection_output, baselines):
    rows = []

    for user, data in detection_output.items():
        for window in data["windows"]:

            events = window.get("raw_events", [])

            features = build_features_for_window(events, baselines)

            if features is None:
                continue

            # -----------------------------
            # Label logic
            # -----------------------------
            if window["score"] >= 7:
                label = 1
            elif window["score"] <= 2:
                label = 0
            else:
                label = 1 if random.random() < 0.12 else 0

            features["label"] = label
            features["user"] = user

            rows.append(features)

    df = pd.DataFrame(rows)

    # -----------------------------
    # Encode categorical
    # -----------------------------
    df = pd.get_dummies(
        df,
        columns=["sequence_signature", "first_event", "last_event"]
    )

    return df