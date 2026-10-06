import streamlit as st
import pandas as pd
from utils.ui import setup_page, header, location_picker, BADGE
from utils.service import enrich_stations
from utils.recommendation import recommend, DEFAULT_WEIGHTS
from utils.database import DatabaseError

setup_page("Recommendations", "⭐")
header("Recommended Stations", "Ranked by a transparent weighted score, not only distance")

lat, lon, _ = location_picker()
with st.expander("⚖️ Adjust score weights"):
    w = {k: st.slider(k.title(), 0.0, 1.0, v, 0.05) for k, v in DEFAULT_WEIGHTS.items()}
if sum(w.values()) == 0:
    st.error("At least one weight must be above zero."); st.stop()

try:
    ranked = recommend(enrich_stations(lat, lon), w)
except DatabaseError as e:
    st.error(str(e)); st.stop()
if not ranked:
    st.warning("No open stations available right now."); st.stop()

best = ranked[0]
st.success(f"### ⭐ Recommended: {best['name']}  (score {best['score']}/100)")
a, b, c, d = st.columns(4)
a.metric("Distance", f"{best['distance_km']} km")
b.metric("Availability", f"{BADGE[best['pred_availability']]} {best['pred_availability']}")
c.metric("Waiting time", f"{best['pred_wait']} min")
d.metric("Traffic", best["traffic"])
st.write(f"**Why recommended:** {best['why']}")
st.link_button("🧭 Navigate", best["nav_url"])

st.subheader("All open stations ranked")
table = pd.DataFrame([{
    "Rank": i + 1, "Station": s["name"], "Score": s["score"], "Distance (km)": s["distance_km"],
    "Travel (min)": s["travel_min"], "AI Availability": s["pred_availability"],
    "Wait (min)": s["pred_wait"], "Traffic": s["traffic"]} for i, s in enumerate(ranked)])
st.dataframe(table, hide_index=True, use_container_width=True)

st.subheader("How the score is calculated")
st.markdown("Score = weighted average of five factors (each scaled 0 to 1) x 100. "
            "Distance, waiting time and travel time score higher when **smaller**; availability and traffic score higher when **better**.")
parts = pd.DataFrame([{"Station": s["name"], **{k.title(): round(v, 2) for k, v in s["score_parts"].items()}}
                      for s in ranked])
st.dataframe(parts, hide_index=True, use_container_width=True)
st.caption("Based on AI predictions from sample/historical data, not confirmed real-time availability.")
