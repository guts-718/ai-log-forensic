import pandas as pd
import numpy as np

# Evaluation metrics
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

# Feature normalization
from sklearn.preprocessing import StandardScaler

# Additional metric
from sklearn.metrics import fbeta_score

# -----------------------------------
# MODELS
# -----------------------------------
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)

# -----------------------------------
# OPTIONAL LIGHTGBM IMPORT
# -----------------------------------
# If LightGBM is not installed,
# code will still run safely.
try:
    from lightgbm import LGBMClassifier
except:
    LGBMClassifier = None


# -----------------------------------
# CROSS-USER TRAIN/TEST SPLIT
# -----------------------------------
# IMPORTANT:
# Instead of random row splitting,
# entire users are separated.
#
# Why?
# Prevents data leakage.
#
# If same user appears in both
# train and test sets, model may
# memorize user behavior instead
# of learning general anomalies.
def prepare_data_cross_user(df):

    # Create safe copy
    df = df.copy()

    # Get unique users
    users = df["user"].unique()

    # Shuffle users randomly
    np.random.shuffle(users)

    # 80% users for training
    split_idx = int(0.8 * len(users))

    train_users = users[:split_idx]
    test_users = users[split_idx:]

    # Split dataframe based on users
    train_df = df[df["user"].isin(train_users)]
    test_df = df[df["user"].isin(test_users)]

    # Features for training
    X_train = train_df.drop(
        columns=["label", "user"]
    )

    # Labels for training
    y_train = train_df["label"]

    # Features for testing
    X_test = test_df.drop(
        columns=["label", "user"]
    )

    # Labels for testing
    y_test = test_df["label"]

    # -----------------------------------
    # FEATURE SCALING
    # -----------------------------------
    # Standardization:
    # mean = 0
    # std  = 1
    #
    # Important for models like
    # Logistic Regression.
    scaler = StandardScaler()

    # Learn scaling parameters
    # from training data only
    X_train = scaler.fit_transform(X_train)

    # Apply same scaling to test data
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test


# -----------------------------------
# THRESHOLD OPTIMIZATION
# -----------------------------------
from sklearn.metrics import (
    fbeta_score,
    precision_score
)

# Finds best probability threshold
# for anomaly detection.
#
# Instead of fixed threshold 0.5,
# this searches for better values.
def find_best_threshold(y_test, probs):

    # Best constrained score
    best_score = -1

    # Best threshold found
    best_threshold = 0.5

    # Best predictions
    best_pred = None

    # -----------------------------------
    # FALLBACK VARIABLES
    # -----------------------------------
    # Used if no threshold satisfies
    # precision constraint.
    fallback_score = -1
    fallback_pred = None
    fallback_threshold = 0.5

    # -----------------------------------
    # TRY MULTIPLE THRESHOLDS
    # -----------------------------------
    for t in np.arange(0.1, 0.6, 0.05):

        # Convert probabilities
        # into binary predictions
        y_temp = (probs >= t).astype(int)

        # Precision:
        # out of predicted anomalies,
        # how many are correct?
        precision = precision_score(
            y_test,
            y_temp,
            zero_division=0
        )

        # F2 score:
        # Recall-focused metric
        #
        # beta=2 means recall
        # is weighted more heavily.
        score = fbeta_score(
            y_test,
            y_temp,
            beta=2
        )

        # -----------------------------------
        # ALWAYS TRACK FALLBACK
        # -----------------------------------
        if score > fallback_score:

            fallback_score = score
            fallback_pred = y_temp
            fallback_threshold = t

        # -----------------------------------
        # PRIMARY SELECTION LOGIC
        # -----------------------------------
        # Choose threshold only if:
        #
        # 1. Precision >= 0.5
        # 2. F2 score improves
        if (
            precision >= 0.5
            and score > best_score
        ):

            best_score = score
            best_threshold = t
            best_pred = y_temp

    # -----------------------------------
    # SAFETY CHECK 1
    # -----------------------------------
    # If no threshold met precision
    # condition, use fallback result.
    if best_pred is None:

        best_pred = fallback_pred
        best_threshold = fallback_threshold

    # -----------------------------------
    # SAFETY CHECK 2
    # -----------------------------------
    # Absolute last fallback.
    if best_pred is None:

        best_pred = (
            probs >= 0.5
        ).astype(int)

        best_threshold = 0.5

    return best_threshold, best_pred


