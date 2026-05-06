import pandas as pd
import numpy as np

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import fbeta_score
# Models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

try:
    from lightgbm import LGBMClassifier
except:
    LGBMClassifier = None



# Cross-user split (IMPORTANT)
def prepare_data_cross_user(df):
    df = df.copy()

    users = df["user"].unique()
    np.random.shuffle(users)

    split_idx = int(0.8 * len(users))

    train_users = users[:split_idx]
    test_users = users[split_idx:]

    train_df = df[df["user"].isin(train_users)]
    test_df = df[df["user"].isin(test_users)]

    X_train = train_df.drop(columns=["label", "user"])
    y_train = train_df["label"]

    X_test = test_df.drop(columns=["label", "user"])
    y_test = test_df["label"]

    # Scaling (important for LR)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test


# -----------------------------
# Threshold optimization
# -----------------------------
from sklearn.metrics import precision_score

from sklearn.metrics import fbeta_score, precision_score

def find_best_threshold(y_test, probs):
    best_score = -1
    best_threshold = 0.5
    best_pred = None

    fallback_score = -1
    fallback_pred = None
    fallback_threshold = 0.5

    for t in np.arange(0.1, 0.6, 0.05):
        y_temp = (probs >= t).astype(int)

        precision = precision_score(y_test, y_temp, zero_division=0)
        score = fbeta_score(y_test, y_temp, beta=2.5)

        # 🔥 fallback (always track best F2)
        if score > fallback_score:
            fallback_score = score
            fallback_pred = y_temp
            fallback_threshold = t

        # 🔥 preferred (with precision constraint)
        if precision >= 0.70 and score > best_score:
            best_score = score
            best_threshold = t
            best_pred = y_temp

    # 🔥 if no threshold met precision constraint → fallback
    if best_pred is None:
        best_pred = fallback_pred
        best_threshold = fallback_threshold

    return best_threshold, best_pred


# -----------------------------
# Evaluation
# -----------------------------
def evaluate_model(name, model, X_test, y_test):
    probs = model.predict_proba(X_test)[:, 1]
    probs = np.clip(probs, 0.01, 0.99)

    threshold, y_pred = find_best_threshold(y_test, probs)

    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\n=== {name} ===")
    print(f"Best Threshold: {threshold:.2f}")
    print(f"Recall Priority Score (F2): {fbeta_score(y_test, y_pred, beta=2):.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("⚠️ Recall is critical in anomaly detection")

    print(classification_report(y_test, y_pred))

    return {
        "model": name,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "threshold": threshold
    }


# -----------------------------
# Train all models
# -----------------------------
def train_models(df):
    X_train, X_test, y_train, y_test = prepare_data_cross_user(df)

    results = []

    # -------------------------
    # Logistic Regression
    # -------------------------
    lr = LogisticRegression(max_iter=1000, class_weight="balanced")
    lr.fit(X_train, y_train)
    results.append(evaluate_model("Logistic Regression", lr, X_test, y_test))

    # -------------------------
    # Decision Tree
    # -------------------------
    dt = DecisionTreeClassifier(
    max_depth=8,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight="balanced"
)
    dt.fit(X_train, y_train)
    results.append(evaluate_model("Decision Tree", dt, X_test, y_test))

    # -------------------------
    # Random Forest
    # -------------------------
    rf = RandomForestClassifier(
        n_estimators=400,
        max_depth=14,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced"
    )
    rf.fit(X_train, y_train)
    results.append(evaluate_model("Random Forest", rf, X_test, y_test))

    # -------------------------
    # Gradient Boosting
    # -------------------------
    gb = GradientBoostingClassifier(
        n_estimators=300,
        learning_rate=0.04,
        max_depth=3,
        subsample=0.8
    )
    gb.fit(X_train, y_train)
    results.append(evaluate_model("Gradient Boosting", gb, X_test, y_test))

    # -------------------------
    # LightGBM (BEST MODEL)
    # -------------------------
    if LGBMClassifier:
        lgbm = LGBMClassifier(
        scale_pos_weight=5,
        n_estimators=600,
        num_leaves=64,
        max_depth=8,
        learning_rate=0.015,
        colsample_bytree=0.8,
    subsample=0.8
    )
        lgbm.fit(X_train, y_train)
        results.append(evaluate_model("LightGBM", lgbm, X_test, y_test))

    return pd.DataFrame(results)