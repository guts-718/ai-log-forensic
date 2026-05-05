import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score
import numpy as np

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier


# Optional (install if needed)
try:
    from xgboost import XGBClassifier
except:
    XGBClassifier = None

try:
    from lightgbm import LGBMClassifier
except:
    LGBMClassifier = None



from sklearn.preprocessing import StandardScaler

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

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test


from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler


def prepare_data(df):
    df = df.copy()

    X = df.drop(columns=["label", "user"])
    y = df["label"]
    groups = df["user"]

    gss = GroupShuffleSplit(test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train = X.iloc[train_idx]
    y_train = y.iloc[train_idx]

    X_test = X.iloc[test_idx]
    y_test = y.iloc[test_idx]

    # Scaling (important for LR)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test

# -----------------------------
# Evaluation helper
# -----------------------------
def evaluate_model(name, model, X_test, y_test):
    probs = model.predict_proba(X_test)[:, 1]

    # lower threshold → higher recall
    threshold = 0.40

    y_pred = (probs >= threshold).astype(int)

    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\n=== {name} ===")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(classification_report(y_test, y_pred))
    
    print(f"⚠️ Recall is critical in anomaly detection")
    print(classification_report(y_test, y_pred))
    return {
        "model": name,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

from sklearn.model_selection import cross_val_score

def cross_validate(model, X, y):
    scores = cross_val_score(model, X, y, cv=5, scoring="f1")
    return scores.mean()

import pandas as pd

def show_feature_importance(model, feature_names):
    importances = model.feature_importances_
    df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values(by="importance", ascending=False)

    print("\nTop Features:")
    print(df.head(10))

    return df


# -----------------------------
# Train all models
# -----------------------------
def train_models(df):
    X_train, X_test, y_train, y_test = prepare_data_cross_user(df)

    results = []

    # -------------------------
    # 🥉 Weak Models
    # -------------------------

    # Logistic Regression
    lr = LogisticRegression(max_iter=2000, class_weight="balanced")
    lr.fit(X_train, y_train)
    results.append(evaluate_model("Logistic Regression", lr, X_test, y_test))
    cv_score = cross_validate(lr, X_train, y_train)
    print("LR CV F1:", cv_score)

    # Decision Tree
    dt = DecisionTreeClassifier(max_depth=7, class_weight="balanced")
    dt.fit(X_train, y_train)
    results.append(evaluate_model("Decision Tree", dt, X_test, y_test))

    # 🥈 Mid Models

    # Random Forest
    rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        min_samples_split=5,
        class_weight="balanced"
    )
    rf.fit(X_train, y_train)
    results.append(evaluate_model("Random Forest", rf, X_test, y_test))

    feature_names = df.drop(columns=["label", "user"]).columns
    show_feature_importance(rf, feature_names)

    # Gradient Boosting
    gb = GradientBoostingClassifier()
    gb.fit(X_train, y_train)
    results.append(evaluate_model("Gradient Boosting", gb, X_test, y_test))

    # 🥇 Strong Models

    if XGBClassifier:
        xgb = XGBClassifier(eval_metric="logloss")
        xgb.fit(X_train, y_train)
        results.append(evaluate_model("XGBoost", xgb, X_test, y_test))

    if LGBMClassifier:
        lgbm = LGBMClassifier(scale_pos_weight=3)
        lgbm.fit(X_train, y_train)
        results.append(evaluate_model("LightGBM", lgbm, X_test, y_test))

    results_df = pd.DataFrame(results)
    results_df.to_csv("results.csv", index=False)
    return results_df