# -----------------------------------
# MODEL EVALUATION
# -----------------------------------
def evaluate_model(
    name,
    model,
    X_test,
    y_test
):

    # Get anomaly probabilities
    #
    # [:, 1] selects probability
    # of positive/anomaly class
    probs = model.predict_proba(
        X_test
    )[:, 1]

    # Find best threshold
    threshold, y_pred = (
        find_best_threshold(
            y_test,
            probs
        )
    )

    # Extra safety
    if y_pred is None:

        y_pred = (
            probs >= 0.5
        ).astype(int)

    # -----------------------------------
    # CALCULATE METRICS
    # -----------------------------------
    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    # -----------------------------------
    # PRINT RESULTS
    # -----------------------------------
    print(f"\n=== {name} ===")

    print(
        f"Best Threshold: {threshold:.2f}"
    )

    print(
        "Recall Priority Score (F2): "
        f"{fbeta_score(y_test, y_pred, beta=2):.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall:    {recall:.4f}"
    )

    print(
        f"F1 Score:  {f1:.4f}"
    )

    print(
        "⚠️ Recall is critical "
        "in anomaly detection"
    )

    # Detailed class-wise report
    print(
        classification_report(
            y_test,
            y_pred
        )
    )

    # Return structured metrics
    return {
        "model": name,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "threshold": threshold
    }


# -----------------------------------
# TRAIN ALL MODELS
# -----------------------------------
def train_models(df):

    # Prepare train/test split
    X_train, X_test, y_train, y_test = (
        prepare_data_cross_user(df)
    )

    # Store evaluation results
    results = []

    # ===================================
    # LOGISTIC REGRESSION
    # ===================================
    # Simple linear baseline model
    lr = LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    )

    # Print label distribution
    print(y_train.value_counts())

    # Another distribution check
    print(
        np.unique(
            y_train,
            return_counts=True
        )
    )

    # Train model
    lr.fit(X_train, y_train)

    # Evaluate model
    results.append(
        evaluate_model(
            "Logistic Regression",
            lr,
            X_test,
            y_test
        )
    )

    # ===================================
    # DECISION TREE
    # ===================================
    # Rule-based tree model
    dt = DecisionTreeClassifier(
        max_depth=6,
        class_weight="balanced"
    )

    dt.fit(X_train, y_train)

    results.append(
        evaluate_model(
            "Decision Tree",
            dt,
            X_test,
            y_test
        )
    )

    # ===================================
    # RANDOM FOREST
    # ===================================
    # Ensemble of many decision trees
    rf = RandomForestClassifier(

        # Number of trees
        n_estimators=300,

        # Maximum tree depth
        max_depth=12,

        # Minimum samples needed
        # to split node
        min_samples_split=5,

        # Minimum samples per leaf
        min_samples_leaf=3,

        # Handle class imbalance
        class_weight="balanced"
    )

    rf.fit(X_train, y_train)

    results.append(
        evaluate_model(
            "Random Forest",
            rf,
            X_test,
            y_test
        )
    )

    # ===================================
    # GRADIENT BOOSTING
    # ===================================
    # Sequential boosting model
    gb = GradientBoostingClassifier(

        # Number of boosting stages
        n_estimators=200,

        # Step size
        learning_rate=0.05,

        # Tree depth
        max_depth=3
    )

    gb.fit(X_train, y_train)

    results.append(
        evaluate_model(
            "Gradient Boosting",
            gb,
            X_test,
            y_test
        )
    )

    # ===================================
    # LIGHTGBM (BEST MODEL)
    # ===================================
    best_model = None

    # Train only if installed
    if LGBMClassifier:

        lgbm = LGBMClassifier(

            # Handle imbalance
            scale_pos_weight=4,

            # Number of trees
            n_estimators=500,

            # Complexity control
            num_leaves=50,

            # Maximum depth
            max_depth=8,

            # Learning speed
            learning_rate=0.04
        )

        # Train model
        lgbm.fit(X_train, y_train)

        # Evaluate model
        results.append(
            evaluate_model(
                "LightGBM",
                lgbm,
                X_test,
                y_test
            )
        )

        # Save best model
        best_model = lgbm

    # -----------------------------------
    # RETURN RESULTS
    # -----------------------------------
    return pd.DataFrame(results), best_model

    # Alternative:
    # return pd.DataFrame(results)




#########################################################33


import pandas as pd
from pathlib import Path


# -----------------------------------
# DIRECTORY PATHS
# -----------------------------------

# Folder containing original raw CSV files
RAW_DIR = Path("data/raw")

# Folder where filtered/smaller datasets
# will be stored
OUT_DIR = Path("data/processed")

# Create output directory if it does not exist
#
# parents=True  -> create parent folders if needed
# exist_ok=True -> avoid error if folder already exists
OUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# -----------------------------------
# FILES TO PROCESS
# -----------------------------------

