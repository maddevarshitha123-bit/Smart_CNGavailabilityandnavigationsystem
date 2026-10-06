"""Train and compare ML models, then save the best ones to ml/model.pkl.

Run from the project root:  python -m ml.train_model
"""
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support,
                             confusion_matrix, mean_absolute_error,
                             mean_squared_error, r2_score)
from config import DATA_PATH, MODEL_PATH, METRICS_PATH

LEVEL = {"Low": 0, "Medium": 1, "High": 2}        # ordered categories -> numbers
FEATURES = ["station_id", "hour", "day_of_week", "is_weekend", "queue_length",
            "traffic_level", "vehicles_per_hour", "previous_waiting_time",
            "previous_availability"]
CLASSES = ["Low", "Medium", "High"]


def load_and_clean(path=DATA_PATH):
    df = pd.read_csv(path)
    df = df.dropna().drop_duplicates()
    df = df[(df["queue_length"] >= 0) & (df["waiting_time"] >= 0)]
    df["date"] = pd.to_datetime(df["date"])
    return df


def encode(df):
    """Turn text levels into numbers so the models can use them."""
    X = df.copy()
    X["traffic_level"] = X["traffic_level"].map(LEVEL)
    X["previous_availability"] = X["previous_availability"].map(LEVEL)
    return X[FEATURES]


def main():
    df = load_and_clean()
    # Time-aware split: train on the earlier 80% of dates, test on the latest 20%
    # (more realistic than a random split, because we predict the future).
    cutoff = df["date"].sort_values().iloc[int(len(df) * 0.8)]
    train, test = df[df["date"] < cutoff], df[df["date"] >= cutoff]
    Xtr, Xte = encode(train), encode(test)
    print(f"Train rows: {len(train)}   Test rows: {len(test)}")

    # ---------- Classification: availability ----------
    clf_models = {
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=3,
                                                random_state=42, n_jobs=-1),
    }
    clf_scores, best_clf, best_f1 = {}, None, -1
    for name, m in clf_models.items():
        m.fit(Xtr, train["availability"])
        pred = m.predict(Xte)
        p, r, f1, _ = precision_recall_fscore_support(
            test["availability"], pred, average="weighted", zero_division=0)
        acc = accuracy_score(test["availability"], pred)
        clf_scores[name] = dict(accuracy=acc, precision=p, recall=r, f1=f1)
        print(f"[Classifier] {name}: acc={acc:.3f} f1={f1:.3f}")
        if f1 > best_f1:
            best_f1, best_clf, best_clf_name = f1, m, name
    cm = confusion_matrix(test["availability"], best_clf.predict(Xte), labels=CLASSES)

    # ---------- Regression: waiting time ----------
    reg_models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_leaf=3,
                                               random_state=42, n_jobs=-1),
    }
    reg_scores, best_reg, best_mae = {}, None, 1e9
    for name, m in reg_models.items():
        m.fit(Xtr, train["waiting_time"])
        pred = m.predict(Xte)
        mae = mean_absolute_error(test["waiting_time"], pred)
        rmse = float(np.sqrt(mean_squared_error(test["waiting_time"], pred)))
        r2 = r2_score(test["waiting_time"], pred)
        reg_scores[name] = dict(mae=mae, rmse=rmse, r2=r2)
        print(f"[Regressor]  {name}: MAE={mae:.2f} min RMSE={rmse:.2f} R2={r2:.3f}")
        if mae < best_mae:
            best_mae, best_reg, best_reg_name = mae, m, name

    joblib.dump({"classifier": best_clf, "regressor": best_reg,
                 "features": FEATURES, "classes": CLASSES}, MODEL_PATH, compress=3)
    metrics = {"data_note": "Scores are on SYNTHETIC data, not real-world accuracy.",
               "classification": clf_scores, "regression": reg_scores,
               "best_classifier": best_clf_name, "best_regressor": best_reg_name,
               "confusion_matrix": {"labels": CLASSES, "matrix": cm.tolist()},
               "feature_importance": dict(zip(FEATURES,
                                              map(float, best_clf.feature_importances_)))
               if hasattr(best_clf, "feature_importances_") else {}}
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    print(f"Saved model -> {MODEL_PATH}\nBest classifier: {best_clf_name} | Best regressor: {best_reg_name}")


if __name__ == "__main__":
    main()
