"""Load the saved model and predict availability + waiting time."""
import joblib
import pandas as pd
from config import MODEL_PATH
from ml.train_model import LEVEL, FEATURES

_cache = None


class ModelMissingError(Exception):
    """Raised when model.pkl does not exist (run python -m ml.train_model)."""


def load_model():
    global _cache
    if _cache is None:
        if not MODEL_PATH.exists():
            raise ModelMissingError("Model file not found. Run: python -m ml.train_model")
        _cache = joblib.load(MODEL_PATH)
    return _cache


def predict(station_id, hour, day_of_week, queue_length, traffic_level,
            vehicles_per_hour, previous_waiting_time, previous_availability):
    """Return dict: availability, waiting_time (min), confidence, probabilities.

    These are ML ESTIMATES ("AI Predicted Availability"), not confirmed live data.
    """
    if traffic_level not in LEVEL or previous_availability not in LEVEL:
        raise ValueError("traffic_level / previous_availability must be Low, Medium or High")
    if not (0 <= hour <= 23 and 0 <= day_of_week <= 6):
        raise ValueError("hour must be 0-23 and day_of_week 0-6")
    if queue_length < 0 or vehicles_per_hour < 0 or previous_waiting_time < 0:
        raise ValueError("Numeric inputs cannot be negative")
    bundle = load_model()
    row = pd.DataFrame([{
        "station_id": station_id, "hour": hour, "day_of_week": day_of_week,
        "is_weekend": int(day_of_week >= 5), "queue_length": queue_length,
        "traffic_level": LEVEL[traffic_level], "vehicles_per_hour": vehicles_per_hour,
        "previous_waiting_time": previous_waiting_time,
        "previous_availability": LEVEL[previous_availability]}])[FEATURES]
    clf, reg = bundle["classifier"], bundle["regressor"]
    proba = clf.predict_proba(row)[0]
    probs = {c: float(p) for c, p in zip(clf.classes_, proba)}
    label = max(probs, key=probs.get)
    wait = max(0, int(round(float(reg.predict(row)[0]))))
    return {"availability": label, "waiting_time": wait,
            "confidence": probs[label], "probabilities": probs}