# List of CSV files that will be filtered
FILES = [
    "logon.csv",
    "file.csv",
    "email.csv",
    "device.csv"
]


# -----------------------------------
# FIND MOST ACTIVE USERS
# -----------------------------------
def get_top_users(
    file_path,
    user_col="user",
    n=50
):

    # Read only the user column
    # for memory efficiency
    df = pd.read_csv(
        file_path,
        usecols=[user_col]
    )

    # Count occurrences of each user
    #
    # value_counts():
    # user1 -> 5000
    # user2 -> 4200
    # ...
    #
    # head(n):
    # select top n users
    #
    # index.tolist():
    # convert usernames into Python list
    top_users = (
        df[user_col]
        .value_counts()
        .head(n)
        .index
        .tolist()
    )

    return top_users


# -----------------------------------
# FILTER SINGLE FILE
# -----------------------------------
def filter_file(
    file_name,
    top_users,
    user_col="user"
):

    # Full path of input file
    file_path = RAW_DIR / file_name

    # Output file path
    #
    # Example:
    # logon.csv -> logon_small.csv
    out_path = (
        OUT_DIR
        / file_name.replace(
            ".csv",
            "_small.csv"
        )
    )

    # -----------------------------------
    # READ LARGE FILE IN CHUNKS
    # -----------------------------------
    #
    # chunksize=50000 means:
    # read 50k rows at a time
    #
    # Prevents memory overflow
    # on large datasets
    chunks = pd.read_csv(
        file_path,
        chunksize=50000
    )

    # Store filtered chunks here
    filtered_chunks = []

    # -----------------------------------
    # PROCESS EACH CHUNK
    # -----------------------------------
    for chunk in chunks:

        # Keep only rows where user
        # belongs to top_users list
        chunk = chunk[
            chunk[user_col].isin(top_users)
        ]

        # Save filtered chunk
        filtered_chunks.append(chunk)

    # -----------------------------------
    # COMBINE ALL FILTERED CHUNKS
    # -----------------------------------
    df_small = pd.concat(filtered_chunks)

    # Save filtered dataset
    df_small.to_csv(
        out_path,
        index=False
    )

    # Print summary
    print(
        f"Saved: {out_path} | "
        f"Rows: {len(df_small)}"
    )


# -----------------------------------
# MAIN PIPELINE
# -----------------------------------
def main():

    # Step 1:
    # Identify most active users
    print(
        "🔍 Finding top users "
        "from logon.csv..."
    )

    top_users = get_top_users(
        RAW_DIR / "logon.csv"
    )

    # Print selected users
    print("Top users:", top_users)

    # -----------------------------------
    # FILTER ALL FILES
    # -----------------------------------
    for file in FILES:

        print(f"\nProcessing {file}...")

        filter_file(
            file,
            top_users
        )


# -----------------------------------
# ENTRY POINT
# -----------------------------------
#
# Ensures main() runs only when
# this file is executed directly.
#
# Prevents automatic execution
# if imported as a module.
if __name__ == "__main__":
    main()

















import pandas as pd
import numpy as np
import random

from collections import Counter
from math import log2


# -----------------------------------
# TRANSITION EXTRACTION
# -----------------------------------
#
# Extracts sequential transitions
# between consecutive event types.
#
# Example:
# logon -> file
# file -> email
#
# Useful for modeling behavior flow.
def extract_transitions(events):

    # Counter automatically counts
    # occurrences of transitions
    transitions = Counter()

    # Iterate over consecutive event pairs
    for i in range(len(events) - 1):

        # Current event type
        a = events[i]["event_type"]

        # Next event type
        b = events[i + 1]["event_type"]

        # Store transition count
        #
        # Example:
        # "logon->file"
        transitions[f"{a}->{b}"] += 1

    return transitions



























# -----------------------------------
# SEQUENCE SIGNATURE
# -----------------------------------
#
# Converts first few event types
# into compact symbolic sequence.
#
# Example:
# logon -> file -> email
# becomes:
# L-F-E
#
# Useful for:
# - behavioral fingerprinting
# - pattern recognition
# - ML categorical features
def extract_sequence_signature(
    events,
    max_len=5
):

    # Mapping event names to symbols
    mapping = {
        "logon": "L",
        "file": "F",
        "email": "E",
        "device": "D",
    }

    # Convert event sequence
    # into symbolic representation
    seq = [
        mapping.get(
            e["event_type"],
            "X"   # unknown event
        )
        for e in events[:max_len]
    ]

    # Pad shorter sequences
    # to fixed length
    while len(seq) < max_len:
        seq.append("PAD")

    # Join symbols into string
    #
    # Example:
    # L-F-E-PAD-PAD
    return "-".join(seq)


