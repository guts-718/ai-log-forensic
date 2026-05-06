from src.api.app import ingest_events  # or import EVENT_STORE directly
from src.services.ingestion_service import EVENT_STORE
from src.detection.engine import run_detection
from src.ml.features.feature_builder import build_feature_dataset
from src.ml.train import train_models
from src.detection.baseline.baseline_builder import build_user_baselines

import json

from typing import Dict, Any


from typing import TypedDict, List, Dict, Any


class WindowResult(TypedDict):
    window_id: int
    event_count: int
    score: int
    risk_level: str
    detections: List[Dict[str, Any]]
    raw_events: List[Dict[str, Any]]


class UserResult(TypedDict):
    risk_score: int
    risk_level: str
    total_events: int
    num_windows: int
    detections: List[Dict[str, Any]]
    windows: List[WindowResult]


DetectionOutput = Dict[str, UserResult]


# -----------------------------
# STEP 0 — Load test data
# -----------------------------
from src.pipeline.run_pipeline import run as run_data_pipeline


def load_real_data():
    print("🔹 Running data pipeline (CERT)...")
    sequences = run_data_pipeline()

    # flatten sequences → events
    events = []
    for user, seq in sequences.items():
        events.extend(seq)

    print("Total events:", len(events))
    return events

# -----------------------------
# MAIN PIPELINE
# -----------------------------
def main():
    print("🔹 Loading real data...")
    events = load_real_data()

    # -----------------------------
    # STEP 1 — Ingest events
    # -----------------------------
    print("🔹 Ingesting events...")
    EVENT_STORE.clear()
    EVENT_STORE.extend(events)

    print(f"Total events: {len(EVENT_STORE)}")

    # -----------------------------
    # STEP 2 — Run detection engine
    # -----------------------------
    print("🔹 Running detection engine...")
    detection_output: DetectionOutput = run_detection(EVENT_STORE) # type: ignore

    print("🔹 Building user baselines...")
    baselines = build_user_baselines(EVENT_STORE)
    
    print(type(detection_output))
    print(list(detection_output.keys())[:3])
    first_user = next(iter(detection_output))

    user_data = detection_output[first_user]

    if "windows" in user_data and user_data["windows"]:
        print("\nSample detection output:")
        print(user_data["windows"][0])
    else:
        print("No windows found for user")


    # -----------------------------
    # STEP 3 — Build feature dataset
    # -----------------------------
    print("🔹 Building feature dataset...")
    df = build_feature_dataset(detection_output, baselines)

    print(f"Dataset shape: {df.shape}")
    print(df.head())

    # -----------------------------
    # STEP 4 — Train models
    # -----------------------------
    print("🔹 Training models...")
    results = train_models(df)

    print("\nFinal Results:")
    print(results)


if __name__ == "__main__":
    main()