"""Shared Streamlit UI helpers: CSS, sidebar, and the location picker."""
import streamlit as st
from config import BASE_DIR
from utils import auth
from utils.location import geocode, default_location
from utils.distance import is_valid_coordinate

BADGE = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}


def setup_page(title, icon="⛽"):
    st.set_page_config(page_title=f"{title} | Smart CNG Finder", page_icon=icon, layout="wide")
    css = BASE_DIR / "assets" / "style.css"
    if css.exists():
        st.markdown(f"<style>{css.read_text()}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("### ⛽ Smart CNG Finder")
        user = auth.current_user()
        if user:
            st.success(f"Logged in: {user['name']} ({user['role']})")
            if st.button("Logout"):
                auth.logout(); st.rerun()
        else:
            st.info("Not logged in. Use the Account page.")


def header(title, subtitle=""):
    st.markdown(f"<div class='app-header'><h1>{title}</h1><p>{subtitle}</p></div>", unsafe_allow_html=True)


def location_picker():
    """Sidebar/section widget. Returns (lat, lon, label). Never forces GPS permission."""
    if "loc" not in st.session_state:
        st.session_state["loc"] = default_location()
    with st.expander("📍 Your location (optional)", expanded=False):
        c1, c2 = st.columns([3, 1])
        text = c1.text_input("Type an area or address", placeholder="e.g. Ameerpet, Hyderabad")
        if c2.button("Search", use_container_width=True):
            found = geocode(text)
            if found:
                st.session_state["loc"] = found
            else:
                st.warning("Place not found or network unavailable. Try another name, or use coordinates below.")
        c3, c4 = st.columns(2)
        lat = c3.number_input("Latitude", value=float(st.session_state["loc"][0]), format="%.6f")
        lon = c4.number_input("Longitude", value=float(st.session_state["loc"][1]), format="%.6f")
        if st.button("Use these coordinates"):
            if is_valid_coordinate(lat, lon):
                st.session_state["loc"] = (lat, lon, f"{lat:.4f}, {lon:.4f}")
            else:
                st.error("Invalid coordinates: latitude -90..90, longitude -180..180.")
        try:
            from streamlit_geolocation import streamlit_geolocation
            st.caption("Or use your device location (browser will ask permission):")
            g = streamlit_geolocation()
            if g and g.get("latitude") and is_valid_coordinate(g["latitude"], g["longitude"]):
                st.session_state["loc"] = (g["latitude"], g["longitude"], "Your device location")
        except Exception:
            st.caption("Device location not available here; use the search or coordinates.")
    lat, lon, label = st.session_state["loc"]
    st.caption(f"Using location: **{label}**")
    return lat, lon, label
