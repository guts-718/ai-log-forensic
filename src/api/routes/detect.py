from fastapi import APIRouter
from src.api.state import EVENT_STORE, DETECTION_RESULTS, BASELINES

from src.detection.engine import run_detection
from src.detection.baseline.baseline_builder import build_user_baselines
from src.ml.features.feature_builder import build_feature_dataset
from src.ml.train import train_models

router = APIRouter()

@router.post("/detect")
def run_full_detection():
    if not EVENT_STORE:
        return {"error": "No logs ingested"}

    # Step 1: baselines
    baselines = build_user_baselines(EVENT_STORE)

    # Step 2: rule-based detection
    detection_output = run_detection(EVENT_STORE)

    # Step 3: ML dataset
    df = build_feature_dataset(detection_output, baselines)

    # Step 4: train models
    results = train_models(df)

    DETECTION_RESULTS["rules"] = detection_output
    DETECTION_RESULTS["ml_results"] = results.to_dict()

    return {
        "message": "Detection + ML completed",
        "models": results.to_dict()
    }