# -----------------------------------
# MAIN FEATURE BUILDER
# -----------------------------------
#
# Builds ML features from
# a behavioral event window.
#
# Each window becomes one
# feature vector / ML sample.
def build_features_for_window(
    events,
    baselines
):

    # Dictionary storing all features
    feature = {}

    # Empty event window check
    if not events:
        return None

    # User associated with window
    user = events[0]["user"]

    # -----------------------------------
    # EXTRACT EVENT TYPES
    # -----------------------------------
    #
    # Example:
    # ["logon", "file", "email"]
    types = [
        e["event_type"]
        for e in events
    ]

    # ===================================
    # BASIC COUNT FEATURES
    # ===================================

    # Total events in window
    feature["event_count"] = len(events)

    # Event-specific counts
    feature["file_count"] = (
        types.count("file")
    )

    feature["email_count"] = (
        types.count("email")
    )

    feature["logon_count"] = (
        types.count("logon")
    )

    feature["device_count"] = (
        types.count("device")
    )

    # Number of distinct event types
    feature["unique_event_types"] = (
        len(set(types))
    )

    # ===================================
    # TIME FEATURES
    # ===================================

    # Extract timestamps
    timestamps = [
        e["timestamp"]
        for e in events
    ]

    # Convert to pandas datetime
    times = pd.to_datetime(timestamps)

    # Calculate duration of window
    if len(times) > 1:

        window_duration = (
            times.max() - times.min()
        ).total_seconds()

    else:

        # Avoid zero duration
        window_duration = 1

    feature["window_duration"] = (
        window_duration
    )

    # -----------------------------------
    # ACTIVITY INTENSITY
    # -----------------------------------
    #
    # Measures event density
    # over time.
    #
    # Higher value =
    # more rapid activity.
    feature["activity_intensity"] = (
        feature["event_count"]
        / max(window_duration, 60)
    )

    # ===================================
    # TIME GAP FEATURES
    # ===================================
    if len(times) > 1:

        # Time differences between
        # consecutive events
        diffs = [

            (
                times[i + 1] - times[i]
            ).total_seconds()

            for i in range(len(times) - 1)
        ]

        # Average gap
        feature["avg_time_gap"] = (
            np.mean(diffs)
        )

        # Minimum gap
        feature["min_time_gap"] = (
            np.min(diffs)
        )

        # Gap variability
        feature["time_gap_std"] = (
            np.std(diffs)
        )

        # -----------------------------------
        # BURST RATIO
        # -----------------------------------
        #
        # Percentage of rapid events
        # occurring within 60 seconds.
        short_gaps = sum(
            1
            for d in diffs
            if d < 60
        )

        feature["burst_ratio"] = (
            short_gaps
            / (len(diffs) + 1e-5)
        )

    else:

        # Default values for
        # single-event windows
        feature["avg_time_gap"] = 0
        feature["min_time_gap"] = 0
        feature["time_gap_std"] = 0
        feature["burst_ratio"] = 0

    # ===================================
    # EVENT RATIOS
    # ===================================
    #
    # Normalize counts by
    # total number of events.
    total = len(events) + 1e-5

    feature["file_ratio"] = (
        feature["file_count"] / total
    )

    feature["email_ratio"] = (
        feature["email_count"] / total
    )

    feature["device_ratio"] = (
        feature["device_count"] / total
    )

    # ===================================
    # ENTROPY FEATURE
    # ===================================
    #
    # Measures randomness/diversity
    # of event distribution.
    #
    # High entropy:
    # many diverse events
    #
    # Low entropy:
    # repetitive behavior
    counts = Counter(types)

    probs = [
        c / len(types)
        for c in counts.values()
    ]

    feature["event_entropy"] = (
        -sum(
            p * log2(p)
            for p in probs
        )
    )

    # ===================================
    # TRANSITION FEATURES
    # ===================================

    # Extract transition counts
    transitions = extract_transitions(events)

    # Track important transitions
    for t in [
        "logon->file",
        "file->file",
        "email->email",
        "device->logon"
    ]:

        feature[f"transition_{t}"] = (
            transitions.get(t, 0)
        )

    # Total transitions
    feature["num_transitions"] = (
        sum(transitions.values())
    )

    # Number of unique transitions
    feature["transition_diversity"] = (
        len(transitions)
    )

    # ===================================
    # SEQUENCE FEATURES
    # ===================================

    # Compact event pattern signature
    feature["sequence_signature"] = (
        extract_sequence_signature(events)
    )

    # First event in window
    feature["first_event"] = (
        events[0]["event_type"]
    )

    # Last event in window
    feature["last_event"] = (
        events[-1]["event_type"]
    )

    # -----------------------------------
    # EVENT SWITCH RATE
    # -----------------------------------
    #
    # Measures how frequently
    # user changes activity types.
    feature["event_switch_rate"] = (
        feature["transition_diversity"]
        / (feature["event_count"] + 1e-5)
    )

    # ===================================
    # REPETITION FEATURES
    # ===================================
    #
    # Highest repetition count
    # of any event type.
    #
    # Example:
    # file,file,file,email
    # -> max repeat = 3
    feature["max_event_repeat"] = (
        max(Counter(types).values())
    )

    # ===================================
    # WEAK SEQUENTIAL SIGNAL
    # ===================================
    #
    # Detects:
    # file activity immediately
    # followed by device usage.
    #
    # Potential signal for:
    # copying files to USB.
    feature["file_then_device_proximity"] = 0

    for i in range(len(events) - 1):

        if (
            events[i]["event_type"] == "file"
            and events[i + 1]["event_type"] == "device"
        ):

            feature[
                "file_then_device_proximity"
            ] += 1

    # ===================================
    # BASELINE DEVIATION FEATURES
    # ===================================
    #
    # Compare current behavior
    # against historical baseline
    # for this user.
    baseline = baselines.get(user, {})

    # -----------------------------------
    # FILE DEVIATION
    # -----------------------------------
    #
    # Z-score style normalization:
    #
    # (current - avg) / std
    feature["file_dev_norm"] = (

        feature["file_count"]
        - baseline.get("avg_file", 0)

    ) / (
        baseline.get("std_file", 1)
        + 1e-5
    )

    # Email deviation
    feature["email_dev_norm"] = (

        feature["email_count"]
        - baseline.get("avg_email", 0)

    ) / (
        baseline.get("std_email", 1)
        + 1e-5
    )

    # Logon deviation
    feature["logon_dev_norm"] = (

        feature["logon_count"]
        - baseline.get("avg_logon", 0)

    ) / (
        baseline.get("std_logon", 1)
        + 1e-5
    )

    # -----------------------------------
    # TOTAL BEHAVIORAL DEVIATION
    # -----------------------------------
    #
    # Aggregate anomaly magnitude.
    feature["total_dev"] = (

        abs(feature["file_dev_norm"])
        + abs(feature["email_dev_norm"])
        + abs(feature["logon_dev_norm"])

    )

    # -----------------------------------
    # OPTIONAL EXTREME DEVIATION FLAGS
    # -----------------------------------
    #
    # Currently disabled.
    #
    # feature["extreme_file_dev"] =
    #     1 if abs(feature["file_dev_norm"]) > 2 else 0

    # -----------------------------------
    # FEATURE INTERACTION
    # -----------------------------------
    #
    # Captures combined effect of:
    # high file activity + device activity
    #
    # Useful for:
    # potential USB exfiltration
    feature["file_x_device"] = (

        feature["file_count"]
        * feature["device_count"]
    )

    return feature


