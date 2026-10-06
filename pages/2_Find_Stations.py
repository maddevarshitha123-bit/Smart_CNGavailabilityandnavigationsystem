import streamlit as st
import folium
from streamlit_folium import st_folium
from utils.ui import setup_page, header, location_picker, BADGE
from utils.service import enrich_stations
from utils.database import DatabaseError

setup_page("Find Stations", "📍")
header("Find CNG Stations", "Nearby stations with AI predicted availability and waiting time")

lat, lon, label = location_picker()
try:
    stations = enrich_stations(lat, lon)
except DatabaseError as e:
    st.error(f"Could not load stations. {e}")
    st.stop()
except ValueError as e:
    st.error(f"Invalid location: {e}")
    st.stop()

if not stations:
    st.warning("No stations found. Ask the admin to add stations.")
    st.stop()
if not stations[0]["ml_ok"]:
    st.warning("ML model missing: showing last station-reported values instead of AI predictions. "
               "Run `python -m ml.train_model`.")

c1, c2, c3 = st.columns([2, 1, 1])
search = c1.text_input("Search by station name or address")
max_km = c2.slider("Max distance (km)", 1, 50, 25)
only_open = c3.checkbox("Only open stations", value=False)
shown = [s for s in stations if s["distance_km"] <= max_km
         and (not only_open or s["status"] == "open")
         and (search.lower() in (s["name"] + s["address"]).lower())]
if not shown:
    st.info("No stations match your filters.")
    st.stop()

m = folium.Map(location=[lat, lon], zoom_start=12)
folium.Marker([lat, lon], tooltip="You", icon=folium.Icon(color="blue", icon="user", prefix="fa")).add_to(m)
for s in shown:
    color = {"High": "green", "Medium": "orange", "Low": "red"}[s["pred_availability"]]
    folium.Marker([s["latitude"], s["longitude"]],
                  tooltip=f"{s['name']} ({s['distance_km']} km)",
                  popup=f"{s['name']}<br>AI predicted: {s['pred_availability']}",
                  icon=folium.Icon(color=color, icon="gas-pump", prefix="fa")).add_to(m)
st_folium(m, height=380, use_container_width=True, returned_objects=[])

for s in shown:
    pill = f"<span class='pill pill-{s['status']}'>{s['status'].title()}</span>"
    st.markdown(f"""<div class='station-card'><h4>{s['name']} {pill}</h4>
    📍 {s['address']}<br>
    <b>Distance:</b> {s['distance_km']} km &nbsp;|&nbsp; <b>Travel:</b> ~{s['travel_min']} min<br>
    {BADGE[s['pred_availability']]} <b>AI Predicted Availability:</b> {s['pred_availability']}
    &nbsp;|&nbsp; <b>Predicted wait:</b> {s['pred_wait']} min
    &nbsp;|&nbsp; <b>Queue:</b> {s['queue']} vehicles</div>""", unsafe_allow_html=True)
    a, b = st.columns([1, 4])
    a.link_button("🧭 Navigate", s["nav_url"])
    with b.expander("Station details"):
        st.write(f"**Phone:** {s['phone'] or 'N/A'}  \n**Hours:** {s['operating_hours']}  \n"
                 f"**Traffic:** {s['traffic']}  \n"
                 f"**Last admin update:** {s['updated_at'] or 'never'} "
                 f"(availability: {s['admin_availability'] or 'n/a'}, wait: {s['admin_wait'] if s['admin_wait'] is not None else 'n/a'} min)")
        if s["confidence"]:
            st.caption(f"Model confidence: {s['confidence']:.0%}")
st.caption("AI predictions are estimates from historical/sample data, not confirmed real-time availability.")
