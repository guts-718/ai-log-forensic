from src.detection.utils import group_events_by_user, create_time_windows

from src.detection.rules.auth_rules import detect_login_burst, detect_off_hours
from src.detection.rules.data_rules import detect_file_spike
from src.detection.rules.exfiltration_rules import (
    detect_file_to_usb,
    detect_file_to_email,
    detect_multi_exfiltration
)
from src.detection.rules.device_rules import detect_device_usage
from src.detection.rules.behavior_rules import (
    detect_long_session,
    detect_event_switching,
    detect_suspicious_transition
)


def evaluate_window(events, seen_devices):
    detections = []

    rules = [
        detect_login_burst,
        detect_off_hours,
        detect_file_spike,
        detect_file_to_usb,
        detect_file_to_email,
        detect_multi_exfiltration,
        lambda e: detect_device_usage(e, seen_devices),
        detect_long_session,
        detect_event_switching,
        detect_suspicious_transition,
    ]

    for rule in rules:
        result = rule(events)
        if result:
            detections.append(result)

    score = sum(d["score"] for d in detections)

    return detections, score


def get_risk_level(score):
    if score >= 7:
        return "HIGH"
    elif score >= 3:
        return "MEDIUM"
    return "LOW"


def run_detection(events):
    user_map = group_events_by_user(events)

    final_results = {}

    for user, user_events in user_map.items():
        windows = create_time_windows(user_events)

        user_score = 0
        all_detections = []
        seen_devices = set()

        window_results = []

        for w in windows:
            detections, score = evaluate_window(w, seen_devices)

            window_results.append({
                "window_events": len(w),
                "score": score,
                "detections": detections
            })

            user_score += score
            all_detections.extend(detections)

        final_results[user] = {
            "risk_score": user_score,
            "risk_level": get_risk_level(user_score),
            "detections": all_detections,
            "windows": window_results
        }

    return final_results