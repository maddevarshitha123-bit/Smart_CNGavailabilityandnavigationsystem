import streamlit as st
from utils.ui import setup_page, header

setup_page("About", "ℹ️")
header("About the Project", "Smart CNG Availability Prediction and Navigation System Using AI")
st.markdown("""
**Purpose:** help CNG vehicle users find nearby stations, estimate queue/waiting time and choose a good station.

**How it works:** historical data + station updates + user input → Machine Learning (Random Forest / Linear Regression)
→ *AI Predicted Availability* and waiting time → transparent recommendation score → navigation link.

**Important limitations**
- No live IoT or fuel-company feed is connected. Predictions are estimates, **not confirmed real-time availability**.
- The included dataset and stations are **synthetic sample data** for demonstration.
- Model scores are on synthetic data and do not represent real-world accuracy.
- Routing uses free OpenStreetMap services; road distance falls back to straight-line estimates if they are unreachable.

**Technology:** Python, Streamlit, MySQL, Scikit-learn, Pandas, Plotly, Folium (OpenStreetMap), Nominatim, bcrypt.

**Future scope:** IoT sensors / station APIs for real-time data, retraining from live logs, mobile app, payment and booking.
""")
