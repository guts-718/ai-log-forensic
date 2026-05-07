from fastapi import APIRouter
from src.api.state import EVENT_STORE, DETECTION_RESULTS, BASELINES

# import your pipeline
from src.detection.engine import run_detection
from src.detection.baseline.baseline_builder import build_user_baselines

router = APIRouter()

@router.post("/detect")
def run_detection_pipeline():
    if not EVENT_STORE:
        return {"error": "No logs ingested"}

    # build baselines
    baselines = build_user_baselines(EVENT_STORE)

    # run detection
    detection_output = run_detection(EVENT_STORE)

    DETECTION_RESULTS["output"] = detection_output
    BASELINES.update(baselines)

    return {
        "message": "Detection completed",
        "users_processed": len(detection_output)
    }