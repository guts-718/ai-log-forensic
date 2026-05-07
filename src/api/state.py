from src.api.db import get_logs

EVENT_STORE = get_logs()
DETECTION_RESULTS = {}
BASELINES = {}