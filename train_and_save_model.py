import joblib

from src.services.ingestion_service import EVENT_STORE
from src.pipeline.run_pipeline import run as run_data_pipeline

from src.detection.engine import run_detection
from src.detection.baseline.baseline_builder import build_user_baselines
from src.ml.features.feature_builder import build_feature_dataset
from src.ml.train import train_models


# -----------------------------
# STEP 1 — Load CERT data
# -----------------------------
def load_real_data():
    print("🔹 Running data pipeline (CERT)...")

    sequences = run_data_pipeline()

    # flatten sequences → events
    events = []
    for user, seq in sequences.items():
        events.extend(seq)

    print(f"Total events loaded: {len(events)}")
    return events


# -----------------------------
# MAIN TRAINING PIPELINE
# -----------------------------
def main():
    # -----------------------------
    # STEP 1 — Load data
    # -----------------------------
    events = load_real_data()

    # -----------------------------
    # STEP 2 — Ingest into store
    # -----------------------------
    print("🔹 Ingesting events...")
    EVENT_STORE.clear()
    EVENT_STORE.extend(events)

    print(f"Total events in store: {len(EVENT_STORE)}")

    # -----------------------------
    # STEP 3 — Run rule engine
    # -----------------------------
    print("🔹 Running detection engine...")
    detection_output = run_detection(EVENT_STORE)

    # -----------------------------
    # STEP 4 — Build baselines
    # -----------------------------
    print("🔹 Building baselines...")
    baselines = build_user_baselines(EVENT_STORE)

    # -----------------------------
    # STEP 5 — Build ML dataset
    # -----------------------------
    print("🔹 Building feature dataset...")
    df = build_feature_dataset(detection_output, baselines)

    if df.empty:
        raise ValueError("❌ Feature dataset is empty!")
    

    X = df.drop(columns=["label", "user"], errors="ignore")

    # 🔥 SAVE FEATURE COLUMNS
    feature_columns = X.columns.tolist()
    joblib.dump(feature_columns, "feature_columns.pkl")

    print("Dataset shape:", df.shape)
    print("Label distribution:")
    print(df["label"].value_counts())

    # -----------------------------
    # STEP 6 — Train models
    # -----------------------------
    print("🔹 Training models...")
    results_df, best_model = train_models(df)

    print("\nFinal Results:")
    print(results_df)

    # -----------------------------
    # STEP 7 — Save model + baselines
    # -----------------------------
    print("🔹 Saving model...")
    joblib.dump(best_model, "model.pkl")

    print("🔹 Saving baselines...")
    joblib.dump(baselines, "baselines.pkl")

    print("✅ Model + baselines saved successfully!")


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()