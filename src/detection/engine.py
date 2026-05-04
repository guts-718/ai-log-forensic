from collections import defaultdict

from src.detection.utils import group_events_by_user, create_time_windows
from src.detection.baseline.baseline_builder import build_user_baselines

# Rules
from src.detection.rules.auth_rules import detect_login_burst, detect_off_hours
from src.detection.rules.data_rules import detect_file_spike
from src.detection.rules.exfiltration_rules import (
    detect_file_to_usb,
    detect_file_to_email,
    detect_multi_exfiltration,
    detect_email_spike
)
from src.detection.rules.device_rules import detect_device_usage
from src.detection.rules.behavior_rules import (
    detect_long_session,
    detect_event_switching,
    detect_suspicious_transition
)


# -------------------------
# Risk Level
# -------------------------
def get_risk_level(score):
    if score >= 7:
        return "HIGH"
    elif score >= 3:
        return "MEDIUM"
    return "LOW"


# -------------------------
# Evaluate single window
# -------------------------
def evaluate_window(events, baseline, seen_devices):
    detections = []

    rules = [
        lambda e: detect_login_burst(e, baseline),
        detect_off_hours,
        lambda e: detect_file_spike(e, baseline),
        detect_file_to_usb,
        detect_file_to_email,
        detect_multi_exfiltration,
        lambda e: detect_device_usage(e, seen_devices),
        lambda e: detect_email_spike(e, baseline),
        detect_long_session,
        detect_event_switching,
        detect_suspicious_transition,
    ]

    for rule in rules:
        try:
            result = rule(events)
            if result:
                detections.append(result)
        except Exception as ex:
            # don't break pipeline for one rule failure
            print(f"[Rule Error] {rule.__name__}: {ex}")

    score = sum(d.get("score", 0) for d in detections)

    return detections, score


# -------------------------
# Main Detection Engine
# -------------------------
def run_detection(events, window_size="1H"):
    """
    Input:
        events: list of unified events

    Output:
        per-user + per-window detection results
    """

    if not events:
        return {"error": "no events provided"}

    # -------------------------
    # Build baselines
    # -------------------------
    baselines = build_user_baselines(events)

    # -------------------------
    # Group by user
    # -------------------------
    user_map = group_events_by_user(events)

    final_results = {}

    # -------------------------
    # Process each user
    # -------------------------
    for user, user_events in user_map.items():
        baseline = baselines.get(user, {})

        # sort events once (important)
        user_events = sorted(user_events, key=lambda x: x["timestamp"])

        # create time windows
        windows = create_time_windows(user_events, window=window_size)

        user_score = 0
        all_detections = []
        seen_devices = set()

        window_results = []

        # -------------------------
        # Evaluate each window
        # -------------------------
        for idx, w in enumerate(windows):
            detections, score = evaluate_window(w, baseline, seen_devices)

            window_results.append({
                "window_id": idx,
                "event_count": len(w),
                "score": score,
                "risk_level": get_risk_level(score),
                "detections": detections,
                 "raw_events": w
            })

            user_score += score
            all_detections.extend(detections)

        # -------------------------
        # Aggregate user result
        # -------------------------
        final_results[user] = {
            "risk_score": user_score,
            "risk_level": get_risk_level(user_score),
            "total_events": len(user_events),
            "num_windows": len(window_results),
            "detections": all_detections,
            "windows": window_results
        }

    return final_results