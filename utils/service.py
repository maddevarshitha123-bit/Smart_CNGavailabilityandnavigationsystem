"""Glue layer: combines DB stations + distance + ML prediction for the pages."""
from datetime import datetime
from utils import database as db
from utils.distance import haversine, estimate_travel_minutes, navigation_url
from ml.predict import predict, ModelMissingError


def enrich_stations(user_lat, user_lon, now=None):
    """Return a list of station dicts with distance, travel time and AI prediction.

    Raises DatabaseError if MySQL is unreachable. If the ML model is missing, the
    admin-entered values are used and 'ml_ok' is False.
    """
    now = now or datetime.now()
    out, ml_ok = [], True
    for s in db.get_stations_with_status():
        lat, lon = float(s["latitude"]), float(s["longitude"])
        dist = haversine(user_lat, user_lon, lat, lon)
        queue = s["queue_length"] if s["queue_length"] is not None else 0
        traffic = s["traffic_level"] or "Medium"
        prev_wait = s["waiting_time"] if s["waiting_time"] is not None else 10
        prev_av = s["availability"] or "Medium"
        item = {**s, "latitude": lat, "longitude": lon, "distance_km": round(dist, 2),
                "travel_min": estimate_travel_minutes(dist), "traffic": traffic,
                "queue": queue, "admin_availability": s["availability"],
                "admin_wait": s["waiting_time"],
                "nav_url": navigation_url(lat, lon, user_lat, user_lon)}
        try:
            p = predict(s["station_id"], now.hour, now.weekday(), queue, traffic,
                        max(2, queue * 3), prev_wait, prev_av)
            item.update(pred_availability=p["availability"], pred_wait=p["waiting_time"],
                        confidence=p["confidence"])
        except ModelMissingError:
            ml_ok = False
            item.update(pred_availability=prev_av, pred_wait=prev_wait, confidence=None)
        out.append(item)
    for item in out:
        item["ml_ok"] = ml_ok
    return sorted(out, key=lambda x: x["distance_km"])
