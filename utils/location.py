"""Location helpers: manual search (geocoding) and validation."""
from config import DEFAULT_LOCATION, DEFAULT_LOCATION_NAME
from utils.distance import is_valid_coordinate


def geocode(query):
    """Convert a typed place name to (lat, lon, display_name) using free Nominatim.

    Returns None if the text is empty, nothing is found, or the network fails.
    """
    if not query or not query.strip():
        return None
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="smart_cng_college_project", timeout=6)
        result = geolocator.geocode(query.strip())
        if result and is_valid_coordinate(result.latitude, result.longitude):
            return result.latitude, result.longitude, result.address
    except Exception:
        return None
    return None


def default_location():
    return DEFAULT_LOCATION[0], DEFAULT_LOCATION[1], DEFAULT_LOCATION_NAME
