"""Home page. Run with:  streamlit run app.py"""
import streamlit as st
from utils.ui import setup_page, header
from utils import database as db
from config import MODEL_PATH

setup_page("Home")
header("⛽ Smart CNG Finder", "AI-powered CNG availability prediction and navigation")

c1, c2, c3 = st.columns(3)
c1.markdown("#### 📍 Find stations\nSearch nearby CNG stations with distance and travel time.")
c2.markdown("#### 🤖 AI prediction\nPredicted availability and waiting time from historical patterns.")
c3.markdown("#### ⭐ Recommendations\nA transparent score, not just the nearest station.")

st.info("**Note:** Availability shown here is **AI Predicted Availability** based on historical "
        "(sample) data and station updates. It is **not** confirmed real-time fuel availability.")

st.subheader("System status")
s1, s2 = st.columns(2)
if db.test_connection():
    s1.success("Database: connected")
else:
    s1.error("Database: not reachable. Check .env and start MySQL, then run `python scripts/init_db.py`.")
if MODEL_PATH.exists():
    s2.success("ML model: loaded")
else:
    s2.warning("ML model: missing. Run `python generate_dataset.py` then `python -m ml.train_model`.")

st.markdown("Use the **sidebar** to open Account, Find Stations, AI Prediction, Recommendations and more.")
