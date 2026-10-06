"""Distance, travel time, and navigation links."""
import math
from urllib.parse import urlencode
import requests
from config import AVG_SPEED_KMH

EARTH_RADIUS_KM = 6371.0088


def is_valid_coordinate(lat, lon):
    try:
        return -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
    except (TypeError, ValueError):
        return False


def haversine(lat1, lon1, lat2, lon2):
    """Straight-line ("as the crow flies") distance in km between two points.

    Simple idea: the Earth is a sphere, so we cannot use flat-plane Pythagoras.
    The formula turns the latitude/longitude gaps into an angle at the Earth's
    centre, then multiplies by the radius: distance = 2R * asin(sqrt(a)).
    """
    if not (is_valid_coordinate(lat1, lon1) and is_valid_coordinate(lat2, lon2)):
        raise ValueError("Invalid coordinates")
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def estimate_travel_minutes(distance_km, speed_kmh=AVG_SPEED_KMH):
    """Rough travel time from distance and an average city speed."""
    return max(1, round(distance_km / speed_kmh * 60))


def road_route(lat1, lon1, lat2, lon2, timeout=5):
    """Try the free OSRM demo server for real road distance/time.

    Returns (km, minutes, True) on success, or falls back to
    (haversine * 1.3 road factor, estimated minutes, False) on any failure.
    """
    try:
        url = (f"https://router.project-osrm.org/route/v1/driving/"
               f"{lon1},{lat1};{lon2},{lat2}?overview=false")
        data = requests.get(url, timeout=timeout).json()
        route = data["routes"][0]
        return route["distance"] / 1000, max(1, round(route["duration"] / 60)), True
    except Exception:
        km = haversine(lat1, lon1, lat2, lon2) * 1.3
        return km, estimate_travel_minutes(km), False


def navigation_url(dest_lat, dest_lon, origin_lat=None, origin_lon=None):
    """OpenStreetMap directions link (no API key needed)."""
    if not is_valid_coordinate(dest_lat, dest_lon):
        raise ValueError("Invalid destination coordinates")
    if origin_lat is not None and origin_lon is not None and is_valid_coordinate(origin_lat, origin_lon):
        q = urlencode({"engine": "fossgis_osrm_car",
                       "route": f"{origin_lat},{origin_lon};{dest_lat},{dest_lon}"})
        return f"https://www.openstreetmap.org/directions?{q}"
    return f"https://www.openstreetmap.org/?mlat={dest_lat}&mlon={dest_lon}#map=16/{dest_lat}/{dest_lon}"
