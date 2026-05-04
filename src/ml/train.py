import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score

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


# -----------------------------
# Prepare dataset
# -----------------------------
from sklearn.preprocessing import StandardScaler

def prepare_data(df):
    df = df.copy()

    X = df.drop(columns=["label", "user"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test

# -----------------------------
# Evaluation helper
# -----------------------------
def evaluate_model(name, model, X_test, y_test):
    probs = model.predict_proba(X_test)[:, 1]
    y_pred = (probs > 0.6).astype(int)

    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    print(f"\n=== {name} ===")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
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


# -----------------------------
# Train all models
# -----------------------------
def train_models(df):
    X_train, X_test, y_train, y_test = prepare_data(df)

    results = []

    # -------------------------
    # 🥉 Weak Models
    # -------------------------

    # Logistic Regression
    lr = LogisticRegression(max_iter=1000, class_weight="balanced")
    lr.fit(X_train, y_train)
    results.append(evaluate_model("Logistic Regression", lr, X_test, y_test))
    cv_score = cross_validate(lr, X_train, y_train)
    print("LR CV F1:", cv_score)

    # Decision Tree
    dt = DecisionTreeClassifier(max_depth=5, class_weight="balanced")
    dt.fit(X_train, y_train)
    results.append(evaluate_model("Decision Tree", dt, X_test, y_test))

    # 🥈 Mid Models

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, class_weight="balanced")
    rf.fit(X_train, y_train)
    results.append(evaluate_model("Random Forest", rf, X_test, y_test))

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
        lgbm = LGBMClassifier()
        lgbm.fit(X_train, y_train)
        results.append(evaluate_model("LightGBM", lgbm, X_test, y_test))

    results_df = pd.DataFrame(results)
    results_df.to_csv("results.csv", index=False)
    return results_df