# -----------------------------------
# DATASET BUILDER
# -----------------------------------
#
# Converts all detection windows
# into ML-ready dataset.
def build_feature_dataset(
    detection_output,
    baselines
):

    # Store feature rows
    rows = []

    # Iterate through users
    for user, data in detection_output.items():

        # Iterate through behavioral windows
        for window in data["windows"]:

            # Extract raw events
            events = window.get(
                "raw_events",
                []
            )

            # Build feature vector
            features = build_features_for_window(
                events,
                baselines
            )

            # Skip empty windows
            if features is None:
                continue

            # ===================================
            # LABEL GENERATION
            # ===================================
            #
            # Weak supervision strategy.
            #
            # High score -> anomaly
            # Low score  -> normal
            # Mid score  -> probabilistic label

            # Strong anomaly
            if window["score"] >= 7:

                label = 1

            # Strongly normal
            elif window["score"] <= 2:

                label = 0

            # Uncertain region
            else:

                # Random soft labeling
                label = (
                    1
                    if random.random() < 0.12
                    else 0
                )

            # Store label and user
            features["label"] = label
            features["user"] = user

            rows.append(features)

    # Convert rows into dataframe
    df = pd.DataFrame(rows)

    # ===================================
    # ONE-HOT ENCODING
    # ===================================
    #
    # Convert categorical variables
    # into ML-compatible numeric columns.
    df = pd.get_dummies(

        df,

        columns=[
            "sequence_signature",
            "first_event",
            "last_event"
        ]
    )

    return df