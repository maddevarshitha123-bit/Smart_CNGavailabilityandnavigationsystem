"""Transparent station recommendation score (0-100, higher = better)."""

AVAIL_SCORE = {"High": 1.0, "Medium": 0.5, "Low": 0.1}
TRAFFIC_SCORE = {"Low": 1.0, "Medium": 0.6, "High": 0.2}

DEFAULT_WEIGHTS = {"distance": 0.25, "waiting": 0.30, "availability": 0.25,
                   "travel": 0.10, "traffic": 0.10}


def _inverse_norm(value, max_value):
    """Smaller value -> higher score (1 = best, 0 = worst)."""
    if max_value <= 0:
        return 1.0
    return max(0.0, 1 - value / max_value)


def score_station(s, max_dist, max_wait, max_travel, weights=None):
    """s needs: distance_km, pred_wait, pred_availability, travel_min, traffic."""
    w = weights or DEFAULT_WEIGHTS
    parts = {
        "distance": _inverse_norm(s["distance_km"], max_dist),
        "waiting": _inverse_norm(s["pred_wait"], max_wait),
        "availability": AVAIL_SCORE[s["pred_availability"]],
        "travel": _inverse_norm(s["travel_min"], max_travel),
        "traffic": TRAFFIC_SCORE[s["traffic"]],
    }
    total = sum(parts[k] * w[k] for k in parts) / sum(w.values()) * 100
    return round(total, 1), parts


def _reasons(s, parts):
    out = []
    if parts["distance"] >= 0.7: out.append("short distance")
    if parts["availability"] >= 1.0: out.append("high predicted availability")
    if parts["waiting"] >= 0.7: out.append("low predicted waiting time")
    if parts["traffic"] >= 1.0: out.append("light traffic")
    if parts["travel"] >= 0.7: out.append("quick travel")
    return out or ["best overall balance among the open stations"]


def recommend(stations, weights=None):
    """Rank a list of station dicts. Closed/maintenance stations are excluded.

    Returns a list sorted best-first, each with 'score', 'score_parts', 'why'.
    """
    open_st = [s for s in stations if s.get("status") == "open"]
    if not open_st:
        return []
    md = max(s["distance_km"] for s in open_st)
    mw = max(s["pred_wait"] for s in open_st)
    mt = max(s["travel_min"] for s in open_st)
    ranked = []
    for s in open_st:
        score, parts = score_station(s, md, mw, mt, weights)
        ranked.append({**s, "score": score, "score_parts": parts,
                       "why": " + ".join(_reasons(s, parts)).capitalize()})
    return sorted(ranked, key=lambda x: x["score"], reverse=True)
