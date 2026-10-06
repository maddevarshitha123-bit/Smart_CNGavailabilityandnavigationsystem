"""Run:  pytest -v      (DB tests are skipped automatically if MySQL is not set up)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from utils.distance import haversine, navigation_url, is_valid_coordinate, estimate_travel_minutes
from utils.recommendation import recommend
from utils.location import geocode


def test_distance_known():          # Hyderabad -> Secunderabad approx 7-9 km
    assert 5 < haversine(17.3850, 78.4867, 17.4399, 78.4983) < 10

def test_distance_zero():
    assert haversine(17.4, 78.5, 17.4, 78.5) == pytest.approx(0, abs=1e-9)

def test_invalid_coordinates():
    with pytest.raises(ValueError):
        haversine(200, 78, 17, 78)
    assert not is_valid_coordinate("abc", 5)

def test_empty_location():
    assert geocode("") is None and geocode("   ") is None

def test_travel_time_positive():
    assert estimate_travel_minutes(5) >= 1

def test_navigation_url():
    assert "17.4%2C78.5" in navigation_url(17.4, 78.5, 17.3, 78.4)
    assert "mlat=17.4" in navigation_url(17.4, 78.5)
    with pytest.raises(ValueError):
        navigation_url(999, 0)

def _st(name, d, w, av, tr="Low", status="open"):
    return dict(name=name, distance_km=d, pred_wait=w, pred_availability=av,
                travel_min=int(d * 2.4) + 1, traffic=tr, status=status)

def test_recommendation_not_just_nearest():
    near_bad = _st("near", 1, 40, "Low", "High")
    far_good = _st("far", 4, 5, "High", "Low")
    assert recommend([near_bad, far_good])[0]["name"] == "far"

def test_recommendation_skips_closed_and_empty():
    assert recommend([_st("x", 1, 1, "High", status="closed")]) == []
    assert recommend([]) == []

def test_ml_prediction():
    from ml.predict import predict, ModelMissingError
    try:
        r = predict(1, 8, 1, 10, "High", 40, 20, "Medium")
    except ModelMissingError:
        pytest.skip("model not trained")
    assert r["availability"] in ("High", "Medium", "Low")
    assert r["waiting_time"] >= 0

def test_ml_waiting_time_increases_with_queue():
    from ml.predict import predict, ModelMissingError
    try:
        a = predict(1, 8, 1, 2, "Low", 10, 5, "High")["waiting_time"]
        b = predict(1, 8, 1, 25, "Low", 10, 5, "High")["waiting_time"]
    except ModelMissingError:
        pytest.skip("model not trained")
    assert b > a

def test_ml_invalid_input():
    from ml.predict import predict, ModelMissingError
    with pytest.raises(ValueError):
        predict(1, 30, 1, 5, "Low", 10, 5, "High")

# ---- auth (need bcrypt/streamlit installed) ----
def test_password_rules():
    auth = pytest.importorskip("utils.auth")
    assert auth.validate_password("Abcdef1!") == []
    assert auth.validate_password("weak")
    assert auth.validate_email("a@b.com") and not auth.validate_email("bad")

def test_password_hashing():
    auth = pytest.importorskip("utils.auth")
    h = auth.hash_password("Abcdef1!")
    assert h != "Abcdef1!" and auth.verify_password("Abcdef1!", h) and not auth.verify_password("x", h)

# ---- database (skipped if MySQL not ready) ----
@pytest.fixture
def db():
    pytest.importorskip("mysql.connector")
    from utils import database
    if not database.test_connection():
        pytest.skip("MySQL not available")
    return database

def test_db_connection(db):
    assert db.test_connection()

def test_admin_station_crud(db):
    sid = db.add_station("TEST", "addr", 17.4, 78.5, "1", "24h", "open")
    db.add_status(sid, "High", 1, 2, "Low")
    assert any(s["station_id"] == sid for s in db.get_stations_with_status())
    db.delete_station(sid)
    assert not any(s["station_id"] == sid for s in db.get_stations_with_status())

def test_invalid_login(db):
    auth = pytest.importorskip("utils.auth")
    ok, _ = auth.login_user("nobody@nowhere.com", "Wrong@123")
    assert not ok
